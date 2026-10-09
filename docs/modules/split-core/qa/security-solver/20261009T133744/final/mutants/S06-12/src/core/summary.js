// The text a person pastes into the group chat.
import { formatMoney, formatRate } from "./money.js";

// Every control character (Cc: all C0 and C1 controls, so LF, CR, VT, FF, NEL, NUL, ESC, FS, GS and RS),
// the line and paragraph separators LS and PS, and the bidi controls (RLO and the like). Some reader ends
// a line or the whole text at the first two kinds (NUL ends a C-string clipboard, FS to RS end a line for
// Python), and a bidi control reverses how the rest of its row reads. The text input strips only CR and LF.
const CONTROLS = /[\n\r\u000B\u000C\u0085\x00\x1C\x1D\x1E\x1B\u{2028}\u{2029}\p{Bidi_Control}]/gu;

/**
 * One line per person and nothing else. A name cannot forge a line (a fake "Adds up to", say), cut the
 * text short or reorder its row, because each character of it in [\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]
 * (`CONTROLS`) prints as one space (R24). Space separators such as NBSP are kept.
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
