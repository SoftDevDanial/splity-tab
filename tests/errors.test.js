// Unit tests for src/errors.js (split-app R10): when an inline error shows. The browser suite proves the same rules
// through the page; these pin the whole matrix, for every kind of field, without a browser (code review WR-02).
import test from "node:test";
import assert from "node:assert/strict";
import { flagsFor, forgetPrice, leftField, newErrorFlags, typedInto, visibleErrors } from "../src/errors.js";
import { newBill } from "../src/core/bill.js";

// One text per kind that fails its parser, and one that passes. "Empty" is never an error (ruling 1).
const KINDS = ["subtotal", "price", "service", "sst"];
const BAD = { subtotal: "0", price: "13.505", service: "31", sst: "20.01" };
const BAD_TOO = { subtotal: "0.00", price: "abc", service: "30.01", sst: "x" }; // a different text that also fails
const GOOD = { subtotal: "12.50", price: "13.50", service: "10", sst: "6" };
const ID = "i5"; // the item id a price flag belongs to

const item = (id, priceText) => ({ id, name: "Tea", priceText, who: [] });
/** A bill whose one field of `kind` holds `text`; every other field is valid. */
function billWith(kind, text) {
  const bill = { ...newBill(), mode: "item", subtotalText: GOOD.subtotal, serviceText: GOOD.service, sstText: GOOD.sst,
    items: [item(ID, GOOD.price)] };
  if (kind === "price") bill.items = [item(ID, text)];
  else bill[`${kind}Text`] = text;
  return bill;
}
const shown = (flags, kind, text) => (kind === "price" ? visibleErrors(flags, billWith(kind, text)).price[ID]
  : visibleErrors(flags, billWith(kind, text))[kind]);
const flagOf = (flags, kind) => (kind === "price" ? flags.price[ID] : flags[kind]);

test("@R10 newErrorFlags starts with nothing flagged, and every call is a new object", () => {
  assert.deepEqual(newErrorFlags(), { subtotal: false, service: false, sst: false, price: {} });
  const first = newErrorFlags();
  first.price[ID] = true;
  first.subtotal = true;
  assert.deepEqual(newErrorFlags(), { subtotal: false, service: false, sst: false, price: {} });
});

test("@R10 b flagsFor flags a restored field only when its text is not empty and fails its parser", () => {
  const bad = { ...newBill(), mode: "item", subtotalText: BAD.subtotal, serviceText: BAD.service, sstText: BAD.sst,
    items: [item("i3", BAD.price), item("i4", GOOD.price), item("i5", "")] };
  assert.deepEqual(flagsFor(bad), { subtotal: true, service: true, sst: true, price: { i3: true, i4: false, i5: false } });
  const quiet = { ...newBill(), subtotalText: "   ", serviceText: "", sstText: GOOD.sst, items: [] };
  assert.deepEqual(flagsFor(quiet), newErrorFlags());
  assert.deepEqual(flagsFor(newBill()), newErrorFlags());
});

test("@R10 a leftField sets the flag for bad text, and for nothing else", () => {
  for (const kind of KINDS) {
    const flags = newErrorFlags();
    leftField(flags, kind, BAD[kind], ID);
    assert.equal(flagOf(flags, kind), true, kind);
    for (const text of [GOOD[kind], "", "   "]) {
      const quiet = newErrorFlags();
      leftField(quiet, kind, text, ID);
      assert.notEqual(flagOf(quiet, kind), true, `${kind} ${JSON.stringify(text)}`);
    }
  }
});

test("@R10 a leftField sets only the flag of its own kind, and of its own item", () => {
  const flags = newErrorFlags();
  leftField(flags, "price", BAD.price, "i4");
  assert.deepEqual(flags, { subtotal: false, service: false, sst: false, price: { i4: true } });
  leftField(flags, "sst", BAD.sst);
  assert.deepEqual(flags, { subtotal: false, service: false, sst: true, price: { i4: true } });
});

test("@R10 c typing text that is valid or empty clears a flag, for every kind of field", () => {
  for (const kind of KINDS) {
    for (const text of [GOOD[kind], "", " "]) {
      const flags = newErrorFlags();
      leftField(flags, kind, BAD[kind], ID);
      typedInto(flags, kind, text, ID);
      assert.equal(flagOf(flags, kind), false, `${kind} ${JSON.stringify(text)}`);
    }
  }
});

test("@R10 c typing bad text keeps a flag that is already set, and never sets one", () => {
  for (const kind of KINDS) {
    const flags = newErrorFlags();
    typedInto(flags, kind, BAD[kind], ID);
    assert.notEqual(flagOf(flags, kind), true, `${kind}: typing sets nothing`);
    leftField(flags, kind, BAD[kind], ID);
    typedInto(flags, kind, BAD_TOO[kind], ID);
    assert.equal(flagOf(flags, kind), true, `${kind}: bad to bad keeps the error on screen`);
  }
});

test("@R10 c a cleared error does not come back until the field is left again", () => {
  for (const kind of KINDS) {
    const flags = newErrorFlags();
    leftField(flags, kind, BAD[kind], ID);
    assert.equal(shown(flags, kind, BAD[kind]), true, `${kind}: shown after the first blur`);
    typedInto(flags, kind, GOOD[kind], ID); // the user types a valid text ...
    assert.equal(shown(flags, kind, GOOD[kind]), false, `${kind}: gone at valid text`);
    typedInto(flags, kind, BAD[kind], ID); // ... and then spoils it again, still in the field
    assert.equal(shown(flags, kind, BAD[kind]), false, `${kind}: not back while the field keeps focus`);
    leftField(flags, kind, BAD[kind], ID); // the next blur
    assert.equal(shown(flags, kind, BAD[kind]), true, `${kind}: back when the field is left`);
  }
});

test("@R10 visibleErrors shows an error only while its flag is set and its text is still bad", () => {
  for (const kind of KINDS) {
    const flagged = newErrorFlags();
    leftField(flagged, kind, BAD[kind], ID);
    assert.equal(shown(flagged, kind, BAD[kind]), true, `${kind}: flag and bad text`);
    assert.equal(shown(flagged, kind, GOOD[kind]), false, `${kind}: flag, text now valid`);
    assert.equal(shown(flagged, kind, ""), false, `${kind}: flag, text now empty`);
    assert.equal(shown(newErrorFlags(), kind, BAD[kind]), false, `${kind}: bad text, field not left yet`);
  }
});

test("@R10 visibleErrors reports every field, and a price flag belongs to its item alone", () => {
  const flags = newErrorFlags();
  leftField(flags, "price", BAD.price, "i4");
  const bill = { ...newBill(), mode: "item", items: [item("i3", BAD.price), item("i4", BAD.price), item("i5", GOOD.price)] };
  assert.deepEqual(visibleErrors(flags, bill), {
    subtotal: false, service: false, sst: false, price: { i3: false, i4: true, i5: false } });
  assert.deepEqual(visibleErrors(newErrorFlags(), newBill()), { subtotal: false, service: false, sst: false, price: {} });
});

test("@R10 forgetPrice drops the flag of a removed item, so a later item with that id starts clean", () => {
  const flags = newErrorFlags();
  leftField(flags, "price", BAD.price, ID);
  leftField(flags, "price", BAD.price, "i6");
  forgetPrice(flags, ID);
  assert.deepEqual(flags.price, { i6: true });
  assert.equal(shown(flags, "price", BAD.price), false);
  forgetPrice(flags, "i9"); // an id that was never flagged is not an error
  assert.deepEqual(flags.price, { i6: true });
});
