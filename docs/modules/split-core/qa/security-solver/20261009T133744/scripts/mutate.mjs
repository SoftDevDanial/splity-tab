// Mutation run for the split-core security fix batch, round 2 (SEC-05, SEC-06).
// Usage: node mutate.mjs <project root> <output dir> <stage> [id,id,...]
// For each mutant: copies src/ and tests/ into <output>/<stage>/mutants/<id>/, renames *.test.js to
// *.mutcase.js (so no "*.test.js" glob picks the copies up), applies the edits, runs the copied suite in
// a child process and records which tests fail and the child's PID. Verdicts:
//   KILLED            every expected test failed
//   KILLED-ONLY       KILLED, and no other test failed
//   SURVIVED          an expected test passed (a weak test)
//   CONTROL-HELD      a control with no expected failures stayed green, as designed
//   CONTROL-BROKEN    a control went red
// "RED" controls put back a test file from BASE (the commit before this round) to show the old suite
// stays green on the same mutant. The project tree itself is never written.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, copyFileSync, statSync } from "node:fs";
import { spawnSync, execFileSync } from "node:child_process";

const [project, output, stage, only] = process.argv.slice(2);
const BASE = "a47bcb7";
const NL = String.fromCharCode(10);
const pick = only ? new Set(only.split(",")) : null;

const base = (file) => execFileSync("git", ["-C", project, "show", `${BASE}:${file}`], { encoding: "utf8" });
const swap = (search, replace) => (text) => {
  const hits = text.split(search).length - 1;
  if (hits !== 1) throw new Error(`search text found ${hits} times: ${search}`);
  return text.replace(search, replace);
};
const append = (code) => (text) => `${text}${NL}${code}${NL}`;
const fromBase = (file) => () => base(file);

// The plants are read from the suite itself, so this evidence cannot drift from what the suite serves.
const hygiene = readFileSync(`${project}/tests/hygiene.test.js`, "utf8");
const plantsFrom = hygiene.indexOf("const AUDITOR_PLANTS = [");
const AUDITOR_PLANTS = new Function(`${hygiene.slice(plantsFrom, hygiene.indexOf("];", plantsFrom) + 2)}\nreturn AUDITOR_PLANTS;`)();
const MISSED_BY_THE_SCAN = new Set(["F1", "F2", "F3", "F4b", "F5", "F6b", "F7", "F8", "F9", "F10"]);

const TRAP_CLEAN = "@R25 runtime trap: the core touches no banned global or method while it loads and runs";
const PROPERTY = "@R24 exactly the R24 class prints as a space";
const ABOVE = "@R24 every code point above U+2069 prints as typed";
const CORE = ["money.js", "allocate.js", "bill.js", "result.js", "summary.js"];

const CLASS = "[\\p{Cc}\\p{Zl}\\p{Zp}\\p{Bidi_Control}]";
const TWELVE = "\\n\\r\\u000B\\u000C\\u0085\\x00\\x1C\\x1D\\x1E\\x1B\\u{2028}\\u{2029}";
const narrow = (inner) => swap(`const CONTROLS = /${CLASS}/gu;`, `const CONTROLS = /[${inner}]/gu;`);

// [id, finding, what, [[file, edit], ...], [substring of each test title that must fail], onlyThese]
const mutants = [];
AUDITOR_PLANTS.forEach(([id, , plant], index) => {
  const file = CORE[index % CORE.length];
  mutants.push([`S05-${id}`, "SEC-05", `the re-check's ${id} plant written into src/core/${file}`,
    [[`src/core/${file}`, append(plant)]], [TRAP_CLEAN], false]);
  if (MISSED_BY_THE_SCAN.has(id)) {
    mutants.push([`S05-${id}-RED`, "SEC-05", `CONTROL: ${id} in src/core/${file} with the hygiene test as it was before this round. Expected to stay green (the gap)`,
      [[`src/core/${file}`, append(plant)], ["tests/hygiene.test.js", fromBase("tests/hygiene.test.js")]], [], false]);
  }
});
// The name is split so no banned word appears in the text, even inside a string: only the trap can see it.
const RUN_TIME_ONLY = "  const whole = wholePart(bp) + ((() => 0).constructor(\"return typeof f\" + \"etch\")() === \"x\" ? 1 : 0);";
mutants.push(["S05-RUN", "SEC-05", "formatRate reaches fetch through the constructor route, only when it runs",
  [["src/core/money.js", swap("  const whole = wholePart(bp);", RUN_TIME_ONLY)]], [TRAP_CLEAN], true]);
mutants.push(["S05-RUN-RED", "SEC-05", "CONTROL: S05-RUN with the hygiene test as it was before this round. Expected to stay green",
  [["src/core/money.js", swap("  const whole = wholePart(bp);", RUN_TIME_ONLY)],
    ["tests/hygiene.test.js", fromBase("tests/hygiene.test.js")]], [], false]);
