// Mutation run for the split-core security fix batch (SEC-01 to SEC-04).
// Usage: node mutate.mjs <project root> <output dir> <stage> [id,id,...]
// For each mutant: copies src/ and tests/ into <output>/<stage>/mutants/<id>/, renames *.test.js to
// *.mutcase.js (so no "*.test.js" glob picks the copies up), applies the edits, runs the copied suite in
// a child process and records which tests fail and the child's PID. Verdicts:
//   KILLED            every expected test failed
//   KILLED-ONLY       KILLED, and no other test failed ("each mutant fails only its own test")
//   SURVIVED          an expected test passed (a weak test)
//   CONTROL-HELD      a control with no expected failures stayed green, as designed
//   CONTROL-BROKEN    a control went red
// "RED" mutants restore a file from BASE (the commit before this batch) to show the new tests fail on the
// old code. The project tree itself is never written.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, copyFileSync, statSync } from "node:fs";
import { spawnSync, execFileSync } from "node:child_process";

const [project, output, stage, only] = process.argv.slice(2);
const BASE = "e034951";
const NL = String.fromCharCode(10);
const pick = only ? new Set(only.split(",")) : null;

const base = (file) => execFileSync("git", ["-C", project, "show", `${BASE}:${file}`], { encoding: "utf8" });
const swap = (search, replace) => (text) => {
  const hits = text.split(search).length - 1;
  if (hits !== 1) throw new Error(`search text found ${hits} times: ${search}`);
  return text.replace(search, replace);
};
const append = (line) => (text) => `${text}${NL}${line}${NL}`;
const fromBase = (file) => () => base(file);

const R24_OTHER = (label) => `@R24 a ${label} inside a name prints as a space, so no reader can cut the summary there`;
const OTHER = [["NUL", "\\x00"], ["FS", "\\x1C"], ["GS", "\\x1D"], ["RS", "\\x1E"], ["ESC", "\\x1B"]];
const RLO_TEST = "@R24 a right-to-left override in a name cannot reorder the share";
const scanOf = (file) => `@R25 ${file} uses no banned name`;

// [id, finding, what, [[file, edit], ...], [substring of each test title that must fail], onlyThese]
const mutants = [
  ["S01-RED", "SEC-01", "RED: summary.js as it was before the batch (the seven line breaks only)",
    [["src/core/summary.js", fromBase("src/core/summary.js")]],
    OTHER.map(([label]) => R24_OTHER(label)), false],
  ...OTHER.map(([label, escape]) => [`S01-${label}`, "SEC-01", `the class lets ${label} through`,
    [["src/core/summary.js", swap("const CONTROLS = /[", `const CONTROLS = /(?!${escape})[`)]],
    [R24_OTHER(label)], true]),
  ["S02-RED", "SEC-02", "RED: the class without \\p{Bidi_Control}",
    [["src/core/summary.js", swap("\\p{Bidi_Control}", "")]],
    [RLO_TEST], true],
];

// SEC-04: one planted use per name, each in a different core file. Each must fail only that file's scan.
const PLANTS = [
  ["eval", "money.js", "const run = (text) => eval(text);"],
  ["Function()", "allocate.js", "const make = (body) => Function(body);"],
  ["new Function", "bill.js", "const build = (body) => new Function(body);"],
  ["import()", "result.js", "const load = (name) => import(name);"],
  ["queueMicrotask", "summary.js", "const soon = (fn) => queueMicrotask(fn);"],
  ["setImmediate", "money.js", "const later = (fn) => setImmediate(fn);"],
  ["performance", "allocate.js", "const now = () => performance.now();"],
  ["crypto", "bill.js", "const pick = () => crypto.getRandomValues(new Uint32Array(1))[0];"],
  ["WebSocket", "result.js", "const open = (url) => new WebSocket(url);"],
  ["process", "summary.js", "const env = () => process.env.SPLIT;"],
  ["require", "money.js", "const load = (name) => require(name);"],
];
PLANTS.forEach(([name, file, line], index) => {
  mutants.push([`S04-${String(index + 1).padStart(2, "0")}`, "SEC-04", `planted ${name} in ${file}: ${line}`,
    [[`src/core/${file}`, append(line)]], [scanOf(file)], true]);
});
mutants.push(["S04-RED", "SEC-04", "CONTROL: every plant at once with the hygiene test as it was before the batch. Expected to stay green, which is the gap SEC-04 closes",
  [...PLANTS.map(([, file, line]) => [`src/core/${file}`, append(line)]),
    ["tests/hygiene.test.js", fromBase("tests/hygiene.test.js")]],
  [], false]);
mutants.push(["S04-PROSE", "SEC-04", "CONTROL: every new word only in a comment and a string. Expected to stay green (code-only matching)",
  [["src/core/summary.js", append("// eval, Function(x), new Function, import(x), queueMicrotask, setImmediate, performance, crypto, WebSocket, process, require" + NL +
    "const PROSE = \"eval Function(x) new Function import(x) queueMicrotask setImmediate performance crypto WebSocket process require\";")]],
  [], false]);

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
  const run = spawnSync(process.execPath, ["--test", "tests/**/*.mutcase.js"], { cwd: dir, encoding: "utf8", timeout: 120000, killSignal: "SIGKILL" });
  const text = run.stdout + run.stderr;
  writeFileSync(`${dir}/node-test.txt`, text);
  const count = (label) => Number((text.match(new RegExp(`^ℹ ${label} (\\d+)`, "m")) ?? [])[1] ?? NaN);
  const failed = [...new Set(text.split(NL).filter((line) => /^✖ /.test(line) && !/failing tests:/.test(line))
    .map((line) => line.replace(/^✖ /, "").replace(/ \([0-9.]+ms\)$/, "")))];
  const missed = expect.filter((needle) => !failed.some((title) => title.includes(needle)));
  const extra = failed.filter((title) => !expect.some((needle) => title.includes(needle)));
  let verdict;
  if (expect.length === 0) verdict = failed.length === 0 ? "CONTROL-HELD" : "CONTROL-BROKEN";
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
  console.log(`${row.id} ${row.verdict ?? row.error} fail=${row.fail ?? "-"}/${row.tests ?? "-"} pid=${row.childPid ?? "-"} exit=${row.exitStatus ?? "-"} ${row.what}`);
}
