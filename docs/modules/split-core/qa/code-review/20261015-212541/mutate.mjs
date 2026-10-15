// Code-review finder (read-only) mutation runner. Copies src/ and the Node tests of the project into
// scratch/mutants/<id>/, applies one exact single-occurrence edit, and runs node --test there.
// Usage: node mutate.mjs <projectRoot> <outDir> [ids...]
// Run 2026-10-15 from the session scratch folder split-cr-step5/, on HEAD d58f4ce, Node v24.11.1.
import { cpSync, mkdirSync, readFileSync, writeFileSync, rmSync, existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const [root, out, ...only] = process.argv.slice(2);

const M = [
  ["K01", "src/core/spare.js", "    spare,\n    nextId: bill.nextId,\n", "    spare,\n", "withSpare drops nextId"],
  ["K02", "src/core/result.js", "return weights.map((weight) => allocateByWeight(amount, [total - weight, weight])[1]);",
    "return weights.map((weight) => Math.floor((amount * weight) / total));", "floorParts in float, BigInt path bypassed"],
  ["K03", "src/core/result.js", "      const taken = [];\n", "      const taken = [];\n      cursor = 0;\n", "At random cursor restarts at every division"],
  ["K04", "src/core/result.js", "recipients: (members, count) => Array(count).fill(chosen) }",
    "recipients: (members, count) => (members.includes(chosen) ? Array(count).fill(chosen) : members.slice(0, count)) }", "One person takes only spare sen of divisions it is in"],
  ["K05", "src/core/result.js", "if (spare.rule === \"one\" && sparePeople(bill).includes(spare.personId))", "if (spare.rule === \"one\")", "One person never falls back"],
  ["K06", "src/core/result.js", ".filter((index) => items[index] > 0);", ".filter(() => true);", "charges division members include people with no items"],
  ["K07", "src/core/spare.js", "const ROW_FIELDS = [\"share\", \"items\", \"charges\"];", "const ROW_FIELDS = [\"share\"];", "Pick again compares shares only"],
  ["K08", "src/core/spare.js", "const MAX_DRAWS = 64;", "const MAX_DRAWS = 63;", "63 draws"],
  ["K09", "src/core/spare.js", "  if (rule === bill.spare.rule) return bill;\n", "", "choosing the rule already set redraws"],
  ["K10", "src/core/bill.js", "  if (bill.mode === \"even\") return everyone;\n  const onAnItem", "  return everyone;\n  const onAnItem", "sparePeople ignores items"],
  ["K11", "src/core/bill.js", "return spare.rule === \"random\" ? { rule: \"random\", order: [...spare.order, personId] } : spare;", "return spare;", "addPerson leaves the order short"],
  ["K12", "src/core/bill.js", "return spare.rule === \"one\" && spare.personId === personId ? { rule: \"top\" } : spare;", "return spare;", "removing the chosen person keeps the choice"],
  ["K13", "src/core/spare.js", "  for (let i = order.length - 1; i > 0; i -= 1) {", "  for (let i = order.length - 1; i >= 0; i -= 1) {", "one extra draw"],
  ["K14", "src/core/result.js", "if (!parsed.some((price) => price.ok)) return blocked(\"no-prices\");", "if (bill.items.length === 0) return blocked(\"no-prices\");", "1.0 row (c)"],
  ["K15", "src/core/result.js", "const ahead = drawn.findIndex((_, k) => members.includes(drawn[(cursor + k) % drawn.length]));", "const ahead = 0;", "At random ignores membership"],
  ["K16", "src/core/spare.js", "  return {\n    mode: bill.mode,\n    people: bill.people,\n    subtotalText: bill.subtotalText,\n    items: bill.items,\n    serviceText: bill.serviceText,\n    sstText: bill.sstText,\n    spare,\n    nextId: bill.nextId,\n  };",
    "  return { ...bill, spare };", "withSpare spreads the parsed bill (threat model, object integrity)"],
  ["K17", "src/core/spare.js", "return first === undefined ? bill : withSpare(bill, { rule: \"one\", personId: first });", "return withSpare(bill, { rule: \"one\", personId: first });", "One person with nobody stores undefined"],
  ["K18", "src/core/money.js", "return `RM ${formatAmount(cents)}`;", "return `RM ${String((cents - (cents % 100)) / 100)}.${String(cents % 100).padStart(2, \"0\")}`;", "formatMoney without the comma (1.0)"],
  ["D01", "src/draft.js", "  const everyoneOnce = Array.isArray(order) && order.length === personIds.size\n    && order", "  const everyoneOnce = Array.isArray(order)\n    && order", "D13 order may leave a person out"],
  ["D02", "src/draft.js", "if (raw.rule === \"one\") return personIds.has(raw.personId) ? { rule: \"one\", personId: raw.personId } : null;", "if (raw.rule === \"one\") return { rule: \"one\", personId: raw.personId };", "D13 one person unchecked"],
  ["D03", "src/draft.js", "const spare = draft.version === 1 ? { rule: \"top\" } : readSpare(raw.spare, personIds);", "const spare = readSpare(raw.spare, personIds) ?? { rule: \"top\" };", "D14 v1 reads spare, v2 bad spare falls back"],
  ["D04", "src/draft.js", "return everyoneOnce ? { rule: \"random\", order: [...order] } : null;", "return everyoneOnce ? raw : null;", "D13 spare copied wholesale"],
  ["R01", "src/ui/repeat.js", "return press.timeStamp - previous.timeStamp < REPEAT_TAP_MS", "return press.timeStamp - previous.timeStamp <= REPEAT_TAP_MS", "500 ms inclusive"],
  ["R02", "src/ui/repeat.js", "if (!press.tap || press.detail !== 1 || previous === null) return false;", "if (!press.tap || previous === null) return false;", "a tap of count 0 may repeat"],
];

mkdirSync(out, { recursive: true });
const summary = [];
for (const [id, file, from, to, what] of M) {
  if (only.length && !only.includes(id)) continue;
  const dir = join(out, id);
  if (existsSync(dir)) throw new Error(`refusing to reuse ${dir}`);
  mkdirSync(dir, { recursive: true });
  cpSync(join(root, "src"), join(dir, "src"), { recursive: true });
  mkdirSync(join(dir, "tests"));
  cpSync(join(root, "tests", "support"), join(dir, "tests", "support"), { recursive: true });
  for (const f of ["allocate", "bill", "draft", "errors", "hygiene", "invariants", "money", "repeat", "result", "spare", "summary"]) {
    cpSync(join(root, "tests", `${f}.test.js`), join(dir, "tests", `${f}.test.js`));
  }
  const target = join(dir, file);
  const text = readFileSync(target, "utf8").replace(/\r\n/g, "\n");
  const hits = text.split(from).length - 1;
  if (hits !== 1) { summary.push({ id, what, error: `pattern found ${hits} times` }); continue; }
  writeFileSync(target, text.replace(from, to));
  const run = spawnSync(process.execPath, ["--test", "--test-reporter=tap", "tests/**/*.test.js"], { cwd: dir, encoding: "utf8", timeout: 180000 });
  const outText = (run.stdout ?? "") + (run.stderr ?? "");
  writeFileSync(join(dir, "node-test.txt"), outText);
  const num = (k) => Number((outText.match(new RegExp(`^# ${k} (\\d+)`, "m")) ?? [])[1]);
  const failing = [...outText.matchAll(/^not ok \d+ - (.*)$/gm)].map((m) => m[1]);
  summary.push({ id, file, what, tests: num("tests"), pass: num("pass"), fail: num("fail"), killed: num("fail") > 0, failing: failing.slice(0, 8) });
}
writeFileSync(join(out, "mutation-summary.json"), JSON.stringify(summary, null, 2));
for (const s of summary) console.log(`${s.id} ${s.killed ? "KILLED  " : s.error ? "ERROR   " : "SURVIVED"} pass ${s.pass} fail ${s.fail} ${s.what}${s.error ? " " + s.error : ""}`);
