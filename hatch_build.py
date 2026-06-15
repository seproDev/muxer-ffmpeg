from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.tags import mac_platforms, platform_tags


class CustomBuildHook(BuildHookInterface[Any]):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        if version != "editable":
            exe = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
            binary = Path("src/muxer_ffmpeg/_bin") / exe
            if not binary.is_file():
                msg = f"Missing bundled FFmpeg binary: {binary}. Run scripts/build_ffmpeg.py first."
                raise RuntimeError(msg)

        build_data["pure_python"] = False
        build_data["tag"] = f"py3-none-{_platform_tag()}"


def _platform_tag() -> str:
    if sys.platform == "darwin":
        deployment_target = os.environ.get("MACOSX_DEPLOYMENT_TARGET")
        if deployment_target:
            major, minor, *_ = deployment_target.split(".")
            return next(mac_platforms((int(major), int(minor)), platform.machine()))

    return next(platform_tags())
