// Runs the hygiene file 10 times alone and the full suite under several runner variants, each as a waited child
// (spawnSync), and prints one line per run. Usage (project root): OUT=<path relative to the project root> node <this file>
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";

const lines = [];
const say = (line) => { lines.push(line); console.log(line); };
const root = process.cwd();

function run(label, args, cwd = root) {
  const result = spawnSync(process.execPath, args, { cwd, encoding: "utf8", timeout: 180000, killSignal: "SIGKILL" });
  const out = `${result.stdout}\n${result.stderr}`;
  const num = (name) => Number(new RegExp(`ℹ ${name} (\\d+)`).exec(out)?.[1] ?? NaN);
  say(`${label} tests=${num("tests")} pass=${num("pass")} fail=${num("fail")} exit=${result.status} pid=${result.pid}`);
}

for (let n = 1; n <= 10; n += 1) run(`hygiene alone #${n}`, ["--test", "tests/hygiene.test.js"]);
const suite = ["tests/**/*.test.js"];
run("suite default", ["--test", ...suite]);
run("suite --test-isolation=none", ["--test", "--test-isolation=none", ...suite]);
run("suite --test-concurrency=1", ["--test", "--test-concurrency=1", ...suite]);
run("suite --experimental-test-coverage", ["--test", "--experimental-test-coverage", ...suite]);
run("suite --enable-source-maps", ["--enable-source-maps", "--test", ...suite]);
run("suite --stack-trace-limit=2", ["--stack-trace-limit=2", "--test", ...suite]);
run("suite --jitless", ["--jitless", "--test", ...suite]);
run("hygiene run directly (no --test)", ["tests/hygiene.test.js"]);
if (process.env.OUT) writeFileSync(resolve(root, process.env.OUT), `${lines.join("\n")}\n`);
