// The saved bill (C7, R25 to R28): one draft in localStorage under DRAFT_KEY.
// localStorage is untrusted input (another page of the same origin can write it), so decodeDraft is an
// all-or-nothing gate. split-core shares untouched people and items by reference and treats any mode that
// is not "even" as by-item, so everything split-core relies on is checked here (D1 to D12), and the Bill is
// rebuilt as new objects from known fields only (D12), never copied from the parsed value.
// Only the storage object passed in is touched, and no function here throws.
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

function decode(text) {
  const draft = JSON.parse(text); // D1
  if (!isObject(draft) || draft.version !== 1 || !isObject(draft.bill)) return REJECTED; // D2, D3, D4
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
  return {
    ok: true,
    bill: {
      mode: raw.mode, people, subtotalText: raw.subtotalText, items,
      serviceText: raw.serviceText, sstText: raw.sstText, nextId,
    },
  };
}

/** @returns {string} the text stored under DRAFT_KEY */
export function encodeDraft(bill) {
  return JSON.stringify({ version: 1, bill });
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

/** @returns {{ state: "none" } | { state: "ok", bill: object } | { state: "unreadable" }} */
export function loadDraft(storage) {
  if (storage === null) return { state: "none" };
  let text;
  try {
    text = storage.getItem(DRAFT_KEY);
  } catch {
    return { state: "none" };
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
