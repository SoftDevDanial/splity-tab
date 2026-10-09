// The text a person pastes into the group chat.
import { formatMoney, formatRate } from "./money.js";

// The mandatory breaks of Unicode line breaking (UAX #14): LF, CR, VT, FF, NEL, LS and PS. The text
// input strips only CR and LF, so the others can reach a name.
const LINE_BREAKS = /[\n\r\u000C\u0085\u{2028}\u{2029}]/gu;

/**
 * One line per person and nothing else. A name cannot forge a line (a fake "Adds up to", say),
 * because every line-breaking character in it prints as one space (R24).
 * @param {import("./result.js").Result} result an `even` or `item` result
 * @returns {string} lines joined with "\n", no trailing newline (R24)
 * @throws {TypeError} for any other kind, since only those carry shares to print
 */
export function summaryText(result) {
  if (result.kind !== "even" && result.kind !== "item") {
    throw new TypeError("summaryText needs an even or item result");
  }
  const { charges } = result;
  return [
    "Bill split",
    `Total ${formatMoney(charges.total)} (subtotal ${formatMoney(charges.subtotal)}, ` +
      `service ${formatRate(charges.serviceBp)} ${formatMoney(charges.service)}, ` +
      `SST ${formatRate(charges.sstBp)} ${formatMoney(charges.sst)})`,
    ...result.rows.map((row) => `${row.name.replace(LINE_BREAKS, " ")} ${formatMoney(row.share)}`),
    `Adds up to ${formatMoney(result.check.share)}`,
  ].join("\n");
}
