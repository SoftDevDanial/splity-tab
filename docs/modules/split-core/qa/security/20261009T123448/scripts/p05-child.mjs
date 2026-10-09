// P05 child: times one hostile-string case at one size. Run only by p05-redos.mjs, which kills it hard
// on timeout. Prints one JSON line.
import { parseAmount, parseRate } from "../../../../../../../src/core/money.js";
import { personLabel } from "../../../../../../../src/core/bill.js";
import { computeResult } from "../../../../../../../src/core/result.js";
import { summaryText } from "../../../../../../../src/core/summary.js";
import { ch } from "./fixtures.mjs";

const [caseName, sizeText] = process.argv.slice(2);
const n = Number(sizeText);
const S2 = { mode: "even", people: [{ id: "p1", name: "A" }, { id: "p2", name: "B" }, { id: "p3", name: "C" }], subtotalText: "100.00", items: [], serviceText: "10", sstText: "6", nextId: 4 };
const CASES = {
  "digits then x": () => parseAmount("1".repeat(n) + "x"),
  "digits dot then x": () => parseAmount("1".repeat(n) + ".x"),
  "digits dot 3 digits": () => parseAmount("1".repeat(n) + ".123"),
  "zeros then 1 (valid)": () => parseAmount("0".repeat(n) + "1"),
  "all digits (too long)": () => parseAmount("9".repeat(n)),
  "1 dot then zeros": () => parseAmount("1." + "0".repeat(n)),
  "dots": () => parseAmount(".".repeat(n)),
  "spaces only": () => parseAmount(" ".repeat(n)),
  "LS only": () => parseAmount(ch(0x2028).repeat(n)),
  "rate digits then x": () => parseRate("1".repeat(n) + "x", 30),
  "label with breaks": () => personLabel({ name: `A${ch(0x2028, 0x20).repeat(n / 2)}B` }, 0),
  "summary name all breaks": () => summaryText(computeResult({ ...S2, people: [S2.people[0], S2.people[1], { id: "p3", name: `C${ch(0x0a, 0x2029, 0x85, 0x0b).repeat(n / 4)}D` }] })),
  "computeResult long subtotal": () => computeResult({ ...S2, subtotalText: "1".repeat(n) + "x" }),
};
const run = CASES[caseName];
run(); // warm-up at size n, so the timed run is not the first compile
const t0 = process.hrtime.bigint();
const out = run();
const ms = Number(process.hrtime.bigint() - t0) / 1e6;
console.log(JSON.stringify({ caseName, n, ms: Math.round(ms * 100) / 100, out: typeof out === "string" ? `string(${out.length})` : out }));
