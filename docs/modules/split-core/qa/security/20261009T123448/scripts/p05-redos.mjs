// P05. Unbounded time or memory on hostile strings. Each case runs in its own child process with a
// hard kill after 20 s, so a catastrophic case is reported as TIMEOUT instead of hanging this probe.
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const child = fileURLToPath(new URL("./p05-child.mjs", import.meta.url));
const CASES = [
  "digits then x", "digits dot then x", "digits dot 3 digits", "zeros then 1 (valid)", "all digits (too long)",
  "1 dot then zeros", "dots", "spaces only", "LS only", "rate digits then x", "label with breaks",
  "summary name all breaks", "computeResult long subtotal",
];
const SIZES = [1e6, 2e6, 4e6, 8e6, 16e6];
let worstRatio = 0, timeouts = 0;
const pids = [];
for (const name of CASES) {
  const times = [];
  for (const n of SIZES) {
    const res = spawnSync(process.execPath, ["--max-old-space-size=2048", child, name, String(n)], { timeout: 20000, killSignal: "SIGKILL", encoding: "utf8" });
    pids.push(res.pid);
    if (res.error || res.status !== 0) {
      timeouts += 1;
      times.push(`n=${n}: ${res.error ? res.error.code : `exit ${res.status} ${res.signal ?? ""}`} ${res.stderr.split("\n").find((l) => /Error/.test(l)) ?? ""}`);
      continue;
    }
    const j = JSON.parse(res.stdout.trim().split("\n").at(-1));
    times.push(j);
  }
  const ms = times.filter((t) => typeof t === "object").map((t) => t.ms);
  const ratio = ms.length >= 2 ? Math.max(...ms.slice(1).map((m, i) => m / Math.max(ms[i], 0.05))) : 0;
  worstRatio = Math.max(worstRatio, ratio);
  console.log(`${name.padEnd(30)} ${times.map((t) => (typeof t === "object" ? `${t.n / 1e6}M:${t.ms}ms` : t)).join("  ")}  result=${JSON.stringify(times.find((t) => typeof t === "object")?.out)}  max step ratio=${ratio.toFixed(2)}`);
}
console.log(`\nchild PIDs (all exited, spawnSync waits for each): ${pids.join(",")}`);
console.log(`worst time ratio per doubling of the input: ${worstRatio.toFixed(2)} (about 2 means linear, about 4 means quadratic)`);
console.log(`P05 RESULT: ${timeouts === 0 && worstRatio < 3.2 ? "PASS" : "CHECK"} (timeouts or crashes ${timeouts})`);
