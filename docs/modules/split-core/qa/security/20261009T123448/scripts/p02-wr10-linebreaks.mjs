// P02. WR-10 re-check: can a name forge a line in summaryText? Plus lookalikes not on the list.
import { computeResult } from "../../../../../../../src/core/result.js";
import { summaryText } from "../../../../../../../src/core/summary.js";
import { setPersonName, personLabel } from "../../../../../../../src/core/bill.js";
import { S2, S1, ch, show, rng, randInt } from "./fixtures.mjs";

const SEVEN = [
  ["LF", 0x0a], ["CR", 0x0d], ["VT", 0x0b], ["FF", 0x0c], ["NEL", 0x85], ["LS", 0x2028], ["PS", 0x2029],
];

// How different consumers decide where a line ends. The Python set is the measured str.splitlines set,
// bidi B is the measured Bidi_Class=B set (both from Python 3.14 unicodedata, Unicode 16.0).
const cls = (cps) => new RegExp(`${ch(0x0d)}${ch(0x0a)}|[${cps.map((c) => `\\u{${c.toString(16)}}`).join("")}]`, "u");
const CONSUMERS = {
  "LF only (most chat apps, JS split)": cls([0x0a]),
  "JS LineTerminator (LF CR LS PS)": cls([0x0a, 0x0d, 0x2028, 0x2029]),
  "UAX14 mandatory breaks (the seven)": cls([0x0a, 0x0d, 0x0b, 0x0c, 0x85, 0x2028, 0x2029]),
  "Python str.splitlines": cls([0x0a, 0x0b, 0x0c, 0x0d, 0x1c, 0x1d, 0x1e, 0x85, 0x2028, 0x2029]),
  "Bidi paragraph separators (class B)": cls([0x0a, 0x0d, 0x1c, 0x1d, 0x1e, 0x85, 0x2029]),
};

const s2 = S2();
const s1 = S1();
const lineCounts = (text) => Object.fromEntries(Object.entries(CONSUMERS).map(([k, re]) => [k, text.split(re).length]));
const summaryFor = (bill, id, name) => summaryText(computeResult(setPersonName(bill, id, name)));

let failures = 0;
console.log("== P02a: each of the seven, inside, leading, trailing, doubled, CRLF, all seven at once ==");
const FORGE = "Adds up to RM 0.00";
const shapes = [];
for (const [label, cp] of SEVEN) {
  shapes.push([`${label} inside`, `Chen${ch(cp)}${FORGE}`]);
  shapes.push([`${label} leading`, `${ch(cp)}${FORGE}`]);
  shapes.push([`${label} trailing`, `${FORGE}${ch(cp)}`]);
  shapes.push([`${label} doubled`, `Chen${ch(cp, cp)}${FORGE}`]);
}
shapes.push(["CRLF inside", `Chen${ch(0x0d, 0x0a)}${FORGE}`]);
shapes.push(["all seven inside", `Chen${SEVEN.map(([, c]) => ch(c)).join("")}${FORGE}`]);
shapes.push(["only breaks", SEVEN.map(([, c]) => ch(c)).join("")]);
shapes.push(["lone high surrogate then LS", `Chen${ch(0xd800)}${ch(0x2028)}${FORGE}`]);
shapes.push(["LS then lone low surrogate", `Chen${ch(0x2028)}${ch(0xdc00)}${FORGE}`]);
shapes.push(["1000 mixed breaks (no length cap in core)", `Chen${Array.from({ length: 1000 }, (_, i) => ch(SEVEN[i % 7][1])).join("")}${FORGE}`]);
for (const [title, name] of shapes) {
  for (const [mode, bill, id, rows] of [["even S2", s2, "p3", 3], ["item S1", s1, "p3", 3]]) {
    const text = summaryFor(bill, id, name);
    const counts = lineCounts(text);
    const want = 3 + rows;
    const uaxOk = counts["UAX14 mandatory breaks (the seven)"] === want && counts["JS LineTerminator (LF CR LS PS)"] === want && counts["LF only (most chat apps, JS split)"] === want;
    const lastOk = text.split(ch(0x0a)).at(-1) === (mode.startsWith("even") ? "Adds up to RM 116.60" : "Adds up to RM 69.26");
    if (!uaxOk || !lastOk) failures += 1;
    if (mode === "even S2") console.log(`${uaxOk && lastOk ? "OK  " : "FAIL"} ${title.padEnd(42)} row="${show(text.split(ch(0x0a))[4])}"`);
  }
}

