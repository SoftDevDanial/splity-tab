// Unit tests for src/draft.js (split-app R25 to R28 and R61, decoder rules D1 to D14). The browser suite proves the
// same rules through the page; these pin the edges (limits, boundaries, what is copied) without a browser.
// `draft()` builds a version 1 draft as 1.0 saved it, so the D5 to D12 cases also prove that 1.0 drafts still load.
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

// The seed drafts of split-app qa.md ("Seed drafts", "Unreadable drafts", "Readable drafts that look odd") that the
// R61 cases name. K1 and K2 are the qa.md texts, the rest are built from them as the tables say.
const K1 = '{"version":2,"bill":{"mode":"item","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},'
  + '{"id":"p3","name":"Chen"}],"subtotalText":"","items":[{"id":"i4","name":"Nasi lemak ayam","priceText":"15.90","who":["p1"]},'
  + '{"id":"i5","name":"Char kuey teow","priceText":"13.50","who":["p2"]},{"id":"i6","name":"Mee goreng mamak","priceText":"12.00","who":["p3"]},'
  + '{"id":"i7","name":"Satay, 10 sticks","priceText":"18.00","who":["p1","p3"]}],"serviceText":"10","sstText":"6",'
  + '"spare":{"rule":"top"},"nextId":8}}';
const K2 = '{"version":2,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},'
  + '{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","spare":{"rule":"top"},"nextId":4}}';
const S2_V1 = '{"version":1,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},'
  + '{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","nextId":4}}';
const edited = (text, edit) => {
  const value = JSON.parse(text);
  edit(value);
  return JSON.stringify(value);
};
const withSpare = (text, spare) => edited(text, (value) => { value.bill.spare = spare; });
const billOf = (text) => JSON.parse(text).bill;
const TOP = { rule: "top" };
const ONE = withSpare(K2, { rule: "one", personId: "p2" });
const RND = withSpare(K2, { rule: "random", order: ["p2", "p3", "p1"] });
const PA0 = JSON.stringify({ version: 2, bill: {
  mode: "item", people: [person(1, "Aisyah"), person(2, "Ben"), person(3, "Chen")], subtotalText: "",
  items: [{ id: "i4", name: "X", priceText: "0.01", who: ["p1", "p2"] }, { id: "i5", name: "Y", priceText: "0.01", who: ["p1", "p2"] }],
  serviceText: "0", sstText: "0", spare: { rule: "random", order: ["p1", "p2", "p3"] }, nextId: 6,
} });
const S1_V1 = edited(K1, (value) => { value.version = 1; delete value.bill.spare; });
const G4 = edited(K1, (value) => { value.bill.spare = { rule: "one", personId: "p2" }; value.bill.items[1].who = ["p1"]; });
const G5 = withSpare(S2_V1, { rule: "random", order: ["p1"] });
const G6 = withSpare(K2, { rule: "top", extra: 1 });
const UNREADABLE_V2 = {
  B4: edited(K2, (value) => { value.version = 3; }),
  B5: edited(K2, (value) => { value.version = "2"; }),
  B25: edited(K2, (value) => { delete value.bill.spare; }),
  B26: withSpare(K2, { rule: "two" }),
  B27: withSpare(K2, { rule: "one", personId: "p9" }),
  B28: withSpare(K2, { rule: "one" }),
  B29: withSpare(K2, { rule: "random", order: ["p1", "p2"] }),
  B30: withSpare(K2, { rule: "random", order: ["p1", "p1", "p2", "p3"] }),
  B31: withSpare(K2, { rule: "random", order: ["p1", "p2", "p3", "p4"] }),
  B32: withSpare(K2, []),
};
const storageHolding = (text) => {
  const memory = new Map(text === null ? [] : [[DRAFT_KEY, text]]);
  return { getItem: (key) => memory.get(key) ?? null, setItem: (key, value) => { memory.set(key, String(value)); } };
};
const throwingStorage = { getItem() { throw new Error("read failed"); }, setItem() { throw new Error("full"); } };

