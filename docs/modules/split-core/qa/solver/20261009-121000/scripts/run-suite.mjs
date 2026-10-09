// Runs the project's unit suite exactly as CLAUDE.md says and saves the full output as evidence.
// Usage: node run-suite.mjs <project root> <output file>
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";

const [project, output] = process.argv.slice(2);
const run = spawnSync(process.execPath, ["--test", "tests/**/*.test.js"], { cwd: project, encoding: "utf8" });
const text = `$ node --test "tests/**/*.test.js"   (Node ${process.version}, cwd ${project})\n` +
  run.stdout + run.stderr + `exit ${run.status}\n`;
writeFileSync(output, text);
console.log(text.split("\n").filter((line) => /^ℹ (tests|pass|fail)|^exit/.test(line)).join("\n"));
