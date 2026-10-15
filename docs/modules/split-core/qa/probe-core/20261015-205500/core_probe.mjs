// QA finder (read-only) independent probe of split-core, written from the qa.md tables and not from tests/.
// Run: node core_probe.mjs <absolute project root with forward slashes>
import { pathToFileURL } from "node:url";

const root = process.argv[2];
const load = (p) => import(pathToFileURL(root + "/src/core/" + p).href);
const money = await load("money.js");
const alloc = await load("allocate.js");
const bill = await load("bill.js");
const result = await load("result.js");
const spare = await load("spare.js");
const summary = await load("summary.js");

let pass = 0;
let fail = 0;
const check = (name, got, want) => {
  const canon = (v) => JSON.stringify(v, (k, x) => (x && typeof x === "object" && !Array.isArray(x) ? Object.fromEntries(Object.keys(x).sort().map((q) => [q, x[q]])) : x));
  const ok = canon(got) === canon(want);
  if (ok) pass++;
  else fail++;
  console.log((ok ? "PASS " : "FAIL ") + name + (ok ? "" : "\n   got  " + JSON.stringify(got) + "\n   want " + JSON.stringify(want)));
};

// Build S2 and S1 from newBill and the actions, as qa.md names them.
let s2 = bill.newBill();
s2 = bill.addPerson(s2);
s2 = bill.setPersonName(s2, "p1", "Aisyah");
s2 = bill.setPersonName(s2, "p2", "Ben");
s2 = bill.setPersonName(s2, "p3", "Chen");
s2 = bill.setSubtotalText(s2, "100.00");
const r2 = result.computeResult(s2);
check("S2 kind", r2.kind, "even");
check("S2 charges", r2.charges, { subtotal: 10000, service: 1000, sstBase: 11000, sst: 660, total: 11660, serviceBp: 1000, sstBp: 600 });
check("S2 shares top", r2.rows.map((r) => r.share), [3887, 3887, 3886]);
check("S2 text", summary.summaryText(r2),
  "Bill split\nTotal RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)\nAisyah RM 38.87\nBen RM 38.87\nChen RM 38.86\nAdds up to RM 116.60");

const one = spare.chooseSparePerson(spare.chooseSpareRule(s2, "one"), "p2");
check("S2 one p2", result.computeResult(one).rows.map((r) => r.share), [3886, 3888, 3886]);
check("S2 one p2 spare", result.computeResult(one).spare, { count: 2, rule: "one", personId: "p2" });
const seq = (...n) => { let i = 0; return () => n[i++]; };
const rnd = spare.chooseSpareRule(s2, "random", seq(0, 0));
check("S2 random order from 0,0", rnd.spare, { rule: "random", order: ["p2", "p3", "p1"] });
check("S2 random shares", result.computeResult(rnd).rows.map((r) => r.share), [3886, 3887, 3887]);

let s1 = bill.setMode(s2, "item");
s1 = bill.removePerson(s1, "p1") === s1 ? s1 : s1; // no-op placeholder, keeps S2's people for S1
const items = [["Nasi lemak ayam", "15.90", ["p1"]], ["Char kuey teow", "13.50", ["p2"]], ["Mee goreng mamak", "12.00", ["p3"]], ["Satay, 10 sticks", "18.00", ["p1", "p3"]]];
let b = bill.setMode(s2, "item");
items.forEach(([name, price, who], k) => {
  b = bill.addItem(b);
  const id = b.items[b.items.length - 1].id;
  b = bill.setItemName(b, id, name);
  b = bill.setItemPriceText(b, id, price);
  who.forEach((p) => { b = bill.toggleItemPerson(b, id, p); });
});
const rs1 = result.computeResult(b);
check("S1 kind", rs1.kind, "item");
check("S1 charges", [rs1.charges.subtotal, rs1.charges.service, rs1.charges.sst, rs1.charges.total], [5940, 594, 392, 6926]);
check("S1 shares", rs1.rows.map((r) => r.share), [2904, 1574, 2448]);
check("S1 item ids start at i4", b.items.map((i) => i.id), ["i4", "i5", "i6", "i7"]);

