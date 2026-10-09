// QA oracle: computes what the screen must show for a list of Bills, straight from split-core (src/core).
// Usage: node oracle.mjs <project root>   with {"bills":[Bill, ...]} on stdin. Writes JSON to stdout.
// Read-only: it imports the core and prints. It never touches the clipboard, the network or the project files.
import { pathToFileURL } from "node:url";

const root = process.argv[2];
const load = (file) => import(pathToFileURL(`${root}/src/core/${file}`).href);
const [billMod, money, resultMod, summaryMod] = await Promise.all([load("bill.js"), load("money.js"), load("result.js"), load("summary.js")]);

let input = "";
for await (const chunk of process.stdin) input += chunk;
const { bills } = JSON.parse(input);

const f = money.formatMoney;
const fr = money.formatRate;

function summaryRows(c) {
  return [
    ["Subtotal", f(c.subtotal), ""],
    ["+Service charge", f(c.service), `${fr(c.serviceBp)} of ${f(c.subtotal)}`],
    ["+SST", f(c.sst), `${fr(c.sstBp)} of ${f(c.sstBase)}`],
    ["=Total", f(c.total), ""],
  ];
}

function expectFor(bill) {
  const r = resultMod.computeResult(bill);
  const out = { kind: r.kind };
  if (r.kind === "blocked") out.reason = r.reason;
  if (r.kind === "unassigned") {
    out.count = r.count;
    out.summary = summaryRows(r.charges);
  }
  if (r.kind === "even") {
    out.summary = summaryRows(r.charges);
    out.rows = r.rows.map((row) => [row.name, f(row.share)]);
    out.check = [f(r.check.share)];
    out.copy = summaryMod.summaryText(r);
  }
  if (r.kind === "item") {
    out.summary = summaryRows(r.charges);
    out.rows = r.rows.map((row) => [row.name, f(row.items), f(row.charges), f(row.share)]);
    out.check = [f(r.check.items), f(r.check.charges), f(r.check.share)];
    out.copy = summaryMod.summaryText(r);
  }
  // Which fields hold text that is not empty and fails its parser (R10): these are the ones whose error may show.
  const bad = (text, ok) => text !== "" && !ok;
  out.invalid = {
    subtotal: bad(bill.subtotalText, money.parseAmount(bill.subtotalText).ok),
    service: bad(bill.serviceText, money.parseRate(bill.serviceText, 30).ok),
    sst: bad(bill.sstText, money.parseRate(bill.sstText, 20).ok),
    prices: Object.fromEntries(bill.items.map((it) => [it.id, bad(it.priceText, money.parseAmount(it.priceText).ok)])),
  };
  out.labels = {
    people: bill.people.map((p, i) => billMod.personLabel(p, i)),
    items: bill.items.map((it, i) => billMod.itemLabel(it, i)),
  };
  return out;
}

process.stdout.write(JSON.stringify({ results: bills.map(expectFor), newBill: billMod.newBill() }));
