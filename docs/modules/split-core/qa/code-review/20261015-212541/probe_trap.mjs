// Code-review finder (read-only) probe P1. A by-item bill whose charges division is the R8 "BigInt trap" row
// 61846725 over [49676084, 322894546] (a 372570630 subtotal at 10% and 6%). Run against the real src/ and the
// K02 mutant copy (floorParts in float). Usage: node probe_trap.mjs <srcRootOfCopy> [<srcRootOfCopy> ...]
import { pathToFileURL } from "node:url";
import { join } from "node:path";

const MAXP = 9999999;
function pricesFor(total) {
  const prices = [];
  let rest = total;
  while (rest > 0) {
    const p = Math.min(MAXP, rest);
    prices.push(p);
    rest -= p;
  }
  return prices;
}
const text = (cents) => `${Math.floor(cents / 100)}.${String(cents % 100).padStart(2, "0")}`;

for (const root of process.argv.slice(2)) {
  const bill = await import(pathToFileURL(join(root, "src/core/bill.js")));
  const { computeResult } = await import(pathToFileURL(join(root, "src/core/result.js")));
  const { allocateByWeight } = await import(pathToFileURL(join(root, "src/core/allocate.js")));
  let b = bill.setMode(bill.newBill(), "item");
  const plan = [["p1", pricesFor(49676084)], ["p2", pricesFor(322894546)]];
  for (const [who, prices] of plan) {
    for (const p of prices) {
      b = bill.addItem(b);
      const id = b.items[b.items.length - 1].id;
      b = bill.setItemPriceText(b, id, text(p));
      b = bill.toggleItemPerson(b, id, who);
    }
  }
  const r = computeResult(b);
  const exact = allocateByWeight(r.charges.service + r.charges.sst, r.rows.map((row) => row.items));
  console.log(JSON.stringify({
    root, items: b.items.length, kind: r.kind, subtotal: r.charges.subtotal, chargesTotal: r.charges.service + r.charges.sst,
    rowsItems: r.rows.map((row) => row.items), rowsCharges: r.rows.map((row) => row.charges),
    allocateByWeight: exact, equalToR21Point4: JSON.stringify(exact) === JSON.stringify(r.rows.map((row) => row.charges)),
    checkShare: r.check.share, total: r.charges.total,
  }));
}
