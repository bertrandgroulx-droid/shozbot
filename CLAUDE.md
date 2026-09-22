# shozbot.com — the studio site

Read this first. It is the map for every future session in this repo.

## What this is

The **Shozbot** studio homepage, and the front door for every app Bertrand
makes. Plain HTML and CSS — no framework, no build step. Open `index.html` in
a browser and what you see is what ships.

Brand tagline: **Handmade apps for curious minds**.

The mascot is a photograph of a real handmade robot — wood-block body, wire
limbs, resin hands and feet, purple-and-white mohawk. Its physical, slightly
wonky quality is the whole point of the brand. **Never redraw, filter or
stylise the photo.** The drawn icons in `assets/icons/` are a separate thing:
they exist only because the photo turns to mush at 16 pixels.

## Who this is for

Bertrand owns this and is not a programmer. Explain things in plain language,
one step at a time, and never ask him to edit code or config. When you need
him, stop and say so in a numbered list.

## URLs

`shozbot.com` is a Vercel project serving this repo. Every app keeps living in
its own repo with its own deploys; `vercel.json` rewrites map studio URLs onto
wherever each app actually is.

| Path on shozbot.com | Actually served from | Rewrite in place? |
|---|---|---|
| `/` | this repo | — |
| `/statterbrain/` | `statterbrain.vercel.app` | **no — Phase 2** |
| `/better-weather/` | `bertrandgroulx-droid.github.io/better-weather` | yes |
| `/mogo/` | `…github.io/mogo` | yes |
| `/word-square/` | `…github.io/word-square` | yes |
| `/word-ninja/` | `…github.io/word-ninja` | yes |
| `/letter-drop/` | `…github.io/letter_drop` (note the underscore) | yes |
| `/fauxcabulary/` | `…github.io/fauxcabulary` | yes |
| `/acronumbskull/` | `…github.io/acronumbskull` | yes |

`/<app>` without the trailing slash redirects to `/<app>/`, so relative links
inside each app resolve correctly.

The homepage's Statterbrain card points at `https://statterbrain.vercel.app/`
for now. In Phase 2 — once Statterbrain is built with base path
`/statterbrain/` — change that href to `/statterbrain/`, add the rewrite to
`vercel.json`, and add the URL back to `sitemap.xml`.

## Layout of this repo

```
index.html          the homepage
404.html            the robot, a dry line, a way home
site.css            all of the site's styling; design tokens live at the top
vercel.json         rewrites and redirects for every app
site.webmanifest    installable-to-home-screen metadata
sitemap.xml         robots.txt
assets/
  photos/                   the photographs exactly as Bertrand sent them
  robot.png / .webp         cut out of the photo, 766×900
  robot-small.png / .webp   160px wide, for the footer
  robot-three-eyes*         the second robot — he is the 404 page
  social/                   square opaque icons for LinkedIn (1200/400/300)
  og.png                    1200×630 share preview
  favicon.svg .ico, apple-touch-icon.png, icon-192.png, icon-512.png
  icons/                    the three browser-icon candidates as SVG
  apps/                     each app's own icon, copied from its repo
  fonts/jetbrains-mono-latin.woff2  the wordmark face, self-hosted, variable
  fonts/karla-latin.woff2           the tagline face, self-hosted, variable
kit/                shared studio kit — see below
preview/            decision pages for Bertrand; noindex, not linked from the site
tools/make-icons.py  rebuilds the whole favicon set from one candidate SVG
tools/make-social.py rebuilds the share image and the LinkedIn icons
tools/fonts/         static JetBrains Mono, used only for drawing the share image
```

## Brand

Set in `site.css` under `:root`, sampled from the robot itself:

