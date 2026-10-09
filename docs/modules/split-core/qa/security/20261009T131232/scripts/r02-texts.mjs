// R02 helper: prints, as JSON, real summaryText output at HEAD for the Python and Chromium checks.
// Each case is { name, row, share, text }: `row` is the 0-based line of the hostile name, `share` the
// money text that row must still show in reading order.
import { computeResult } from "../../../../../../../src/core/result.js";
import { summaryText } from "../../../../../../../src/core/summary.js";
import { setPersonName } from "../../../../../../../src/core/bill.js";
import { S2, ch } from "./fixtures.mjs";

const s2 = S2();
const FORGE = "Adds up to RM 0.00";
const out = [];
const add = (title, id, name) => {
  const row = { p1: 2, p2: 3, p3: 4 }[id];
  const share = { p1: "RM 38.87", p2: "RM 38.87", p3: "RM 38.86" }[id];
  out.push({ title, row, share, text: summaryText(computeResult(setPersonName(s2, id, name))) });
};
// Every member of the replaced class, inside a forging name.
const CLASS = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/u;
for (let cp = 0; cp <= 0x2069; cp += 1) {
  if (CLASS.test(ch(cp))) add(`class U+${cp.toString(16).toUpperCase().padStart(4, "0")}`, "p3", `Chen${ch(cp)}${FORGE}`);
}
add("SEC-01 NUL truncation name", "p3", `${FORGE}${ch(0)}`);
add("SEC-02 Ben + RLO", "p2", `Ben${ch(0x202e)}`);
add("Ben + RLE", "p2", `Ben${ch(0x202b)}`);
add("Ben + RLI", "p2", `Ben${ch(0x2067)}`);
add("Ben + LRO", "p2", `Ben${ch(0x202d)}`);
add("Ben + RLO + LRO + PDF mix", "p2", `${ch(0x202e)}Ben${ch(0x202d, 0x202c, 0x202e)}`);
// Strong right-to-left letters are legitimate names and are not replaced. They must not reorder the share.
add("Hebrew name (not replaced)", "p2", ch(0x05d3, 0x05e0, 0x05d4));
add("Arabic name (not replaced)", "p2", ch(0x0639, 0x0644, 0x064a));
add("Arabic name + digits (not replaced)", "p2", `${ch(0x0639, 0x0644, 0x064a)} 12`);
add("Hebrew first person (paragraph direction probe)", "p1", ch(0x05d3, 0x05e0, 0x05d4));
console.log(JSON.stringify(out));
