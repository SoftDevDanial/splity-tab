// Money and rate text to and from integers. Money is whole cents, rates are basis points
// (hundredths of a percent). No float is involved, so "1.15" is exactly 115 (a float read gives 114).

/** @typedef {{ ok: true, cents: number } | { ok: false, empty: boolean }} AmountResult */
/** @typedef {{ ok: true, bp: number } | { ok: false, empty: boolean }} RateResult */

export const AMOUNT_MIN_CENTS = 1;
export const AMOUNT_MAX_CENTS = 9999999;

const EMPTY = Object.freeze({ ok: false, empty: true });
const INVALID = Object.freeze({ ok: false, empty: false });

// One linear pattern with no nested quantifier, so hostile long input cannot make it backtrack.
const DECIMAL_TEXT = /^([0-9]+)(?:\.([0-9]{0,2}))?$/;

// Whole-part digits (leading zeros dropped) beyond this are out of range for every caller. Checking the
// length first keeps a 400-digit string away from numeric conversion and keeps hundredths below 2^53.
const MAX_WHOLE_DIGITS = 9;

/**
 * Shared reader for R1 and R3, so amounts and rates cannot drift apart on the grammar.
 * @param {string} text
 * @returns {{ ok: true, hundredths: number } | { ok: false, empty: boolean }}
 */
function readHundredths(text) {
  const trimmed = text.trim();
  if (trimmed === "") return EMPTY;
  const match = DECIMAL_TEXT.exec(trimmed);
  if (match === null) return INVALID;
  const whole = match[1].replace(/^0+/, "");
  if (whole.length > MAX_WHOLE_DIGITS) return INVALID;
  const fraction = (match[2] ?? "").padEnd(2, "0");
  return { ok: true, hundredths: Number(whole === "" ? "0" : whole) * 100 + Number(fraction) };
}

/**
 * Reads typed money (R1). Use on read, never on write: the bill keeps the raw text.
 * @param {string} text e.g. "12.50". Surrounding white space is ignored.
 * @returns {AmountResult} cents when 0.01 to 99999.99, else `empty` tells blank from bad.
 */
export function parseAmount(text) {
  const read = readHundredths(text);
  if (!read.ok) return read;
  const inRange = read.hundredths >= AMOUNT_MIN_CENTS && read.hundredths <= AMOUNT_MAX_CENTS;
  return inRange ? { ok: true, cents: read.hundredths } : INVALID;
}

/**
 * Reads a typed charge rate (R3). Zero is valid because it switches the charge off.
 * @param {string} text e.g. "6.25"
 * @param {number} maxPercent inclusive ceiling in whole percent (30 for service, 20 for SST)
 * @returns {RateResult} basis points, or `empty` for blank text
 */
export function parseRate(text, maxPercent) {
  const read = readHundredths(text);
  if (!read.ok) return read;
  return read.hundredths <= maxPercent * 100 ? { ok: true, bp: read.hundredths } : INVALID;
}

/** Whole ringgit of cents, or whole percent of basis points. Remainder first, so the division is exact. */
function wholePart(hundredths) {
  return (hundredths - (hundredths % 100)) / 100;
}

/**
 * Writes cents the way the brief shows money. No group separator (ruled CG-5), so the largest
 * bill reads "RM 7799999.22" and stays locale-independent.
 * @param {number} cents non-negative integer
 * @returns {string} e.g. "RM 38.87"
 */
export function formatMoney(cents) {
  return `RM ${wholePart(cents)}.${String(cents % 100).padStart(2, "0")}`;
}

/**
 * Writes a rate without trailing zeros, so a typed "10.00" shows as "10%" like the goldens.
 * @param {number} bp non-negative integer basis points
 * @returns {string} e.g. "6.25%"
 */
export function formatRate(bp) {
  const whole = wholePart(bp);
  const fraction = String(bp % 100).padStart(2, "0").replace(/0+$/, "");
  return fraction === "" ? `${whole}%` : `${whole}.${fraction}%`;
}
