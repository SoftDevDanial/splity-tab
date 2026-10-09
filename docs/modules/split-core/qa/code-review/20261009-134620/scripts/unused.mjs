// Crude dead-code check: a declared or imported name that appears only once in its file.
// Run from the project root: node <this file>
import { readFileSync } from "node:fs";

const FILES = [
  "src/core/money.js", "src/core/allocate.js", "src/core/bill.js", "src/core/result.js", "src/core/summary.js",
  "tests/hygiene.test.js", "tests/summary.test.js", "tests/money.test.js", "tests/allocate.test.js",
  "tests/bill.test.js", "tests/result.test.js", "tests/invariants.test.js", "tests/support/bills.js", "tests/support/rng.js",
];
const escape = (name) => name.replace(/[$]/g, "[$]");

for (const file of FILES) {
  const source = readFileSync(file, "utf8");
  const names = new Set();
  for (const m of source.matchAll(/\b(?:const|let|function|class)\s+([A-Za-z_$][\w$]*)/g)) names.add(m[1]);
  for (const m of source.matchAll(/\b(?:const|let)\s+\{([^}]*)\}/g)) for (const part of m[1].split(",")) names.add(part.trim().split(":").pop().trim());
  for (const m of source.matchAll(/import\s*\{([^}]*)\}/g)) for (const part of m[1].split(",")) names.add(part.trim().split(/\s+as\s+/).pop());
  const unused = [...names].filter((name) => name && (source.match(new RegExp(`(?<![\\w$])${escape(name)}(?![\\w$])`, "g")) ?? []).length < 2);
  console.log(file.padEnd(28), unused.length === 0 ? "-" : unused.join(", "));
}
