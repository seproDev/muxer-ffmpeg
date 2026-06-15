# muxer-ffmpeg

`muxer-ffmpeg` is a Python library for muxing media files with a bundled, minimal FFmpeg binary.

> [!WARNING]
> This software is currently alpha. The API may change.

## Usage

```python
from muxer_ffmpeg import mux_streams

mux_streams(["video.mp4", "audio.m4a"], "output.mp4")
```

## Development

Editable installs do not include FFmpeg automatically. Build the local bundled binary with:

```sh
uv run python scripts/build_ffmpeg.py
```

## License

The Python code in this repository is licensed under the [MIT License](LICENSE).

Binary wheels also include a bundled FFmpeg executable.
The bundled FFmpeg build is licensed under LGPL-2.1-or-later.
See [LICENSES/LGPL-2.1-or-later.txt](LICENSES/LGPL-2.1-or-later.txt) for the FFmpeg license text.
Source distributions do not include the FFmpeg executable.
