"""
Bounded parallel execution with a serial fallback.

The thread-pool-with-progress-bar block was re-implemented in every generator.
One implementation here; ``workers <= 1`` runs serially so a stack trace during
debugging is not buried in a pool.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, Iterator, Optional, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def run_tasks(
    items: Sequence[T],
    fn: Callable[[T], R],
    *,
    workers: int = 1,
    description: str = "working",
    show_progress: bool = True,
) -> Iterator[R]:
    """Apply ``fn`` to each item, yielding results as they complete.

    Results arrive out of order when ``workers > 1``; callers that need a stable
    order sort afterwards. Exceptions propagate -- a failing item should not be
    silently dropped from a dataset build.
    """
    progress = _progress(len(items), description, show_progress)

    if workers <= 1:
        for item in items:
            yield fn(item)
            progress.update(1)
        progress.close()
        return

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(fn, item) for item in items]
        for future in as_completed(futures):
            yield future.result()
            progress.update(1)
    progress.close()


def _progress(total: int, description: str, enabled: bool):
    if not enabled:
        return _NullProgress()
    try:
        from tqdm import tqdm

        return tqdm(total=total, desc=description)
    except ImportError:  # pragma: no cover
        return _NullProgress()


class _NullProgress:
    def update(self, _n: int = 1) -> None:
        pass

    def close(self) -> None:
        pass


__all__ = ["run_tasks"]
