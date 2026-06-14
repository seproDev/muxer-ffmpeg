from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from muxer_ffmpeg import ffmpeg_version, find_ffmpeg


@pytest.fixture(autouse=True)
def clear_find_ffmpeg_cache() -> None:
    find_ffmpeg.cache_clear()


def test_find_ffmpeg_returns_bundled_binary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    ffmpeg = tmp_path / "ffmpeg"
    ffmpeg.write_text("", encoding="utf-8")
    monkeypatch.setattr("muxer_ffmpeg._ffmpeg._bundled_ffmpeg_path", lambda: ffmpeg)

    assert find_ffmpeg() == ffmpeg


def test_find_ffmpeg_is_cached(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    ffmpeg = tmp_path / "ffmpeg"
    ffmpeg.write_text("", encoding="utf-8")
    calls = 0

    def fake_bundled_ffmpeg_path() -> Path:
        nonlocal calls
        calls += 1
        return ffmpeg

    monkeypatch.setattr("muxer_ffmpeg._ffmpeg._bundled_ffmpeg_path", fake_bundled_ffmpeg_path)

    assert find_ffmpeg() == ffmpeg
    assert find_ffmpeg() == ffmpeg
    assert calls == 1


def test_find_ffmpeg_rejects_missing_bundled_binary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "muxer_ffmpeg._ffmpeg._bundled_ffmpeg_path",
        lambda: tmp_path / "missing-ffmpeg",
    )

    with pytest.raises(FileNotFoundError, match="No bundled ffmpeg"):
        find_ffmpeg()


def test_ffmpeg_version_runs_bundled_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any) -> Any:
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, "ffmpeg version 7.1.1\n", "")

    monkeypatch.setattr("muxer_ffmpeg._ffmpeg.find_ffmpeg", lambda: Path("ffmpeg"))
    monkeypatch.setattr("subprocess.run", fake_run)

    assert ffmpeg_version() == "ffmpeg version 7.1.1"
    assert commands == [["ffmpeg", "-version"]]


def test_ffmpeg_version_rejects_unexpected_output(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command: list[str], **kwargs: Any) -> Any:
        return subprocess.CompletedProcess(command, 0, "not ffmpeg\n", "")

    monkeypatch.setattr("muxer_ffmpeg._ffmpeg.find_ffmpeg", lambda: Path("ffmpeg"))
    monkeypatch.setattr("subprocess.run", fake_run)

    with pytest.raises(RuntimeError, match="Unexpected"):
        ffmpeg_version()
