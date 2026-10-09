// Unit tests for src/draft.js (split-app R25 to R28, decoder rules D1 to D12). The browser suite proves the
// same rules through the page; these pin the edges (limits, boundaries, what is copied) without a browser.
import test from "node:test";
import assert from "node:assert/strict";
import { DRAFT_KEY, encodeDraft, decodeDraft, getStorage, loadDraft, saveDraft } from "../src/draft.js";
import { newBill } from "../src/core/bill.js";

const person = (n, name = `P${n}`) => ({ id: `p${n}`, name });
const bill = (changes = {}) => ({
  mode: "even", people: [person(1), person(2)], subtotalText: "", items: [],
  serviceText: "10", sstText: "6", nextId: 3, ...changes,
});
const draft = (changes) => JSON.stringify({ version: 1, bill: bill(changes) });
const rejects = (text) => assert.deepEqual(decodeDraft(text), { ok: false });

test("@R25 encodeDraft and decodeDraft round-trip a new bill and an item bill", () => {
  assert.deepEqual(decodeDraft(encodeDraft(newBill())), { ok: true, bill: newBill() });
  const full = bill({ mode: "item", items: [{ id: "i3", name: "Tea", priceText: "5", who: ["p2"] }], nextId: 4 });
  assert.deepEqual(decodeDraft(encodeDraft(full)), { ok: true, bill: full });
});

test("@R26 D1 to D4 reject text, shapes and versions that are not a draft", () => {
  for (const text of ["not json", "", "[]", "null", "5", '"x"', '{"version":1}', '{"version":1,"bill":[]}',
    '{"version":2,"bill":{}}', '{"version":"1","bill":{}}']) rejects(text);
  rejects(undefined);
  rejects(null);
});

test("@R26 D5 rejects an unknown mode", () => {
  for (const mode of ["split", "", undefined, null, 1, "Even"]) rejects(draft({ mode }));
});

test("@R26 D6 takes 2 to 12 people with unique ids of the form p<digits>", () => {
  const people = (count) => Array.from({ length: count }, (_, i) => person(i + 1));
  assert.equal(decodeDraft(draft({ people: people(12), nextId: 13 })).ok, true);
  rejects(draft({ people: people(1) }));
  rejects(draft({ people: people(13), nextId: 14 }));
  rejects(draft({ people: [person(1), person(1)] }));
  for (const id of ["x1", "p", "p-1", "p01x", "p12345678901", "P1", 1, null]) rejects(draft({ people: [{ id, name: "A" }, person(2)] }));
  rejects(draft({ people: [{ id: "p1", name: 5 }, person(2)] }));
  rejects(draft({ people: [person(1), "p2"] }));
});

test("@R26 D7 takes 0 to 50 items whose who is a duplicate-free list of known people", () => {
  const item = (n, who = []) => ({ id: `i${n + 2}`, name: "x", priceText: "1", who });
  const items = (count) => Array.from({ length: count }, (_, i) => item(i + 1));
  assert.equal(decodeDraft(draft({ items: items(50), nextId: 53 })).ok, true);
  rejects(draft({ items: items(51), nextId: 54 }));
  rejects(draft({ items: [item(1), item(1)], nextId: 10 }));
  for (const who of [["p9"], ["p1", "p1"], "p1", [1], null]) rejects(draft({ items: [item(1, who)], nextId: 10 }));
  rejects(draft({ items: [{ id: "i3", name: "x", priceText: "1" }], nextId: 10 })); // no who at all
  rejects(draft({ items: [{ ...item(1), priceText: 15.9 }], nextId: 10 }));
  rejects(draft({ items: [{ ...item(1), id: "p3" }], nextId: 10 }));
});

test("@R26 D8 counts grapheme clusters and refuses line breaks", () => {
  const flags = "\u{1F1F2}\u{1F1FE}".repeat(20); // 20 clusters, 80 UTF-16 units
  assert.equal(decodeDraft(draft({ people: [person(1, flags), person(2)] })).ok, true);
  rejects(draft({ people: [person(1, "A".repeat(21)), person(2)] }));
  rejects(draft({ people: [person(1, "Ai\nsyah"), person(2)] }));
  rejects(draft({ people: [person(1, "Ai\rsyah"), person(2)] }));
  const long = { id: "i3", name: "x".repeat(41), priceText: "1", who: [] };
  rejects(draft({ items: [long], nextId: 4 }));
  assert.equal(decodeDraft(draft({ items: [{ ...long, name: "x".repeat(40) }], nextId: 4 })).ok, true);
});

test("@R26 D9 wants the three text fields as strings", () => {
  for (const field of ["subtotalText", "serviceText", "sstText"]) {
    for (const value of [100, null, undefined, ["1"]]) rejects(draft({ [field]: value }));
  }
});

test("@R26 D10 wants nextId an integer above every id and at most 1,000,000,000", () => {
  assert.equal(decodeDraft(draft({ nextId: 3 })).ok, true);
  assert.equal(decodeDraft(draft({ people: [person(999999998), person(2)], nextId: 1_000_000_000 })).ok, true);
  for (const nextId of [2, 1, 0, -1, 1.5, 1_000_000_001, 2_000_000_000, "3", null, undefined, NaN]) rejects(draft({ nextId }));
});

test("@R26 D11 and D12 drop unknown keys and build new objects from known fields", () => {
  const dirty = JSON.stringify({
    version: 1, extra: 1,
    bill: { ...bill({ items: [{ id: "i3", name: "T", priceText: "1", who: ["p1"], colour: "red" }], nextId: 4 }),
      people: [{ id: "p1", name: "A", colour: "red" }, person(2)], flag: true, ["__proto__"]: { polluted: true } },
  });
  assert.ok(dirty.includes('"__proto__":{"polluted":true}')); // a computed key is an own key, as JSON.parse reads it
  const decoded = decodeDraft(dirty);
  assert.equal(decoded.ok, true);
  assert.deepEqual(Object.keys(decoded.bill), ["mode", "people", "subtotalText", "items", "serviceText", "sstText", "nextId"]);
  assert.deepEqual(Object.keys(decoded.bill.people[0]), ["id", "name"]);
  assert.deepEqual(Object.keys(decoded.bill.items[0]), ["id", "name", "priceText", "who"]);
  assert.equal(({}).polluted, undefined);
  assert.equal(Object.getPrototypeOf(decoded.bill), Object.prototype);
  assert.equal(JSON.stringify(decoded.bill).includes("colour"), false);
});

test("@R28 getStorage, loadDraft and saveDraft never throw", () => {
  assert.equal(getStorage(), null); // no window here, which is what a blocked localStorage looks like
  assert.deepEqual(loadDraft(null), { state: "none" });
  assert.equal(saveDraft(null, newBill()), false);
  const broken = { getItem() { throw new Error("no"); }, setItem() { throw new Error("full"); } };
  assert.deepEqual(loadDraft(broken), { state: "none" });
  assert.equal(saveDraft(broken, newBill()), false);
});

test("@R27 loadDraft tells none, ok and unreadable apart, and saveDraft writes the encoded draft", () => {
  const memory = new Map();
  const storage = { getItem: (key) => memory.get(key) ?? null, setItem: (key, value) => memory.set(key, value) };
  assert.deepEqual(loadDraft(storage), { state: "none" });
  assert.equal(saveDraft(storage, newBill()), true);
  assert.equal(memory.get(DRAFT_KEY), encodeDraft(newBill()));
  assert.deepEqual(loadDraft(storage), { state: "ok", bill: newBill() });
  memory.set(DRAFT_KEY, "not json");
  assert.deepEqual(loadDraft(storage), { state: "unreadable" });
});
