// Decoder cases that no existing test pins. Usage: node kill_decoder.mjs <tree>
// The shipped decoder must reject both. A mutant that accepts one is a hole.
// Result on the shipped tree: 4 PASS. On mutant D: the first three FAIL (the decoder said ok=true).
import { pathToFileURL } from "node:url";
import path from "node:path";

const tree = process.argv[2];
const { decodeDraft } = await import(pathToFileURL(path.join(tree, "src", "draft.js")).href);

const person = (n) => ({ id: `p${n}`, name: `P${n}` });
const draft = (bill) => JSON.stringify({ version: 1, bill });
const base = { mode: "item", people: [person(1), person(2)], subtotalText: "", serviceText: "10", sstText: "6" };

// D10 with the highest id on an ITEM: people p1, p2, item i3, nextId 3 is stale (a new item would get id i3 again).
const staleNextId = draft({ ...base, items: [{ id: "i3", name: "Tea", priceText: "5", who: [] }], nextId: 3 });
// D8 with a line break in an ITEM name (the unit tests use a person name only).
const itemNewline = draft({ ...base, items: [{ id: "i3", name: "Te\na", priceText: "5", who: [] }], nextId: 4 });
const itemCarriageReturn = draft({ ...base, items: [{ id: "i3", name: "Te\ra", priceText: "5", who: [] }], nextId: 4 });
const okayItem = draft({ ...base, items: [{ id: "i3", name: "Tea", priceText: "5", who: [] }], nextId: 4 });

const cases = [
  ["D10 stale nextId against an item id is rejected", staleNextId, false],
  ["D8 a line feed in an item name is rejected", itemNewline, false],
  ["D8 a carriage return in an item name is rejected", itemCarriageReturn, false],
  ["control: a clean item bill is accepted", okayItem, true],
];
let bad = 0;
for (const [name, text, expectOk] of cases) {
  const ok = decodeDraft(text).ok;
  const pass = ok === expectOk;
  if (!pass) bad += 1;
  console.log(`${pass ? "PASS" : "FAIL"} ${name} (decoder said ok=${ok})`);
}
process.exitCode = bad === 0 ? 0 : 1;
