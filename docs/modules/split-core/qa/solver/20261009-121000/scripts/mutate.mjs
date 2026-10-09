// Mutation run for the split-core solver batch (code-review WR-01 to WR-10).
// Usage: node mutate.mjs <project root> <output dir> [id,id,...]
// Copies src/ and tests/ into <output dir>/mutants/<id>/, renames *.test.js to *.mutcase.js (so no
// "*.test.js" glob ever picks the copies up), applies the edits of one mutant, runs the copied suite
// and records which tests fail. A mutant is KILLED only when every test named in `expect` fails.
// The project tree itself is never written.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, copyFileSync, statSync } from "node:fs";
import { spawnSync } from "node:child_process";

const [project, output, only] = process.argv.slice(2);
const NL = String.fromCharCode(10);
const pick = only ? new Set(only.split(",")) : null;

// [id, finding, what, [[file, search, replace], ...], [substring of each test title that must fail]]
const mutants = [
  ["S01", "WR-01", "allocateByWeight floors with a float product and a float divide (M04)",
    [["src/core/allocate.js",
      "const floors = weights.map((w) => (bigAmount * BigInt(w)) / total);",
      "const floors = weights.map((w) => BigInt(Math.floor((amount * w) / Number(total))));"]],
    ["BigInt trap: allocateByWeight(236419679", "BigInt trap: allocateByWeight(61846725",
      "BigInt trap: allocateByWeight(178450942"]],
  ["S02", "WR-01", "allocateByWeight rounds the product in float, then divides exactly",
    [["src/core/allocate.js",
      "const floors = weights.map((w) => (bigAmount * BigInt(w)) / total);",
      "const floors = weights.map((w) => BigInt(amount * w) / total);"]],
    ["BigInt trap: allocateByWeight(236419679", "BigInt trap: allocateByWeight(61846725",
      "BigInt trap: allocateByWeight(178450942"]],
  ["S03", "WR-03", "setMode spreads the whole bill (M12, the threat model forbids it)",
    [["src/core/bill.js", "  return billWith(bill, { mode });", "  return { ...bill, mode };"]],
    ["@R16 setMode on a parsed bill builds only known fields"]],
  ["S04", "WR-03", "itemWith spreads the item it rebuilds",
    [["src/core/bill.js", "  return {" + NL + "    id: item.id,", "  return {" + NL + "    ...item," + NL + "    id: item.id,"]],
    ["@R16 removePerson on a parsed bill", "@R16 setItemName on a parsed bill",
      "@R16 setItemPriceText on a parsed bill", "@R16 toggleItemPerson on a parsed bill"]],
  ["S05", "WR-03", "setPersonName spreads the person (M11)",
    [["src/core/bill.js", "personWith(person, { name })", "({ ...person, name })"]],
    ["@R16 setPersonName on a parsed bill", "@R16 setPersonName (person with a __proto__ key) on a parsed bill"]],
  ["S06", "WR-04", "addPerson builds the id from the list length, not nextId (M07)",
    [["src/core/bill.js", "const person = { id: `p${bill.nextId}`, name: \"\" };",
      "const person = { id: `p${bill.people.length + 1}`, name: \"\" };"]],
    ["@R11 a new person's id comes from nextId"]],
  ["S07", "WR-05", "summaryText trims row names in place (M08, mutates its input)",
    [["src/core/summary.js", "  const { charges } = result;",
      "  const { charges } = result;" + NL + "  result.rows.forEach((row) => { row.name = row.name.trim(); });"]],
    ["@R16 summaryText leaves a deep-frozen result alone"]],
  ["S08", "WR-05", "allocateByWeight reverses its weights and back (writes, same output)",
    [["src/core/allocate.js", "  assertAmount(amount);" + NL + "  if (weights.length === 0",
      "  assertAmount(amount);" + NL + "  weights.reverse().reverse();" + NL + "  if (weights.length === 0"]],
    ["@R16 allocateByWeight leaves frozen weights alone"]],
  ["S09", "WR-05", "itemLabel writes the name back onto the item",
    [["src/core/bill.js", "return labelOf(item.name, \"Item\", index);", "return labelOf((item.name = item.name), \"Item\", index);"]],
    ["@R16 @R17 the labels leave a frozen person or item alone"]],
  ["S10", "WR-05", "personLabel writes the name back onto the person",
    [["src/core/bill.js", "return labelOf(person.name, \"Person\", index);", "return labelOf((person.name = person.name), \"Person\", index);"]],
    ["@R16 @R17 the labels leave a frozen person or item alone", "@R21 @R23 by-item result for S1"]],
  ["S11", "WR-05", "computeResult writes to a by-item bill only at the price maximum, then restores it",
    [["src/core/result.js", "  const prices = parsed.map((price) => price.cents);",
      "  const prices = parsed.map((price) => price.cents);" + NL +
      "  if (prices.includes(9999999)) bill.items.reverse().reverse();"]],
    ["@R21 @R23 by-item result for MAX-I"]],
  ["S11c", "WR-05", "CONTROL: S11 with the fixtures left unfrozen. Expected to SURVIVE, which shows the freeze kills S11",
    [["src/core/result.js", "  const prices = parsed.map((price) => price.cents);",
      "  const prices = parsed.map((price) => price.cents);" + NL +
      "  if (prices.includes(9999999)) bill.items.reverse().reverse();"],
    ["tests/support/bills.js", "const fixture = (spec) => deepFreeze(buildBill(spec));",
      "const fixture = (spec) => buildBill(spec);"]],
    []],
  ["S12", "WR-06", "remove the digit cap (M01)",
    [["src/core/money.js", "  if (whole.length > String(wholePart(maxHundredths)).length) return INVALID;" + NL, ""]],
    ["@R1 @R3 a whole part longer than the ceiling's is refused before any numeric conversion"]],
  ["S13", "WR-06", "digit cap back to the old magic number 9",
    [["src/core/money.js", "whole.length > String(wholePart(maxHundredths)).length", "whole.length > 9"]],
    ["@R1 @R3 a whole part longer than the ceiling's is refused before any numeric conversion"]],
  ["S15", "WR-07", "formatMoney via a float divide and toLocaleString (M09)",
    [["src/core/money.js", "return `RM ${wholePart(cents)}.${String(cents % 100).padStart(2, \"0\")}`;",
      "return `RM ${(cents / 100).toLocaleString(\"en\", { minimumFractionDigits: 2, maximumFractionDigits: 2, useGrouping: false })}`;"]],
    ["@R25 money.js uses no banned name"]],
  ["S16", "WR-07", "formatMoney via Intl.NumberFormat",
    [["src/core/money.js", "return `RM ${wholePart(cents)}.${String(cents % 100).padStart(2, \"0\")}`;",
      "return `RM ${new Intl.NumberFormat(\"en\", { minimumFractionDigits: 2, useGrouping: false }).format(cents / 100)}`;"]],
    ["@R25 money.js uses no banned name"]],
  ["S17", "WR-07", "planted toLocaleDateString in summary.js",
    [["src/core/summary.js", "export function summaryText(result) {",
      "const stamp = (when) => when.toLocaleDateString(\"en-MY\");" + NL + "export function summaryText(result) {"]],
    ["@R25 summary.js uses no banned name"]],
  ["S18", "WR-07", "planted setTimeout in bill.js",
    [["src/core/bill.js", "export function newBill() {",
      "const later = (fn) => setTimeout(fn, 0);" + NL + "export function newBill() {"]],
    ["@R25 bill.js uses no banned name"]],
  ["S19", "WR-07", "planted setInterval in result.js",
    [["src/core/result.js", "export function computeResult(bill) {",
      "const tick = (fn) => setInterval(fn, 1000);" + NL + "export function computeResult(bill) {"]],
    ["@R25 result.js uses no banned name"]],
  ["S20", "WR-07", "planted requestAnimationFrame in allocate.js",
    [["src/core/allocate.js", "export function allocateEvenly(amount, count) {",
      "const nextFrame = (fn) => requestAnimationFrame(fn);" + NL + "export function allocateEvenly(amount, count) {"]],
    ["@R25 allocate.js uses no banned name"]],
  ["S14", "WR-06", "digit cap from the amount ceiling only, not the caller's",
    [["src/core/money.js", "whole.length > String(wholePart(maxHundredths)).length",
      "whole.length > String(wholePart(AMOUNT_MAX_CENTS)).length"]],
    ["@R1 @R3 a whole part longer than the ceiling's is refused before any numeric conversion"]],
];

