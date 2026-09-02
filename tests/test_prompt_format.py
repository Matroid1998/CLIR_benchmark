"""The prompt templates stay hard-wrapped.

Run ``python scripts/format_prompts.py`` to fix a failure here. The formatter
only ever splits an over-long line, so it can never change what the model is
sent beyond where the newlines fall -- it refuses to write otherwise.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMATTER = ROOT / "scripts" / "format_prompts.py"


def test_prompts_are_formatted() -> None:
    result = subprocess.run(
        [sys.executable, str(FORMATTER), "--check"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
