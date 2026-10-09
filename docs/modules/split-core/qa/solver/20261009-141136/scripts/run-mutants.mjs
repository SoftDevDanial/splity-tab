// Runs each mutant of ./mutants.mjs in a child `node --import preload.mjs <tests>` with a SIGKILL timeout and
// prints one JSON line per mutant plus a summary. Every child is waited for (spawnSync), so none outlives this run.
// Usage (from the project root): node <this file> <id-or-prefix>...   (no argument runs every mutant)
//   FULL=1  list every failing test name instead of the first 8
//   OUT=<path relative to the project root>  also write the printed lines to that file (Node fs, no shell redirect)
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { MUTANTS } from "./mutants.mjs";

const PRELOAD = pathToFileURL(resolve(import.meta.dirname, "preload.mjs")).href;
const wanted = process.argv.slice(2);
const ids = [...MUTANTS.keys()].filter((id) => wanted.length === 0 || wanted.some((w) => id === w || id.startsWith(w)));
const limit = process.env.FULL ? Infinity : 8;

const lines = [];
const say = (line) => { lines.push(line); console.log(line); };
const rows = [];
for (const id of ids) {
  const mutant = MUTANTS.get(id);
  const started = Date.now();
  const run = spawnSync(process.execPath, ["--import", PRELOAD, ...mutant.tests], {
    cwd: process.cwd(), env: { ...process.env, MUT_ID: id }, encoding: "utf8", timeout: 120000, killSignal: "SIGKILL",
  });
  const out = `${run.stdout}\n${run.stderr}`;
  const num = (label) => Number(new RegExp(`ℹ ${label} (\\d+)`).exec(out)?.[1] ?? NaN);
  const failed = [...new Set([...out.matchAll(/^\s*✖ (.+?) \(\d/gm)].map((m) => m[1]))];
  const files = Object.keys(mutant.edits);
  const applied = files.every((file) => out.includes(`MUT-APPLIED ${id} ${file}`));
  const verdict = run.error || run.signal ? "TIMEOUT-OR-ERROR"
    : !applied ? "NOT-APPLIED"
    : run.status === 0 && num("fail") === 0 ? "SURVIVES" : "KILLED";
  rows.push({ id, verdict });
  say(JSON.stringify({
    id, desc: mutant.desc, verdict, applied, status: run.status, pid: run.pid, ms: Date.now() - started,
    tests: num("tests"), pass: num("pass"), fail: num("fail"), failed: failed.slice(0, limit), failedCount: failed.length,
  }));
}
const count = (v) => rows.filter((r) => r.verdict === v).length;
say(`SUMMARY mutants=${rows.length} killed=${count("KILLED")} survives=${count("SURVIVES")} not-applied=${count("NOT-APPLIED")} error=${count("TIMEOUT-OR-ERROR")}`);
if (process.env.OUT) writeFileSync(resolve(process.cwd(), process.env.OUT), `${lines.join("\n")}\n`);
