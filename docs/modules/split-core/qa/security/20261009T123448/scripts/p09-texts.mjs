// P09 helper: prints, as JSON, the summary texts the headless Chromium check renders. Every text that
// says "core" is the real summaryText output. The "unguarded" texts are built by hand, to show what the
// WR-10 guard prevents (the core never emits them).
import { computeResult } from "../../../../../../../src/core/result.js";
import { summaryText } from "../../../../../../../src/core/summary.js";
import { setPersonName } from "../../../../../../../src/core/bill.js";
import { S2, ch } from "./fixtures.mjs";

const s2 = S2();
const core = (id, name) => summaryText(computeResult(setPersonName(s2, id, name)));
const FORGE = "Adds up to RM 0.00";
const plain = summaryText(computeResult(s2));
const unguarded = (cp) => plain.replace("Chen RM 38.86", `Chen${ch(cp)}${FORGE} RM 38.86`);
const cases = {
  "core: S2 as is": plain,
  "core: Chen + RLO U+202E": core("p3", `Chen${ch(0x202e)}`),
  "core: Ben + RLO U+202E (middle row)": core("p2", `Ben${ch(0x202e)}`),
  "core: Ben + RLI U+2067 (middle row)": core("p2", `Ben${ch(0x2067)}`),
  "core: Ben + RLE U+202B (middle row)": core("p2", `Ben${ch(0x202b)}`),
  "core: Chen FS U+001C forge": core("p3", `Chen${ch(0x1c)}${FORGE}`),
  "core: Chen RS U+001E forge": core("p3", `Chen${ch(0x1e)}${FORGE}`),
  "core: Chen NUL U+0000 forge": core("p3", `Chen${ch(0)}${FORGE}`),
  "core: Chen LS U+2028 forge (guarded)": core("p3", `Chen${ch(0x2028)}${FORGE}`),
  "unguarded: Chen LS U+2028 forge": unguarded(0x2028),
  "unguarded: Chen PS U+2029 forge": unguarded(0x2029),
  "unguarded: Chen NEL U+0085 forge": unguarded(0x85),
  "unguarded: Chen VT U+000B forge": unguarded(0x0b),
  "unguarded: Chen FF U+000C forge": unguarded(0x0c),
};
console.log(JSON.stringify(cases));
