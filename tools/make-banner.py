#!/usr/bin/env python3
"""Build the LinkedIn banners.

    python3 tools/make-banner.py

Writes two, because LinkedIn uses two different shapes and crops each one
differently:

  assets/social/linkedin-banner-1584x396.png   a personal profile's background
  assets/social/linkedin-cover-1128x191.png    a company page's cover
  assets/social/shozbot-banner-1536x768.png    a 2:1 image, asked for by size
  assets/social/shozbot-banner-1512x256.png    a 5.9:1 strip, asked for by size
  assets/social/shozbot-banner-4200x700.png    a 6:1 strip, asked for by size
  assets/social/youtube-banner-2560x1440.png   the YouTube channel banner

The YouTube one is a different problem again: YouTube takes a 2560x1440 image
and shows a different crop of it on every screen — the whole thing on a TV, a
2560x423 strip across a laptop, and only the middle 1546x423 on a phone. So
everything that matters is composed inside that central 1546x423 "safe area",
at the same proportions as the LinkedIn profile banner, and the rest of the
canvas is plain paper. There is no purple rule: on a TV it would cut across
the middle of the picture.

The two LinkedIn ones leave the bottom-left corner empty on purpose. LinkedIn drops the profile
picture (or the page logo) over that corner, so anything put there is hidden
behind it — and the crop is tighter again on a phone, which is where most
people will see it. Everything that has to be readable therefore sits right of
the overlap and inside a margin.

The 1536x768 one is not laid out around that overlap, because it is not a
profile slot: it is a standalone 2:1 image, so it is composed centred and the
robot is given the room the taller shape allows.

Needs pillow, and the static TTFs in tools/fonts/.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"

PAPER = (244, 245, 247)   # site --paper, cool neutral since 2026-10-11
INK = (26, 27, 30)
PURPLE = (108, 79, 163)
MUTED = (101, 106, 115)


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
           mark_px, tag_px, url_px, wordmark_y, tag_y, url_y, canvas=None):
    """Compose one banner. With `canvas`, the composition is pasted centred on
    a larger plain canvas of that size, for a slot that crops to its middle."""
    w, h = size
    im = Image.new("RGB", size, PAPER)
    d = ImageDraw.Draw(im)

    # The purple rule along the top, as on the share image.
    if rule > 0:
        d.rectangle([0, 0, w, rule], fill=PURPLE)

    robot = Image.open(ROOT / "assets/robot.png").convert("RGBA")
    # The cut-out is 766x900. Asking for more than that stretches a photograph
    # past its own resolution, and the mohawk fibres and wire limbs are exactly
    # what goes to mush first — so refuse rather than quietly ship a soft one.
    if robot_h > robot.height:
        raise SystemExit(
            f"{path.name}: robot_h={robot_h} exceeds the photo's {robot.height}px. "
            "Re-cut a larger robot.png from assets/photos/ rather than upscaling."
        )
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

    if canvas:
        full = Image.new("RGB", canvas, PAPER)
        full.paste(im, ((canvas[0] - w) // 2, (canvas[1] - h) // 2))
        im = full

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

    # 1512x256, asked for by size. It is the same 5.9:1 shape as the company
    # cover above, so it is drawn at those proportions scaled up rather than by
    # enlarging that PNG, which would soften the type and the photograph. The
    # bottom-left is kept clear on the same reasoning as the cover: the shape
    # says this is likely to sit under a logo, and the empty corner costs
    # nothing if it turns out not to.
    banner(out / "shozbot-banner-1512x256.png", (1512, 256),
           rule=7, robot_h=228, robot_pad=112, robot_bottom=12, text_x=310,
           mark_px=70, tag_px=27, url_px=18,
           wordmark_y=66, tag_y=160, url_y=200)

    # 4200x700, asked for by size. Near enough the 1512x256's shape, but not a
    # LinkedIn slot either, so it follows the 1536x768 above and is composed for
    # itself rather than around a logo — the type starts nearer the left edge
    # than the cover's does. The robot lands at 633px tall against a 900px
    # original, so it is still being scaled down and stays sharp.
    banner(out / "shozbot-banner-4200x700.png", (4200, 700),
           rule=18, robot_h=616, robot_pad=300, robot_bottom=34, text_x=380,
           mark_px=180, tag_px=60, url_px=38,
           wordmark_y=175, tag_y=405, url_y=495)

    # YouTube. Composed inside the 1546x423 the phone shows, on the 2560x1440
    # YouTube asks for. Nothing overlaps it, so the type starts near the left
    # of the safe area and the robot stands at its right. Two-step verification
    # is not the only thing YouTube is strict about: a banner under 2048x1152
    # is refused outright, so the canvas size is not negotiable.
    banner(out / "youtube-banner-2560x1440.png", (1546, 423),
           rule=0, robot_h=372, robot_pad=90, robot_bottom=24, text_x=110,
           mark_px=110, tag_px=38, url_px=24,
           wordmark_y=108, tag_y=250, url_y=318, canvas=(2560, 1440))

    # A 2:1 image at the size Bertrand asked for. Nothing overlaps it, so it is
    # balanced for its own sake: type left, robot right, both given the room the
    # taller shape allows.
    banner(out / "shozbot-banner-1536x768.png", (1536, 768),
           rule=12, robot_h=600, robot_pad=110, robot_bottom=44, text_x=120,
           mark_px=150, tag_px=50, url_px=30,
           wordmark_y=250, tag_y=452, url_y=540)


if __name__ == "__main__":
    main()
