// The saved bill (C7, R25 to R28, R61): one draft in localStorage under DRAFT_KEY, written as version 2.
// localStorage is untrusted input (another page of the same origin can write it), so decodeDraft is an
// all-or-nothing gate. split-core shares untouched people and items by reference and treats any mode that
// is not "even" as by-item, so everything split-core relies on is checked here (D1 to D14), and the Bill is
// rebuilt as new objects from known fields only (D12), never copied from the parsed value.
// A version 1 draft, saved by 1.0, still loads, with the spare choice Top of the list (D14).
// Only the storage object passed in is touched, except getStorage, which reads window.localStorage. No function here throws.
import { LIMITS } from "./core/bill.js";

export const DRAFT_KEY = "split.draft";

const PERSON_ID = /^p([0-9]{1,10})$/;
const ITEM_ID = /^i([0-9]{1,10})$/;
const MAX_NEXT_ID = 1_000_000_000;
const REJECTED = Object.freeze({ ok: false });
// Grapheme clusters, because WebKit counts maxlength that way and Chromium counts UTF-16 units (D8).
const graphemes = new Intl.Segmenter(undefined, { granularity: "grapheme" });

const isObject = (value) => typeof value === "object" && value !== null && !Array.isArray(value);
const isString = (value) => typeof value === "string";

/** D8: at most `max` grapheme clusters, and no line break (a name is one line in the clipboard text). */
function nameFits(name, max) {
  return isString(name) && !/[\r\n]/.test(name) && [...graphemes.segment(name)].length <= max;
}

function readPerson(raw) {
  if (!isObject(raw) || !isString(raw.id) || !PERSON_ID.test(raw.id) || !nameFits(raw.name, LIMITS.personNameMax)) return null;
  return { id: raw.id, name: raw.name };
}

function readItem(raw, personIds) {
  if (!isObject(raw) || !isString(raw.id) || !ITEM_ID.test(raw.id)) return null;
  if (!nameFits(raw.name, LIMITS.itemNameMax) || !isString(raw.priceText)) return null;
  const { who } = raw;
  const known = Array.isArray(who) && who.every((id) => isString(id) && personIds.has(id));
  if (!known || new Set(who).size !== who.length) return null;
  return { id: raw.id, name: raw.name, priceText: raw.priceText, who: [...who] };
}

const hasDuplicates = (ids) => new Set(ids).size !== ids.length;
const idNumber = (id) => Number(id.slice(1));

/** D13: the stored spare choice when it is one of core R27's three for these people, else null. Keeps only the field its rule needs. */
function readSpare(raw, personIds) {
  if (!isObject(raw)) return null;
  if (raw.rule === "top") return { rule: "top" };
  if (raw.rule === "one") return personIds.has(raw.personId) ? { rule: "one", personId: raw.personId } : null;
  if (raw.rule !== "random") return null;
  const { order } = raw;
  const everyoneOnce = Array.isArray(order) && order.length === personIds.size
    && order.every((id) => personIds.has(id)) && !hasDuplicates(order);
  return everyoneOnce ? { rule: "random", order: [...order] } : null;
}

function decode(text) {
  const draft = JSON.parse(text); // D1
  if (!isObject(draft) || (draft.version !== 1 && draft.version !== 2) || !isObject(draft.bill)) return REJECTED; // D2, D3, D4
  const raw = draft.bill;
  if (raw.mode !== "even" && raw.mode !== "item") return REJECTED; // D5
  if (!Array.isArray(raw.people) || raw.people.length < LIMITS.minPeople || raw.people.length > LIMITS.maxPeople) return REJECTED;
  const people = raw.people.map(readPerson);
  if (people.includes(null) || hasDuplicates(people.map((person) => person.id))) return REJECTED; // D6
  if (!Array.isArray(raw.items) || raw.items.length > LIMITS.maxItems) return REJECTED;
  const personIds = new Set(people.map((person) => person.id));
  const items = raw.items.map((item) => readItem(item, personIds));
  if (items.includes(null) || hasDuplicates(items.map((item) => item.id))) return REJECTED; // D7
  if (![raw.subtotalText, raw.serviceText, raw.sstText].every(isString)) return REJECTED; // D9
  const highest = Math.max(...[...people, ...items].map((entry) => idNumber(entry.id)));
  const { nextId } = raw;
  if (!Number.isInteger(nextId) || nextId < 1 || nextId > MAX_NEXT_ID || nextId <= highest) return REJECTED; // D10
  const spare = draft.version === 1 ? { rule: "top" } : readSpare(raw.spare, personIds); // D14, D13
  if (spare === null) return REJECTED;
  return {
    ok: true,
    bill: {
      mode: raw.mode, people, subtotalText: raw.subtotalText, items,
      serviceText: raw.serviceText, sstText: raw.sstText, spare, nextId,
    },
  };
}

/** @returns {string} the text stored under DRAFT_KEY, always version 2 (R61) */
export function encodeDraft(bill) {
  return JSON.stringify({ version: 2, bill });
}

/** @param {string} text @returns {{ ok: true, bill: object } | { ok: false }} never throws */
export function decodeDraft(text) {
  try {
    return decode(text);
  } catch {
    return REJECTED;
  }
}

/** R28: reading window.localStorage can throw (blocked cookies, a sandboxed frame). Then there is no storage. */
export function getStorage() {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

/**
 * "failed" when there is no storage or getItem throws, so boot can tell a failed read from an empty store (R46).
 * @returns {{ state: "failed" } | { state: "none" } | { state: "ok", bill: object } | { state: "unreadable" }}
 */
export function loadDraft(storage) {
  if (storage === null) return { state: "failed" };
  let text;
  try {
    text = storage.getItem(DRAFT_KEY);
  } catch {
    return { state: "failed" };
  }
  if (text === null) return { state: "none" };
  const decoded = decodeDraft(text);
  return decoded.ok ? { state: "ok", bill: decoded.bill } : { state: "unreadable" };
}

/** @returns {boolean} false when there is no storage or the write failed (quota, security). The caller carries on. */
export function saveDraft(storage, bill) {
  if (storage === null) return false;
  try {
    storage.setItem(DRAFT_KEY, encodeDraft(bill));
    return true;
  } catch {
    return false;
  }
}