| Token | Value | Where it came from |
|---|---|---|
| `--mohawk` | `#6c4fa3` | the mohawk, deepened so it passes AA on paper |
| `--mohawk-deep` | `#4a3372` | badge text |
| `--mohawk-soft` | `#efe9f7` | badge background |
| `--wood` / `--wood-light` | `#8a7457` / `#c8a87a` | the head and body blocks |
| `--resin-orange/yellow/blue/red` | `#f08a18` `#ffd23f` `#2d54cd` `#8b1d1e` | hands, feet, chest stripe |
| `--paper` / `--ink` | `#faf7f2` / `#241f1a` | page and text |

The mascot photographs live in `assets/photos/`. The cut-outs in `assets/` were
made from them with `rembg` (the `isnet-general-use` model, alpha matting on),
which is what kept the mohawk fibres and the wire limbs intact. If a photo is
ever replaced, cut the new one the same way rather than by hand.

There is a **second robot** — blue-and-white chevron body, teal-and-red mohawk,
three brass sockets for eyes. He is the 404 page: a different robot makes
"This page wandered off" land better than the mascot does.

One thing to know if his cut-out is ever regenerated: both rembg models leave a
faint ghost of the white door frame behind his head, above the head's top edge
and to the right of the mohawk. It is low-alpha, so it reads as a pale smear
rather than an obvious rectangle, and it is easy to miss. The fix was to clear
the alpha right of the mohawk's own solid edge for every row above the head.

Purple, wood and paper carry the design; the resin colours are accents only.
There is a dark-mode block right below the light tokens — change a colour in
both places.

Wordmark: **JetBrains Mono Bold, lowercase `shozbot`** — Bertrand's pick
(option B1), tracked at `letter-spacing: -0.02em` (his pick K2). Casing is set
in exactly one place, `.wordmark { text-transform }` in `site.css`, and the
tracking sits right beside it. `kit/kit.css` repeats the same tracking for the
bar at the top of every app — change both together.

A monospaced face gives every pair the same gap, so `zb` gets the room `ot`
needs. Bertrand knows, and has parked it: a custom wordmark with the pairs
drawn or hand-kerned properly is a later job, not a bug to fix now.

Tagline: **Karla Medium**, via `--font-tagline`. It is deliberately the one
line on the site that is not mono — the mono reads as software, the tagline
should read as a person. Do not fold it back into `--font-display`.

`preview/brand.html` still shows the first-round candidates.

Browser icon: **`assets/icons/studio-robot.svg`** — the drawn robot that used
to be Statterbrain's favicon. Bertrand moved it to the studio: it is the
Shozbot mark now, and Statterbrain gets a new icon of its own later, built
around a brain. Until that happens the Statterbrain card on the homepage shows
this same robot, so the card and the browser tab match each other; that
resolves itself when the new Statterbrain icon lands.

The three drawn candidates from the first round are still in `assets/icons/`
in case they are ever wanted. To switch the whole set to any of them:

```
python3 tools/make-icons.py option-2-monogram
```

That rewrites `favicon.svg`, `favicon.ico`, `apple-touch-icon.png`,
`icon-192.png` and `icon-512.png` in one go. It needs `pillow` and `cairosvg`.

## The shared studio kit

`kit/kit.css` and `kit/kit.js` put a slim dark bar at the top of every app with
`← shozbot` linking home. One line goes into each app:

```html
<script src="https://shozbot.com/kit/kit.js" defer></script>
```

Options on the tag: `data-app="Word Ninja"` shows the app's name on the right;
`data-hide-standalone` hides the bar when the app is running from a phone home
screen. Everything is namespaced `shozkit-`, the script is safe to include
twice, and the CSS is fetched from shozbot.com — so changing this one file
changes every app at once, wherever it is hosted.

## Storage-key prefixes

All apps share the `shozbot.com` origin now, so unprefixed localStorage keys
would collide between them. The studio site itself stores nothing. Current
state, found by reading each repo (Phases 3 and 4 fix the unprefixed ones):

