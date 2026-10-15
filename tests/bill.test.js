import { test } from "node:test";
import assert from "node:assert/strict";
import {
  LIMITS, newBill, addPerson, removePerson, setPersonName, setMode, setSubtotalText,
  setServiceText, setSstText, addItem, removeItem, setItemName, setItemPriceText,
  toggleItemPerson, personLabel, itemLabel, sparePeople, plainName,
} from "../src/core/bill.js";
import { chooseSpareRule, chooseSparePerson, pickAgain } from "../src/core/spare.js";
import { computeResult } from "../src/core/result.js";
import { summaryText } from "../src/core/summary.js";
import { S1, S2, I2, I3, D2, MAX_E, MAX_I, deepFreeze, withSpare } from "./support/bills.js";
import { scripted, constant } from "./support/rng.js";

// A random source for the cases that must not draw: it throws if the code under test asks it for a number.
const never = scripted();
const BILL_KEYS = ["mode", "people", "subtotalText", "items", "serviceText", "sstText", "spare", "nextId"];

test("@R10 a new bill has two people, even mode, the default rates and Top of the list", () => {
  assert.deepEqual(newBill(), {
    mode: "even",
    people: [{ id: "p1", name: "Person 1" }, { id: "p2", name: "Person 2" }],
    subtotalText: "",
    items: [],
    serviceText: "10",
    sstText: "6",
    spare: { rule: "top" },
    nextId: 3,
  });
});