// WR-10: no replacement at all, then one mutant per character left out of the class. The class is
// written with \u{...} escapes for U+2028 and U+2029, exactly as in src/core/summary.js.
const BREAK_TOKENS = [["LF", "\\n"], ["CR", "\\r"], ["VT", "\\u000B"], ["FF", "\\u000C"],
  ["NEL", "\\u0085"], ["LS", "\\u{2028}"], ["PS", "\\u{2029}"]];
const BREAK_CLASS = `[${BREAK_TOKENS.map(([, token]) => token).join("")}]`;
mutants.push(["S21", "WR-10", "summaryText prints row names without replacing line breaks",
  [["src/core/summary.js", "${row.name.replace(LINE_BREAKS, \" \")}", "${row.name}"]],
  [...BREAK_TOKENS.map(([label]) => `a ${label} inside a name`), "@R24 by-item rows get the same line-break guard"]]);
BREAK_TOKENS.forEach(([label, token], index) => {
  mutants.push([`S${22 + index}`, "WR-10", `the line-break class leaves out ${label}`,
    [["src/core/summary.js", BREAK_CLASS, BREAK_CLASS.replace(token, "")]],
    [`a ${label} inside a name`]]);
});

function copyTree(from, to, rename) {
  mkdirSync(to, { recursive: true });
  for (const name of readdirSync(from)) {
    const source = `${from}/${name}`;
    if (statSync(source).isDirectory()) {
      if (name === "browser") continue;
      copyTree(source, `${to}/${name}`, rename);
    } else if (name.endsWith(".js")) {
      copyFileSync(source, `${to}/${rename(name)}`);
    }
  }
}

