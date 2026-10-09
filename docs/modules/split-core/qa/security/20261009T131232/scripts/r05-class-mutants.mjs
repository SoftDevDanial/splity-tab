// R05. Do the new R24 tests pin the whole replaced class, or only the characters they name? Each mutant
// narrows CONTROLS in memory; the REAL tests/summary.test.js runs against it; then the mutant is asked
// which class members it would let through. A green run that lets a member through is a coverage gap.
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = fileURLToPath(new URL("../../../../../../../", import.meta.url));
const PRELOAD = pathToFileURL(fileURLToPath(new URL("./r05-preload-mutant.mjs", import.meta.url))).href;
const BS = String.fromCharCode(92);
const esc = (cp) => `${BS}u{${cp.toString(16)}}`;
const FULL = new RegExp(`[${BS}p{Cc}${BS}p{Zl}${BS}p{Zp}${BS}p{Bidi_Control}]`, "u");

const TESTED = [0x0a, 0x0d, 0x0b, 0x0c, 0x85, 0x2028, 0x2029, 0x00, 0x1c, 0x1d, 0x1e, 0x1b];
const MUTANTS = [
  ["M0 HEAD class (control, must stay green)", null],
  ["M1 bidi narrowed to RLO only", `/[${BS}p{Cc}${BS}p{Zl}${BS}p{Zp}${esc(0x202e)}]/gu`],
  ["M2 controls narrowed to the 12 tested ones", `/[${TESTED.map(esc).join("")}${BS}p{Bidi_Control}]/gu`],
  ["M3 both narrowed (13 named characters only)", `/[${TESTED.map(esc).join("")}${esc(0x202e)}]/gu`],
  ["M4 bidi dropped (control, must go red)", `/[${BS}p{Cc}${BS}p{Zl}${BS}p{Zp}]/gu`],
];

const pids = [];
for (const [title, source] of MUTANTS) {
  const env = { ...process.env, R05_CLASS: source ? Buffer.from(source, "utf8").toString("base64") : "" };
  const run = spawnSync(process.execPath, ["--import", PRELOAD, "tests/summary.test.js"], { cwd: ROOT, env, timeout: 60000, killSignal: "SIGKILL", encoding: "utf8" });
  pids.push(run.pid);
  const num = (key) => Number((run.stdout.match(new RegExp(`(?:^|\\n)(?:# |${String.fromCodePoint(0x2139)} )${key} (\\d+)`)) ?? [])[1]);
  let leaks = [];
  if (source) {
    const body = source.slice(1, source.lastIndexOf("/"));
    const re = new RegExp(body, "u");
    for (let cp = 0; cp <= 0x2069; cp += 1) {
      const c = String.fromCodePoint(cp);
      if (FULL.test(c) && !re.test(c)) leaks.push(`U+${cp.toString(16).toUpperCase().padStart(4, "0")}`);
    }
  }
  const counted = Number.isInteger(num("pass"));
  console.log(`${title}\n  real tests/summary.test.js: ${counted ? `tests ${num("tests")}, pass ${num("pass")}, fail ${num("fail")}` : `HARNESS ERROR exit ${run.status} ${run.stderr.split("\n").find((l) => /Error/.test(l)) ?? ""}`}`);
  console.log(`  class members the mutant lets through (${leaks.length}): ${leaks.slice(0, 20).join(" ")}${leaks.length > 20 ? " ..." : ""}`);
}
console.log(`child PIDs (all exited, spawnSync waits): ${pids.join(",")}`);
