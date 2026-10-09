// Money and rate text to and from integers. Money is whole cents, rates are basis points
// (hundredths of a percent). No float is involved, so "1.15" is exactly 115 (a float read gives 114).

/** @typedef {{ ok: true, cents: number } | { ok: false, empty: boolean }} AmountResult */
/** @typedef {{ ok: true, bp: number } | { ok: false, empty: boolean }} RateResult */

export const AMOUNT_MIN_CENTS = 1;
export const AMOUNT_MAX_CENTS = 9999999;

const EMPTY = Object.freeze({ ok: false, empty: true });
const INVALID = Object.freeze({ ok: false, empty: false });

// No nested quantifier, so matching stays linear in the input length (no catastrophic backtracking).
const DECIMAL_TEXT = /^([0-9]+)(?:\.([0-9]{0,2}))?$/;

/** Whole ringgit of cents, or whole percent of basis points. Remainder first, so the division is exact. */
function wholePart(hundredths) {
  return (hundredths - (hundredths % 100)) / 100;
}

/**
 * Shared reader for R1 and R3, so amounts and rates cannot drift apart on the grammar or the ceiling.
 * @param {string} text
 * @param {number} maxHundredths the caller's inclusive ceiling: AMOUNT_MAX_CENTS, or maxPercent x 100
 * @returns {{ ok: true, hundredths: number } | { ok: false, empty: boolean }} INVALID above the ceiling
 */
function readHundredths(text, maxHundredths) {
  const trimmed = text.trim();
  if (trimmed === "") return EMPTY;
  const match = DECIMAL_TEXT.exec(trimmed);
  if (match === null) return INVALID;
  const whole = match[1].replace(/^0+/, "");
  // The digit cap is the digit count of the ceiling's whole part. A longer whole part (leading zeros
  // dropped) is above the ceiling, so it is refused before Number() sees it, and a 400-digit string is
  // never converted. The range check below decides the rest.
  if (whole.length > String(wholePart(maxHundredths)).length) return INVALID;
  const fraction = (match[2] ?? "").padEnd(2, "0");
  const hundredths = Number(whole === "" ? "0" : whole) * 100 + Number(fraction);
  return hundredths <= maxHundredths ? { ok: true, hundredths } : INVALID;
}

/**
 * Reads typed money (R1). Use on read, never on write: the bill keeps the raw text.
 * @param {string} text e.g. "12.50". Surrounding white space is ignored.
 * @returns {AmountResult} cents when 0.01 to 99999.99, else `empty` tells blank from bad.
 */
export function parseAmount(text) {
  const read = readHundredths(text, AMOUNT_MAX_CENTS);
  if (!read.ok) return read;
  return read.hundredths >= AMOUNT_MIN_CENTS ? { ok: true, cents: read.hundredths } : INVALID;
}

/**
 * Reads a typed charge rate (R3). Zero is valid because it switches the charge off.
 * @param {string} text e.g. "6.25"
 * @param {number} maxPercent inclusive ceiling in whole percent (30 for service, 20 for SST)
 * @returns {RateResult} basis points, or `empty` for blank text
 */
export function parseRate(text, maxPercent) {
  const read = readHundredths(text, maxPercent * 100);
  return read.ok ? { ok: true, bp: read.hundredths } : read;
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

let r04Hits = 0; const r04Rate = r04Hits++ / process.uptime();
