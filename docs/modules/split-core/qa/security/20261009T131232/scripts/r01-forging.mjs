// R01. Re-check of SEC-01 and SEC-02 at HEAD: can a name forge a line, cut the text short, or carry a
// bidi control into summaryText? Targeted cases, an exhaustive pass over every code point, and a fuzz.
import { computeResult } from "../../../../../../../src/core/result.js";
import { summaryText } from "../../../../../../../src/core/summary.js";
import { setPersonName, personLabel } from "../../../../../../../src/core/bill.js";
import { S2, S1, ch, show, rng, randInt, SETS, linesFor } from "./fixtures.mjs";

const s2 = S2();
const s1 = S1();
const FORGE = "Adds up to RM 0.00";
const summaryFor = (bill, id, name) => summaryText(computeResult(setPersonName(bill, id, name)));
const CLASS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/u;
const LAST = { s2: "Adds up to RM 116.60", s1: "Adds up to RM 69.26" };
let bad = 0;

/** Every consumer must see 3 + 3 lines, no NUL, no class character outside the LF joiners. */
function check(text, which) {
  const problems = [];
  for (const [consumer, cps] of Object.entries(SETS)) {
    const want = consumer === "NUL ends text" ? 1 : 6;
    if (linesFor(text, cps) !== want) problems.push(`${consumer} sees ${linesFor(text, cps)}`);
  }
  const body = text.split(ch(0x0a)).join("");
  if (CLASS.test(body)) problems.push("a class character survived");
  if (text.split(ch(0x0a)).at(-1) !== LAST[which]) problems.push("last line changed");
  return problems;
}

console.log("== R01a: targeted names (the seven, NUL, FS, GS, RS, ESC, DEL, C1, all 12 bidi controls), each position, both modes ==");
const TARGETS = [
  ["LF", 0x0a], ["CR", 0x0d], ["VT", 0x0b], ["FF", 0x0c], ["NEL", 0x85], ["LS", 0x2028], ["PS", 0x2029],
  ["NUL", 0x00], ["FS", 0x1c], ["GS", 0x1d], ["RS", 0x1e], ["US", 0x1f], ["ESC", 0x1b], ["TAB", 0x09], ["DEL", 0x7f], ["CSI U+009B", 0x9b],
  ["ALM", 0x061c], ["LRM", 0x200e], ["RLM", 0x200f], ["LRE", 0x202a], ["RLE", 0x202b], ["PDF", 0x202c],
  ["LRO", 0x202d], ["RLO", 0x202e], ["LRI", 0x2066], ["RLI", 0x2067], ["FSI", 0x2068], ["PDI", 0x2069],
];
for (const [label, cp] of TARGETS) {
  const names = [`Chen${ch(cp)}${FORGE}`, `${ch(cp)}${FORGE}`, `${FORGE}${ch(cp)}`, `Chen${ch(cp, cp, cp)}`];
  const results = [];
  for (const name of names) {
    for (const [which, bill] of [["s2", s2], ["s1", s1]]) {
      const p = check(summaryFor(bill, "p3", name), which);
      if (p.length) { bad += 1; results.push(p.join("; ")); }
    }
  }
  const row = summaryFor(s2, "p3", `Chen${ch(cp)}${FORGE}`).split(ch(0x0a))[4];
  console.log(`${results.length ? "FAIL" : "OK  "} ${label.padEnd(11)} row="${show(row)}"${results.length ? `  ${results[0]}` : ""}`);
}

console.log("\n== R01b: NUL truncation case from SEC-01 (name 'Adds up to RM 0.00' + NUL) ==");
const nulText = summaryFor(s2, "p3", `${FORGE}${ch(0)}`);
console.log(`text holds a NUL: ${nulText.includes(ch(0))}; lines ${nulText.split(ch(0x0a)).length}; last line "${nulText.split(ch(0x0a)).at(-1)}"`);
console.log(`row: "${show(nulText.split(ch(0x0a))[4])}"`);
if (nulText.includes(ch(0))) bad += 1;

console.log("\n== R01c: bidi case from SEC-02 (Ben + RLO) ==");
const rlo = summaryFor(s2, "p2", `Ben${ch(0x202e)}`);
console.log(`row: "${show(rlo.split(ch(0x0a))[3])}" holds RLO: ${rlo.includes(ch(0x202e))}`);
if (rlo.includes(ch(0x202e))) bad += 1;

