// Rebuilds each commit from `git archive` into a scratch directory OUTSIDE the project, runs the full suite
// there, and prints one line per commit. Every child is waited for (execFileSync / spawnSync), none is left running.
// Usage (project root): SCRATCH=<abs dir, empty or new> OUT=<path relative to the project root> node <this file> <hash>...
import { execFileSync, spawnSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

const scratch = process.env.SCRATCH;
if (!scratch) throw new Error("set SCRATCH to a directory outside the project");
const lines = [];
const say = (line) => { lines.push(line); console.log(line); };

for (const hash of process.argv.slice(2)) {
  const dir = join(scratch, hash);
  mkdirSync(dir, { recursive: true });
  execFileSync("git", ["archive", "--format=tar", "-o", join(dir, "tree.tar"), hash]);
  execFileSync("tar", ["-xf", "tree.tar"], { cwd: dir });
  const run = spawnSync(process.execPath, ["--test", "tests/**/*.test.js"], { cwd: dir, encoding: "utf8", timeout: 180000, killSignal: "SIGKILL" });
  const out = `${run.stdout}\n${run.stderr}`;
  const num = (label) => Number(new RegExp(`ℹ ${label} (\\d+)`).exec(out)?.[1] ?? NaN);
  const subject = execFileSync("git", ["log", "-1", "--format=%s", hash], { encoding: "utf8" }).trim();
  say(`${hash} tests=${num("tests")} pass=${num("pass")} fail=${num("fail")} exit=${run.status} pid=${run.pid} ${subject}`);
}
if (process.env.OUT) writeFileSync(resolve(process.cwd(), process.env.OUT), `${lines.join("\n")}\n`);
