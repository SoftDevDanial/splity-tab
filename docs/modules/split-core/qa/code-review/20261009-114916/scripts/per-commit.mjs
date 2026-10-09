// Checks the task rule "each commit leaves node --test green". Reads each commit's src/ and tests/ with
// `git show` (read-only on the repo), writes them under <evidence>/commits/<sha>/ with *.test.js renamed
// to *.mutcase.js, and runs the suite there.
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { spawnSync } from "node:child_process";

const project = process.argv[2];
const evidence = process.argv[3];
const commits = ["bb3fba9", "3399736", "5d98d13", "8228969", "e40c171", "50b6a8b", "27458ba", "025e232"];
const NL = String.fromCharCode(10);
const git = (...args) => spawnSync("git", args, { cwd: project, encoding: "utf8" }).stdout;

const lines = [];
for (const sha of commits) {
  const dir = `${evidence}/commits/${sha}`;
  const files = git("ls-tree", "-r", "--name-only", sha, "src", "tests").split(NL).filter(Boolean)
    .filter((f) => f.endsWith(".js") && !f.startsWith("tests/browser/"));
  for (const file of files) {
    const target = `${dir}/${file.replace(/\.test\.js$/, ".mutcase.js")}`;
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, git("show", `${sha}:${file}`));
  }
  const run = spawnSync(process.execPath, ["--test", "tests/*.mutcase.js"], { cwd: dir, encoding: "utf8" });
  const text = run.stdout + run.stderr;
  writeFileSync(`${dir}/node-test.txt`, text);
  const count = (key) => (text.match(new RegExp(`ℹ ${key} (\\d+)`)) ?? [])[1];
  lines.push(`${sha} files=${files.length} tests=${count("tests")} pass=${count("pass")} fail=${count("fail")} exit=${run.status}`);
}
writeFileSync(`${evidence}/per-commit-summary.txt`, lines.join(NL) + NL);
console.log(lines.join(NL));
