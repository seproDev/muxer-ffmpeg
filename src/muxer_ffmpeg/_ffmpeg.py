from __future__ import annotations

import subprocess
import sys
from functools import cache
from pathlib import Path


@cache
def find_ffmpeg() -> Path:
    """Return the bundled FFmpeg path."""
    path = _bundled_ffmpeg_path()
    if path.is_file():
        return path

    msg = (
        "No bundled ffmpeg binary was found. Install a platform wheel that includes "
        "ffmpeg, or run `uv run python scripts/build_ffmpeg.py` for local development."
    )
    raise FileNotFoundError(msg)


def _bundled_ffmpeg_path() -> Path:
    binary = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    return Path(__file__).parent / "_bin" / binary


def ffmpeg_version() -> str:
    """Run bundled FFmpeg and return its version banner first line."""
    executable = find_ffmpeg()
    completed = subprocess.run(
        [str(executable), "-version"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        detail = f"\n{stderr}" if stderr else ""
        msg = f"ffmpeg -version failed with exit code {completed.returncode}{detail}"
        raise RuntimeError(msg)

    first_line = completed.stdout.splitlines()[0] if completed.stdout else ""
    if not first_line.startswith("ffmpeg version "):
        msg = f"Unexpected ffmpeg version output: {first_line!r}"
        raise RuntimeError(msg)
    return first_line