| App | Keys today | Target prefix |
|---|---|---|
| Better Weather | `bw-recents`, `bw-units` | `betterweather:` |
| Mogo | `mogoSound`, `mogoVoice` | `mogo:` |
| Fauxcabulary | `fauxcabulary.bests` | `fauxcabulary:` |
| Acronumbskull | `acronumbskull.bests` | `acronumbskull:` |
| Word Square, Word Ninja, Letter Drop | keys are built at runtime — read the code | `wordsquare:` `wordninja:` `letterdrop:` |
| Statterbrain | none found in `src/` | `statterbrain:` |

Migrate existing keys when prefixing, so nobody loses a high score.

## How it deploys

**Live since 2026-09-22 at <https://shozbot-chi.vercel.app>.**

The Vercel project is called **shozbot** and is linked to this repo. Its
production branch is `claude/festive-wozniak-mu5wnh`, which is also this repo's
default branch — there is no `main`. Push to that branch and Vercel redeploys
within a minute. There is no build command; Vercel serves the files as they are.

shozbot.com is not pointed at it yet. DNS stays at **Squarespace** — records
are added there and point at Vercel. **Do not move the nameservers to Vercel**,
or Bertrand's free email forwarding stops working.

### Verified on the live deployment, 2026-09-22

Bertrand clicked through all of it. The homepage, the 404, and every one of the
seven rewritten apps load *and work* — not merely load. `/mogo` without the
trailing slash redirects correctly. The phone layout is fine.

The one failure was the expected one: **Better Weather's radar map is blank**,
because the Mapbox token is restricted to the address the app used to live at.
That is now confirmed rather than predicted. The forecast itself is unaffected.

## Ground rules

- Cost ceiling is **$0/month** beyond the domain. If something would cost
  money, stop and ask.
- Free, no ads, no payments, no accounts, no tracking that needs a cookie
  banner.
- Never delete a repo or a Vercel project.
- Small commits, clear messages.

## What reading the other repos turned up

Notes for Phases 2–4, gathered by reading the code rather than guessing.

**Statterbrain has no URL router.** It is Vite + React 19, and pages are held
in a `PageId`-keyed `ROUTES` record in `src/routes.tsx` — the address bar never
changes. So moving it to `/statterbrain/` is a `base` setting in
`vite.config.ts` (which is currently bare) and nothing more: there are no inner
URLs to refresh, and no deep links to break. Check the asset paths afterwards
all the same.

**Better Weather needs no weather key, but it does use a Mapbox one.**
*Confirmed broken off-origin on 2026-09-22 — see the deploy notes above.* The
forecast comes from Open-Meteo, which takes no key. The radar map uses a
*public* Mapbox token (`pk.…`, base64-encoded in `index.html` only to keep
GitHub's secret scanner quiet) and, per the comment beside it, that token is
**restricted to the site's URL**. Served from shozbot.com the browser's origin
changes, so the map will stop loading until `shozbot.com` is added to that
token's allowed URLs in Bertrand's Mapbox account. Nothing is leaking — a
public token is meant to be visible — but this is a Phase 3 step, and it is
his account, so he has to do it.

**Every app is dependency-free static HTML** except Statterbrain, which is the
only one with a build step.

## Still open

- Analytics is not installed yet (Phase 1g): a free, cookieless service,
  Bertrand creates the account.
- `shozbot@shozbot.com` is in the footer; the Squarespace forwarding that makes
  it work has to be confirmed before launch.
- A new Statterbrain icon, built around a brain, replacing the robot it lent
  to the studio.
- **LinkedIn content, once the site is live.** Bertrand wants to post about
  Shozbot there. `assets/social/shozbot-icon-*.png` is already sized for the
  profile or page image — square, opaque, and inset so LinkedIn's circular crop
  takes only flat colour. The writing itself is still to do, and it waits until
  shozbot.com actually resolves.
- **A custom wordmark, later.** JetBrains Mono at -0.02em is what ships, and
  Bertrand is happy with it for now, but he wants to come back to a properly
  kerned or custom-drawn `shozbot` at some point. Raise it, don't act on it.
