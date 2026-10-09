// The named example bills of qa.md. Built through the real actions, like the app builds them,
// so ids and nextId match what a person would get by tapping (S1 ends at nextId 8, D2 at 5).
import {
  newBill, addPerson, addItem, setPersonName, setItemName, setItemPriceText,
  toggleItemPerson, setMode, setSubtotalText, setServiceText, setSstText,
} from "../../src/core/bill.js";

/**
 * @param {{ mode?: string, names?: string[], subtotal?: string, service?: string, sst?: string,
 *           items?: { name?: string, price: string, who?: string[] }[] }} spec
 *   `names` replaces the default "Person 1", "Person 2" (at least two). `who` lists person ids in tap order.
 */
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

/** Freezes every nested object and array, so any write by the code under test throws. */
export function deepFreeze(value) {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    Object.values(value).forEach(deepFreeze);
  }
  return value;
}

const TRIO = ["Aisyah", "Ben", "Chen"];
const s1Items = () => [
  { name: "Nasi lemak ayam", price: "15.90", who: ["p1"] },
  { name: "Char kuey teow", price: "13.50", who: ["p2"] },
  { name: "Mee goreng mamak", price: "12.00", who: ["p3"] },
  { name: "Satay, 10 sticks", price: "18.00", who: ["p1", "p3"] },
];

export const S2 = buildBill({ names: TRIO, subtotal: "100.00" });
export const S1 = buildBill({ mode: "item", names: TRIO, items: s1Items() });
export const S5 = buildBill({
  mode: "item",
  names: TRIO,
  items: s1Items().map((item) => (item.name === "Mee goreng mamak" ? { ...item, who: [] } : item)),
});
export const E1 = buildBill({ names: ["A", "B", "C", "D"], subtotal: "87.65" });
export const E2 = buildBill({ names: TRIO, subtotal: "10.00", service: "0", sst: "0" });
export const E3 = buildBill({ subtotal: "50.00", service: "12.5", sst: "6.25" });
export const I2 = buildBill({
  mode: "item",
  names: TRIO,
  items: [
    { name: "X", price: "10.00", who: ["p2"] },
    { name: "Y", price: "5.01", who: ["p2", "p3"] },
  ],
});
export const I3 = buildBill({ mode: "item", names: TRIO, items: [{ price: "10.01", who: ["p3", "p1"] }] });
export const I4 = buildBill({
  mode: "item",
  names: TRIO,
  service: "0",
  sst: "0",
  items: [{ price: "0.10", who: ["p1", "p2", "p3"] }],
});

const TWELVE = Array.from({ length: 12 }, (_, index) => `Person ${index + 1}`);
export const MAX_E = buildBill({ names: TWELVE, subtotal: "99999.99", service: "30", sst: "20" });
export const MAX_I = buildBill({
  mode: "item",
  names: TWELVE,
  service: "30",
  sst: "20",
  items: Array.from({ length: 50 }, (_, k) => ({ price: "99999.99", who: [`p${(k % 12) + 1}`] })),
});

export const D1 = buildBill({ names: ["Ben", "Ben", "Chen"], subtotal: "100.00" });
export const D2 = buildBill({
  mode: "item",
  names: ["Ben", "Ben", "Chen"],
  items: [{ name: "Tea", price: "10.00", who: ["p2"] }],
});
