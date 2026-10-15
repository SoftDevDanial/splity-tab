// Browser mutation runner for the step 5 re-check (code-review finder, read-only). Each mutant is one exact text edit
// on a fresh copy of ./base under ./app-runs/<id>/, then a targeted headless pytest run there (the copy's own conftest,
// so its clipboard stand-in, its server and its evidence folder all stay inside the copy). Writes only inside this
// scratch folder. Usage: node mutate_app.mjs <engine> <id> [<id> ...]
import { cpSync, readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const HERE = import.meta.dirname;
const BASE = join(HERE, "base");
const RUNS = join(HERE, "app-runs");
const R62 = "R62";

const MUTANTS = {
  BASE: { why: "the unmutated copy", k: "R62 or R41 or R58_a_run or R20 or R9_the_accessible", edits: [] },
  BASE62: { why: "the unmutated copy, R62 only", k: R62, edits: [] },
  UC1: { why: "A22, the caret at the end of the plain text", k: R62, edits: [["src/ui/dom.js",
    "const caret = plainName(typed.slice(0, input.selectionStart)).length;", "const caret = plain.length;"]] },
  UC2: { why: "A22, the caret less every removed unit, not only those before it", k: R62, edits: [["src/ui/dom.js",
    "const caret = plainName(typed.slice(0, input.selectionStart)).length;",
    "const caret = input.selectionStart - (typed.length - plain.length);"]] },
  UC3: { why: "A22, no setSelectionRange after the write", k: R62, edits: [["src/ui/dom.js",
    "    input.setSelectionRange(caret, caret);\n", ""]] },
  UC4: { why: "A22, the item name field reports the raw value", k: R62, edits: [["src/ui/items.js",
    "onName(id, plainNameField(name))", "onName(id, name.value)"]] },
  UC5: { why: "A22, plainNameField returns the typed text", k: R62, edits: [["src/ui/dom.js",
    "  return plain;\n}", "  return typed;\n}"]] },
  U4: { why: "CR-S5-7, a floor in place of the ceiling for --rows", k: "R20", edits: [["src/ui/receipt.js",
    "String(Math.ceil(result.rows.length / 2))", "String(Math.floor(result.rows.length / 2))"]] },
  E1: { why: "CR-S5-14, evidence_dir back on exist_ok=True", k: "R58_a_run", edits: [["tests/browser/conftest.py",
    "folder.mkdir(parents=True)", "folder.mkdir(parents=True, exist_ok=True)"]] },
  G1: { why: "CR-S5-6, the guard reads live_e2e.py only (no helpers)", k: "R41", edits: [["tests/browser/test_app.py",
    "run = [(tree, module_strings(tree)), *((function, helper_strings) for function in gate_helpers(tree, helper_tree))]",
    "run = [(tree, module_strings(tree))]"]] },
  PROBE: { why: "Known limits probe, a double click on Dismiss note and on a mode label", k: "probe_known_limit", edits: [],
    extra: "probe_known_limit.py" },
};

const count = (haystack, needle) => haystack.split(needle).length - 1;
const [engine, ...ids] = process.argv.slice(2);
mkdirSync(RUNS, { recursive: true });
for (const id of ids) {
  const mutant = MUTANTS[id];
  const dir = join(RUNS, `${id}-${engine}`);
  if (existsSync(dir)) rmSync(dir, { recursive: true, force: true });
  cpSync(BASE, dir, { recursive: true, filter: (source) => !source.includes("__pycache__") });
  let applied = true;
  for (const [file, find, replace] of mutant.edits) {
    const path = join(dir, file);
    const text = readFileSync(path, "utf8");
    if (count(text, find) !== 1) { applied = false; break; }
    writeFileSync(path, text.replace(find, () => replace));
  }
  if (mutant.extra) cpSync(join(HERE, mutant.extra), join(dir, "tests", "browser", `test_${mutant.extra}`));
  if (!applied) { console.log(JSON.stringify({ id, engine, applied: false })); continue; }
  const args = ["-m", "pytest", "tests/browser", "-q", "-p", "no:cacheprovider", "-k", mutant.k, "--engine", engine, "-rA", "-s"];
  if (mutant.extra) args[2] = `tests/browser/test_${mutant.extra}`;
  const started = Date.now();
  const run = spawnSync("python", args, { cwd: dir, encoding: "utf8", env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" },
    maxBuffer: 64 * 1024 * 1024, timeout: 15 * 60 * 1000 });
  const text = `${run.stdout}\n----- stderr -----\n${run.stderr}`;
  writeFileSync(join(dir, "pytest.txt"), text);
  const summary = (run.stdout.trim().split("\n").filter((line) => /passed|failed|error/.test(line)).at(-1)) ?? "no summary";
  const failed = [...run.stdout.matchAll(/^FAILED (\S+)/gm)].map((m) => m[1].split("::").at(-1));
  console.log(JSON.stringify({ id, engine, why: mutant.why, exit: run.status, signal: run.signal, seconds: Math.round((Date.now() - started) / 1000),
    summary, failed }));
}
