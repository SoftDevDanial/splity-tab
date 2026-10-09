// Rebuilds src/ and tests/ of each given commit from git (never from the working tree), renames
// *.test.js to *.mutcase.js, runs the suite there in a child process and records the counts and the
// child's PID. Shows every commit of the batch left the suite green on its own.
// Usage: node per-commit.mjs <project root> <output dir> <commit> [<commit> ...]
import { execFileSync, spawnSync } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";

const [project, output, ...commits] = process.argv.slice(2);
const git = (...args) => execFileSync("git", ["-C", project, ...args], { encoding: "utf8", maxBuffer: 1 << 26 });
const lines = [];
for (const commit of commits) {
  const dir = `${output}/commits/${commit}`;
  const files = git("ls-tree", "-r", "--name-only", commit, "src", "tests").split("\n")
    .filter((name) => name.endsWith(".js") && !name.startsWith("tests/browser/"));
  for (const name of files) {
    const target = `${dir}/${name.replace(/\.test\.js$/, ".mutcase.js")}`;
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, git("show", `${commit}:${name}`));
  }
  const run = spawnSync(process.execPath, ["--test", "tests/**/*.mutcase.js"], { cwd: dir, encoding: "utf8", timeout: 120000, killSignal: "SIGKILL" });
  const text = run.stdout + run.stderr;
  writeFileSync(`${dir}/node-test.txt`, text);
  const count = (label) => (text.match(new RegExp(`^ℹ ${label} (\\d+)`, "m")) ?? [])[1] ?? "?";
  const subject = git("log", "-1", "--format=%s", commit).trim();
  lines.push(`${commit} files=${files.length} tests=${count("tests")} pass=${count("pass")} fail=${count("fail")} exit=${run.status} pid=${run.pid} ${subject}`);
}
writeFileSync(`${output}/per-commit-summary.txt`, lines.join("\n") + "\n");
console.log(lines.join("\n"));