mutants.push(["S05-EXPORT", "SEC-05", "a new export that the trap workload never calls",
  [["src/core/money.js", append("export function r25Extra() { return 1; }")]], [TRAP_CLEAN], true]);

mutants.push(
  ["S06-RLO", "SEC-06", "bidi part narrowed to RLO only", [["src/core/summary.js", narrow("\\p{Cc}\\p{Zl}\\p{Zp}\\u{202E}")]], [PROPERTY], true],
  ["S06-12", "SEC-06", "control part narrowed to the 12 named controls", [["src/core/summary.js", narrow(`${TWELVE}\\p{Bidi_Control}`)]], [PROPERTY], true],
  ["S06-BOTH", "SEC-06", "the 12 named controls plus RLO only", [["src/core/summary.js", narrow(`${TWELVE}\\u{202E}`)]], [PROPERTY], true],
  ["S06-OVER", "SEC-06", "space separators replaced too (NBSP, U+3000 and the rest of Zs)",
    [["src/core/summary.js", narrow("\\p{Cc}\\p{Zl}\\p{Zp}\\p{Bidi_Control}\\p{Zs}")]], [PROPERTY, ABOVE], true],
  ["S06-ASTRAL", "SEC-06", "one astral code point (U+1F600) replaced too",
    [["src/core/summary.js", narrow("\\p{Cc}\\p{Zl}\\p{Zp}\\p{Bidi_Control}\\u{1F600}")]], [ABOVE], true],
  ["S06-RLO-RED", "SEC-06", "CONTROL: S06-RLO with summary tests as they were before this round. Expected to stay green (the gap)",
    [["src/core/summary.js", narrow("\\p{Cc}\\p{Zl}\\p{Zp}\\u{202E}")], ["tests/summary.test.js", fromBase("tests/summary.test.js")]], [], false],
  ["S06-12-RED", "SEC-06", "CONTROL: S06-12 with summary tests as they were before this round. Expected to stay green (the gap)",
    [["src/core/summary.js", narrow(`${TWELVE}\\p{Bidi_Control}`)], ["tests/summary.test.js", fromBase("tests/summary.test.js")]], [], false],
);

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
for (const [id, finding, what, edits, expect, onlyThese] of mutants) {
  if (pick && !pick.has(id)) continue;
  const dir = `${output}/${stage}/mutants/${id}`;
  copyTree(`${project}/src`, `${dir}/src`, (name) => name);
  copyTree(`${project}/tests`, `${dir}/tests`, toMutcase);
  let broken = null;
  for (const [file, edit] of edits) {
    const target = `${dir}/${toMutcase(file)}`;
    try {
      const before = readFileSync(target, "utf8");
      const after = edit(before);
      if (after === before) throw new Error("edit changed nothing");
      writeFileSync(target, after);
    } catch (error) {
      broken = `${file}: ${error.message}`;
      break;
    }
  }
  if (broken) {
    rows.push({ id, finding, what, error: broken });
    continue;
  }
  const run = spawnSync(process.execPath, ["--test", "tests/**/*.mutcase.js"], { cwd: dir, encoding: "utf8", timeout: 180000, killSignal: "SIGKILL" });
  const text = run.stdout + run.stderr;
  writeFileSync(`${dir}/node-test.txt`, text);
  const count = (label) => Number((text.match(new RegExp(`^ℹ ${label} (\\d+)`, "m")) ?? [])[1] ?? NaN);
  const failed = [...new Set(text.split(NL).filter((line) => /^✖ /.test(line) && !/failing tests:/.test(line))
    .map((line) => line.replace(/^✖ /, "").replace(/ \([0-9.]+ms\)$/, "")))];
  const missed = expect.filter((needle) => !failed.some((title) => title.includes(needle)));
  const extra = failed.filter((title) => !expect.some((needle) => title.includes(needle)));
  let verdict;
  if (!Number.isInteger(count("tests"))) verdict = "HARNESS-ERROR";
  else if (expect.length === 0) verdict = failed.length === 0 ? "CONTROL-HELD" : "CONTROL-BROKEN";
  else if (missed.length > 0) verdict = "SURVIVED";
  else verdict = onlyThese && extra.length === 0 ? "KILLED-ONLY" : "KILLED";
  rows.push({
    id, finding, what, childPid: run.pid, exitStatus: run.status, signal: run.signal,
    tests: count("tests"), pass: count("pass"), fail: count("fail"), verdict,
    expectedToFail: expect, expectedButPassed: missed, alsoFailed: extra, failed,
  });
}
writeFileSync(`${output}/${stage}/mutation-summary.json`, JSON.stringify(rows, null, 2) + NL);
for (const row of rows) {
  console.log(`${row.id} ${row.verdict ?? row.error} fail=${row.fail ?? "-"}/${row.tests ?? "-"} pid=${row.childPid ?? "-"} exit=${row.exitStatus ?? "-"} also=${row.alsoFailed?.length ?? "-"} ${row.what}`);
}
