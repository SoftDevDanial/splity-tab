// The text a person pastes into the group chat.
import { formatMoney, formatRate } from "./money.js";

// Every control character (Cc: all C0 and C1 controls, so LF, CR, VT, FF, NEL, NUL, ESC, FS, GS and RS)
// plus the line and paragraph separators LS and PS. Some reader ends a line or the whole text at each
// one (NUL ends a C-string clipboard, FS to RS end a line for Python). The text input strips only CR and LF.
const CONTROLS = /(?!\x1C)[\p{Cc}\p{Zl}\p{Zp}]/gu;

/**
 * One line per person and nothing else. A name cannot forge a line (a fake "Adds up to", say) or cut
 * the text short, because every control character or separator in it prints as one space (R24).
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
