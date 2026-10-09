// R04. Try to break codeOnly (tests/hygiene.test.js, SEC-04 fix). For each planted snippet:
//   exec   - a child imports src/core/money.js with the snippet appended in memory and records which banned
//            global it really reaches (proof that the snippet is live code, not prose);
//   real   - a child runs the REAL, unchanged tests/hygiene.test.js with a preload that appends the snippet
//            to every core file in memory; a false negative is a fully green run;
//   mirror - bannedNamesIn and codeOnly extracted at run time from HEAD's tests/hygiene.test.js (no copy),
//            applied to each real core file plus the snippet.
// Every child is spawnSync with a SIGKILL timeout. A run whose counts cannot be read is a HARNESS ERROR.
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = fileURLToPath(new URL("../../../../../../../", import.meta.url));
const HERE = fileURLToPath(new URL("./", import.meta.url));
const PRELOAD = pathToFileURL(`${HERE}r04-preload-plant.mjs`).href;
const BS = String.fromCharCode(92);

// Extract the scanner from HEAD's test file at run time, so the mirror cannot drift from it.
const testSource = readFileSync(`${ROOT}tests/hygiene.test.js`, "utf8");
const from = testSource.indexOf("const BANNED = [");
const to = testSource.indexOf("function specifiersIn");
const scanner = new Function(`${testSource.slice(from, to)}\nreturn { codeOnly, bannedNamesIn };`)();
const coreNames = ["allocate.js", "bill.js", "money.js", "result.js", "summary.js"];
const coreSources = coreNames.map((n) => [n, readFileSync(`${ROOT}src/core/${n}`, "utf8")]);

// Fidelity: the solver's own control assertions must hold for the extracted scanner.
const fidelity = [
  [scanner.bannedNamesIn("const t = `took ${performance.now()} ms`;"), ["performance"]],
  [scanner.bannedNamesIn("const t = `a ${`b ${eval(x)}`} c`;"), ["eval"]],
  [scanner.bannedNamesIn("const half = total / 2; const quote = /'/; require(x);"), ["require"]],
  [scanner.bannedNamesIn("const evaluate = 1; const processed = 2; myFunction(3); importer(4);"), []],
  ...coreSources.map(([, s]) => [scanner.bannedNamesIn(s), []]),
];
const fidelityOk = fidelity.every(([got, want]) => JSON.stringify(got) === JSON.stringify(want));
console.log(`extracted scanner: ${to - from} characters from HEAD tests/hygiene.test.js; solver controls and 5 real files reproduce: ${fidelityOk}`);

const PLANTS = [
  ["CTRL plain call (must go red)", "performance", "const r04Now = performance.now();"],
  ["CTRL nested template (must go red)", "performance", "const r04T = `a ${`b ${performance.now()}`} c`;"],
  ["CTRL regex after = with a quote (must go red)", "performance", "const r04Re = /'/; const r04N2 = performance.now();"],
  ["F1 postfix ++ then division", "process", "let r04Hits = 0; const r04Rate = r04Hits++ / process.uptime();"],
  ["F2 keyword-named member then division", "performance", "const r04Range = { in: 2 }; const r04Ratio = r04Range.in / performance.now();"],
  ["F3 regex after if (...) holding a quote", "performance", "const r04Q = \"'\"; if (r04Q) /'/.test(r04Q) && performance.now();"],
  ["F4 regex after if (...) holding a backtick, next line hidden", "process", "const r04K = \"k\"; if (r04K) /`/.test(r04K);\nconst r04Env = process.env.PATH;"],
  ["F4b same, closed again on the line by a backtick in a string", "process", "const r04K = \"k\"; if (r04K) /`/.test(r04K) || process.env.PATH; const r04Tick = \"`\";"],
  ["F5 regex after if (...) holding //", "performance", `const r04U = "u"; if (r04U) /${BS}/${BS}//.test(r04U) || performance.now();`],
  ["F6 template ${x++ / 2} desyncs, code after the function hidden", "process", "export function r04Label(n) {\n  return `${n++ / 2} items`;\n}\nconst r04Pid = process.pid;"],
  ["F6b same, resynced by a backtick in a string", "process", "export function r04Label(n) {\n  return `${n++ / 2} items`;\n}\nconst r04Pid = process.pid; const r04Tick = \"`\";"],
  ["F7 Function referenced without a call", "Function", "const r04F = Function; const r04V = r04F(\"return 1\")();"],
  ["F8 unicode escape in an identifier (new list)", "process", `const r04P = ${BS}u{70}rocess.pid;`],
  ["F9 unicode escape in an identifier (original list)", "Date", `const r04D = ${BS}u{44}ate.now();`],
  ["F10 constructor route, no name at all", "Function.prototype.constructor", "const r04C = (() => 0).constructor(\"return 1\")();"],
];