// W1: S1 plus an unnamed 964.50 item for Aisyah.
let w1 = bill.addItem(b);
const wid = w1.items[w1.items.length - 1].id;
w1 = bill.setItemPriceText(w1, wid, "964.50");
w1 = bill.toggleItemPerson(w1, wid, "p1");
const rw = result.computeResult(w1);
check("W1 total", rw.charges.total, 119387);
check("W1 rows", rw.rows.map((r) => r.share), [115365, 1574, 2448]);
check("W1 text lines", summary.summaryText(rw).split("\n").slice(1, 2)[0], "Total RM 1,193.87 (subtotal RM 1,023.90, service 10% RM 102.39, SST 6% RM 67.58)");

// Unassigned and blocked
let su = bill.toggleItemPerson(bill.toggleItemPerson(b, "i6", "p3"), "i7", "p3");
check("S5 unassigned i6", result.computeResult(bill.toggleItemPerson(b, "i6", "p3")), { kind: "unassigned", count: 1, charges: result.computeResult(b).charges });
check("blocked rates", result.computeResult(bill.setServiceText(s2, "")), { kind: "blocked", reason: "rates" });
check("blocked subtotal", result.computeResult(bill.setSubtotalText(s2, "0")), { kind: "blocked", reason: "subtotal" });

// Parsers and formatters
check("parseAmount 12.5", money.parseAmount("12.5"), { ok: true, cents: 1250 });
check("parseAmount 1,000", money.parseAmount("1,000"), { ok: false, empty: false });
check("parseAmount blank", money.parseAmount("  "), { ok: false, empty: true });
check("parseRate 6.25/20", money.parseRate("6.25", 20), { ok: true, bp: 625 });
check("parseRate 30.01/30", money.parseRate("30.01", 30), { ok: false, empty: false });
check("formatMoney 779999922", money.formatMoney(779999922), "RM 7,799,999.22");
check("formatAmount 100000", money.formatAmount(100000), "1,000.00");
check("formatRate 605", money.formatRate(605), "6.05%");

// Allocation
check("allocateEvenly 1,3", alloc.allocateEvenly(1, 3), [1, 0, 0]);
check("allocateByWeight 986", alloc.allocateByWeight(986, [2490, 1350, 2100]), [414, 224, 348]);
check("allocateByWeight BigInt trap", alloc.allocateByWeight(236419679, [314963010, 157876348]), [157481505, 78938174]);
let threw = 0;
for (const f of [() => alloc.allocateEvenly(10, 0), () => alloc.allocateByWeight(10, [0, 0]), () => alloc.allocateEvenly(-1, 2)]) {
  try { f(); } catch (e) { if (e instanceof RangeError) threw++; }
}
check("RangeError on impossible input", threw, 3);

// MAX-E
let mx = bill.newBill();
for (let i = 0; i < 10; i++) mx = bill.addPerson(mx);
mx = bill.setSubtotalText(mx, "99999.99");
mx = bill.setServiceText(mx, "30");
mx = bill.setSstText(mx, "20");
const rmx = result.computeResult(mx);
check("MAX-E total", rmx.charges.total, 15599999);
check("MAX-E shares", [rmx.rows.slice(0, 11).every((r) => r.share === 1300000), rmx.rows[11].share], [true, 1299999]);

// Name hygiene in the summary
let hn = bill.setPersonName(s2, "p3", "Chen Adds up to RM 0.00");
check("LS in name", summary.summaryText(result.computeResult(hn)).split("\n")[4], "Chen Adds up to RM 0.00 RM 38.86");

// Pick again
let pa = spare.chooseSpareRule(s2, "random", seq(0.9, 0.1));
check("random 0.9,0.1 order", pa.spare.order, ["p2", "p1", "p3"]);
const again = spare.pickAgain(spare.chooseSpareRule(s2, "random", seq(0, 0)), seq(0, 0.5, 0.5, 0.5));
check("pickAgain order", again.spare.order, ["p1", "p3", "p2"]);

console.log(`probe checks: ${pass} pass, ${fail} fail`);
process.exitCode = fail ? 1 : 0;
