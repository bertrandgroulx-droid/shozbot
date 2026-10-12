// node --test kit/test/daily.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const ShozDaily = require("../daily.js");

function fakeStorage() {
  const m = new Map();
  return { getItem: k => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)), removeItem: k => m.delete(k), key: i => [...m.keys()][i], get length() { return m.size; }, _m: m };
}
const at = (y, mo, d) => () => new Date(y, mo - 1, d, 15, 30);

test("day numbering and seed are stable and per game", () => {
  const s = fakeStorage();
  const a = ShozDaily.create({ game: "letter-drop", storage: s, now: at(2026, 10, 12) });
  const b = ShozDaily.create({ game: "whittle", storage: s, now: at(2026, 10, 12) });
  const m = a.todayMeta();
  assert.equal(m.iso, "2026-10-12");
  assert.equal(m.number, 285);
  assert.equal(a.todayMeta().seed, m.seed);
  assert.notEqual(b.todayMeta().seed, m.seed);
  assert.equal(a.store, "letterdrop:");
  assert.equal(ShozDaily.create({ game: "x", storage: s, now: at(2026, 1, 1) }).todayMeta().number, 1);
});

test("rng is deterministic for a seed and shuffle uses it", () => {
  const r1 = ShozDaily.rng(123), r2 = ShozDaily.rng(123);
  const x = [r1(), r1(), r1()], y = [r2(), r2(), r2()];
  assert.deepEqual(x, y);
  assert.ok(x.every(v => v >= 0 && v < 1));
  assert.deepEqual(ShozDaily.shuffle([1, 2, 3, 4, 5], ShozDaily.rng(7)), ShozDaily.shuffle([1, 2, 3, 4, 5], ShozDaily.rng(7)));
});

test("first score is kept, later plays do not overwrite", () => {
  const s = fakeStorage();
  const d = ShozDaily.create({ game: "fauxcabulary", storage: s, now: at(2026, 10, 12) });
  const m = d.todayMeta();
  assert.deepEqual(d.save(m, { score: 7, max: 10, results: [1, 1, 0, 1, 1, 1, 0, 1, 0, 1] }), { first: true, saved: true });
  assert.deepEqual(d.save(m, { score: 10, max: 10, results: [] }), { first: false, saved: false });
  assert.equal(d.record(m.iso).score, 7);
  assert.ok(s._m.has("fauxcabulary:daily:2026-10-12"));
  assert.equal(d.savedLine(m, true), "Saved as your score for today.");
  assert.equal(d.savedLine(m, false), "Your first score for this puzzle is the one that is kept.");
  assert.deepEqual(d.save({ mode: "practice" }, { score: 1 }), { first: false, saved: false });
});

test("streak counts days in a row ending today or yesterday", () => {
  const s = fakeStorage();
  const d = ShozDaily.create({ game: "acronumbskull", storage: s, now: at(2026, 10, 12) });
  assert.equal(d.streak(), 0);
  for (const day of [9, 10, 11]) d.save(d.metaFor(new Date(2026, 9, day)), { score: 5, max: 10 });
  assert.equal(d.streak(), 3, "yesterday's run still counts before today is played");
  d.save(d.todayMeta(), { score: 8, max: 10 });
  assert.equal(d.streak(), 4);
  assert.equal(d.streakLine(), "4 days in a row");
  const gap = ShozDaily.create({ game: "acronumbskull", storage: s, now: at(2026, 10, 14) });
  assert.equal(gap.streak(), 0, "a missed day breaks it");
});

test("share text matches the Puzzling shape", () => {
  const s = fakeStorage();
  const d = ShozDaily.create({ game: "fauxcabulary", title: "Fauxcabulary", storage: s, now: at(2026, 10, 12) });
  const m = d.todayMeta();
  const t = d.shareText({ meta: m, score: 7, max: 10, results: [1, 1, 0, 1, 1, 1, 0, 1, 0, 1], url: "https://shozbot.com/fauxcabulary/" });
  assert.equal(t.split("\n")[0], "Fauxcabulary No. 285 · " + d.fmtTiny(m.date));
  assert.equal(t.split("\n")[1], "7/10 🟩🟩⬜🟩🟩🟩⬜🟩⬜🟩");
  assert.equal(t.split("\n")[2], "https://shozbot.com/fauxcabulary/");
  assert.equal(d.shareText({ meta: m, score: 1240, max: null, url: "u" }).split("\n")[1], "Score 1240");
  assert.equal(d.shareText({ meta: m, score: 3, max: 5, squares: "🟩🟩🟩", url: "u" }).split("\n")[1], "3/5 🟩🟩🟩");
  assert.equal(d.shareText({ meta: { mode: "practice" }, score: 2, max: 3, results: [1, 1, 0], url: "u" }).split("\n")[0], "Fauxcabulary random puzzles");
});

test("verdicts and labels", () => {
  const d = ShozDaily.create({ game: "g", storage: fakeStorage(), now: at(2026, 10, 12) });
  const m = d.todayMeta();
  assert.equal(d.verdict(10, 10, m), "A perfect game.");
  assert.equal(d.verdict(7, 10, m), "A strong game.");
  assert.equal(d.verdict(4, 10, m), "A fair game.");
  assert.equal(d.verdict(1, 10, m), "A tough one. Tomorrow’s is different.");
  assert.equal(d.verdict(1, 10, { mode: "practice" }), "A tough one. The next one is different.");
  assert.ok(d.label(m).startsWith("Daily No. 285 · "));
  assert.equal(d.label({ mode: "practice" }), "Random puzzles");
  assert.equal(d.pastDays(3).length, 4);
  assert.equal(d.pastDays(3)[0].isToday, true);
});

test("a blocked storage never throws", () => {
  const broken = { getItem() { throw new Error("no"); }, setItem() { throw new Error("no"); }, key() { return null; }, length: 0 };
  const d = ShozDaily.create({ game: "g", storage: broken, now: at(2026, 10, 12) });
  assert.equal(d.record("2026-10-12"), null);
  assert.deepEqual(d.save(d.todayMeta(), { score: 1, max: 1 }), { first: true, saved: true });
  assert.equal(d.streak(), 0);
});