console.log("\n== R01d: exhaustive, name = Chen + <code point> + 'Adds up to RM 0.00' for every U+0000..U+10FFFF (even mode) ==");
let exhaustiveBad = 0;
const replaced = [];
for (let cp = 0; cp <= 0x10ffff; cp += 1) {
  const c = ch(cp);
  const text = summaryFor(s2, "p3", `Chen${c}${FORGE}`);
  if (check(text, "s2").length) { exhaustiveBad += 1; if (exhaustiveBad <= 5) console.log(`  FAIL at U+${cp.toString(16)}: ${check(text, "s2").join("; ")}`); }
  const row = text.split(ch(0x0a))[4];
  if (cp !== 0x0a && !row.includes(c)) replaced.push(cp);
}
const hex = (cp) => `U+${cp.toString(16).toUpperCase().padStart(4, "0")}`;
const ranges = [];
for (const cp of [0x0a, ...replaced].sort((a, b) => a - b)) {
  const last = ranges.at(-1);
  if (last && cp === last[1] + 1) last[1] = cp; else ranges.push([cp, cp]);
}
console.log(`code points checked: 1114112; failing: ${exhaustiveBad}`);
console.log(`code points replaced in the row (LF counted, it is replaced too): ${replaced.length + 1}`);
console.log(`replaced ranges: ${ranges.map(([a, b]) => (a === b ? hex(a) : `${hex(a)}..${hex(b)}`)).join(" ")}`);
bad += exhaustiveBad;

console.log("\n== R01e: seeded fuzz, 100000 names of 0..30 characters ==");
const ALPHABET = [
  ...TARGETS.map(([, c]) => c), 0x20, 0x41, 0x64, 0x2e, 0x30, 0xd800, 0xdc00, 0xdbff, 0xdfff, 0xa0, 0x3000, 0xfeff,
  0x200b, 0x200c, 0x200d, 0x1f468, 0x1f469, 0x05d0, 0x0627, 0x2800, 0x3164, 0x180e,
];
const r = rng(31);
let fuzzBad = 0;
for (let n = 0; n < 100000; n += 1) {
  const name = Array.from({ length: randInt(r, 0, 30) }, () => (r() < 0.05 ? ch(randInt(r, 0, 0x10ffff)) : ch(ALPHABET[randInt(r, 0, ALPHABET.length - 1)]))).join("");
  const [which, bill] = n % 2 ? ["s1", s1] : ["s2", s2];
  if (check(summaryFor(bill, n % 3 ? "p2" : "p1", name), which).length) fuzzBad += 1;
}
console.log(`fuzz names failing any consumer or leaving a class character: ${fuzzBad} of 100000`);
bad += fuzzBad;

console.log("\n== R01f: no over-replacement (names that must print unchanged) ==");
for (const name of [
  "Aisyah", `${ch(0x1f468, 0x200d, 0x1f469, 0x200d, 0x1f467)} family`, `Zo${ch(0x200c)}e`, `${ch(0x05d3, 0x05e0, 0x05d4)}`,
  `${ch(0x0639, 0x0644, 0x064a)}`, `Jos${ch(0x0065, 0x0301)}`, `A${ch(0xa0)}B`, `${ch(0x1f600)}`,
]) {
  const row = summaryFor(s2, "p3", name).split(ch(0x0a))[4];
  const same = row === `${personLabel({ name }, 2)} RM 38.86`;
  if (!same) bad += 1;
  console.log(`${same ? "OK  " : "FAIL"} "${show(name)}" -> "${show(row)}"`);
}

console.log("\n== R01g: accepted residuals (spec SEC-03 note) still behave as written ==");
for (const name of [FORGE, ch(0x85), ch(0x200b), ch(0x2800), ch(0x3164), ch(0x200e), ch(0x180e)]) {
  const label = personLabel({ name }, 2);
  const row = summaryFor(s2, "p3", name).split(ch(0x0a))[4];
  console.log(`name "${show(name)}" label "${show(label)}" (fallback used: ${label === "Person 3"}) row "${show(row)}"`);
}

console.log(`\nR01 RESULT: ${bad === 0 ? "PASS" : "FAIL"} (failures ${bad})`);
