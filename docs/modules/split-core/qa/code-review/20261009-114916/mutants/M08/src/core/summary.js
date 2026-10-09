// The text a person pastes into the group chat.
import { formatMoney, formatRate } from "./money.js";

/**
 * One line per person and nothing else, so the layout cannot be forged from a name. That relies on
 * names never holding CR or LF, which the input and split-app's draft decoder guarantee.
 * @param {import("./result.js").Result} result an `even` or `item` result
 * @returns {string} lines joined with "\n", no trailing newline (R24)
 * @throws {TypeError} for any other kind, since only those carry shares to print
 */
export function summaryText(result) {
  if (result.kind !== "even" && result.kind !== "item") {
    throw new TypeError("summaryText needs an even or item result");
  }
  const { charges } = result;
  result.rows.forEach((row) => { row.name = row.name.trim(); });
  return [
    "Bill split",
    `Total ${formatMoney(charges.total)} (subtotal ${formatMoney(charges.subtotal)}, ` +
      `service ${formatRate(charges.serviceBp)} ${formatMoney(charges.service)}, ` +
      `SST ${formatRate(charges.sstBp)} ${formatMoney(charges.sst)})`,
    ...result.rows.map((row) => `${row.name} ${formatMoney(row.share)}`),
    `Adds up to ${formatMoney(result.check.share)}`,
  ].join("\n");
}