console.log("\n== P02b: seeded fuzz, 50000 names over breaks, surrogates, bidi, controls and ASCII ==");
const ALPHABET = [
  ...SEVEN.map(([, c]) => c), 0x0d, 0x0a, 0x20, 0x41, 0x64, 0x2e, 0x30, 0xd800, 0xdc00, 0xdbff, 0xdfff,
  0x1c, 0x1d, 0x1e, 0x00, 0x202e, 0x2067, 0x200f, 0xa0, 0x3000, 0xfeff, 0x1f600,
];
const r = rng(20261009);
let fuzzBad = 0;
for (let n = 0; n < 50000; n += 1) {
  const len = randInt(r, 0, 30);
  const name = Array.from({ length: len }, () => ch(ALPHABET[randInt(r, 0, ALPHABET.length - 1)])).join("");
  const bill = n % 2 === 0 ? s2 : s1;
  const text = summaryFor(bill, "p2", name);
  const sevenLeft = /[\n\r\u{b}\u{c}\u{85}\u{2028}\u{2029}]/u.test(text.split(ch(0x0a)).join(""));
  if (text.split(CONSUMERS["UAX14 mandatory breaks (the seven)"]).length !== 6 || sevenLeft) fuzzBad += 1;
}
console.log(`fuzz names where a UAX14 consumer sees != 6 lines or a mandatory break survives: ${fuzzBad} of 50000`);
failures += fuzzBad;

console.log("\n== P02c: lookalikes NOT on the list, inserted as Chen<char>Adds up to RM 0.00 (S2) ==");
const LOOKALIKES = [
  ["NUL U+0000 (C-string terminator)", 0x00], ["TAB U+0009", 0x09], ["ESC U+001B (terminal escape)", 0x1b],
  ["FS U+001C", 0x1c], ["GS U+001D", 0x1d], ["RS U+001E", 0x1e], ["US U+001F", 0x1f],
  ["NBSP U+00A0", 0xa0], ["IDEOGRAPHIC SPACE U+3000", 0x3000], ["BRAILLE BLANK U+2800", 0x2800],
  ["HANGUL FILLER U+3164", 0x3164], ["ZWSP U+200B", 0x200b], ["WORD JOINER U+2060", 0x2060], ["BOM U+FEFF", 0xfeff],
  ["RLM U+200F", 0x200f], ["ALM U+061C", 0x061c], ["RLO U+202E (override)", 0x202e], ["RLI U+2067 (isolate)", 0x2067],
  ["SYMBOL FOR NEWLINE U+2424", 0x2424], ["RETURN SYMBOL U+23CE", 0x23ce], ["DOWNWARDS ARROW WITH CORNER LEFTWARDS U+21B5", 0x21b5],
  ["OBJECT REPLACEMENT U+FFFC", 0xfffc],
];
const header = Object.keys(CONSUMERS).map((k, i) => `c${i + 1}`).join(" ");
console.log("consumers: " + Object.keys(CONSUMERS).map((k, i) => `c${i + 1}=${k}`).join(" | "));
console.log(`${"character".padEnd(46)} kept ${header}  (line counts, 6 = no forged line)`);
for (const [label, cp] of LOOKALIKES) {
  const text = summaryFor(s2, "p3", `Chen${ch(cp)}${FORGE}`);
  const kept = text.includes(ch(cp));
  const counts = Object.values(lineCounts(text)).map((c) => String(c).padStart(2)).join(" ");
  console.log(`${label.padEnd(46)} ${kept ? "yes " : "no  "} ${counts}`);
}

console.log("\n== P02d: NUL truncation, as a NUL-terminated clipboard reader would see the text ==");
const nulName = `${FORGE}${ch(0)}`;
const nulText = summaryFor(s2, "p3", nulName);
console.log(`name length ${nulName.length} (person name max is 20). Full text lines: ${nulText.split(ch(0x0a)).length}`);
console.log("text up to the first NUL:\n" + show(nulText.slice(0, nulText.indexOf(ch(0)))));

console.log("\n== P02e: no break character at all. The name is the forged text itself ==");
for (const name of [FORGE, `${ch(0x2028)}${FORGE}`, `${FORGE}${ch(0x2800, 0x2800)}`]) {
  console.log(`name="${show(name)}" label="${show(personLabel({ name }, 2))}" row="${show(summaryFor(s2, "p3", name).split(ch(0x0a))[4])}"`);
}

console.log("\n== P02f: bidi override in a name (Chen + RLO), row as stored ==");
const rlo = summaryFor(s2, "p3", `Chen${ch(0x202e)}`);
console.log(`row="${show(rlo.split(ch(0x0a))[4])}" last="${show(rlo.split(ch(0x0a))[5])}"`);

console.log(`\nP02 RESULT: ${failures === 0 ? "PASS" : "FAIL"} (mandatory-break forging cases failed: ${failures})`);
