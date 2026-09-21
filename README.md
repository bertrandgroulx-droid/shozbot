# shozbot.com

The Shozbot studio site — *handmade apps for curious minds*.

Plain HTML and CSS, no build step. `index.html` is the homepage; `vercel.json`
maps `shozbot.com/<app>/` onto wherever each app already lives, so every app
keeps its own repo and its own deploys.

## Looking at it locally

```
python3 -m http.server 8000
```

then open <http://localhost:8000>. (Opening `index.html` straight off the disk
mostly works too, but the links that start with `/` won't.)

## Two decisions still to make

- <http://localhost:8000/preview/brand.html> — the wordmark in three typefaces
  and three casings, plus the palette.
- <http://localhost:8000/preview/icons.html> — three browser icons at the sizes
  they'll really be used.

## Rebuilding the browser icon set

```
pip install pillow cairosvg
python3 tools/make-icons.py option-1-head    # or option-2-monogram, option-3-silhouette
```

More detail, and the rules of the place, in [CLAUDE.md](CLAUDE.md).
