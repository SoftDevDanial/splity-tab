// Security audit probe helpers (split-core). Read-only on src/. Bills are built through the real
// actions, the way split-app would build them. Special characters are written as code points only,
// so no raw control or line-break character sits in any probe file.
import {
  newBill, addPerson, addItem, setPersonName, setItemName, setItemPriceText,
  toggleItemPerson, setMode, setSubtotalText, setServiceText, setSstText,
} from "../../../../../../../src/core/bill.js";

export const ch = (...cps) => String.fromCodePoint(...cps);

export function buildBill({ mode = "even", names, subtotal = "", service = "10", sst = "6", items = [] }) {
  let bill = newBill();
  if (names !== undefined) {
    while (bill.people.length < names.length) bill = addPerson(bill);
    names.forEach((name, index) => {
      bill = setPersonName(bill, bill.people[index].id, name);
    });
  }
  for (const spec of items) {
    bill = addItem(bill);
    const id = bill.items[bill.items.length - 1].id;
    bill = setItemName(bill, id, spec.name ?? "");
    bill = setItemPriceText(bill, id, spec.price);
    for (const personId of spec.who ?? []) bill = toggleItemPerson(bill, id, personId);
  }
  bill = setSubtotalText(bill, subtotal);
  bill = setServiceText(bill, service);
  bill = setSstText(bill, sst);
  return setMode(bill, mode);
}

export const TRIO = ["Aisyah", "Ben", "Chen"];
export const s1Items = () => [
  { name: "Nasi lemak ayam", price: "15.90", who: ["p1"] },
  { name: "Char kuey teow", price: "13.50", who: ["p2"] },
  { name: "Mee goreng mamak", price: "12.00", who: ["p3"] },
  { name: "Satay, 10 sticks", price: "18.00", who: ["p1", "p3"] },
];
export const S2 = () => buildBill({ names: TRIO, subtotal: "100.00" });
export const S1 = () => buildBill({ mode: "item", names: TRIO, items: s1Items() });

export function deepFreeze(value) {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    Object.values(value).forEach(deepFreeze);
  }
  return value;
}

/** Printable form: every character outside printable ASCII becomes <U+XXXX>. */
export function show(text) {
  return String(text).replace(/[^\x20-\x7e]/gu, (c) => `<U+${c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}>`);
}

/** mulberry32, the same family the suite uses, re-implemented here so the probe has its own seed. */
export function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export const randInt = (r, lo, hi) => lo + Math.floor(r() * (hi - lo + 1));