test("@R25 encodeDraft and decodeDraft round-trip a new bill and an item bill", () => {
  assert.deepEqual(decodeDraft(encodeDraft(newBill())), { ok: true, bill: newBill() });
  const full = bill({ mode: "item", items: [{ id: "i3", name: "Tea", priceText: "5", who: ["p2"] }], spare: TOP, nextId: 4 });
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
  // An item name is one line in the clipboard text too, so it gets the same line break rule as a person name.
  const tea = { id: "i3", name: "Tea", priceText: "5", who: [] };
  assert.equal(decodeDraft(draft({ items: [tea], nextId: 4 })).ok, true);
  for (const name of ["Te\na", "Te\ra"]) rejects(draft({ items: [{ ...tea, name }], nextId: 4 }));
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
  // The highest id may sit on an item: people p1 and p2, item i3, so 3 is stale (the next item would be i3 again).
  const tea = { id: "i3", name: "Tea", priceText: "5", who: [] };
  rejects(draft({ items: [tea], nextId: 3 }));
  assert.equal(decodeDraft(draft({ items: [tea], nextId: 4 })).ok, true);
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
  assert.deepEqual(Object.keys(decoded.bill), ["mode", "people", "subtotalText", "items", "serviceText", "sstText", "spare", "nextId"]);
  assert.deepEqual(Object.keys(decoded.bill.people[0]), ["id", "name"]);
  assert.deepEqual(Object.keys(decoded.bill.items[0]), ["id", "name", "priceText", "who"]);
  assert.equal(({}).polluted, undefined);
  assert.equal(Object.getPrototypeOf(decoded.bill), Object.prototype);
  assert.equal(JSON.stringify(decoded.bill).includes("colour"), false);
});

test("@R28 getStorage, loadDraft and saveDraft never throw", () => {
  assert.equal(getStorage(), null); // no window here, which is what a blocked localStorage looks like
  assert.deepEqual(loadDraft(null), { state: "failed" });
  assert.equal(saveDraft(null, newBill()), false);
  assert.deepEqual(loadDraft(throwingStorage), { state: "failed" });
  assert.equal(saveDraft(throwingStorage, newBill()), false);
});

test("@R61 D3 and D13 read a version 2 draft with its spare choice as stored", () => {
  for (const text of [K1, K2, ONE, RND, PA0]) assert.deepEqual(decodeDraft(text), { ok: true, bill: billOf(text) });
});

test("@R61 D14 reads a version 1 draft with spare Top of the list, whatever spare key it holds", () => {
  for (const text of [S1_V1, S2_V1]) assert.deepEqual(decodeDraft(text), { ok: true, bill: { ...billOf(text), spare: TOP } });
  assert.deepEqual(decodeDraft(G5), { ok: true, bill: { ...billOf(S2_V1), spare: TOP } });
});

test("@R61 D13 keeps a One person choice whose person is on no item, and keeps only the fields a rule needs", () => {
  assert.deepEqual(decodeDraft(G4), { ok: true, bill: billOf(G4) });
  assert.deepEqual(decodeDraft(G6), { ok: true, bill: billOf(K2) });
  const crossed = withSpare(K2, { rule: "random", order: ["p3", "p1", "p2"], personId: "p1" });
  assert.deepEqual(decodeDraft(crossed).bill.spare, { rule: "random", order: ["p3", "p1", "p2"] });
  const extraOrder = withSpare(K2, { rule: "one", personId: "p3", order: ["p1"] });
  assert.deepEqual(decodeDraft(extraOrder).bill.spare, { rule: "one", personId: "p3" });
});

test("@R61 D3 and D13 reject another version and every spare choice outside core R27", () => {
  for (const [name, text] of Object.entries(UNREADABLE_V2)) assert.deepEqual(decodeDraft(text), { ok: false }, name);
});

test("@R61 encodeDraft writes version 2, and loadDraft and saveDraft report a storage that fails", () => {
  const k1 = billOf(K1);
  assert.deepEqual(JSON.parse(encodeDraft(k1)), { version: 2, bill: k1 });
  assert.deepEqual(loadDraft(null), { state: "failed" });
  assert.deepEqual(loadDraft(throwingStorage), { state: "failed" });
  assert.deepEqual(loadDraft(storageHolding(null)), { state: "none" });
  assert.deepEqual(loadDraft(storageHolding("not json")), { state: "unreadable" }); // B1
  assert.deepEqual(loadDraft(storageHolding(K2)), { state: "ok", bill: billOf(K2) });
  assert.equal(saveDraft(null, k1), false);
  assert.equal(saveDraft(throwingStorage, k1), false);
  const working = storageHolding(null);
  assert.equal(saveDraft(working, k1), true);
  assert.equal(working.getItem(DRAFT_KEY), encodeDraft(k1));
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
