from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from muxer_ffmpeg import MergeError, mux_streams


def test_mux_streams_builds_stream_copy_command(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    inputs = [tmp_path / "video.mp4", tmp_path / "audio.m4a"]
    for input_path in inputs:
        input_path.write_text("", encoding="utf-8")
    output = tmp_path / "out.mp4"
    commands: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("muxer_ffmpeg._merge.find_ffmpeg", lambda: Path("ffmpeg"))
    monkeypatch.setattr(subprocess, "run", fake_run)

    mux_streams(inputs, output)

    assert commands == [
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-y",
            "-i",
            str(inputs[0]),
            "-i",
            str(inputs[1]),
            "-map",
            "0",
            "-map",
            "1",
            "-c",
            "copy",
            str(output),
        ]
    ]


def test_mux_streams_raises_on_ffmpeg_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "input.mp4"
    input_path.write_text("", encoding="utf-8")

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, "", "bad mux")

    monkeypatch.setattr("muxer_ffmpeg._merge.find_ffmpeg", lambda: Path("ffmpeg"))
    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(MergeError, match="bad mux"):
        mux_streams([input_path], tmp_path / "out.mp4")


def test_merge_requires_existing_inputs(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        mux_streams([tmp_path / "missing.mp4"], tmp_path / "out.mp4")
