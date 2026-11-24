"""Copy the bundled front-page image to the output directory.

Entry for make.fun news-image-20261124: "THE WORLD" front page summing up
Tuesday 24 November 2026. Standard library only; deterministic output.

The bundled image is validated before it is copied: it must be a whole PNG
of 1024x1024 pixels and at most 1 MiB, so a corrupt or oversized bundle can
never be submitted silently. The output is verified byte-for-byte against
the source after the copy.
"""

import hashlib
import os
import shutil
import struct
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
MAX_BYTES = 1_048_576
EXPECT_WIDTH = 1024
EXPECT_HEIGHT = 1024


def png_dimensions(data: bytes) -> tuple:
    """Read width/height from a PNG IHDR chunk (stdlib only)."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main() -> None:
    data = SOURCE.read_bytes()
    if len(data) == 0 or len(data) > MAX_BYTES:
        raise ValueError(f"entry.png size {len(data)} bytes is out of bounds")
    width, height = png_dimensions(data)
    if (width, height) != (EXPECT_WIDTH, EXPECT_HEIGHT):
        raise ValueError(f"entry.png is {width}x{height}, expected 1024x1024")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(SOURCE, target)
    written = target.read_bytes()
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(data).hexdigest():
        raise ValueError("output bytes differ from entry.png")
    print(f"wrote {target} ({len(written)} bytes, 1024x1024)")


if __name__ == "__main__":
    main()
