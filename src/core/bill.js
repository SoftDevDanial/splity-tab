// Bill state rules. Every action takes a Bill and returns a new one, never editing arrays in place,
// so the browser shell can keep the previous bill as is and never edits state itself.
// Text fields are stored exactly as typed. Parsing happens on read (see result.js).
// An unknown id, or a move past a limit, returns the same bill object so callers can skip a re-render.
// The Bill and any person, item or spare choice an action changes are rebuilt from known fields, never
// spread, so no stray or __proto__ key is copied into what an action builds. Untouched people, items and
// spare choice are shared by reference, so cleaning a bill parsed from JSON is split-app's draft decoder's job.

/** @typedef {"even" | "item"} Mode */
/** @typedef {{ id: string, name: string }} Person */
/** @typedef {{ id: string, name: string, priceText: string, who: string[] }} Item */
/** @typedef {{ rule: "top" } | { rule: "one", personId: string } | { rule: "random", order: string[] }} Spare */
/**
 * @typedef {{
 *   mode: Mode, people: Person[], subtotalText: string, items: Item[],
 *   serviceText: string, sstText: string, spare: Spare, nextId: number
 * }} Bill
 */

/** The name maxima are enforced by split-app (maxlength, draft decoder), not by these actions. */
export const LIMITS = Object.freeze({
  minPeople: 2, maxPeople: 12, maxItems: 50,
  personNameMax: 20, itemNameMax: 40,
  serviceMaxPercent: 30, sstMaxPercent: 20,
});

// The Bill fields in Bill order. newBill is the one list that core's copies read (billWith here, and withSpare in
// spare.js, which reads the same keys because the Contracts keep billWith private). The Bill typedef above and
// split-app's decoder (decode in draft.js, D12) list the fields too, so a new field goes in all three.
const BILL_FIELDS = Object.keys(newBill());

/** The bill with `changes` applied, built from BILL_FIELDS only, so no action can forget a field when copying. */
function billWith(bill, changes) {
  return Object.fromEntries(BILL_FIELDS.map((field) => [field, changes[field] ?? bill[field]]));
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

/** @returns {Bill} the starting bill (R10): two people, even mode, 10% service, 6% SST, Top of the list */
export function newBill() {
  return {
    mode: "even",
    people: [{ id: "p1", name: "Person 1" }, { id: "p2", name: "Person 2" }],
    subtotalText: "",
    items: [],
    serviceText: "10",
    sstText: "6",
    spare: { rule: "top" },
    nextId: 3,
  };
}

// The two keep R27 true when the people change: a drawn order holds every person once, and a chosen
// person must still be on the bill. The choice is rebuilt from known fields, never spread, like a person.
function spareWith(spare, personId) {
  return spare.rule === "random" ? { rule: "random", order: [...spare.order, personId] } : spare;
}

function spareWithout(spare, personId) {
  if (spare.rule === "random") return { rule: "random", order: spare.order.filter((id) => id !== personId) };
  return spare.rule === "one" && spare.personId === personId ? { rule: "top" } : spare;
}

/** Adds an unnamed person (R11). The empty name shows as "Person N" through personLabel (ruled CG-1). */
export function addPerson(bill) {
  if (bill.people.length >= LIMITS.maxPeople) return bill;
  const person = { id: `p${bill.nextId}`, name: "" };
  return billWith(bill, {
    people: [...bill.people, person],
    spare: spareWith(bill.spare, person.id),
    nextId: bill.nextId + 1,
  });
}

/**
 * Removes a person and every tap of theirs (R12), so no item keeps an id that is gone, and takes them
 * out of the spare choice (R27).
 */
export function removePerson(bill, personId) {
  const known = bill.people.some((person) => person.id === personId);
  if (!known || bill.people.length <= LIMITS.minPeople) return bill;
  return billWith(bill, {
    people: bill.people.filter((person) => person.id !== personId),
    items: bill.items.map((item) => itemWith(item, { who: item.who.filter((id) => id !== personId) })),
    spare: spareWithout(bill.spare, personId),
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

/**
 * The people who can be chosen to take spare sen (R28). A person on no item has a split of 0 under every
 * rule, so in by-item mode they cannot take one. Written once here because result.js (the One person
 * fallback) and spare.js both need it.
 * @param {Bill} bill
 * @returns {string[]} person ids in list order
 */
export function sparePeople(bill) {
  const everyone = bill.people.map((person) => person.id);
  if (bill.mode === "even") return everyone;
  const onAnItem = new Set(bill.items.flatMap((item) => item.who));
  return everyone.filter((id) => onAnItem.has(id));
}

// The characters no name keeps (R35) and the summary prints as a space (R24), which are the C0 and C1 controls, the
// line and paragraph separators and the bidi controls. Some reader ends a line or the whole text at a control or a
// separator (NUL ends a C-string clipboard, FS to RS end a line for Python), and a bidi control reverses how the rest
// of its line reads. Space separators such as NBSP are not in it. Written once, so the names on screen and the copied
// summary cannot disagree. Read only through String.prototype.replace, which starts at 0 on every call, so the g flag
// carries no state from one caller to the next.
export const NAME_CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/gu;

/**
 * A name with every character of NAME_CONTROLS deleted and every other one kept in order (R35). split-app calls it at
 * its name inputs and in its draft decoder (app R62). No action here calls it, they store a name as given (R15).
 * @param {string} text
 * @returns {string} the text without the class, "" when it held nothing else
 */
export function plainName(text) {
  return text.replace(NAME_CONTROLS, "");
}
