#!/usr/bin/env python3
"""Build the LinkedIn banners.

    python3 tools/make-banner.py

Writes two, because LinkedIn uses two different shapes and crops each one
differently:

  assets/social/linkedin-banner-1584x396.png   a personal profile's background
  assets/social/linkedin-cover-1128x191.png    a company page's cover

Both leave the bottom-left corner empty on purpose. LinkedIn drops the profile
picture (or the page logo) over that corner, so anything put there is hidden
behind it — and the crop is tighter again on a phone, which is where most
people will see it. Everything that has to be readable therefore sits right of
the overlap and inside a margin.

Needs pillow, and the static TTFs in tools/fonts/.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"

PAPER = (250, 247, 242)
INK = (36, 31, 26)
PURPLE = (108, 79, 163)
MUTED = (109, 99, 88)


def tracked(draw, xy, text, font, fill, track):
    """Monospaced type sits too far apart at display size; close it up.

    Same -0.02em the wordmark carries in site.css.
    """
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x


def banner(path, size, *, rule, robot_h, robot_pad, robot_bottom, text_x,
           mark_px, tag_px, url_px, wordmark_y, tag_y, url_y):
    w, h = size
    im = Image.new("RGB", size, PAPER)
    d = ImageDraw.Draw(im)

    # The purple rule along the top, as on the share image.
    d.rectangle([0, 0, w, rule], fill=PURPLE)

    robot = Image.open(ROOT / "assets/robot.png").convert("RGBA")
    robot = robot.resize(
        (round(robot.width * robot_h / robot.height), robot_h), Image.LANCZOS
    )
    # Standing clear of the bottom edge: flush against it, the resin feet get
    # sliced off and it reads as a mistake rather than a crop.
    im.paste(robot, (w - robot_pad - robot.width, h - robot_h - robot_bottom), robot)

    tracked(d, (text_x, wordmark_y), "shozbot",
            ImageFont.truetype(str(FONTS / "JetBrainsMono-Bold.ttf"), mark_px),
            INK, -mark_px * 0.02)
    d.text((text_x + 2, tag_y), "Handmade apps for curious minds",
           font=ImageFont.truetype(str(FONTS / "Karla-Medium.ttf"), tag_px), fill=PURPLE)
    d.text((text_x + 3, url_y), "shozbot.com",
           font=ImageFont.truetype(str(FONTS / "JetBrainsMono-Medium.ttf"), url_px), fill=MUTED)

    im.save(path, optimize=True)
    print(path.relative_to(ROOT), im.size)


def main():
    out = ROOT / "assets/social"
    out.mkdir(parents=True, exist_ok=True)

    # Personal profile. The photo circle covers roughly the left 380px at the
    # bottom, so the type starts well clear of it.
    banner(out / "linkedin-banner-1584x396.png", (1584, 396),
           rule=8, robot_h=318, robot_pad=195, robot_bottom=26, text_x=430,
           mark_px=96, tag_px=34, url_px=22,
           wordmark_y=118, tag_y=246, url_y=306)

    # Company page. Shorter and wider, and the logo tile covers the left ~200px.
    banner(out / "linkedin-cover-1128x191.png", (1128, 191),
           rule=5, robot_h=152, robot_pad=78, robot_bottom=14, text_x=250,
           mark_px=52, tag_px=20, url_px=14,
           wordmark_y=50, tag_y=120, url_y=150)


if __name__ == "__main__":
    main()
