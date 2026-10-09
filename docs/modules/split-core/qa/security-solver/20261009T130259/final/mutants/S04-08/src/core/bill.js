// Bill state rules. Every action takes a Bill and returns a new one, never editing arrays in place,
// so the browser shell can keep the previous bill as is and never edits state itself.
// Text fields are stored exactly as typed. Parsing happens on read (see result.js).
// An unknown id, or a move past a limit, returns the same bill object so callers can skip a re-render.
// The Bill and any person or item an action changes are rebuilt from known fields, never spread, so no
// stray or __proto__ key is copied into what an action builds. Untouched people and items are shared by
// reference, so cleaning a bill parsed from JSON is split-app's draft decoder's job.

/** @typedef {"even" | "item"} Mode */
/** @typedef {{ id: string, name: string }} Person */
/** @typedef {{ id: string, name: string, priceText: string, who: string[] }} Item */
/**
 * @typedef {{
 *   mode: Mode, people: Person[], subtotalText: string, items: Item[],
 *   serviceText: string, sstText: string, nextId: number
 * }} Bill
 */

/** The name maxima are enforced by split-app (maxlength, draft decoder), not by these actions. */
export const LIMITS = Object.freeze({
  minPeople: 2, maxPeople: 12, maxItems: 50,
  personNameMax: 20, itemNameMax: 40,
  serviceMaxPercent: 30, sstMaxPercent: 20,
});

/** One place that lists the Bill fields, so no action can forget one when copying. */
function billWith(bill, changes) {
  return {
    mode: changes.mode ?? bill.mode,
    people: changes.people ?? bill.people,
    subtotalText: changes.subtotalText ?? bill.subtotalText,
    items: changes.items ?? bill.items,
    serviceText: changes.serviceText ?? bill.serviceText,
    sstText: changes.sstText ?? bill.sstText,
    nextId: changes.nextId ?? bill.nextId,
  };
}

function personWith(person, changes) {
  return { id: person.id, name: changes.name ?? person.name };
}

function itemWith(item, changes) {
  return {
    id: item.id,
    name: changes.name ?? item.name,
    priceText: changes.priceText ?? item.priceText,
    who: changes.who ?? item.who,
  };
}

/** @returns {Bill} the starting bill (R10): two people, even mode, 10% service and 6% SST */
export function newBill() {
  return {
    mode: "even",
    people: [{ id: "p1", name: "Person 1" }, { id: "p2", name: "Person 2" }],
    subtotalText: "",
    items: [],
    serviceText: "10",
    sstText: "6",
    nextId: 3,
  };
}

/** Adds an unnamed person (R11). The empty name shows as "Person N" through personLabel (ruled CG-1). */
export function addPerson(bill) {
  if (bill.people.length >= LIMITS.maxPeople) return bill;
  const person = { id: `p${bill.nextId}`, name: "" };
  return billWith(bill, { people: [...bill.people, person], nextId: bill.nextId + 1 });
}

/** Removes a person and every tap of theirs (R12), so no item keeps an id that is gone. */
export function removePerson(bill, personId) {
  const known = bill.people.some((person) => person.id === personId);
  if (!known || bill.people.length <= LIMITS.minPeople) return bill;
  return billWith(bill, {
    people: bill.people.filter((person) => person.id !== personId),
    items: bill.items.map((item) => itemWith(item, { who: item.who.filter((id) => id !== personId) })),
  });
}

export function setPersonName(bill, personId, name) {
  if (!bill.people.some((person) => person.id === personId)) return bill;
  return billWith(bill, {
    people: bill.people.map((person) => (person.id === personId ? personWith(person, { name }) : person)),
  });
}

/** Adds an empty, unassigned item (R13). */
export function addItem(bill) {
  if (bill.items.length >= LIMITS.maxItems) return bill;
  const item = { id: `i${bill.nextId}`, name: "", priceText: "", who: [] };
  return billWith(bill, { items: [...bill.items, item], nextId: bill.nextId + 1 });
}

export function removeItem(bill, itemId) {
  if (!bill.items.some((item) => item.id === itemId)) return bill;
  return billWith(bill, { items: bill.items.filter((item) => item.id !== itemId) });
}

/**
 * Shared by the item actions: an unknown item id returns the same bill.
 * @param {(item: Item) => Partial<Item>} changesFor the new field values, given the current item
 */
function changeItem(bill, itemId, changesFor) {
  if (!bill.items.some((item) => item.id === itemId)) return bill;
  return billWith(bill, {
    items: bill.items.map((item) => (item.id === itemId ? itemWith(item, changesFor(item)) : item)),
  });
}

export function setItemName(bill, itemId, name) {
  return changeItem(bill, itemId, () => ({ name }));
}

export function setItemPriceText(bill, itemId, text) {
  return changeItem(bill, itemId, () => ({ priceText: text }));
}

/** Taps a person on or off an item (R14). Ids are addressed, never names (R26). */
export function toggleItemPerson(bill, itemId, personId) {
  if (!bill.people.some((person) => person.id === personId)) return bill;
  return changeItem(bill, itemId, (item) => ({
    who: item.who.includes(personId) ? item.who.filter((id) => id !== personId) : [...item.who, personId],
  }));
}

export function setSubtotalText(bill, text) {
  return billWith(bill, { subtotalText: text });
}

export function setServiceText(bill, text) {
  return billWith(bill, { serviceText: text });
}

export function setSstText(bill, text) {
  return billWith(bill, { sstText: text });
}

/** Changes only `mode`, so subtotal and items both survive any number of switches (R15). */
export function setMode(bill, mode) {
  if (mode !== "even" && mode !== "item") return bill;
  return billWith(bill, { mode });
}

/** The label follows the list position, so it renumbers after a removal (R17). */
function labelOf(name, fallbackPrefix, index) {
  const trimmed = name.trim();
  return trimmed === "" ? `${fallbackPrefix} ${index + 1}` : trimmed;
}

/**
 * @param {Person} person
 * @param {number} index 0-based position in the current list
 * @returns {string} trimmed name, or "Person N" when blank
 */
export function personLabel(person, index) {
  return labelOf(person.name, "Person", index);
}

/**
 * @param {Item} item
 * @param {number} index 0-based position in the current list
 * @returns {string} trimmed name, or "Item N" when blank
 */
export function itemLabel(item, index) {
  return labelOf(item.name, "Item", index);
}

const pick = () => crypto.getRandomValues(new Uint32Array(1))[0];
