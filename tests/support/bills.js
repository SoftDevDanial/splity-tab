// The named example bills of qa.md. Built through the real actions, like the app builds them,
// so ids and nextId match what a person would get by tapping (S1 ends at nextId 8, D2 at 5).
// Every fixture is deep-frozen, so a function that writes to its input throws in each test that uses
// one (R16), instead of silently changing the fixture for the tests after it.
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

/** A copy of `bill` with its spare choice set directly, so a test names the choice without the choose actions. */
export const withSpare = (bill, spare) => deepFreeze({ ...structuredClone(bill), spare });

const fixture = (spec) => deepFreeze(buildBill(spec));

const TRIO = ["Aisyah", "Ben", "Chen"];
const s1Items = () => [
  { name: "Nasi lemak ayam", price: "15.90", who: ["p1"] },
  { name: "Char kuey teow", price: "13.50", who: ["p2"] },
  { name: "Mee goreng mamak", price: "12.00", who: ["p3"] },
  { name: "Satay, 10 sticks", price: "18.00", who: ["p1", "p3"] },
];

export const S2 = fixture({ names: TRIO, subtotal: "100.00" });
export const S1 = fixture({ mode: "item", names: TRIO, items: s1Items() });
// S1 plus one RM 964.50 item for Aisyah, so the bill passes RM 1,000 (bill-large golden, thousands comma).
export const W1 = fixture({
  mode: "item",
  names: TRIO,
  items: [...s1Items(), { price: "964.50", who: ["p1"] }],
});
export const S5 = fixture({
  mode: "item",
  names: TRIO,
  items: s1Items().map((item) => (item.name === "Mee goreng mamak" ? { ...item, who: [] } : item)),
});
export const E1 = fixture({ names: ["A", "B", "C", "D"], subtotal: "87.65" });
export const E2 = fixture({ names: TRIO, subtotal: "10.00", service: "0", sst: "0" });
export const E3 = fixture({ subtotal: "50.00", service: "12.5", sst: "6.25" });
export const I2 = fixture({
  mode: "item",
  names: TRIO,
  items: [
    { name: "X", price: "10.00", who: ["p2"] },
    { name: "Y", price: "5.01", who: ["p2", "p3"] },
  ],
});
export const I3 = fixture({ mode: "item", names: TRIO, items: [{ price: "10.01", who: ["p3", "p1"] }] });
export const I4 = fixture({
  mode: "item",
  names: TRIO,
  service: "0",
  sst: "0",
  items: [{ price: "0.10", who: ["p1", "p2", "p3"] }],
});

const TWELVE = Array.from({ length: 12 }, (_, index) => `Person ${index + 1}`);
export const MAX_E = fixture({ names: TWELVE, subtotal: "99999.99", service: "30", sst: "20" });
export const MAX_I = fixture({
  mode: "item",
  names: TWELVE,
  service: "30",
  sst: "20",
  items: Array.from({ length: 50 }, (_, k) => ({ price: "99999.99", who: [`p${(k % 12) + 1}`] })),
});

export const D1 = fixture({ names: ["Ben", "Ben", "Chen"], subtotal: "100.00" });
export const D2 = fixture({
  mode: "item",
  names: ["Ben", "Ben", "Chen"],
  items: [{ name: "Tea", price: "10.00", who: ["p2"] }],
});
