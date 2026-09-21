#!/usr/bin/env python3
"""Build the whole favicon set from one of the candidate SVGs.

    python3 tools/make-icons.py option-1-head

Writes assets/favicon.svg, favicon.ico, apple-touch-icon.png, icon-192.png
and icon-512.png. Re-run it with a different option name to switch the icon
everywhere at once.
"""
import io
import re
import shutil
import sys
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "assets" / "icons"
OUT = ROOT / "assets"

CHOICES = ["option-1-head", "option-2-monogram", "option-3-silhouette"]


def render(src: Path, size: int) -> Image.Image:
    png = cairosvg.svg2png(url=str(src), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def tile_colour(src: Path) -> str:
    """The fill of the icon's background tile, so PNGs can be flattened onto it.

    iOS and Android paint their own shape behind a home-screen icon; a
    transparent corner there shows up as a black one."""
    m = re.search(r'<rect[^>]*fill="(#[0-9a-fA-F]{6})"', src.read_text())
    return m.group(1) if m else "#ffffff"


def flatten(im: Image.Image, colour: str) -> Image.Image:
    bg = Image.new("RGBA", im.size, colour)
    bg.alpha_composite(im)
    return bg.convert("RGB")


def main() -> int:
    choice = sys.argv[1] if len(sys.argv) > 1 else CHOICES[0]
    src = ICONS / f"{choice}.svg"
    if not src.exists():
        print(f"no such option: {choice}\npick one of: {', '.join(CHOICES)}")
        return 1

    shutil.copyfile(src, OUT / "favicon.svg")

    # .ico carries 16/32/48 so Windows and older browsers pick a sharp one.
    render(src, 48).save(
        OUT / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)]
    )

    colour = tile_colour(src)
    for name, size in [
        ("apple-touch-icon.png", 180),
        ("icon-192.png", 192),
        ("icon-512.png", 512),
    ]:
        flatten(render(src, size), colour).save(OUT / name, optimize=True)

    print(f"icon set built from {choice}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
