// Mutants for the split-core code-review re-check. Each one changes source text in memory only
// (see preload.mjs). `edits` maps a project-relative path to a function from old text to new text.
// A mutant is KILLED when at least one test it targets fails, and SURVIVES when every test stays green.
export const MUTANTS = new Map();

const add = (id, desc, tests, edits) => MUTANTS.set(id, { id, desc, tests, edits });
const sub = (from, to) => (text) => {
  if (!text.includes(from)) throw new Error(`pattern not found: ${from}`);
  return text.replace(from, () => to);
};
const append = (code) => (text) => `${text}\n${code}\n`;

const HYG = ["tests/hygiene.test.js"];
const SUM = ["tests/summary.test.js"];
const MON = ["tests/money.test.js"];
const BIL = ["tests/bill.test.js"];
const HYG_TEST = "tests/hygiene.test.js";
const MONEY = "src/core/money.js";
const BILL = "src/core/bill.js";
const SUMMARY = "src/core/summary.js";

// ---- Group H: what the R25 guards see (hygiene.test.js) ----
add("H00", "identity control, no edit", HYG, {});
add("H01", "control: plain Date.now() executed at module top level of money.js (scan and trap should both go red)",
  HYG, { [MONEY]: append("const r04t = Date.now(); void r04t;") });

const ANCHOR = "export function formatRate(bp) {";
add("H02", "F1-style postfix division plus process, inside a branch the workload never takes (formatRate, bp > 1e12)",
  HYG, { [MONEY]: sub(ANCHOR, `${ANCHOR}\n  if (bp > 1e12) { let r04n = 0; const r04v = r04n++ / process.uptime(); void r04v; }`) });
add("H03", "plain Date.now() inside a branch the workload never takes (scan should catch it, trap cannot)",
  HYG, { [MONEY]: sub(ANCHOR, `${ANCHOR}\n  if (bp > 1e12) { void Date.now(); }`) });
add("H04a", "globalThis reference written with a unicode escape, executed at top level (R25 bans globalThis)",
  HYG, { [MONEY]: append(String.raw`const r04g = \u{67}lobalThis; void r04g;`) });
add("H04b", "globalThis reference written plainly, executed at top level (scan should catch it)",
  HYG, { [MONEY]: append("const r04g = globalThis; void r04g;") });
add("H05a", "sourceURL magic comment, then an escaped process access at top level",
  HYG, { [MONEY]: append(String.raw`//# sourceURL=elsewhere.js
const r04p = \u{70}rocess.pid; void r04p;`) });
add("H05b", "control for H05a: the same escaped process access without the sourceURL comment",
  HYG, { [MONEY]: append(String.raw`const r04p = \u{70}rocess.pid; void r04p;`) });
add("H06", "a new export the workload never calls, body uses an escaped Date",
  HYG, { [BILL]: append(String.raw`export function r04Sneaky() { return \u{44}ate.now(); }`) });

// Narrowing sweep: drop one trap from the test's own lists, change nothing else.
const GLOBALS = ["eval", "Function", "setTimeout", "setInterval", "requestAnimationFrame", "queueMicrotask",
  "setImmediate", "performance", "crypto", "WebSocket", "process", "require", "fetch", "XMLHttpRequest", "EventSource",
  "localStorage", "sessionStorage", "indexedDB", "Date", "Intl", "window", "document", "navigator", "parseFloat"];
const METHODS = ["Date.now", "Math.random", "Number.parseFloat", "toFixed", "Number toLocaleString",
  "BigInt toLocaleString", "Array toLocaleString", "Object toLocaleString", "Date toLocaleString",
  "toLocaleDateString", "toLocaleTimeString", "localeCompare", "toLocaleUpperCase", "toLocaleLowerCase"];
const ROUTES = ["Function constructor route", "AsyncFunction constructor route",
  "GeneratorFunction constructor route", "AsyncGeneratorFunction constructor route"];

const dropGlobal = (name) => sub("let armed = false;",
  `{ const i = TRAPPED_GLOBALS.indexOf(${JSON.stringify(name)}); if (i < 0) throw new Error("no such trap"); TRAPPED_GLOBALS.splice(i, 1); }\nlet armed = false;`);
const dropEntry = (array, label) => sub("let armed = false;",
  `{ const i = ${array}.findIndex((e) => e[0] === ${JSON.stringify(label)}); if (i < 0) throw new Error("no such trap"); ${array}.splice(i, 1); }\nlet armed = false;`);

GLOBALS.forEach((name, n) => add(`N-G${String(n + 1).padStart(2, "0")}`, `narrowing: trap for global ${name} removed from TRAPPED_GLOBALS`,
  HYG, { [HYG_TEST]: dropGlobal(name) }));
METHODS.forEach((label, n) => add(`N-M${String(n + 1).padStart(2, "0")}`, `narrowing: trap for method ${label} removed from TRAPPED_METHODS`,
  HYG, { [HYG_TEST]: dropEntry("TRAPPED_METHODS", label) }));
ROUTES.forEach((label, n) => add(`N-R${n + 1}`, `narrowing: ${label} removed from CONSTRUCTOR_ROUTES`,
  HYG, { [HYG_TEST]: dropEntry("CONSTRUCTOR_ROUTES", label) }));

add("H08a", "eval trap removed AND an escaped eval executed at top level of money.js",
  HYG, { [HYG_TEST]: dropGlobal("eval"), [MONEY]: append(String.raw`const r04e = (0, \u{65}val)("1"); void r04e;`) });
add("H08b", "control: the escaped eval alone, trap intact",
  HYG, { [MONEY]: append(String.raw`const r04e = (0, \u{65}val)("1"); void r04e;`) });
