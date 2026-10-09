import { test } from "node:test";
import assert from "node:assert/strict";
import {
  LIMITS, newBill, addPerson, removePerson, setPersonName, setMode, setSubtotalText,
  setServiceText, setSstText, addItem, removeItem, setItemName, setItemPriceText,
  toggleItemPerson, personLabel, itemLabel,
} from "../src/core/bill.js";
import { S1, D2, MAX_E, MAX_I, deepFreeze } from "./support/bills.js";

const BILL_KEYS = ["mode", "people", "subtotalText", "items", "serviceText", "sstText", "nextId"];

test("@R10 a new bill has two people, even mode and the default rates", () => {
  assert.deepEqual(newBill(), {
    mode: "even",
    people: [{ id: "p1", name: "Person 1" }, { id: "p2", name: "Person 2" }],
    subtotalText: "",
    items: [],
    serviceText: "10",
    sstText: "6",
    nextId: 3,
  });
});

test("@R10 every call returns a fresh bill, never a shared one", () => {
  const first = newBill();
  assert.notEqual(newBill(), first);
  assert.notEqual(newBill().people, first.people);
});

test("@R10 the limits constant matches the contract and is frozen", () => {
  assert.deepEqual({ ...LIMITS }, {
    minPeople: 2, maxPeople: 12, maxItems: 50, personNameMax: 20, itemNameMax: 40,
    serviceMaxPercent: 30, sstMaxPercent: 20,
  });
  assert.ok(Object.isFrozen(LIMITS));
});

test("@R11 adding a person appends an empty-named person with the next id", () => {
  const bill = addPerson(newBill());
  assert.equal(bill.people.length, 3);
  assert.deepEqual(bill.people[2], { id: "p3", name: "" });
  assert.equal(bill.nextId, 4);
  assert.deepEqual(addPerson(S1).items, S1.items);
});

test("@R11 the twelfth person is accepted and the thirteenth does nothing", () => {
  let bill = newBill();
  for (let n = 0; n < 10; n += 1) bill = addPerson(bill);
  assert.deepEqual(bill.people.map((p) => p.id), Array.from({ length: 12 }, (_, i) => `p${i + 1}`));
  assert.equal(addPerson(bill), bill);
});

test("@R12 removing a person removes them from every item", () => {
  const bill = removePerson(S1, "p3");
  assert.deepEqual(bill.people.map((p) => p.name), ["Aisyah", "Ben"]);
  assert.deepEqual(bill.items.find((i) => i.id === "i6").who, []);
  assert.deepEqual(bill.items.find((i) => i.id === "i7").who, ["p1"]);
  const knownIds = new Set(bill.people.map((p) => p.id));
  assert.ok(bill.items.every((item) => item.who.every((id) => knownIds.has(id))));
});

test("@R12 removing is refused at 2 people or for an unknown id", () => {
  const fresh = newBill();
  assert.equal(removePerson(fresh, "p1"), fresh);
  assert.equal(removePerson(S1, "p99"), S1);
  const down = removePerson(S1, "p3");
  assert.equal(removePerson(down, "p1"), down);
});

test("@R13 adding an item appends an empty, unassigned item", () => {
  assert.equal(S1.nextId, 8);
  const bill = addItem(S1);
  assert.deepEqual(bill.items[bill.items.length - 1], { id: "i8", name: "", priceText: "", who: [] });
  assert.equal(bill.nextId, 9);
});

test("@R13 the 51st item is refused and removing works at any time", () => {
  assert.equal(MAX_I.items.length, 50);
  assert.equal(addItem(MAX_I), MAX_I);
  const idOfItem25 = MAX_I.items[24].id;
  const bill = removeItem(MAX_I, idOfItem25);
  assert.deepEqual(bill.items.map((i) => i.id), MAX_I.items.map((i) => i.id).filter((id) => id !== idOfItem25));
  assert.equal(bill.items.length, 49);
});

test("@R13 removing an unknown item returns the same bill", () => {
  assert.equal(removeItem(S1, "i99"), S1);
});

test("@R14 tapping toggles a person on an item", () => {
  const on = toggleItemPerson(S1, "i5", "p1");
  assert.deepEqual([...on.items.find((i) => i.id === "i5").who].sort(), ["p1", "p2"]);
  const off = toggleItemPerson(on, "i5", "p1");
  assert.deepEqual(off.items.find((i) => i.id === "i5").who, ["p2"]);
});

test("@R14 an unknown item or person id returns the same bill", () => {
  assert.equal(toggleItemPerson(S1, "i99", "p1"), S1);
  assert.equal(toggleItemPerson(S1, "i5", "p99"), S1);
});

test("@R15 switching modes keeps both sets of input", () => {
  const typed = setSubtotalText(S1, "100.00");
  const roundTrip = setMode(setMode(typed, "even"), "item");
  assert.equal(roundTrip.subtotalText, "100.00");
  assert.deepEqual(roundTrip.items, S1.items);
  assert.equal(roundTrip.items.length, 4);
  assert.equal(setMode(typed, "other"), typed);
  assert.equal(setMode(typed, ""), typed);
});

test("@R15 setters store text exactly as typed", () => {
  const bill = setSubtotalText(setPersonName(newBill(), "p1", "  Ben  "), " 12.5x");
  assert.equal(bill.people[0].name, "  Ben  ");
  assert.equal(bill.subtotalText, " 12.5x");
});

