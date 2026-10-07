#!/usr/bin/env python3
"""Build a LinkedIn carousel (a PDF, one page per slide) for one app.

    python3 tools/make-carousel.py better-weather SHOTS_DIR OUT_DIR

LinkedIn's "carousel" is a document post: upload a PDF and each page becomes
a swipeable slide. 1080x1350 (4:5 portrait) is used because every slide here
is built around a phone screenshot, and portrait gives the shot room while
taking the most feed height a post can.

SHOTS_DIR holds the screenshots as 1.png, 2.png ... matching the slide numbers
in the spec below. Any portrait phone shot works — it is fitted by height and
keeps its own aspect — so an iPhone and an Android shot both land correctly.
A missing shot draws a clearly labelled placeholder saying what to capture, so
the deck can be previewed before a single screenshot exists.

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
PURPLE = (108, 79, 163)
MUTED = (109, 99, 88)
LINE = (230, 222, 210)
PLACEHOLDER = (236, 232, 224)

MARGIN = 80
RULE = 12


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


def phone(shot_path, height, label):
    """A screenshot fitted to `height`, corners rounded, hairline border.

    No drawn bezel: a fake device frame is exactly the kind of stylising the
    brand avoids, and the rounded corners plus hairline already say "a phone".
    """
    if shot_path and shot_path.exists():
        im = Image.open(shot_path).convert("RGB")
        im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    else:
        im = Image.new("RGB", (round(height * 390 / 844), height), PLACEHOLDER)
        d = ImageDraw.Draw(im)
        f = font("JetBrainsMono-Medium.ttf", 26)
        lines = ["screenshot", "goes here", ""] + wrap(d, label, f, im.width - 60)
        y = im.height // 2 - len(lines) * 20
        for ln in lines:
            d.text(((im.width - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=MUTED)
            y += 40
    r = round(height * 0.055)
    im = rounded(im, r)
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, outline=LINE, width=3)
    return im


def footer(d, n, total, url):
    y = H - 62
    f_mark = font("JetBrainsMono-Bold.ttf", 30)
    x = tracked(d, (MARGIN, y), "shozbot", f_mark, INK, -30 * 0.02)
    d.text((x + 22, y + 5), url, font=font("JetBrainsMono-Medium.ttf", 22), fill=MUTED)
    counter = f"{n} / {total}"
    f_num = font("JetBrainsMono-Medium.ttf", 22)
    d.text((W - MARGIN - d.textlength(counter, font=f_num), y + 5), counter, font=f_num, fill=MUTED)


def slide_feature(n, total, spec, shots, url):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, RULE], fill=PURPLE)

    y = text_block(d, (MARGIN, 76), spec["title"], font("Karla-Medium.ttf", 68), INK, W - 2 * MARGIN, 78)
    text_block(d, (MARGIN, y + 10), spec["sub"], font("Karla-Medium.ttf", 36), PURPLE, W - 2 * MARGIN, 46)

    ph = phone(shots / f"{n}.png", 840, spec["shot"])
    im.paste(ph, ((W - ph.width) // 2, H - 110 - ph.height), ph)

    footer(d, n, total, url)
    return im


def slide_cover(n, total, spec, shots, url, app):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, RULE], fill=PURPLE)

    d.text((MARGIN, 70), app, font=font("JetBrainsMono-Medium.ttf", 30), fill=MUTED)
    y = text_block(d, (MARGIN, 120), spec["title"], font("Karla-Medium.ttf", 92), INK, W - 2 * MARGIN, 102)
    text_block(d, (MARGIN, y + 12), spec["sub"], font("Karla-Medium.ttf", 38), PURPLE, W - 2 * MARGIN, 48)

    ph = phone(shots / f"{n}.png", 780, spec["shot"])
    im.paste(ph, ((W - ph.width) // 2 - 60, H - 110 - ph.height), ph)

    # The robot keeps the cover company and is otherwise left off the feature
    # slides, where he would compete with the screenshot.
    robot = Image.open(ROOT / "assets/robot.png").convert("RGBA")
    rh = 300
    robot = robot.resize((round(robot.width * rh / robot.height), rh), Image.LANCZOS)
    im.paste(robot, (W - MARGIN - robot.width + 20, H - 130 - rh), robot)

    footer(d, n, total, url)
    return im


def slide_close(n, total, spec, url, path):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, RULE], fill=PURPLE)

    # Everything that has to be read sits above y=700 or left of x=500; the
    # robot stands bottom-right below and right of both, so nothing can collide
    # with him whatever the text wraps to.
    y = text_block(d, (MARGIN, 110), spec["title"], font("Karla-Medium.ttf", 80), INK, W - 2 * MARGIN, 90)
    y = text_block(d, (MARGIN, y + 24), spec["sub"], font("Karla-Medium.ttf", 38), MUTED, 620, 50)

    tracked(d, (MARGIN, y + 56), path, font("JetBrainsMono-Bold.ttf", 40), PURPLE, -40 * 0.02)

    robot = Image.open(ROOT / "assets/robot.png").convert("RGBA")
    rh = 480
    robot = robot.resize((round(robot.width * rh / robot.height), rh), Image.LANCZOS)
    im.paste(robot, (W - MARGIN - robot.width + 40, H - 110 - rh), robot)

    d.text((MARGIN, H - 150), "Handmade apps for curious minds", font=font("Karla-Medium.ttf", 30), fill=PURPLE)
    footer(d, n, total, url)
    return im


DECKS = {
    "better-weather": {
        "app": "Better Weather",
        "url": "shozbot.com/better-weather",
        "slides": [
            {"kind": "cover",
             "title": "The whole forecast on one screen.",
             "sub": "Then the rabbit holes.",
             "shot": "the main screen, straight after it loads"},
            {"title": "Swipe through time.",
             "sub": "48 hours back and 72 ahead. Seven days back and sixteen ahead. Yesterday is in there, so you can check whether it really was that bad.",
             "shot": "the hourly strip, swiped back into yesterday"},
            {"title": "Tap the moon.",
             "sub": "The real lunar surface, lit and tilted as it is tonight. Scrub it hour by hour through the week.",
             "shot": "the Moon panel, open"},
            {"title": "Find the Moon.",
             "sub": "Hold the phone flat and aim its top edge. Two cards say how far to turn and tilt, and the ring lights up when you are on it — above or below the horizon.",
             "shot": "Find the Moon, with the ring lit"},
            {"title": "Daylight through the year.",
             "sub": "A full year on one screen. The brighter band inside is the vitamin D window — the hours the sun is above 45°. For a good stretch of a Calgary winter it reads “none today”.",
             "shot": "the Daylight panel, scrubbed to a winter day that says none today"},
            {"title": "Where the sun is right now.",
             "sub": "Under the daylight chart: the latitude the sun is directly overhead today, which way it is moving, and how high it climbs at noon where you are standing.",
             "shot": "the Earth-tilt card under the Daylight panel"},
            {"title": "Live radar you can rewind.",
             "sub": "Animated precipitation, scrubbable back through the last few hours and forward into what is coming.",
             "shot": "the radar map, mid-scrub"},
            {"kind": "close",
             "title": "Free. No ads. No account.",
             "sub": "Add it to your home screen and it runs like an app — full screen, and it works offline from the last forecast.",
             "path": "shozbot.com/better-weather"},
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
        if kind == "cover":
            im = slide_cover(i, total, spec, shots, deck["url"], deck["app"])
        elif kind == "close":
            im = slide_close(i, total, spec, deck["url"], spec["path"])
        else:
            im = slide_feature(i, total, spec, shots, deck["url"])
        im.save(out / f"slide-{i}.png", optimize=True)
        pages.append(im)

    pdf = out / f"{sys.argv[1]}-carousel.pdf"
    pages[0].save(pdf, "PDF", save_all=True, append_images=pages[1:], resolution=150)
    print(f"{pdf}  {total} slides")


if __name__ == "__main__":
    main()
