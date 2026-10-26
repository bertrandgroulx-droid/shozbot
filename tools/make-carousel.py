#!/usr/bin/env python3
"""Build a LinkedIn carousel (a PDF, one page per slide) for one app.

    python3 tools/make-carousel.py better-weather SHOTS_DIR OUT_DIR
    python3 tools/make-carousel.py statterbrain assets/social/carousels/statterbrain OUT_DIR

LinkedIn's "carousel" is a document post: upload a PDF and each page becomes
a swipeable slide. 1080x1350 (4:5 portrait) is used because every slide here
is built around a phone screenshot, and portrait gives the shot room while
taking the most feed height a post can. A desktop app's deck sets "size" to a
square instead: a landscape shot on a portrait slide leaves half of it empty.

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

W, H = 1080, 1350   # the default, 4:5 around a phone shot; a deck may set "size"
PAPER = (244, 245, 247)   # site --paper, cool neutral since 2026-10-11
INK = (26, 27, 30)
MUTED = (101, 106, 115)
LINE = (226, 228, 233)
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


def phone(shot_path, height, label, trim, keep=1.0, max_width=None, crop=None):
    """A screenshot fitted to `height`, corners rounded, hairline border.

    `trim` = (top, bottom) pixels cut from the raw shot: the status bar with
    its clock and battery, and the home-indicator strip. Both are the phone,
    not the app, and the app paints its own background behind them, so the
    cut costs nothing and the screen reads as the app rather than a device.

    No drawn bezel: a fake device frame is exactly the kind of stylising the
    brand avoids, and the rounded corners plus hairline already say "a phone".
    """
    if max_width is None:
        max_width = W - 2 * MARGIN
    if shot_path and shot_path.exists():
        im = Image.open(shot_path).convert("RGB")
        # `crop` = (left, top, right, bottom) in the shot's own pixels, applied
        # first: a desktop app's shot carries its sidebar, which every slide
        # would repeat, so the tool slides keep only the page to its right.
        if crop:
            im = im.crop(crop)
        # `keep` < 1 cuts the shot off at that fraction of its height: a panel
        # that opens over the app leaves the bottom half of the screen dimmed
        # and empty, and cropping to the panel lets the chart fill the slide.
        bottom = round(im.height * keep) if keep < 1 else im.height - trim[1]
        im = im.crop((0, trim[0], im.width, bottom))
        scale = min(height / im.height, max_width / im.width)
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    else:
        aspect = 2280 / 1800 if W == H else 1290 / 2517   # a desktop page, or a phone
        im = Image.new("RGB", (min(round(height * aspect), max_width), height), PLACEHOLDER)
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
    ph = phone(shots / spec["file"], H - FOOT - 16 - top, spec["shot"], spec.get("trim", deck["trim"]), spec.get("keep", 1.0),
               crop=spec.get("crop", deck.get("crop") if not cover else None))
    im.paste(ph, ((W - ph.width) // 2, top), ph)

    footer(d, n, total, deck["url"])
    return im


def slide_close(n, total, spec, deck):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # The text runs the full width: the robot stands bottom-right and the
    # two paragraphs finish well above him, so nothing has to clear him.
    robot = Image.open(ROOT / "assets/robot.png").convert("RGBA")
    rh = deck.get("robot_height", 500)
    robot = robot.resize((round(robot.width * rh / robot.height), rh), Image.LANCZOS)

    # On a square slide there is no room above the robot for the whole text,
    # so the paragraphs stop short of him instead: a narrower column.
    width = W - 2 * MARGIN - (robot.width - 20 if W == H else 0)
    f_sub = font("Karla-Medium.ttf", 46 if W < H else 38)
    y = text_block(d, (MARGIN, 100 if W < H else 72), spec["title"], font("Karla-Medium.ttf", 80 if W < H else 64), INK, W - 2 * MARGIN, 90 if W < H else 74)
    for para in spec["sub"]:
        y = text_block(d, (MARGIN, y + 28), para, f_sub, MUTED, width, 60 if W < H else 50)
    tracked(d, (MARGIN, y + 52), deck["url"], font("JetBrainsMono-Bold.ttf", 40), INK, -40 * 0.02)
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
    "statterbrain": {
        "app": "Statterbrain",
        "url": "shozbot.com/statterbrain",
        # A desktop app: landscape shots, so the slide is square rather than
        # 4:5, and the robot on the close is smaller to leave the text room.
        "size": (1080, 1080),
        "robot_height": 420,
        # The shots are the app itself at 1440x900, captured at 2x from the
        # built app with its own example datasets (the oil and gas set the
        # course works through), so there is no status bar to trim. The tool
        # slides drop the sidebar (432px wide at 2x, measured off the shot);
        # the cover keeps it.
        "trim": (0, 0),
        "crop": (440, 0, 2880, 1800),
        "slides": [
            {"kind": "cover", "file": "welcome.png",
             "title": "A statistics workbench for type-well curve work.",
             "sub": "Probit Analysis, Multivariate Analysis, Type-well Curve, Sequential Accumulation and the Estimator Tool. CSV in, charts and tables out. Runs in the browser; the data stays on your computer.",
             "shot": "the Welcome page"},
            {"file": "probit-analysis.png",
             "title": "Probit Analysis",
             "sub": "Cumulative probability plots on log and linear axes, with the best fit and its R\u00b2, the mean, its percentile location and the P10:P90 ratio. Group by any column to test what separates the distribution.",
             "shot": "Probit Analysis \u2014 Plot, grouped"},
            {"file": "multivariate-analysis.png",
             "title": "Multivariate Analysis",
             "sub": "Parallel coordinate distributions and input optimization distributions, each input ranked by separation, eta squared: the share of its variance explained by target quartile. Feature importance and a correlation matrix complete the set.",
             "shot": "Multivariate Analysis \u2014 Parallel Coordinates"},
            {"file": "type-well-curve.png", "keep": 0.845,  # cut at the legend; the values table below it is not the slide
             "title": "Type-well Curve",
             "sub": "Average production profiles from monthly well history: condensed to producing months, aligned on first production or peak rate, as calendar-day rate or cumulative, with P10, P50, P90 and well count by month and by group.",
             "shot": "Type-well Curve \u2014 Plot, grouped by Area"},
            {"file": "sequential-accumulation.png",
             "title": "Sequential Accumulation",
             "sub": "The accumulating mean of wells in drilling order against the trumpet envelope implied by the type mean and the P10:P90 ratio, with the 80% confidence interval.",
             "shot": "Sequential Accumulation \u2014 Plot"},
            {"file": "estimator-tool.png",
             "title": "Estimator Tool",
             "sub": "A lognormal sanity check. From a P90 and a P10 estimate it returns the implied P99 and P1 and the P10:P90 ratio, so a range can be judged by the extremes it commits you to.",
             "shot": "Estimator Tool, with a low and a high entered"},
            {"kind": "close",
             "title": "A free teaching tool for type-well curve work.",
             "sub": ["Companion to the Type-Well Curve Fundamentals course at SAGA Wisdom. Sessions save as files you own. No account, no upload: the data never leaves your computer.",
                     "Six short videos, one per tool, on the Shozbot YouTube channel."]},
        ],
    },
}


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in DECKS:
        raise SystemExit(f"usage: make-carousel.py {{{'|'.join(DECKS)}}} SHOTS_DIR OUT_DIR")
    deck = DECKS[sys.argv[1]]
    global W, H
    W, H = deck.get("size", (W, H))
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
