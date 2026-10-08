#!/usr/bin/env python3
"""Build a LinkedIn carousel (a PDF, one page per slide) for one app.

    python3 tools/make-carousel.py better-weather SHOTS_DIR OUT_DIR

LinkedIn's "carousel" is a document post: upload a PDF and each page becomes
a swipeable slide. 1080x1350 (4:5 portrait) is used because every slide here
is built around a phone screenshot, and portrait gives the shot room while
taking the most feed height a post can.

SHOTS_DIR holds the screenshots, named by what they show (main.png, moon.png,
radar.png ...) and referenced by that name in the spec below — so reordering
the deck never means renumbering files. Any portrait phone shot works — it is fitted by height and
keeps its own aspect — so an iPhone and an Android shot both land correctly.
A missing shot draws a clearly labelled placeholder saying what to capture, so
the deck can be previewed before a single screenshot exists.

The screen is the slide. Title and a short line above, the screenshot taking
everything else, and nothing decorative: no purple rule, no robot — he appears
on the close only, where there is no screenshot to compete with. Bertrand's
call on the first cut (2026-10-08), and right: on a feature slide anything
that is not the app is in the way.

Needs pillow and the static TTFs in tools/fonts/.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"

W, H = 1080, 1350
PAPER = (250, 247, 242)
INK = (36, 31, 26)
MUTED = (109, 99, 88)
LINE = (230, 222, 210)
PLACEHOLDER = (236, 232, 224)

MARGIN = 72
FOOT = 96   # the footer band at the bottom of every slide


def font(name, px):
    return ImageFont.truetype(str(FONTS / name), px)


def tracked(draw, xy, text, fnt, fill, track):
    """The wordmark's -0.02em, as in site.css and make-banner.py."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + track
    return x


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, width, leading):
    x, y = xy
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def phone(shot_path, height, label, trim, keep=1.0, max_width=W - 2 * MARGIN):
    """A screenshot fitted to `height`, corners rounded, hairline border.

    `trim` = (top, bottom) pixels cut from the raw shot: the status bar with
    its clock and battery, and the home-indicator strip. Both are the phone,
    not the app, and the app paints its own background behind them, so the
    cut costs nothing and the screen reads as the app rather than a device.

    No drawn bezel: a fake device frame is exactly the kind of stylising the
    brand avoids, and the rounded corners plus hairline already say "a phone".
    """
    if shot_path and shot_path.exists():
        im = Image.open(shot_path).convert("RGB")
        # `keep` < 1 cuts the shot off at that fraction of its height: a panel
        # that opens over the app leaves the bottom half of the screen dimmed
        # and empty, and cropping to the panel lets the chart fill the slide.
        bottom = round(im.height * keep) if keep < 1 else im.height - trim[1]
        im = im.crop((0, trim[0], im.width, bottom))
        scale = min(height / im.height, max_width / im.width)
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    else:
        im = Image.new("RGB", (round(height * 1290 / 2517), height), PLACEHOLDER)
        d = ImageDraw.Draw(im)
        f = font("JetBrainsMono-Medium.ttf", 26)
        lines = ["screenshot", "goes here", ""] + wrap(d, label, f, im.width - 60)
        y = im.height // 2 - len(lines) * 20
        for ln in lines:
            d.text(((im.width - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=MUTED)
            y += 40
    r = round(height * 0.045)
    im = rounded(im, r)
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, outline=LINE, width=3)
    return im


def footer(d, n, total, url):
    y = H - FOOT + 30
    f_mark = font("JetBrainsMono-Bold.ttf", 28)
    x = tracked(d, (MARGIN, y), "shozbot", f_mark, INK, -28 * 0.02)
    d.text((x + 20, y + 5), url, font=font("JetBrainsMono-Medium.ttf", 21), fill=MUTED)
    counter = f"{n} / {total}"
    f_num = font("JetBrainsMono-Medium.ttf", 21)
    d.text((W - MARGIN - d.textlength(counter, font=f_num), y + 5), counter, font=f_num, fill=MUTED)


def slide_feature(n, total, spec, shots, deck, cover=False):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    width = W - 2 * MARGIN

    if cover:
        d.text((MARGIN, 56), deck["app"], font=font("JetBrainsMono-Medium.ttf", 26), fill=MUTED)
        y = text_block(d, (MARGIN, 96), spec["title"], font("Karla-Medium.ttf", 58), INK, width, 66)  # 58 keeps the title on one line
        y = text_block(d, (MARGIN, y + 8), spec["sub"], font("Karla-Medium.ttf", 36), MUTED, width, 46)
    else:
        y = text_block(d, (MARGIN, 60), spec["title"], font("Karla-Medium.ttf", 62), INK, width, 70)
        y = text_block(d, (MARGIN, y + 6), spec["sub"], font("Karla-Medium.ttf", 35), MUTED, width, 45)

    # The screenshot takes every pixel between the text and the footer.
    top = y + 26
    ph = phone(shots / spec["file"], H - FOOT - 16 - top, spec["shot"], spec.get("trim", deck["trim"]), spec.get("keep", 1.0))
    im.paste(ph, ((W - ph.width) // 2, top), ph)

    footer(d, n, total, deck["url"])
    return im


def slide_close(n, total, spec, deck):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # The text runs the full width: the robot stands bottom-right and the
    # two paragraphs finish well above him, so nothing has to clear him.
    width = W - 2 * MARGIN
    f_sub = font("Karla-Medium.ttf", 46)
    y = text_block(d, (MARGIN, 100), spec["title"], font("Karla-Medium.ttf", 80), INK, width, 90)
    for para in spec["sub"]:
        y = text_block(d, (MARGIN, y + 28), para, f_sub, MUTED, width, 60)
    tracked(d, (MARGIN, y + 52), deck["url"], font("JetBrainsMono-Bold.ttf", 40), INK, -40 * 0.02)

    robot = Image.open(ROOT / "assets/robot.png").convert("RGBA")
    rh = 500
    robot = robot.resize((round(robot.width * rh / robot.height), rh), Image.LANCZOS)
    im.paste(robot, (W - MARGIN - robot.width + 40, H - FOOT - 20 - rh), robot)

    d.text((MARGIN, H - FOOT - 50), "Handmade apps for curious minds", font=font("Karla-Medium.ttf", 30), fill=MUTED)
    footer(d, n, total, deck["url"])
    return im


DECKS = {
    "better-weather": {
        "app": "Better Weather",
        "url": "shozbot.com/better-weather",
        # iPhone Pro at 3x: 177px of status bar above the app, 102px of home
        # indicator below it. Other phones differ; the cut is per deck.
        "trim": (177, 102),
        # `keep`: where a panel opens over the app, the fraction of the shot's
        # height the panel reaches, measured off the screenshot. Below it the
        # screen is dimmed app, which the slide is better off without.
        "slides": [
            {"kind": "cover", "file": "main.png",
             "title": "The whole forecast on one screen.",
             "sub": "Summary, hourly and daily, with no scrolling down \u2014 everything scrolls sideways. Tap any hour or day for a chart, or drill into a summary line.",
             "shot": "the main screen, straight after it loads"},
            {"file": "conditions.png", "keep": 0.735,
             "title": "Tap an hour or a day.",
             "sub": "That day\u2019s temperature and feels-like, a cursor that reads the exact hour, and the rain underneath.",
             "shot": "the Conditions chart"},
            {"file": "moon.png",
             "title": "Tap the moon.",
             "sub": "The real lunar surface, lit and tilted for any hour you scrub to. Then tap Find the Moon and the phone points you at it.",
             "shot": "the Moon panel, open"},
            {"file": "daylight.png",
             "title": "Daylight through the year.",
             "sub": "A full year on one screen, with the clock changes marked. The brighter band is the vitamin D window \u2014 on October 8th at 51\u00b0N it already reads \u201cnone today\u201d.",
             "shot": "the Daylight panel, with the Earth-tilt card"},
            {"file": "wind.png", "keep": 0.52,
             "title": "Wind and gusts, hour by hour.",
             "sub": "Light to severe, arrows pointing the way it blows, and a readout for any hour you drag to.",
             "shot": "the Wind & gusts chart"},
            {"file": "air.png", "keep": 0.555,
             "title": "Air quality, explained.",
             "sub": "Canada\u2019s AQHI here, the US AQI elsewhere \u2014 where your reading sits on the scale, and the pollutants behind it.",
             "shot": "the Air quality panel"},
            {"file": "radar.png", "trim": (177, 102 + 140),  # this shot carries a black strip under the tabs
             "title": "Live radar you can rewind.",
             "sub": "Drag back through the last few hours, or forward into what\u2019s coming. Tap anywhere on the map and drop a pin \u2014 the whole forecast moves to that exact spot.",
             "shot": "the radar map, with a tapped forecast spot"},
            {"kind": "close",
             "title": "Free. No ads. No account.",
             "sub": ["Add it to your home screen and it runs like an app: full screen, no address bar, and it works offline from the last forecast.",
                     "Forecast by Open-Meteo, radar by RainViewer. No keys, no tracking, no sign-in \u2014 and nothing to buy, ever."]},
        ],
    },
}


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in DECKS:
        raise SystemExit(f"usage: make-carousel.py {{{'|'.join(DECKS)}}} SHOTS_DIR OUT_DIR")
    deck = DECKS[sys.argv[1]]
    shots, out = Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)

    total = len(deck["slides"])
    pages = []
    for i, spec in enumerate(deck["slides"], 1):
        kind = spec.get("kind", "feature")
        if kind == "close":
            im = slide_close(i, total, spec, deck)
        else:
            im = slide_feature(i, total, spec, shots, deck, cover=(kind == "cover"))
        im.save(out / f"slide-{i}.png", optimize=True)
        pages.append(im)

    pdf = out / f"{sys.argv[1]}-carousel.pdf"
    pages[0].save(pdf, "PDF", save_all=True, append_images=pages[1:], resolution=150)
    print(f"{pdf}  {total} slides")


if __name__ == "__main__":
    main()