const toMutcase = (name) => name.replace(/\.test\.js$/, ".mutcase.js");
const rows = [];
for (const [id, finding, what, edits, expect] of mutants) {
  if (pick && !pick.has(id)) continue;
  const dir = `${output}/mutants/${id}`;
  copyTree(`${project}/src`, `${dir}/src`, (name) => name);
  copyTree(`${project}/tests`, `${dir}/tests`, toMutcase);
  let broken = null;
  for (const [file, search, replace] of edits) {
    const target = `${dir}/${file.replace(/\.test\.js$/, ".mutcase.js")}`;
    const text = readFileSync(target, "utf8");
    const hits = text.split(search).length - 1;
    if (hits !== 1) {
      broken = `${file}: search text found ${hits} times`;
      break;
    }
    writeFileSync(target, text.replace(search, replace));
  }
  if (broken) {
    rows.push({ id, finding, what, error: broken });
    continue;
  }
  const run = spawnSync(process.execPath, ["--test", "tests/**/*.mutcase.js"], { cwd: dir, encoding: "utf8" });
  const text = run.stdout + run.stderr;
  writeFileSync(`${dir}/node-test.txt`, text);
  const count = (label) => Number((text.match(new RegExp(`^ℹ ${label} (\\d+)`, "m")) ?? [])[1] ?? NaN);
  const failed = [...new Set(text.split(NL).filter((line) => /^✖ /.test(line) && !/failing tests:/.test(line))
    .map((line) => line.replace(/^✖ /, "").replace(/ \([0-9.]+ms\)$/, "")))];
  const missed = expect.filter((needle) => !failed.some((title) => title.includes(needle)));
  rows.push({
    id, finding, what,
    tests: count("tests"), pass: count("pass"), fail: count("fail"),
    verdict: missed.length === 0 && failed.length > 0 ? "KILLED" : "SURVIVED",
    expectedToFail: expect, expectedButPassed: missed, failed,
  });
}
writeFileSync(`${output}/mutation-summary${pick ? `-${[...pick].join("-")}` : ""}.json`, JSON.stringify(rows, null, 2) + NL);
for (const row of rows) {
  console.log(`${row.id} ${row.finding} ${row.verdict ?? row.error} fail=${row.fail ?? "-"}/${row.tests ?? "-"} ${row.what}`);
}
