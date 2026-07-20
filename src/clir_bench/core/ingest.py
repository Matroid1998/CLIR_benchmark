"""
Incremental ingestion machinery.

Built for the constraint that drove the EPO loader: multi-gigabyte archives must
be streamed, filtered and discarded rather than staged on disk, and a run that
dies halfway must resume without re-downloading or duplicating rows.

Nothing here knows what a document is -- a domain supplies the parser and the
filter. The pieces are the manifest (resume state), the archive streamer, and
the accumulator that keeps the best row per (family, language).
"""

from __future__ import annotations

import json
import os
import tarfile
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Optional, Sequence

# Cap on how much of a nested archive is held in memory at once.
MAX_NESTED_BYTES = int(os.environ.get("CLIR_MAX_NESTED_BYTES", 2 * 1024**3))


@dataclass
class Manifest:
    """Resumable ingest state, written atomically.

    Tracks which archive items have been processed and which document families
    have been written, so re-running appends only genuinely new rows. Losing
    this file means duplicate rows on the next run, so it is saved via a
    temp-file rename rather than an in-place write.
    """

    path: Path
    processed_items: set[str] = field(default_factory=set)
    processed_families: set[str] = field(default_factory=set)
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        path = Path(path)
        if not path.exists():
            return cls(path=path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            print(f"[manifest] unreadable at {path}; starting fresh")
            return cls(path=path)
        return cls(
            path=path,
            processed_items={str(x) for x in payload.get("processed_items", [])},
            processed_families={str(x) for x in payload.get("processed_families", [])},
            extra=payload.get("extra", {}),
        )

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "processed_items": sorted(self.processed_items),
            "processed_families": sorted(self.processed_families),
            "extra": self.extra,
        }
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=1), encoding="utf-8")
        tmp.replace(self.path)

    def is_processed(self, item_id: str) -> bool:
        return str(item_id) in self.processed_items

    def mark_processed(self, item_id: str, families: Sequence[str] = ()) -> None:
        self.processed_items.add(str(item_id))
        self.processed_families.update(str(f) for f in families)


# --------------------------------------------------------------------------- #
# Archive streaming
# --------------------------------------------------------------------------- #

def stream_archive_members(
    stream: Iterator[bytes],
    *,
    kind: str,
    keep: Callable[[str], bool] = lambda name: True,
    max_nested_bytes: int = MAX_NESTED_BYTES,
) -> Iterator[tuple[bytes, str]]:
    """Yield ``(payload, member_name)`` from a remote zip/tar byte stream.

    Nested archives are recursed into, which is how bulk deliveries package
    per-document files. Recursion buffers one nested archive at a time and
    refuses anything above ``max_nested_bytes`` so a pathological member cannot
    exhaust memory.
    """
    if kind == "zip":
        yield from _stream_zip(stream, keep=keep, max_nested_bytes=max_nested_bytes)
    elif kind == "tar":
        yield from _stream_tar(stream, keep=keep, max_nested_bytes=max_nested_bytes)
    else:
        raise ValueError(f"unsupported archive kind: {kind!r} (expected 'zip' or 'tar')")


def _stream_zip(
    stream: Iterator[bytes], *, keep: Callable[[str], bool], max_nested_bytes: int
) -> Iterator[tuple[bytes, str]]:
    from stream_unzip import stream_unzip

    for name_bytes, size, chunks in stream_unzip(stream):
        name = name_bytes.decode("utf-8", errors="replace")
        lowered = name.lower()
        if lowered.endswith((".zip", ".tar", ".tar.gz", ".tgz")):
            if size is not None and size > max_nested_bytes:
                print(f"[skip] nested archive too large to buffer: {name} ({size} bytes)")
                _drain(chunks)
                continue
            payload = b"".join(chunks)
            nested_kind = "zip" if lowered.endswith(".zip") else "tar"
            yield from stream_archive_members(
                iter([payload]), kind=nested_kind, keep=keep, max_nested_bytes=max_nested_bytes
            )
            continue
        if not keep(name):
            _drain(chunks)
            continue
        yield b"".join(chunks), name


