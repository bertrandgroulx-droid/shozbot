#!/usr/bin/env python3
"""Build the share image and the LinkedIn-ready icon.

    python3 tools/make-social.py

Writes assets/og.png (the picture that shows up when a shozbot.com link is
pasted into a message) and assets/social/ (square versions of the Shozbot icon,
sized and padded for a LinkedIn profile or company page).
"""
import io
import re
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"          # static TTFs, see README there

PAPER = (250, 247, 242)
INK = (36, 31, 26)
PURPLE = (108, 79, 163)
MUTED = (109, 99, 88)


def tracked(draw, xy, text, font, fill, track):
    """Monospaced type sits too far apart at display size; close it up."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track


def share_image():
    og = Image.new("RGB", (1200, 630), PAPER)
    d = ImageDraw.Draw(og)
    d.rectangle([0, 0, 1200, 10], fill=PURPLE)

    robot = Image.open(ROOT / "assets/robot.png").convert("RGBA")
    h = 470
    robot = robot.resize((round(robot.width * h / robot.height), h), Image.LANCZOS)

    # -0.02em of tracking at 118px, to match .wordmark in site.css
    tracked(d, (92, 196), "shozbot",
            ImageFont.truetype(str(FONTS / "JetBrainsMono-Bold.ttf"), 118), INK, -2.4)
    d.text((94, 352), "Handmade apps for curious minds",
           font=ImageFont.truetype(str(FONTS / "Karla-Medium.ttf"), 42), fill=PURPLE)
    d.text((96, 424), "shozbot.com",
           font=ImageFont.truetype(str(FONTS / "JetBrainsMono-Medium.ttf"), 26), fill=MUTED)

    og.paste(robot, (1200 - 70 - robot.width, (630 - h) // 2 + 8), robot)
    og.save(ROOT / "assets/og.png", optimize=True)
    print("assets/og.png")


def linkedin_icon():
    """A square, opaque icon that also survives being cropped to a circle.

    LinkedIn crops profile pictures to a circle and paints its own background
    behind anything transparent. So: no transparency, the tile colour runs to
    every edge, and the drawing is inset far enough that a circular crop takes
    only flat colour.
    """
    src = ROOT / "assets/icons/studio-robot.svg"
    tile = re.search(r'<rect[^>]*fill="(#[0-9a-fA-F]{6})"', src.read_text()).group(1)

    master = 1200
    inset = round(master * 0.84)          # keeps the drawing inside a circle crop
    art = Image.open(io.BytesIO(cairosvg.svg2png(
        url=str(src), output_width=inset, output_height=inset))).convert("RGBA")

    canvas = Image.new("RGBA", (master, master), tile)
    canvas.alpha_composite(art, ((master - inset) // 2, (master - inset) // 2))
    flat = canvas.convert("RGB")

    out = ROOT / "assets/social"
    out.mkdir(exist_ok=True)
    for size in (1200, 400, 300):
        flat.resize((size, size), Image.LANCZOS).save(
            out / f"shozbot-icon-{size}.png", optimize=True)
        print(f"assets/social/shozbot-icon-{size}.png")


if __name__ == "__main__":
    share_image()
    linkedin_icon()