add("H08c", "fetch trap removed AND an escaped fetch reference executed at top level of money.js",
  HYG, { [HYG_TEST]: dropGlobal("fetch"), [MONEY]: append(String.raw`void \u{66}etch;`) });
add("H08d", "control: the escaped fetch reference alone, trap intact",
  HYG, { [MONEY]: append(String.raw`void \u{66}etch;`) });

// ---- Group B: does the trap machinery itself fail when broken? (edits to hygiene.test.js) ----
add("B1", "global getter for crypto stops recording", HYG, { [HYG_TEST]: sub(
  "replace(globalThis, name, { get() { record(name); return read(); } });",
  'replace(globalThis, name, { get() { if (name !== "crypto") record(name); return read(); } });') });
add("B2", "method wrapper for toFixed stops recording", HYG, { [HYG_TEST]: sub(
  "value: function (...args) { record(label); return real.apply(this, args); }",
  'value: function (...args) { if (label !== "toFixed") record(label); return real.apply(this, args); }') });
add("B3", "stack attribution never finds a core frame", HYG, { [HYG_TEST]: sub(
  String.raw`const fromCore = (new Error().stack ?? "").split("\n").some((line) => line.includes(CORE_URL));`,
  "const fromCore = false;") });
add("B4", "stack attribution counts every access (test code too)", HYG, { [HYG_TEST]: sub(
  String.raw`const fromCore = (new Error().stack ?? "").split("\n").some((line) => line.includes(CORE_URL));`,
  "const fromCore = true;") });
add("B5", "traps never armed", HYG, { [HYG_TEST]: sub("  armed = true;\n  try {", "  try {") });
add("B6", "traps are never restored after a run", HYG, { [HYG_TEST]: sub(
  "for (const [owner, key, descriptor] of saved.reverse()) {", "for (const [owner, key, descriptor] of []) {") });
add("B7", "resolve hook stops carrying the run id onto core-to-core imports", HYG, { [HYG_TEST]: sub(
  "if (!run || !out.url.startsWith(CORE_URL)) return out;", "return out;") });
add("B8", "hits are not cleared between runs", HYG, { [HYG_TEST]: sub("return hits.splice(0);", "return hits.slice();") });
add("B9", "the run id is the same for every import (core copies are shared across runs)", HYG, { [HYG_TEST]: sub(
  "const run = String(runs += 1);\n  const loaded", "const run = \"1\";\n  const loaded") });

// ---- Group P: the R24 property tests (summary.test.js) ----
const CONTROLS = String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/gu;`;
const withClass = (replacement) => sub(CONTROLS, replacement);
add("P00", "identity control, no edit", SUM, {});
add("P01", "g flag dropped: only the first control character in a name is replaced",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/u;`) });
add("P02", "class takes + : a run of adjacent controls collapses to one space",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]+/gu;`) });
add("P03", "class also takes \\p{Cs}: a lone surrogate becomes a space",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}\p{Cs}]/gu;`) });
add("P04", "control: \\p{Bidi_Control} dropped",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}]/gu;`) });
add("P05", "\\p{Cc} narrowed to C0 and DEL (the C1 range passes through)",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\x00-\x1F\x7F\p{Zl}\p{Zp}\p{Bidi_Control}]/gu;`) });
add("P06", "class also takes \\p{Zs} (NBSP, U+3000 and the like)",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}\p{Zs}]/gu;`) });
add("P07", "class also takes the astral code point U+1F600",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}\u{1F600}]/gu;`) });
add("P08", "replacement is the empty string",
  SUM, { [SUMMARY]: sub('.replace(CONTROLS, " ")', '.replace(CONTROLS, "")') });
add("P09", "class also takes \\p{Cn} (unassigned code points)",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}\p{Cn}]/gu;`) });
add("P10", "class also takes \\p{Co} (private use, above U+2069)",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}\p{Co}]/gu;`) });
add("P11", "class also takes \\p{Cf} (format characters such as U+00AD and U+FEFF)",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}\p{Cf}]/gu;`) });
add("P12", "replacement is two spaces",
  SUM, { [SUMMARY]: sub('.replace(CONTROLS, " ")', '.replace(CONTROLS, "  ")') });
add("P13", "u flag dropped (\\p{..} turns into literal text)",
  SUM, { [SUMMARY]: withClass(String.raw`const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/g;`) });
add("P14", "a control that is also white space (TAB, LF, CR, VT, FF, LS, PS) is kept, the rest become a space",
  SUM, { [SUMMARY]: sub('.replace(CONTROLS, " ")', String.raw`.replace(CONTROLS, (m) => (/\s/u.test(m) ? m : " "))`) });

// ---- Group W: money.js digit cap ----
const CAP = "String(wholePart(maxHundredths)).length";
add("W00", "identity control, no edit", MON, {});
add("W01", "digit cap one digit looser", MON, { [MONEY]: sub(`whole.length > ${CAP}`, `whole.length > ${CAP} + 1`) });
add("W02", "digit cap taken from the cents text of the ceiling instead of its whole part",
  MON, { [MONEY]: sub(`whole.length > ${CAP}`, "whole.length > String(maxHundredths).length") });
add("W03", "wholePart uses Math.floor (equivalent output, float divide)",
  MON, { [MONEY]: sub("return (hundredths - (hundredths % 100)) / 100;", "return Math.floor(hundredths / 100);") });

// ---- Group R: bill.js refactor (WR-09) ----
add("R1", "toggleItemPerson no longer checks that the person exists", BIL, { [BILL]: sub(
  "  if (!bill.people.some((person) => person.id === personId)) return bill;\n  return changeItem(bill, itemId, (item) => ({",
  "  return changeItem(bill, itemId, (item) => ({") });