def _stream_tar(
    stream: Iterator[bytes], *, keep: Callable[[str], bool], max_nested_bytes: int
) -> Iterator[tuple[bytes, str]]:
    buffer = BytesIO(b"".join(stream))
    with tarfile.open(fileobj=buffer, mode="r|*") as archive:
        for member in archive:
            if not member.isfile():
                continue
            name = member.name
            lowered = name.lower()
            handle = archive.extractfile(member)
            if handle is None:
                continue
            if lowered.endswith((".zip", ".tar", ".tar.gz", ".tgz")):
                if member.size > max_nested_bytes:
                    print(f"[skip] nested archive too large to buffer: {name} ({member.size} bytes)")
                    continue
                nested_kind = "zip" if lowered.endswith(".zip") else "tar"
                yield from stream_archive_members(
                    iter([handle.read()]),
                    kind=nested_kind,
                    keep=keep,
                    max_nested_bytes=max_nested_bytes,
                )
                continue
            if not keep(name):
                continue
            yield handle.read(), name


def _drain(chunks: Iterator[bytes]) -> None:
    """Consume a member we are skipping (the zip stream must stay in sync)."""
    for _ in chunks:
        pass


def http_stream(url: str, *, session: Any = None, chunk_size: int = 1 << 20, description: str = "") -> Iterator[bytes]:
    """Stream a URL's body in chunks, with a progress bar when the size is known."""
    import requests

    client = session or requests
    with client.get(url, stream=True, timeout=300) as response:
        response.raise_for_status()
        total = int(response.headers.get("Content-Length", 0)) or None
        try:
            from tqdm import tqdm

            bar = tqdm(total=total, unit="B", unit_scale=True, desc=description or "download")
        except ImportError:  # pragma: no cover
            bar = None
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                if bar is not None:
                    bar.update(len(chunk))
                yield chunk
        if bar is not None:
            bar.close()


# --------------------------------------------------------------------------- #
# Accumulation
# --------------------------------------------------------------------------- #

@dataclass
class MultilingualAccumulator:
    """Keeps the best row per (family, language) while streaming.

    A bulk delivery can contain several publications of the same document; the
    richest one wins, decided by a domain-supplied ``rank`` function. Filtering
    to families with enough language coverage happens at ``materialize`` time,
    once all versions have been seen.
    """

    rank: Callable[[Mapping[str, Any]], tuple] = lambda row: (0,)
    rows: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)

    def add(self, family: str, language: str, row: Mapping[str, Any]) -> None:
        if not family or not language:
            return
        key = (family, language)
        current = self.rows.get(key)
        if current is None or self.rank(row) > self.rank(current):
            self.rows[key] = dict(row)

    def materialize(
        self,
        *,
        min_languages: int = 2,
        languages: Sequence[str] = (),
        accept: Optional[Callable[[Sequence[Mapping[str, Any]]], bool]] = None,
    ) -> list[dict[str, Any]]:
        """Rows of every family covered in at least ``min_languages`` languages."""
        wanted = set(languages) if languages else None
        by_family: dict[str, list[dict[str, Any]]] = {}
        for (family, language), row in self.rows.items():
            if wanted is not None and language not in wanted:
                continue
            by_family.setdefault(family, []).append(row)

        out: list[dict[str, Any]] = []
        for family in sorted(by_family):
            group = by_family[family]
            if len({str(r.get("language", "")) for r in group}) < min_languages:
                continue
            if accept is not None and not accept(group):
                continue
            out.extend(group)
        return out

    def stats(self) -> dict[str, int]:
        families = {family for family, _ in self.rows}
        return {"rows": len(self.rows), "families": len(families)}


__all__ = [
    "MAX_NESTED_BYTES",
    "Manifest",
    "MultilingualAccumulator",
    "http_stream",
    "stream_archive_members",
]
