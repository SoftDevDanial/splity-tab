// Mutation run for split-core. Copies src/core and tests into <evidence>/mutants/<id>/, applies one edit,
// renames *.test.js to *.mutcase.js (so no default `node --test` glob picks the copies up), runs the
// suite in that copy and records which tests fail. The project tree itself is never written.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, copyFileSync, statSync } from "node:fs";
import { spawnSync } from "node:child_process";

const project = process.argv[2];
const evidence = process.argv[3];
const NL = String.fromCharCode(10);

const mutants = [
  ["M01", "src/core/money.js", "remove the whole-digit cap",
    "  if (whole.length > MAX_WHOLE_DIGITS) return INVALID;" + NL, ""],
  ["M02", "src/core/result.js", "applyRate truncates instead of rounding half up",
    "amount * bp + BASIS_POINTS / 2", "amount * bp"],
  ["M03", "src/core/result.js", "SST on the subtotal only",
    "const sst = applyRate(sstBase, sstBp);", "const sst = applyRate(subtotal, sstBp);"],
  ["M04", "src/core/allocate.js", "float floors instead of BigInt",
    "const floors = weights.map((w) => (bigAmount * BigInt(w)) / total);",
    "const floors = weights.map((w) => BigInt(Math.floor((amount * w) / Number(total))));"],
  ["M05", "src/core/result.js", "shared item split in tap order",
    "  bill.people.forEach((person, index) => {" + NL + "    if (item.who.includes(person.id)) indexes.push(index);" + NL + "  });",
    "  item.who.forEach((id) => {" + NL + "    const index = bill.people.findIndex((person) => person.id === id);" + NL + "    if (index >= 0) indexes.push(index);" + NL + "  });"],
  ["M06", "src/core/allocate.js", "leftover also goes to zero weights",
    "if (leftover > 0n && weights[index] > 0) {", "if (leftover > 0n) {"],
  ["M07", "src/core/bill.js", "addPerson id from list length, not nextId",
    "const person = { id: `p${bill.nextId}`, name: \"\" };",
    "const person = { id: `p${bill.people.length + 1}`, name: \"\" };"],
  ["M08", "src/core/summary.js", "summaryText trims row names in place (mutates its input)",
    "  const { charges } = result;",
    "  const { charges } = result;" + NL + "  result.rows.forEach((row) => { row.name = row.name.trim(); });"],
  ["M09", "src/core/money.js", "formatMoney via float and toLocaleString (non-goal: locale-aware format)",
    "return `RM ${Math.floor(cents / 100)}.${String(cents % 100).padStart(2, \"0\")}`;",
    "return `RM ${(cents / 100).toLocaleString(\"en\", { minimumFractionDigits: 2, maximumFractionDigits: 2, useGrouping: false })}`;"],
  ["M10", "src/core/result.js", "even rows get the larger shares last",
    "share: shares[index] }));", "share: shares[shares.length - 1 - index] }));"],
  ["M11", "src/core/bill.js", "setPersonName spreads the person (keeps stray keys)",
    "personWith(person, { name })", "({ ...person, name })"],
  ["M12", "src/core/bill.js", "setMode spreads the whole bill (threat model forbids it)",
    "  return billWith(bill, { mode });", "  return { ...bill, mode };"],
  ["M13", "src/core/money.js", "parseRate excludes its maximum",
    "read.hundredths <= maxPercent * 100", "read.hundredths < maxPercent * 100"],
  ["M14", "src/core/bill.js", "removePerson keeps their taps",
    "items: bill.items.map((item) => itemWith(item, { who: item.who.filter((id) => id !== personId) })),",
    "items: bill.items,"],
  ["M15", "src/core/allocate.js", "allocateEvenly puts the extra sen last",
    "(index < extra ? base + 1 : base)", "(index >= count - extra ? base + 1 : base)"],
  ["M16", "src/core/result.js", "check.share copied from the total (equivalent while rows add up)",
    "check: { share: sum(shares) }", "check: { share: charges.total }"],
];

function copyTree(from, to, rename) {
  mkdirSync(to, { recursive: true });
  for (const name of readdirSync(from)) {
    const src = `${from}/${name}`;
    if (statSync(src).isDirectory()) {
      if (name === "browser") continue;
      copyTree(src, `${to}/${name}`, rename);
    } else if (name.endsWith(".js")) {
      copyFileSync(src, `${to}/${rename(name)}`);
    }
  }
}

const toMutcase = (name) => name.replace(/\.test\.js$/, ".mutcase.js");
const rows = [];
for (const [id, file, what, search, replace] of mutants) {
  const dir = `${evidence}/mutants/${id}`;
  copyTree(`${project}/src`, `${dir}/src`, (n) => n);
  copyTree(`${project}/tests`, `${dir}/tests`, toMutcase);
  const target = `${dir}/${file}`;
  const source = readFileSync(target, "utf8");
  const hits = source.split(search).length - 1;
  if (hits !== 1) {
    rows.push({ id, what, error: `search text found ${hits} times` });
    continue;
  }
  writeFileSync(target, source.replace(search, replace));
  const run = spawnSync(process.execPath, ["--test", "tests/*.mutcase.js"], { cwd: dir, encoding: "utf8" });
  const text = run.stdout + run.stderr;
  writeFileSync(`${dir}/node-test.txt`, text);
  const count = (key) => Number((text.match(new RegExp(`ℹ ${key} (\\d+)`)) ?? [])[1]);
  const failed = text.split(NL).filter((line) => /^✖ /.test(line)).map((line) => line.replace(/ \([\d.]+ms\)$/, ""));
  rows.push({ id, file, what, tests: count("tests"), pass: count("pass"), fail: count("fail"),
    verdict: count("fail") > 0 ? "KILLED" : "SURVIVED", failed: [...new Set(failed)] });
}
writeFileSync(`${evidence}/mutation-summary.json`, JSON.stringify(rows, null, 2));
for (const row of rows) {
  console.log(`${row.id} ${row.verdict ?? "ERROR"} tests=${row.tests} fail=${row.fail} ${row.what}${row.error ? " " + row.error : ""}`);
  for (const f of row.failed ?? []) console.log(`    ${f}`);
}