test("@R15 each setter changes only its own field", () => {
  const cases = [
    ["setPersonName", (b) => setPersonName(b, "p1", "Zed"), (e) => { e.people[0].name = "Zed"; }],
    ["setItemName", (b) => setItemName(b, "i4", "Zed"), (e) => { e.items[0].name = "Zed"; }],
    ["setItemPriceText", (b) => setItemPriceText(b, "i4", " 9.5 "), (e) => { e.items[0].priceText = " 9.5 "; }],
    ["setSubtotalText", (b) => setSubtotalText(b, "7"), (e) => { e.subtotalText = "7"; }],
    ["setServiceText", (b) => setServiceText(b, "x"), (e) => { e.serviceText = "x"; }],
    ["setSstText", (b) => setSstText(b, ""), (e) => { e.sstText = ""; }],
    ["setMode", (b) => setMode(b, "even"), (e) => { e.mode = "even"; }],
  ];
  for (const [title, apply, edit] of cases) {
    const expected = structuredClone(S1);
    edit(expected);
    assert.deepEqual(apply(S1), expected, title);
  }
});

test("@R15 setters with an unknown id return the same bill", () => {
  assert.equal(setPersonName(S1, "p99", "x"), S1);
  assert.equal(setItemName(S1, "i99", "x"), S1);
  assert.equal(setItemPriceText(S1, "i99", "1"), S1);
});

test("@R16 no action mutates a deep-frozen bill and changes return new objects", () => {
  const frozen = deepFreeze(structuredClone(S1));
  const changing = [
    () => addPerson(frozen),
    () => removePerson(frozen, "p3"),
    () => setPersonName(frozen, "p1", "Zed"),
    () => addItem(frozen),
    () => removeItem(frozen, "i4"),
    () => setItemName(frozen, "i4", "Zed"),
    () => setItemPriceText(frozen, "i4", "1"),
    () => toggleItemPerson(frozen, "i5", "p1"),
    () => setSubtotalText(frozen, "1"),
    () => setServiceText(frozen, "1"),
    () => setSstText(frozen, "1"),
    () => setMode(frozen, "even"),
  ];
  for (const apply of changing) {
    const result = apply();
    assert.notEqual(result, frozen);
    assert.deepEqual(Object.keys(result), BILL_KEYS);
  }
  assert.deepEqual(frozen, S1);
});

test("@R16 actions rebuild from known fields, so stray and __proto__ keys are dropped", () => {
  const parsed = JSON.parse(
    '{"mode":"even","people":[{"id":"p1","name":"A","x":1},{"id":"p2","name":"B"}],"subtotalText":"",' +
    '"items":[],"serviceText":"10","sstText":"6","nextId":3,"extra":1,"__proto__":{"polluted":true}}',
  );
  const next = setPersonName(setMode(parsed, "item"), "p1", "Z");
  assert.deepEqual(Object.keys(next), BILL_KEYS);
  assert.deepEqual(Object.keys(next.people[0]), ["id", "name"]);
  assert.equal(Object.hasOwn(next, "__proto__"), false);
  assert.equal(next.polluted, undefined);
  assert.equal({}.polluted, undefined);
});

const labels = [
  ["person", { name: "Aisyah" }, 0, "Aisyah"],
  ["person", { name: " Ben " }, 1, "Ben"],
  ["person", { name: "   " }, 2, "Person 3"],
  ["person", { name: "" }, 0, "Person 1"],
  ["item", { name: "Satay" }, 3, "Satay"],
  ["item", { name: "" }, 0, "Item 1"],
];
for (const [kind, entry, index, label] of labels) {
  test(`@R17 ${kind} named ${JSON.stringify(entry.name)} at index ${index} is ${JSON.stringify(label)}`, () => {
    const read = kind === "person" ? personLabel : itemLabel;
    assert.equal(read(entry, index), label);
  });
}

test("@R17 the fallback follows the position after a removal", () => {
  let bill = setPersonName(setPersonName(addPerson(newBill()), "p1", ""), "p2", "Ben");
  assert.deepEqual(bill.people.map(personLabel), ["Person 1", "Ben", "Person 3"]);
  bill = removePerson(bill, "p1");
  assert.deepEqual(bill.people.map(personLabel), ["Ben", "Person 2"]);
});

test("@R26 equal names are stored as typed and nobody is merged", () => {
  let bill = addPerson(newBill());
  bill = setPersonName(bill, "p1", "Ben");
  bill = setPersonName(bill, "p2", "Ben");
  bill = setPersonName(bill, "p3", " ben ");
  assert.deepEqual(bill.people, [
    { id: "p1", name: "Ben" },
    { id: "p2", name: "Ben" },
    { id: "p3", name: " ben " },
  ]);
});

test("@R26 tapping and removing address a person by id, not by name", () => {
  assert.equal(D2.nextId, 5);
  const tapped = toggleItemPerson(D2, "i4", "p1");
  assert.deepEqual([...tapped.items[0].who].sort(), ["p1", "p2"]);
  assert.equal(tapped.people.length, 3);
  assert.deepEqual(tapped.people.map((p) => p.name), ["Ben", "Ben", "Chen"]);
  const removed = removePerson(D2, "p2");
  assert.deepEqual(removed.people, [{ id: "p1", name: "Ben" }, { id: "p3", name: "Chen" }]);
  assert.deepEqual(removed.items[0].who, []);
});

test("@R11 @R12 the twelve-person bill refuses a thirteenth and still removes by id", () => {
  assert.equal(MAX_E.people.length, 12);
  assert.equal(addPerson(MAX_E), MAX_E);
  assert.equal(removePerson(MAX_E, "p12").people.length, 11);
});