const b64 = (s) => Buffer.from(s, "utf8").toString("base64");
const FAIL_LINE = new RegExp(`(?:^|\\n)(?:not ok \\d+ - |${String.fromCodePoint(0x2716)} )(.+)`, "g");
const pids = [];
const rows = [];
for (const [title, target, plant] of PLANTS) {
  const env = { ...process.env, R04_PLANT: b64(plant) };
  const exec = spawnSync(process.execPath, [`${HERE}r04-exec-child.mjs`], { env, timeout: 30000, killSignal: "SIGKILL", encoding: "utf8" });
  pids.push(exec.pid);
  let execOut;
  try { execOut = JSON.parse(exec.stdout.trim().split("\n").at(-1)); } catch { execOut = { reached: [], error: exec.stderr.split("\n").find((l) => /Error/.test(l)) ?? `exit ${exec.status}` }; }
  const real = spawnSync(process.execPath, ["--import", PRELOAD, "tests/hygiene.test.js"], { cwd: ROOT, env, timeout: 60000, killSignal: "SIGKILL", encoding: "utf8" });
  pids.push(real.pid);
  const num = (key) => Number((real.stdout.match(new RegExp(`(?:^|\\n)(?:# |${String.fromCodePoint(0x2139)} )${key} (\\d+)`)) ?? [])[1]);
  const tests = num("tests"), pass = num("pass"), fail = num("fail");
  const failed = [...new Set([...real.stdout.matchAll(FAIL_LINE)].map((m) => m[1].trim().replace(/ \([0-9.]+ms\)$/, "")))];
  const scanFails = failed.filter((t) => /uses no banned name/.test(t)).length;
  const plantFails = failed.filter((t) => /served into each core file/.test(t)).length;
  const mirror = coreSources.map(([, s]) => scanner.bannedNamesIn(`${s}\n${plant}\n`));
  const mirrorHits = [...new Set(mirror.flat())];
  const live = execOut.reached.includes(target) && !execOut.error;
  const counted = Number.isInteger(pass) && Number.isInteger(fail);
  const green = counted && fail === 0 && pass > 0;
  let verdict;
  if (!counted) verdict = `HARNESS ERROR (exit ${real.status}) ${real.stderr.split("\n").find((l) => /Error/.test(l)) ?? ""}`;
  else if (title.startsWith("CTRL")) verdict = green ? "CONTROL BROKEN" : `control red, as it must be (per-file scans failing: ${scanFails})`;
  else if (live && green) verdict = "FALSE NEGATIVE (live code, real test green)";
  else if (green) verdict = "green, but not live";
  else verdict = scanFails > 0 ? "caught by the per-file scan" : `red only by side effect (per-file scans green, ${plantFails} plant self-tests broken)`;
  rows.push({ title, target, live, execError: execOut.error, reached: execOut.reached, tests, pass, fail, mirrorHits, verdict });
}

for (const r of rows) {
  console.log(`\n${r.title}`);
  console.log(`  exec: reaches ${JSON.stringify(r.reached)}${r.execError ? ` error ${r.execError}` : ""} (target ${r.target}, live ${r.live})`);
  console.log(`  real tests/hygiene.test.js, plant appended to all 5 core files: tests ${r.tests}, pass ${r.pass}, fail ${r.fail}`);
  console.log(`  mirror bannedNamesIn on each core file + plant: ${JSON.stringify(r.mirrorHits)}`);
  console.log(`  => ${r.verdict}`);
}
console.log(`\nplanted snippets (exact text, JSON-escaped):`);
for (const [title, , plant] of PLANTS) console.log(`  ${title.split(" ")[0]}: ${JSON.stringify(plant)}`);

// Review of codeOnly on the real core files: every line that holds code and lost characters, source and
// code side by side, so a reader can confirm only literal text was blanked.
console.log("\ncodeOnly on the real core files: code lines that lost characters (comment-only lines left out):");
for (const [name, s] of coreSources) {
  const code = scanner.codeOnly(s);
  if (code.length !== s.length) console.log(`  ${name}: LENGTH CHANGED ${s.length} -> ${code.length}`);
  const srcLines = s.split("\n"), codeLines = code.split("\n");
  srcLines.forEach((line, i) => {
    const t = line.trim();
    if (line === codeLines[i] || t.startsWith("//") || t.startsWith("/*") || t.startsWith("*")) return;
    console.log(`  ${name}:${i + 1}\n    src : ${t}\n    code: ${codeLines[i].trim()}`);
  });
}

// Termination and length on random JS-like input.
const TOKENS = ["/", "//", "/*", "*/", "'", "\"", "`", "${", "}", "{", "(", ")", "[", "]", BS, "\n", "x", "++", "return", " ", "=", ".in", "process", "+"];
let seed = 7, lengthBad = 0;
const rand = () => ((seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);
const t0 = process.hrtime.bigint();
for (let n = 0; n < 20000; n += 1) {
  const s = Array.from({ length: 1 + Math.floor(rand() * 40) }, () => TOKENS[Math.floor(rand() * TOKENS.length)]).join("");
  const c = scanner.codeOnly(s);
  if (c.length !== s.length || c.split("\n").length !== s.split("\n").length) lengthBad += 1;
}
console.log(`\nfuzz: 20000 random token strings, codeOnly returned (no hang) in ${Number(process.hrtime.bigint() - t0) / 1e6} ms; length or line count changed: ${lengthBad}`);
console.log(`child PIDs (all exited, spawnSync waits): ${pids.join(",")}`);
