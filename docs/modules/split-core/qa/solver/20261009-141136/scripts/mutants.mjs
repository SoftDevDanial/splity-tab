// Mutants for the split-core code-review re-check solver round (WR-11 to WR-15). Each one changes source text
// in memory only (see preload.mjs), and runs against the FIXED tests. The reviewer's base mutants are reused
// where their anchor text still exists in the fixed code, and the ones whose anchor moved are redefined below.
import { MUTANTS as BASE } from "../../../code-review/20261009-134620/scripts/mutants.mjs";

export const MUTANTS = new Map(BASE);

const add = (id, desc, tests, edits) => MUTANTS.set(id, { id, desc, tests, edits });
const sub = (from, to) => (text) => {
  if (!text.includes(from)) throw new Error(`pattern not found: ${from}`);
  return text.replace(from, () => to);
};
const HYG = ["tests/hygiene.test.js"];
const HYG_TEST = "tests/hygiene.test.js";

// ---- WR-12: the trap lists are pinned ----
// The reviewer's N-G01..N-G24, N-M01..N-M14 and N-R1..N-R4 drop one entry each. This one drops the new globalThis trap.
add("N-G25", "narrowing: trap for global globalThis removed from TRAPPED_GLOBALS", HYG, { [HYG_TEST]: sub("let armed = false;",
  'TRAPPED_GLOBALS.splice(TRAPPED_GLOBALS.indexOf("globalThis"), 1);\nlet armed = false;') });
add("D1", "drift: a name is added to BANNED (the source scan) and not to any trap list", HYG,
  { [HYG_TEST]: sub("const BANNED = [\n", 'const BANNED = [\n  "structuredClone",\n') });
add("D2", "drift: the exact pin gets one more trap in TRAPPED_GLOBALS (a widening nobody pinned)", HYG,
  { [HYG_TEST]: sub("let armed = false;", 'TRAPPED_GLOBALS.push("structuredClone");\nlet armed = false;') });
// ---- WR-15(e): the reviewer's B3, B4 and B8 anchored on lines this round rewrote, so they are redefined ----
const ATTRIBUTION = 'fromCore = (new Error().stack ?? "").split("\\n").some((line) => line.includes(CORE_URL));';
add("B3", "stack attribution never finds a core frame (redefined for the try/finally in record)", HYG,
  { [HYG_TEST]: sub(ATTRIBUTION, "fromCore = false;") });
add("B4", "stack attribution counts every access, test code too (redefined)", HYG,
  { [HYG_TEST]: sub(ATTRIBUTION, "fromCore = true;") });
add("B8", "hits are not cleared between runs (redefined for the take-in-finally)", HYG,
  { [HYG_TEST]: sub("    found = hits.splice(0);\n", "    found = hits.slice();\n") });
add("L1", "the old leak: hits taken after the try, so a throwing body leaves them for the next run", HYG,
  { [HYG_TEST]: (text) => sub("return found;", "return hits.splice(0);")(sub("    found = hits.splice(0);\n", "")(text)) });
add("L2", "the old record: stackTraceLimit and the recording flag reset without finally", HYG, { [HYG_TEST]: sub(
  `  try {\n    Error.stackTraceLimit = 50;\n    ${ATTRIBUTION}\n  } finally {\n    Error.stackTraceLimit = limit;\n    recording = false;\n  }\n`,
  `  Error.stackTraceLimit = 50;\n  ${ATTRIBUTION}\n  Error.stackTraceLimit = limit;\n  recording = false;\n`) });
add("RS1","restore loop skipped when the body throws (restore moved out of finally, so it only runs on success)", HYG,
  { [HYG_TEST]: sub("  } finally {\n    armed = false;\n", "  } catch (error) {\n    armed = false;\n    throw error;\n  }\n  {\n    armed = false;\n") });
