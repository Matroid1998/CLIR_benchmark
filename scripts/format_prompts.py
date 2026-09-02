#!/usr/bin/env python3
"""Hard-wrap the prompt templates under ``src/clir_bench/domains``.

Prompt files are model input, so this formatter is deliberately narrow. It only
ever *splits* an over-long line; it never joins lines and never reflows a
paragraph. Two properties fall out of that, and both are asserted on every file
before anything is written:

* it is idempotent -- a second run finds no over-long lines left to split;
* it cannot change content -- the whitespace-stripped text is bit-identical, so
  the only thing that moves is where the newlines are.

Blocks that mimic the runtime input format are left verbatim, because the model
is being taught to read them in the shape it will actually receive:

    "### ..." markers       the block headers the generator emits at run time
    "[EN] ..." headers      unit headers inside worked examples
    "Act:" / "Cite as:" / "Location:" / "Title:"    the unit metadata block
    '"..."' excerpts        simulated source text
    JSON keys and braces    the output-contract examples the model copies

Indented prose is *not* exempt: the rubrics carry long indented commentary
("  → The prohibition comes from ...") that wraps under its own indent.

Everything else wraps to --width display columns with continuation lines
indented two spaces. Width is East-Asian aware and Chinese
breaks after its punctuation, so zh.txt wraps as well as en.txt does without a
line ever landing inside a word.

    python scripts/format_prompts.py            # rewrite in place
    python scripts/format_prompts.py --check    # exit 1 if anything would change
"""

from __future__ import annotations

import argparse
import unicodedata
from collections.abc import Iterable, Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT_ROOT = ROOT / "src" / "clir_bench" / "domains"

DEFAULT_WIDTH = 100
CONTINUATION_INDENT = "  "

# Prefixes that mark a line as part of a block shaped like the model's runtime
# input or like the JSON output contract. Taken from what the context builders
# actually emit -- "### ..." headers, "[EN] Article 5 — ..." unit headers, the
# "  Act: ..." metadata block (eurlex_context.py, un_context.py) -- plus the
# quoted source bodies and the JSON keys and braces of the output examples.
_METADATA_KEYS = ("Act:", "Cite as:", "Location:", "Title:")
_VERBATIM_PREFIXES = ("###", "[", "{", "}", "]", '"') + _METADATA_KEYS

# CJK has no spaces, so a break is offered only after one of these marks. Every
# unbreakable run the prompts contain then fits inside the default width, and no
# Chinese word is ever split down the middle.
_CJK_BREAK_AFTER = set("、。，．；：！？）】》〉」』…")

# Kinsoku shori: characters that may not open a line, and may not close one.
_NO_BREAK_BEFORE = set("、。，．：；！？）】》〉」』”’…%") | set(",.;:!?)]}")
_NO_BREAK_AFTER = set("（【《〈「『“‘") | set("([{")


