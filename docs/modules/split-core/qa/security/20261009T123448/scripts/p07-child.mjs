// P07 child: times computeResult on P people with one item tapped by everyone. Run by p07 only.
import { computeResult } from "../../../../../../../src/core/result.js";

const P = Number(process.argv[2]);
const people = Array.from({ length: P }, (_, i) => ({ id: `p${i + 1}`, name: "" }));
const bill = {
  mode: "item", people, subtotalText: "", serviceText: "10", sstText: "6", nextId: P + 2,
  items: [{ id: `i${P + 1}`, name: "", priceText: "99999.99", who: people.map((p) => p.id) }],
};
const t0 = process.hrtime.bigint();
const r = computeResult(bill);
const ms = Number(process.hrtime.bigint() - t0) / 1e6;
console.log(`${ms.toFixed(1)} ms, kind ${r.kind}, adds up ${r.check.share === r.charges.total}, draft JSON about ${JSON.stringify(bill).length} chars`);
