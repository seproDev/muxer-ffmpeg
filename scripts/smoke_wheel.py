from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from muxer_ffmpeg import ffmpeg_version, find_ffmpeg


def main() -> None:
    ffmpeg = find_ffmpeg()
    print(ffmpeg_version())

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subtitle = tmp_path / "input.srt"
        output = tmp_path / "output.mkv"
        subtitle.write_text(
            "1\n00:00:00,000 --> 00:00:01,000\nwheel smoke test\n",
            encoding="utf-8",
        )

        completed = subprocess.run(
            [
                str(ffmpeg),
                "-hide_banner",
                "-nostdin",
                "-y",
                "-i",
                str(subtitle),
                "-map",
                "0",
                "-c",
                "copy",
                str(output),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        if completed.stderr:
            print(completed.stderr, end="")
        completed.check_returncode()

        if not output.is_file() or output.stat().st_size == 0:
            msg = "FFmpeg smoke test did not produce an output file"
            raise RuntimeError(msg)


if __name__ == "__main__":
    main()