def display_width(text: str) -> int:
    """Column count, counting East Asian wide and fullwidth glyphs as two."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


def is_verbatim(line: str) -> bool:
    """True for a line this formatter must not touch.

    Indentation alone is not enough: the rubrics carry plenty of long indented
    prose ("  → The prohibition comes from ...") that is worth wrapping. What is
    protected is a line *shaped* like the model's input or output contract.
    """
    stripped = line.strip()
    return not stripped or stripped.startswith(_VERBATIM_PREFIXES)


def json_span(text: str, start: int) -> int | None:
    """End of the balanced JSON literal opening at ``start``, or None.

    Used to keep an inline literal -- '{"question": "...", ...}', '["111", "110"]'
    -- on one line, so prose can wrap around the examples the model copies
    without a newline landing inside one. A bracket run holding no quote (an
    "[EN]" tag, a "(fact pattern → provision)" aside) is not a literal.
    """
    depth = 0
    in_string = escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
            if depth == 0:
                end = index + 1
                return end if '"' in text[start:end] else None
            if depth < 0:
                return None
    return None


def _atoms(line: str) -> list[tuple[str, str, bool]]:
    """Split into (separator, token, may_break_before) triples.

    A token is one JSON literal, or one run of non-space characters ending at a
    CJK punctuation mark. So Latin breaks only at spaces and CJK only after
    punctuation, and no word of either script is ever split. The separator is the
    original whitespace, kept verbatim when the line does not break there and
    dropped when it does.
    """
    atoms: list[tuple[str, str, bool]] = []
    separator = ""
    index, length = 0, len(line)
    while index < length:
        if line[index].isspace():
            start = index
            while index < length and line[index].isspace():
                index += 1
            separator = line[start:index]
            continue
        if line[index] in "[{":
            literal_end = json_span(line, index)
            if literal_end is not None:
                atoms.append((separator, line[index:literal_end], True))
                separator = ""
                index = literal_end
                continue
        start = index
        while index < length and not line[index].isspace():
            index += 1
            if line[index - 1] in _CJK_BREAK_AFTER:
                break
            if index < length and line[index] in "[{" and json_span(line, index):
                break
        atoms.append((separator, line[start:index], True))
        separator = ""

    resolved: list[tuple[str, str, bool]] = []
    for position, (separator, token, _) in enumerate(atoms):
        previous = atoms[position - 1][1] if position else ""
        may_break = bool(previous) and (bool(separator) or previous[-1] in _CJK_BREAK_AFTER)
        if may_break and token[0] in _NO_BREAK_BEFORE:
            may_break = False
        if may_break and previous[-1] in _NO_BREAK_AFTER:
            may_break = False
        if may_break and token == "-":
            # A continuation opening with "- " would read as a new list item.
            may_break = False
        resolved.append((separator, token, may_break))
    return resolved


def wrap_line(line: str, width: int, indent: str = "") -> list[str]:
    """Greedily split one long line, keeping ``indent`` and hanging the rest.

    A token wider than ``width`` overflows rather than being cut: breaking before
    something that cannot fit anyway only orphans the text in front of it. So
    does a trailing run that may not open a line (closing punctuation, a
    stranded "%").
    """
    continuation = indent + CONTINUATION_INDENT
    lines: list[str] = []
    current = ""
    for separator, token, may_break in _atoms(line.strip()):
        if not current:
            current = indent + token
            continue
        candidate = current + separator + token
        fits_alone = display_width(continuation + token) <= width
        if may_break and fits_alone and display_width(candidate) > width:
            lines.append(current)
            current = continuation + token
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def format_text(text: str, width: int = DEFAULT_WIDTH) -> str:
    """Normalise line endings and whitespace, then split over-long prose."""
    out: list[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw.rstrip()
        if is_verbatim(line) or display_width(line) <= width:
            out.append(line)
        else:
            indent = line[: len(line) - len(line.lstrip())]
            out.extend(wrap_line(line, width, indent))
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out) + "\n" if out else ""


def _canonical(text: str) -> str:
    """The text with every whitespace character removed."""
    return "".join(text.split())


def collect(paths: Iterable[Path]) -> Iterator[Path]:
    for path in paths:
        if path.is_dir():
            yield from path.rglob("*.txt")
        elif path.suffix == ".txt":
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths", nargs="*", type=Path, help=f"files or directories (default: {PROMPT_ROOT})"
    )
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="display columns")
    parser.add_argument(
        "--check", action="store_true", help="report what would change and exit 1 if anything would"
    )
    args = parser.parse_args()

    changed: list[Path] = []
    files = sorted(collect(args.paths or [PROMPT_ROOT]))
    for path in files:
        original = path.read_text(encoding="utf-8")
        formatted = format_text(original, args.width)
        if _canonical(original) != _canonical(formatted):
            parser.exit(2, f"{path}: refusing to write, content would change\n")
        if formatted != format_text(formatted, args.width):
            parser.exit(2, f"{path}: refusing to write, formatting is not stable\n")
        if formatted != original:
            changed.append(path)
            if not args.check:
                path.write_text(formatted, encoding="utf-8")

    for path in changed:
        print(f"{'would reformat' if args.check else 'reformatted'} {path.relative_to(ROOT)}")
    verb = "would be reformatted" if args.check else "reformatted"
    print(f"{len(changed)} {verb}, {len(files) - len(changed)} already formatted")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
