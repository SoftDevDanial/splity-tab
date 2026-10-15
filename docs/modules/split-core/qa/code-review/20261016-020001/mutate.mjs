// Node mutation runner for the step 5 re-check (code-review finder, read-only). Each mutant is one exact text edit on
// a fresh copy of ./base (src and tests of HEAD 6cddc66) under ./runs/<id>/, then node --test runs there. Writes only
// inside this scratch folder. Prints one JSON line per mutant and writes runs/summary.json.
import { cpSync, readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const HERE = import.meta.dirname;
const BASE = join(HERE, "base");
const RUNS = join(HERE, "runs");

const MUTANTS = [
  { id: "BASE", why: "the unmutated copy", edits: [] },
  { id: "K02", why: "CR-S5-1, a float floorParts", edits: [["src/core/result.js",
    "return weights.map((weight) => allocateByWeight(amount, [total - weight, weight])[1]);",
    "return weights.map((weight) => Math.floor((amount * weight) / total));"]] },
  { id: "S2a", why: "CR-S5-2, a spread withSpare", edits: [["src/core/spare.js",
    "return Object.fromEntries(BILL_FIELDS.map((field) => [field, field === \"spare\" ? spare : bill[field]]));",
    "return { ...bill, spare };"]] },
  { id: "S2b", why: "CR-S5-2, a spread billWith", edits: [["src/core/bill.js",
    "return Object.fromEntries(BILL_FIELDS.map((field) => [field, changes[field] ?? bill[field]]));",
    "return { ...bill, ...changes };"]] },
  { id: "S2c", why: "CR-S5-2, withSpare drops nextId", edits: [["src/core/spare.js",
    "const BILL_FIELDS = Object.keys(newBill());",
    "const BILL_FIELDS = Object.keys(newBill()).filter((field) => field !== \"nextId\");"]] },
  { id: "N1", why: "C7, NAME_CONTROLS without the g flag", edits: [["src/core/bill.js",
    "\\p{Bidi_Control}]/gu;", "\\p{Bidi_Control}]/u;"]] },
  { id: "N2", why: "C7, NAME_CONTROLS without Bidi_Control", edits: [["src/core/bill.js",
    "/[\\p{Cc}\\p{Zl}\\p{Zp}\\p{Bidi_Control}]/gu;", "/[\\p{Cc}\\p{Zl}\\p{Zp}]/gu;"]] },
  { id: "N3", why: "C7, plainName replaces with a space", edits: [["src/core/bill.js",
    "return text.replace(NAME_CONTROLS, \"\");", "return text.replace(NAME_CONTROLS, \" \");"]] },
  { id: "N4", why: "C7, plainName also deletes Cf", edits: [["src/core/bill.js",
    "return text.replace(NAME_CONTROLS, \"\");", "return text.replace(NAME_CONTROLS, \"\").replace(/\\p{Cf}/gu, \"\");"]] },
  { id: "N5", why: "C7, summary.js keeps the import and prints only Cc as a space (no Bidi_Control literal)", edits: [["src/core/summary.js",
    "row.name.replace(NAME_CONTROLS, \" \")", "row.name.replace(/[\\p{Cc}]/gu, \" \")"]] },
  { id: "N6", why: "C7, plainName deletes only the first match (replace without g semantics via a fresh non-g copy)", edits: [["src/core/bill.js",
    "return text.replace(NAME_CONTROLS, \"\");", "return text.replace(new RegExp(NAME_CONTROLS.source, \"u\"), \"\");"]] },
  { id: "D1", why: "A22 D8, the count is of the stored name", edits: [["src/draft.js",
    "return [...graphemes.segment(plain)].length <= max ? plain : null;",
    "return [...graphemes.segment(name)].length <= max ? plain : null;"]] },
  { id: "D2", why: "A22 D8, no LF and CR check", edits: [["src/draft.js",
    "if (!isString(name) || /[\\r\\n]/.test(name)) return null;", "if (!isString(name)) return null;"]] },
  { id: "D3", why: "A22 D8, an empty decoded name rejects", edits: [["src/draft.js",
    "return [...graphemes.segment(plain)].length <= max ? plain : null;",
    "return plain && [...graphemes.segment(plain)].length <= max ? plain : null;"]] },
  { id: "D4", why: "A22 D8, the name is not rebuilt", edits: [["src/draft.js",
    "const plain = plainName(name);", "const plain = name;"]] },
  { id: "D5", why: "A22 D8, readPerson keeps raw.name", edits: [["src/draft.js",
    "return name === null ? null : { id: raw.id, name };", "return name === null ? null : { id: raw.id, name: raw.name };"]] },
  { id: "D6", why: "A22 D8, readItem keeps raw.name", edits: [["src/draft.js",
    "return { id: raw.id, name, priceText: raw.priceText, who: [...who] };",
    "return { id: raw.id, name: raw.name, priceText: raw.priceText, who: [...who] };"]] },
];

function count(haystack, needle) {
  return haystack.split(needle).length - 1;
}

mkdirSync(RUNS, { recursive: true });
const only = process.argv.slice(2);
const results = [];
for (const mutant of MUTANTS) {
  if (only.length && !only.includes(mutant.id)) continue;
  const dir = join(RUNS, mutant.id);
  if (existsSync(dir)) rmSync(dir, { recursive: true, force: true });
  cpSync(BASE, dir, { recursive: true, filter: (source) => !source.includes("__pycache__") && !source.includes(join("tests", "browser")) });
  let applied = true;
  for (const [file, find, replace] of mutant.edits) {
    const path = join(dir, file);
    const text = readFileSync(path, "utf8");
    if (count(text, find) !== 1) { applied = false; break; }
    writeFileSync(path, text.replace(find, () => replace));
  }
  if (!applied) {
    results.push({ id: mutant.id, why: mutant.why, applied: false });
    console.log(JSON.stringify(results.at(-1)));
    continue;
  }
  const run = spawnSync(process.execPath, ["--test", "--test-reporter=tap", "tests/**/*.test.js"], { cwd: dir, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  const tap = run.stdout;
  writeFileSync(join(dir, "node-test.tap"), tap);
  const pass = Number((tap.match(/^# pass (\d+)/m) ?? [])[1]);
  const fail = Number((tap.match(/^# fail (\d+)/m) ?? [])[1]);
  const failed = [...tap.matchAll(/^\s*not ok \d+ - (.*)$/gm)].map((m) => m[1]).filter((name) => !name.endsWith(".test.js"));
  results.push({ id: mutant.id, why: mutant.why, applied: true, exit: run.status, pass, fail, killed: fail > 0, failed: failed.slice(0, 12) });
  console.log(JSON.stringify(results.at(-1)));
}
writeFileSync(join(RUNS, "summary.json"), JSON.stringify(results, null, 2) + "\n");
