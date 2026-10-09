// What the surviving mutants P01, P02 and P03 do to a name that holds more than one replaceable character.
// Run with the mutation preload: MUT_ID=P01 node --import <preload.mjs> <this file>   (P00 is the unmutated control).
import { summaryText } from "../../../../../../../src/core/summary.js";
import { computeResult } from "../../../../../../../src/core/result.js";
import { setPersonName, newBill, setSubtotalText } from "../../../../../../../src/core/bill.js";

const NUL = String.fromCharCode(0);
const LONE_HIGH = String.fromCharCode(0xd800);
const base = setSubtotalText(newBill(), "100.00");

function row(name) {
  const text = summaryText(computeResult(setPersonName(base, "p1", name)));
  return text.split("\n")[2];
}
const cases = [
  ["two NULs apart", `A${NUL}B${NUL}C`],
  ["two adjacent NULs", `A${NUL}${NUL}B`],
  ["a lone surrogate", `A${LONE_HIGH}B`],
];
for (const [label, name] of cases) {
  const out = row(name);
  console.log(label.padEnd(20), JSON.stringify(out), "| NULs left:", [...out].filter((c) => c === NUL).length,
    "| lone surrogate left:", out.includes(LONE_HIGH));
}
