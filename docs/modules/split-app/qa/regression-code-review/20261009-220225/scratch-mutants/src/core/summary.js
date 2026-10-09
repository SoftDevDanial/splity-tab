// The text a person pastes into the group chat.
import { formatMoney, formatRate } from "./money.js";

// The class of characters that must not reach a row as typed. Some reader ends a line or the whole text at
// a control or a line separator (NUL ends a C-string clipboard, FS to RS end a line for Python), and a bidi
// control (RLO and the like) reverses how the rest of its row reads. The text input strips only CR and LF.
// Space separators such as NBSP are kept.
const CONTROLS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/gu;

/**
 * One line per person and nothing else. Each character of a name that `CONTROLS` matches prints as one
 * space (R24), so a name cannot forge a line (a fake "Adds up to", say), cut the text short or reorder
 * its row.
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
    ...result.rows.map((row) => `${row.name.replace(CONTROLS, " ")} ${formatMoney(row.share)}`),
    `Adds up to ${formatMoney(result.check.share)}`,
  ].join("\n");
}
