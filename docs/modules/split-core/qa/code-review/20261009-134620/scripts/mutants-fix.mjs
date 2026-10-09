// Suggested fixes, served in memory, to show they do what the findings claim. X: the extra R24 tests must
// kill the surviving mutants P01 to P03 and stay green on the real code. Y: a pin on the trap lists must go
// red on the missing globalThis trap and on every narrowing, and stay green once globalThis is added.
// Z: a probe that a throwing trapped run leaks its hits into the next run.
// Imports the base mutants, so preload.mjs and run-mutants.mjs read this file instead of mutants.mjs.
import { MUTANTS } from "./mutants.mjs";
export { MUTANTS };

const add = (id, desc, tests, edits) => MUTANTS.set(id, { id, desc, tests, edits });
const append = (code) => (text) => `${text}\n${code}\n`;
const SUM_TEST = "tests/summary.test.js";
const HYG_TEST = "tests/hygiene.test.js";
const MONEY = "src/core/money.js";

const SUGGESTED_SUMMARY_TESTS = String.raw`
test("@R24 every replaceable character in one name is replaced, one space each", () => {
  const members = [];
  for (let cp = 0; cp <= 0x2069; cp += 1) if (R24_CLASS.test(String.fromCodePoint(cp))) members.push(String.fromCodePoint(cp));
  const rowOf = (name) => summaryText(computeResult(setPersonName(S2, "p3", name))).split("\n")[4];
  assert.equal(members.length, 79);
  assert.equal(rowOf("A" + members.join("") + "B"), "A" + " ".repeat(79) + "B RM 38.86");
  assert.equal(rowOf("A" + members.join("x") + "B"), "A" + members.map(() => " ").join("x") + "B RM 38.86");
});
test("@R24 a lone surrogate prints as typed", () => {
  const lone = [];
  for (let unit = 0xd800; unit <= 0xdfff; unit += 1) lone.push(String.fromCharCode(unit));
  const name = "A" + lone.join("x") + "B";
  assert.equal(summaryText(computeResult(setPersonName(S2, "p3", name))).split("\n")[4], name + " RM 38.86");
});`;

const withFix = (mutantId) => ({ ...MUTANTS.get(mutantId).edits, [SUM_TEST]: append(SUGGESTED_SUMMARY_TESTS) });
add("X00", "suggested R24 tests on the real code (must stay green)", [SUM_TEST], { [SUM_TEST]: append(SUGGESTED_SUMMARY_TESTS) });
add("X01", "suggested R24 tests against P01 (g flag dropped)", [SUM_TEST], withFix("P01"));
add("X02", "suggested R24 tests against P02 (+ quantifier)", [SUM_TEST], withFix("P02"));
add("X03", "suggested R24 tests against P03 (\\p{Cs} added)", [SUM_TEST], withFix("P03"));

const PIN = String.raw`
const MUST_TRAP = ["window", "document", "globalThis", "localStorage", "sessionStorage", "navigator", "fetch",
  "XMLHttpRequest", "Date", "parseFloat", "Intl", "setTimeout", "setInterval", "requestAnimationFrame", "eval",
  "Function", "queueMicrotask", "setImmediate", "performance", "crypto", "WebSocket", "process", "require"];
const MUST_TRAP_OTHER = ["Math.random", "Number.parseFloat", "toFixed", "toLocaleDateString", "Date.now", "Function constructor route"];
test("@R25 the runtime trap lists cover every name R25 bans", () => {
  const have = new Set([...TRAPPED_GLOBALS, ...TRAPPED_METHODS.map(([label]) => label), ...CONSTRUCTOR_ROUTES.map(([label]) => label)]);
  assert.deepEqual([...MUST_TRAP, ...MUST_TRAP_OTHER].filter((name) => !have.has(name)), []);
});`;
const addGlobalThisTrap = (text) => text.replace('"localStorage", "sessionStorage", "indexedDB",', () => '"localStorage", "sessionStorage", "indexedDB", "globalThis",');
const drop = (array, label, byIndex) => (text) => text.replace("let armed = false;", () =>
  `{ const i = ${array}.${byIndex ? "findIndex((e) => e[0] === " + JSON.stringify(label) + ")" : "indexOf(" + JSON.stringify(label) + ")"}; ${array}.splice(i, 1); }\nlet armed = false;`);
const both = (...fns) => (text) => fns.reduce((acc, fn) => fn(acc), text);

add("Y0", "suggested pin on the trap lists, current code (must go red on the missing globalThis trap)", [HYG_TEST],
  { [HYG_TEST]: append(PIN) });
add("Y1", "pin plus globalThis added to TRAPPED_GLOBALS (must be green)", [HYG_TEST],
  { [HYG_TEST]: both(addGlobalThisTrap, append(PIN)) });
add("Y2", "Y1 plus the escaped globalThis plant H04a (the trap must now catch it)", [HYG_TEST],
  { [HYG_TEST]: both(addGlobalThisTrap, append(PIN)), [MONEY]: append(String.raw`const r04g = \u{67}lobalThis; void r04g;`) });
add("Y3", "Y1 plus the eval trap dropped (the pin must go red)", [HYG_TEST],
  { [HYG_TEST]: both(addGlobalThisTrap, drop("TRAPPED_GLOBALS", "eval", false), append(PIN)) });
add("Y4", "Y1 plus the Date.now trap dropped (the pin must go red)", [HYG_TEST],
  { [HYG_TEST]: both(addGlobalThisTrap, drop("TRAPPED_METHODS", "Date.now", true), append(PIN)) });
add("Y5", "Y1 plus the AsyncFunction route dropped (the pin does not list it, so it stays green: shows the pin is only as wide as its list)",
  [HYG_TEST], { [HYG_TEST]: both(addGlobalThisTrap, drop("CONSTRUCTOR_ROUTES", "AsyncFunction constructor route", true), append(PIN)) });

const LEAK = String.raw`
test("zz probe: a trapped run whose body throws must not leak its hits into the next run", async () => {
  await assert.rejects(trapped(() => importPlanted("money.js", "void Date.now(); throw new Error('boom');")));
  assert.deepEqual(await trapped(async () => {}), []);
});`;
add("Z1", "probe: body throws after a recorded hit, then an empty trapped run (red means hits leak across runs)", [HYG_TEST],
  { [HYG_TEST]: append(LEAK) });
add("Z2", "probe Z1 with the suggested fix: hits cleared in finally (must be green)", [HYG_TEST],
  { [HYG_TEST]: both((text) => text.replace("    armed = false;\n", () => "    armed = false;\n    leaked = hits.splice(0);\n"),
      (text) => text.replace("  return hits.splice(0);", () => "  return leaked;"),
      (text) => text.replace("  armed = true;\n", () => "  let leaked = [];\n  armed = true;\n"),
      append(LEAK)) });
