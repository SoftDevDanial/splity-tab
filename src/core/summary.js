// The text a person pastes into the group chat.
import { formatMoney, formatRate } from "./money.js";
import { NAME_CONTROLS } from "./bill.js";

/**
 * One line per person and nothing else. Each character of a name that `NAME_CONTROLS` matches prints as one
 * space (R24), so a name cannot forge a line (a fake "Adds up to", say), cut the text short or reorder
 * its row. The app removes the same class from names (R35), and this does not rely on that.
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
    ...result.rows.map((row) => `${row.name.replace(NAME_CONTROLS, " ")} ${formatMoney(row.share)}`),
    `Adds up to ${formatMoney(result.check.share)}`,
  ].join("\n");
}
