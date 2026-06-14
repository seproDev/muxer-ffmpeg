from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

FFMPEG_VERSION = "8.1.1"
FFMPEG_URL = f"https://ffmpeg.org/releases/ffmpeg-{FFMPEG_VERSION}.tar.xz"
FFMPEG_SHA256 = "b6863adde98898f42602017462871b5f6333e65aec803fdd7a6308639c52edf3"

CONFIGURE_FLAGS = [
    "--disable-everything",
    "--disable-autodetect",
    "--disable-debug",
    "--disable-doc",
    "--disable-network",
    "--disable-programs",
    "--disable-avdevice",
    "--disable-swscale",
    "--disable-swresample",
    "--disable-x86asm",
    "--disable-shared",
    "--enable-ffmpeg",
    "--enable-static",
    "--cpu=generic",
    "--pkg-config-flags=--static",
    "--enable-protocol=file,pipe",
    "--enable-demuxer=aac,ac3,av1,dts,dtshd,eac3,flac,flv,h264,hevc,live_flv,m4v,matroska,mov,mp3,mpegts,ogg,truehd,wav,webvtt,srt,ass,ttml",
    "--enable-muxer=adts,ac3,eac3,flac,flv,ipod,matroska,mov,mp3,mp4,mpegts,ogg,opus,wav,webm",
    "--enable-parser=aac,aac_latm,ac3,av1,dca,flac,h264,hevc,mpeg4video,mpegaudio,opus,vorbis,vp8,vp9,vvc",
    "--enable-bsf=aac_adtstoasc,av1_metadata,dca_core,eac3_core,extract_extradata,h264_metadata,h264_mp4toannexb,hevc_metadata,hevc_mp4toannexb,opus_metadata,truehd_core,vp9_metadata,vvc_metadata,vvc_mp4toannexb",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vendor-dir", type=Path, default=Path("vendor"))
    parser.add_argument("--target-package", type=Path, default=Path("src/muxer_ffmpeg/_bin"))
    args = parser.parse_args()

    source_dir = prepare_source(args.vendor_dir)
    install_dir = args.vendor_dir / "ffmpeg-install"
    build(source_dir, install_dir)
    install_binary(install_dir, args.target_package)


def prepare_source(vendor_dir: Path) -> Path:
    vendor_dir.mkdir(parents=True, exist_ok=True)
    archive = vendor_dir / f"ffmpeg-{FFMPEG_VERSION}.tar.xz"
    source_dir = vendor_dir / f"ffmpeg-{FFMPEG_VERSION}"

    if not archive.exists():
        print(f"Downloading {FFMPEG_URL}")
        urllib.request.urlretrieve(FFMPEG_URL, archive)

    verify_archive_hash(archive)

    if not source_dir.exists():
        with tarfile.open(archive) as tar:
            tar.extractall(vendor_dir, filter="data")

    return source_dir


def verify_archive_hash(archive: Path) -> None:
    with archive.open("rb") as archive_file:
        actual = hashlib.file_digest(archive_file, "sha256").hexdigest()
    if actual != FFMPEG_SHA256:
        msg = (
            f"FFmpeg {FFMPEG_VERSION} archive hash mismatch: expected {FFMPEG_SHA256}, got {actual}"
        )
        raise RuntimeError(msg)

    print(f"Verified FFmpeg {FFMPEG_VERSION} archive hash")


def build(source_dir: Path, install_dir: Path) -> None:
    if install_dir.exists():
        shutil.rmtree(install_dir)

    flags = [*CONFIGURE_FLAGS]
    if sys.platform == "win32":
        flags.extend(["--extra-ldflags=-static"])
    elif sys.platform == "darwin":
        flags.extend(["--cc=clang"])

    flags.append(f"--prefix={install_dir.resolve()}")
    configure = ["sh", "./configure"] if sys.platform == "win32" else ["./configure"]
    run([*configure, *flags], cwd=source_dir)

    jobs = os.cpu_count() or 2
    run(["make", f"-j{jobs}"], cwd=source_dir)
    run(["make", "install"], cwd=source_dir)


def install_binary(install_dir: Path, target_package: Path) -> None:
    exe = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    built = install_dir / "bin" / exe
    if not built.exists():
        raise FileNotFoundError(f"Expected FFmpeg binary was not produced: {built}")

    target_package.mkdir(parents=True, exist_ok=True)
    target = target_package / exe
    shutil.copy2(built, target)
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    size_mib = target.stat().st_size / (1024 * 1024)
    print(f"Installed bundled FFmpeg at {target} ({size_mib:.2f} MiB)")


def run(command: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


if __name__ == "__main__":
    main()
