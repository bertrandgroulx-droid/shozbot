// Capture the nine Puzzling games at phone size, each played to a representative moment,
// for the LinkedIn deck: node tools/capture-puzzling.mjs SHOTS_DIR
// Random puzzles (?practice), so no day's answer is given away. Timer off where there is
// one, so a clock bar does not sit mid-count in a still. Each shot is then cut 32px under
// its last control (see the puzzling deck in make-carousel.py). Needs Playwright and Chromium.
import { chromium, devices } from "playwright";
import fs from 'node:fs';

const OUT = process.argv[2];
const BASE = 'https://shozbot.com/puzzling/';
const browser = await chromium.launch();
const ctx = await browser.newContext({ ...devices['iPhone 14 Pro Max'], viewport: { width: 430, height: 932 }, colorScheme: 'light' });
// iPhone 14 Pro Max: 430x932 @3x = 1290x2796, the same pixel size as Bertrand's own shots.

async function open(game) {
  const page = await ctx.newPage();
  await page.goto(BASE + game + '/?practice', { waitUntil: 'networkidle' });
  // Timer off, saved before the start card is used; the help dialog closed if it opened.
  await page.evaluate(g => localStorage.setItem(g.replace(/-/g, '') + ':timer', 'false'), game);
  await page.evaluate(() => { const d = document.getElementById('help'); if (d && d.open) d.close(); });
  await page.evaluate(() => { const t = document.getElementById('timerToggle'); if (t && t.checked) { t.click(); } });
  const start = page.locator('#startBtn');
  if (await start.count()) await start.click();
  await page.waitForTimeout(300);
  await page.evaluate(() => { const d = document.getElementById('help'); if (d && d.open) d.close(); });
  // the first-visit Instructions card, dismissed with its own Got it
  const got = page.getByText('Got it', { exact: true });
  if (await got.count()) { await got.first().click(); await page.waitForTimeout(300); }
  return page;
}
async function shot(page, name) {
  await page.evaluate(() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0); });
  await page.waitForTimeout(700); // let flashes and pulses finish
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true });
  const h = await page.evaluate(() => document.querySelector('main.app').getBoundingClientRect().bottom);
  console.log(name, 'content bottom (css px):', Math.round(h), 'of', page.viewportSize().height);
  await page.close();
}

// Whittle: its own script; state is in top-level lets, readable by name.
{
  const page = await open('whittle');
  // the current chain's steps: tap the right letter for clue 1 and clue 2, leaving clue 3 live
  for (let s = 0; s < 2; s++) {
    const idx = await page.evaluate(s => {
      const c = game[ci], w = word, want = c.steps[s][1];
      for (let i = 0; i < w.length; i++) if (w.slice(0, i) + w.slice(i + 1) === want) return i;
      return -1;
    }, s);
    await page.click(`.rung.live .tile[data-i="${idx}"]`);
    await page.waitForTimeout(200);
  }
  await page.evaluate(() => document.querySelectorAll('.rung.just').forEach(r => r.classList.remove('just')));
  await shot(page, 'whittle');
}

// Snowball: type the right word for clue 1 and clue 2, leaving clue 3 live.
{
  const page = await open('snowball');
  for (let s = 0; s < 2; s++) {
    const want = await page.evaluate(s => document.querySelector('.rung.live .rl').textContent && null, s);
    // the answer is not in the DOM; read it from the game's puzzle list by matching the start word
    const ans = await page.evaluate(s => {
      const start = [...document.querySelectorAll('.rung.start .t')].map(t => t.textContent).join('');
      const p = window.SNOWBALL_PUZZLES.find(p => p.start.toUpperCase() === start);
      return p.steps[s][1].toUpperCase();
    }, s);
    await page.fill('#a0', ans);
    await page.click('#f button[type=submit]');
    await page.waitForTimeout(200);
  }
  await page.evaluate(() => document.querySelectorAll('.rung.just').forEach(r => r.classList.remove('just')));
  await shot(page, 'snowball');
}

// Switcheroo: one rung climbed, the second clue live with a letter selected? Keep it simple: one rung climbed.
{
  const page = await open('switcheroo');
  const go = page.locator('#go'); if (await go.count()) await go.click();
  const [i, k] = await page.evaluate(() => {
    const start = [...document.querySelectorAll('.rung.start .t')].map(t => t.textContent).join('');
    const p = window.SWITCHEROO_PUZZLES.find(p => p.start.toUpperCase() === start);
    const want = p.steps[0][1].toUpperCase();
    const i = [...start].findIndex((c, i) => c !== want[i]);
    return [i, want[i]];
  });
  await page.click(`.rung.live .tile[data-i="${i}"]`);
  await page.click(`.key[data-k="${k}"]`);
  await page.waitForTimeout(200);
  await page.evaluate(() => document.querySelectorAll('.rung.just').forEach(r => r.classList.remove('just')));
  await shot(page, 'switcheroo');
}

// Common Thread: a puzzle solved.
{
  const page = await open('common-thread');
  const ans = await page.evaluate(() => game[idx].link);
  await page.fill('#guess', ans);
  await page.click('#check');
  await page.waitForTimeout(200);
  await shot(page, 'common-thread');
}

// Tumble: first word solved, second clue showing.
{
  const page = await open('tumble');
  const ans = await page.evaluate(() => {
    const given = [...document.querySelectorAll('.tile')].map(t => t.textContent).join('');
    const p = window.TUMBLE_PUZZLES.find(p => p.letters.toUpperCase().replace(/[^A-Z]/g, '') === given);
    return p.answers[0].toUpperCase();
  });
  await page.fill('#a0', ans);
  await page.click('#f button[type=submit]');
  await page.waitForTimeout(200);
  await shot(page, 'tumble');
}

// Stowaway and Soundalike: both words typed, not yet checked.
for (const [game, key] of [['stowaway', 'STOWAWAY_PUZZLES'], ['soundalike', 'SOUNDALIKE_PUZZLES']]) {
  const page = await open(game);
  const ans = await page.evaluate(key => {
    const q = document.querySelector('#a0').closest('.field').querySelector('.q').textContent;
    const p = window[key].find(p => p.clues[0] === q);
    return p.answers.map(a => a.toUpperCase());
  }, key);
  await page.fill('#a0', ans[0]);
  await page.fill('#a1', ans[1]);
  await shot(page, game);
}

// Splice: an answer typed, not yet checked.
{
  const page = await open('splice');
  const ans = await page.evaluate(() => {
    const q = document.querySelector('.clues .clue b').textContent;
    const p = window.SPLICE_PUZZLES.find(p => p.clues[0] === q);
    return p.answer.toUpperCase();
  });
  await page.fill('#a0', ans);
  await shot(page, 'splice');
}

// Three of a Kind: the choices showing, nothing tapped.
{
  const page = await open('three-of-a-kind');
  await shot(page, 'three-of-a-kind');
}

await browser.close();
