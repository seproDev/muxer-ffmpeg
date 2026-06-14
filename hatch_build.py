from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.tags import platform_tags


class CustomBuildHook(BuildHookInterface[Any]):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        if version != "editable":
            exe = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
            binary = Path("src/muxer_ffmpeg/_bin") / exe
            if not binary.is_file():
                msg = f"Missing bundled FFmpeg binary: {binary}. Run scripts/build_ffmpeg.py first."
                raise RuntimeError(msg)

        build_data["pure_python"] = False
        build_data["tag"] = f"py3-none-{next(platform_tags())}"
