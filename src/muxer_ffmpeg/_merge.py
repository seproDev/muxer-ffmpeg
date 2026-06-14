from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path

from muxer_ffmpeg._ffmpeg import find_ffmpeg


class MergeError(RuntimeError):
    """Raised when FFmpeg exits unsuccessfully."""


def mux_streams(
    inputs: Sequence[str | Path],
    output: str | Path,
    *,
    overwrite: bool = True,
    extra_args: Sequence[str] = (),
) -> None:
    """Mux streams from multiple input files into one output using stream copy."""
    input_paths = _validate_inputs(inputs)
    output_path = Path(output)

    command: list[str] = []
    command.append("-y" if overwrite else "-n")
    for input_path in input_paths:
        command.extend(["-i", str(input_path)])
    for index in range(len(input_paths)):
        command.extend(["-map", str(index)])
    command.extend(["-c", "copy", *extra_args, str(output_path)])

    _run_ffmpeg(command)


def _validate_inputs(inputs: Sequence[str | Path]) -> list[Path]:
    if not inputs:
        msg = "At least one input file is required"
        raise ValueError(msg)

    paths = [Path(input_path) for input_path in inputs]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        msg = "Input file does not exist: " + ", ".join(missing)
        raise FileNotFoundError(msg)
    return paths


def _run_ffmpeg(args: Sequence[str]) -> None:
    executable = find_ffmpeg()
    command = [str(executable), "-hide_banner", "-nostdin", *args]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode == 0:
        return

    stderr = completed.stderr.strip()
    detail = f"\n{stderr}" if stderr else ""
    msg = f"ffmpeg failed with exit code {completed.returncode}{detail}"
    raise MergeError(msg)