test("@R10 every call returns a fresh bill, never a shared one", () => {
  const first = newBill();
  assert.notEqual(newBill(), first);
  assert.notEqual(newBill().people, first.people);
  assert.notEqual(newBill().spare, first.spare);
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

test("@R11 a new person's id comes from nextId, so it never reuses a removed id", () => {
  let bill = addPerson(addPerson(newBill()));
  bill = addPerson(removePerson(bill, "p3"));
  assert.deepEqual(bill.people.map((p) => p.id), ["p1", "p2", "p4", "p5"]);
  assert.equal(bill.nextId, 6);
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

test("@R27 @R11 adding a person extends the drawn order and keeps the people already drawn in place", () => {
  const drawn = withSpare(S2, { rule: "random", order: ["p2", "p3", "p1"] });
  assert.equal(drawn.nextId, 4);
  const added = addPerson(drawn);
  assert.deepEqual(added.spare, { rule: "random", order: ["p2", "p3", "p1", "p4"] });
  assert.equal(added.nextId, 5);
  for (const spare of [{ rule: "top" }, { rule: "one", personId: "p2" }]) {
    assert.deepEqual(addPerson(withSpare(S2, spare)).spare, spare);
  }
});

const removals = [
  [{ rule: "random", order: ["p2", "p3", "p1"] }, "p3", { rule: "random", order: ["p2", "p1"] }],
  [{ rule: "one", personId: "p2" }, "p2", { rule: "top" }],
  [{ rule: "one", personId: "p2" }, "p3", { rule: "one", personId: "p2" }],
  [{ rule: "top" }, "p1", { rule: "top" }],
];
for (const [before, id, after] of removals) {
  test(`@R27 @R12 removing ${id} from spare ${JSON.stringify(before)} leaves ${JSON.stringify(after)}`, () => {
    assert.deepEqual(removePerson(withSpare(S2, before), id).spare, after);
  });
}

test("@R27 @R12 a refused removal keeps the spare choice as it was", () => {
  const chosen = withSpare(newBill(), { rule: "one", personId: "p1" });
  assert.equal(removePerson(chosen, "p1"), chosen);
  const drawn = withSpare(S2, { rule: "random", order: ["p2", "p3", "p1"] });
  assert.equal(removePerson(drawn, "p99"), drawn);
});

test("@R27 @R15 a mode switch, the setters and the item actions never touch the spare choice", () => {
  const spare = { rule: "one", personId: "p2" };
  const chosen = withSpare(S1, spare);
  const actions = [
    (b) => setMode(setMode(b, "even"), "item"),
    (b) => setSubtotalText(b, "9"),
    (b) => setServiceText(b, "9"),
    (b) => setSstText(b, "9"),
    (b) => setPersonName(b, "p1", "Z"),
    (b) => addItem(b),
    (b) => removeItem(b, "i4"),
    (b) => setItemName(b, "i4", "Z"),
    (b) => setItemPriceText(b, "i4", "9"),
    (b) => toggleItemPerson(b, "i4", "p2"),
  ];
  for (const act of actions) assert.deepEqual(act(chosen).spare, spare);
});

const spareHolders = [
  ["S2", S2, ["p1", "p2", "p3"]],
  ["S1", S1, ["p1", "p2", "p3"]],
  ["I2", I2, ["p2", "p3"]],
  ["I3 (tapped Chen first, still list order)", I3, ["p1", "p3"]],
  ["I2 switched to even mode", setMode(I2, "even"), ["p1", "p2", "p3"]],
  ["D2", D2, ["p2"]],
  ["a new bill switched to by-item mode", setMode(newBill(), "item"), []],
];
for (const [title, bill, ids] of spareHolders) {
  test(`@R28 sparePeople of ${title} is ${JSON.stringify(ids)}`, () => {
    assert.deepEqual(sparePeople(bill), ids);
  });
}

test("@R28 @R16 sparePeople leaves a deep-frozen bill alone and lists a person once", () => {
  const frozen = deepFreeze(structuredClone(S1));
  assert.deepEqual(sparePeople(frozen), ["p1", "p2", "p3"]);
  assert.deepEqual(frozen, S1);
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
    () => chooseSpareRule(frozen, "one", never),
    () => chooseSpareRule(frozen, "random", constant(0)),
    () => chooseSparePerson(frozen, "p2"),
  ];
  for (const apply of changing) {
    const result = apply();
    assert.notEqual(result, frozen);
    assert.deepEqual(Object.keys(result), BILL_KEYS);
  }
  assert.deepEqual(frozen, S1);
});

test("@R16 @R31 pickAgain and the spare choices leave a deep-frozen bill alone and return a new bill", () => {
  const frozen = withSpare(S2, { rule: "random", order: ["p2", "p3", "p1"] });
  const again = pickAgain(frozen, scripted(0.9, 0.9));
  assert.notEqual(again, frozen);
  assert.deepEqual(Object.keys(again), BILL_KEYS);
  assert.deepEqual(frozen.spare, { rule: "random", order: ["p2", "p3", "p1"] });
  assert.deepEqual(chooseSpareRule(frozen, "top", never).spare, { rule: "top" });
  assert.deepEqual(chooseSparePerson(frozen, "p3").spare, { rule: "one", personId: "p3" });
  assert.deepEqual(frozen, withSpare(S2, { rule: "random", order: ["p2", "p3", "p1"] }));
});

// A bill as JSON.parse returns it: stray keys on the bill, on a person and on an item, and own
// __proto__ keys on the bill and on a person.
const parsedBill = () => JSON.parse(
  '{"mode":"even","people":[{"id":"p1","name":"A","x":1},{"id":"p2","name":"B","__proto__":{"polluted":true}},' +
  '{"id":"p3","name":"C"}],"subtotalText":"","items":[{"id":"i4","name":"T","priceText":"1","who":["p1"],' +
  '"stray":1}],"serviceText":"10","sstText":"6","spare":{"rule":"top"},"nextId":5,"extra":1,"__proto__":{"polluted":true}}',
);
const PERSON_KEYS = ["id", "name"];
const ITEM_KEYS = ["id", "name", "priceText", "who"];

// Each action runs on the parsed bill itself, never after another action, so no rebuild elsewhere can
// hide a spread. `rebuilt` picks the person or item the action changed.
const rebuilds = [
  ["setMode", (b) => setMode(b, "item")],
  ["setSubtotalText", (b) => setSubtotalText(b, "1")],
  ["setServiceText", (b) => setServiceText(b, "1")],
  ["setSstText", (b) => setSstText(b, "1")],
  ["addPerson", (b) => addPerson(b)],
  ["addItem", (b) => addItem(b)],
  ["removeItem", (b) => removeItem(b, "i4")],
  ["setPersonName", (b) => setPersonName(b, "p1", "Z"), (next) => next.people[0], PERSON_KEYS],
  ["setPersonName (person with a __proto__ key)", (b) => setPersonName(b, "p2", "Z"), (next) => next.people[1], PERSON_KEYS],
  ["removePerson", (b) => removePerson(b, "p3"), (next) => next.items[0], ITEM_KEYS],
  ["setItemName", (b) => setItemName(b, "i4", "Z"), (next) => next.items[0], ITEM_KEYS],
  ["setItemPriceText", (b) => setItemPriceText(b, "i4", "2"), (next) => next.items[0], ITEM_KEYS],
  ["toggleItemPerson", (b) => toggleItemPerson(b, "i4", "p2"), (next) => next.items[0], ITEM_KEYS],
];
for (const [title, act, rebuilt, keys] of rebuilds) {
  test(`@R16 ${title} on a parsed bill builds only known fields`, () => {
    const parsed = parsedBill();
    const next = act(parsed);
    assert.notEqual(next, parsed);
    assert.deepEqual(Object.keys(next), BILL_KEYS);
    assert.equal(Object.hasOwn(next, "__proto__"), false);
    if (rebuilt) assert.deepEqual(Object.keys(rebuilt(next)), keys);
    assert.equal({}.polluted, undefined);
  });
}

// The spare choice an action rebuilds comes from known fields only, like a person or an item (threat model,
// object integrity). Stray and __proto__ keys on the parsed choice must not travel into the new one.
const parsedWithSpare = (spare) => ({ ...parsedBill(), spare: JSON.parse(spare) });
const STRAY = '"stray":1,"__proto__":{"polluted":true}';
const spareRebuilds = [
  ["addPerson", (b) => addPerson(b), `{"rule":"random","order":["p1","p2","p3"],${STRAY}}`, ["rule", "order"]],
  ["removePerson (random)", (b) => removePerson(b, "p3"), `{"rule":"random","order":["p1","p2","p3"],${STRAY}}`, ["rule", "order"]],
  ["removePerson (the chosen one)", (b) => removePerson(b, "p2"), `{"rule":"one","personId":"p2",${STRAY}}`, ["rule"]],
];
for (const [title, act, spare, keys] of spareRebuilds) {
  test(`@R27 @R16 ${title} on a parsed bill builds the spare choice from known fields`, () => {
    const next = act(parsedWithSpare(spare));
    assert.deepEqual(Object.keys(next.spare), keys);
    assert.equal(Object.hasOwn(next.spare, "__proto__"), false);
    assert.equal({}.polluted, undefined);
  });
}

// The three choice actions (spare.js) build the new Bill and its spare choice from known fields too. pickAgain
// needs shares to compare, so its parsed bill has a subtotal.
const chooseOnParsed = [
  ["chooseSpareRule one", (b) => chooseSpareRule(b, "one", never), "top"],
  ["chooseSpareRule random", (b) => chooseSpareRule(b, "random", constant(0)), "top"],
  ["chooseSpareRule top", (b) => chooseSpareRule(b, "top", never), "one"],
  ["chooseSparePerson", (b) => chooseSparePerson(b, "p2"), "top"],
  ["pickAgain", (b) => pickAgain({ ...b, subtotalText: "100.00" }, scripted(0.5, 0.9)), "random"],
];
const PARSED_SPARE = {
  top: '{"rule":"top"}',
  one: `{"rule":"one","personId":"p1",${STRAY}}`,
  random: `{"rule":"random","order":["p1","p2","p3"],${STRAY}}`,
};
for (const [title, act, before] of chooseOnParsed) {
  test(`@R16 ${title} on a parsed bill builds the bill and the spare choice from known fields`, () => {
    const parsed = parsedWithSpare(PARSED_SPARE[before]);
    const next = act(parsed);
    assert.notEqual(next, parsed);
    assert.deepEqual(Object.keys(next), BILL_KEYS);
    assert.equal(Object.hasOwn(next, "__proto__"), false);
    assert.equal(Object.hasOwn(next.spare, "__proto__"), false);
    assert.equal(Object.hasOwn(next.spare, "stray"), false);
    assert.equal({}.polluted, undefined);
  });
}

test("@R27 @R16 addPerson and removePerson leave a deep-frozen random choice alone", () => {
  const frozen = withSpare(S2, { rule: "random", order: ["p2", "p3", "p1"] });
  const added = addPerson(frozen);
  const removed = removePerson(frozen, "p2");
  assert.notEqual(added, frozen);
  assert.deepEqual(Object.keys(added), BILL_KEYS);
  assert.deepEqual(removed.spare, { rule: "random", order: ["p3", "p1"] });
  assert.deepEqual(frozen.spare, { rule: "random", order: ["p2", "p3", "p1"] });
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

test("@R16 @R17 the labels leave a frozen person or item alone", () => {
  assert.equal(personLabel(Object.freeze({ id: "p1", name: " A " }), 0), "A");
  assert.equal(itemLabel(Object.freeze({ id: "i3", name: " Satay ", priceText: "", who: Object.freeze([]) }), 0), "Satay");
});

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

// ---- R35, a plain name (H-10). The rows of qa.md "plainName deletes the class and keeps everything else". ----
// A title spells every code point outside printable ASCII as U+XXXX, so no bidi control reorders the runner's output.
const spelled = (text) => [...text].map((char) => {
  const cp = char.codePointAt(0);
  return cp >= 0x20 && cp <= 0x7e ? char : `U+${cp.toString(16).toUpperCase().padStart(4, "0")}`;
}).join("");
const PLAIN_ROWS = [
  ["Ben\u{202E}", "Ben"],
  ["Be\u{202E}x\u{2067}n", "Bexn"],
  ["A\u{2028}B\u{2029}C", "ABC"],
  ["\u{0000}Adds up to RM 0.00", "Adds up to RM 0.00"],
  ["Ann\u{0009}Lee", "AnnLee"],
  ["x\u{001B}\u{007F}\u{0085}\u{009F}y", "xy"],
  ["\u{061C}\u{200E}\u{200F}\u{202A}\u{202B}\u{202C}\u{202D}\u{2066}\u{2068}\u{2069}", ""],
  ["A\u{200B}B\u{00A0}C\u{FEFF}\u{00AD}\u{3000}", "A\u{200B}B\u{00A0}C\u{FEFF}\u{00AD}\u{3000}"],
  ["\u{1F468}\u{200D}\u{1F469}\u{200D}\u{1F467}", "\u{1F468}\u{200D}\u{1F469}\u{200D}\u{1F467}"],
  ["\u{0639}\u{0644}\u{064A} Lina", "\u{0639}\u{0644}\u{064A} Lina"],
  ["", ""],
];
for (const [text, plain] of PLAIN_ROWS) {
  test(`@R35 plainName of "${spelled(text)}" is "${spelled(plain)}"`, () => {
    assert.equal(plainName(text), plain);
  });
}

// The proof that the names on screen and the copied summary cannot drift apart (spec R35 point 2). For every code
// point, plainName deletes it exactly when summaryText replaces it in a row name with a space, and both keep every
// other one as typed. The row is compared whole, because a typed U+0020 also reads "A B". 79 is written by hand
// (65 in Cc, LS, PS and 12 in Bidi_Control), because a count read from either class would agree with a wrong class.
test("@R35 @R24 plainName and summaryText read one class, 79 code points, for every code point", () => {
  const s2Rows = computeResult(S2);
  const chenRowAs = (name) => summaryText({ ...s2Rows, rows: s2Rows.rows.map((row, index) => (index === 2 ? { ...row, name } : row)) })
    .split("\n")[4];
  // The row is swapped into the one S2 result for speed. On these it equals the bill with Chen renamed, worked out whole.
  for (const cp of [0x0000, 0x0020, 0x0041, 0x0085, 0x200b, 0x202e, 0x2069, 0x1f468]) {
    const text = `A${String.fromCodePoint(cp)}B`;
    assert.equal(chenRowAs(text), summaryText(computeResult(setPersonName(S2, "p3", text))).split("\n")[4]);
  }
  let removed = 0;
  const wrong = [];
  for (let cp = 0; cp <= 0x10ffff; cp += 1) {
    if (cp >= 0xd800 && cp <= 0xdfff) continue;
    const text = `A${String.fromCodePoint(cp)}B`;
    const plain = plainName(text);
    const deleted = plain === "AB";
    if (deleted) removed += 1;
    const row = chenRowAs(text);
    if ((!deleted && plain !== text) || row !== `${deleted ? "A B" : text} RM 38.86` || plainName(plain) !== plain) {
      wrong.push(spelled(String.fromCodePoint(cp)));
    }
  }
  assert.deepEqual(wrong, []);
  assert.equal(removed, 79);
});
