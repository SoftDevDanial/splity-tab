// Differential check of the WR-06, WR-08 and WR-09 refactors. The old sources come from `git show
// 67e4b6e:<file>` and are imported from in-memory data: URLs, so no file is written. Both modules have
// no imports, which is what makes a data: URL possible.
// Run from the project root: node docs/modules/split-core/qa/code-review/20261009-134620/scripts/diff-old-new.mjs
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const ROOT = process.cwd();
const BASE = "67e4b6e";

async function oldModule(path) {
  const source = execFileSync("git", ["show", `${BASE}:${path}`], { cwd: ROOT, encoding: "utf8", timeout: 20000 });
  return import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
}
const newModule = (path) => import(pathToFileURL(resolve(ROOT, path)).href);

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rnd = mulberry32(20261009);
const pick = (list) => list[Math.floor(rnd() * list.length)];
const int = (lo, hi) => lo + Math.floor(rnd() * (hi - lo + 1));

// ---- money.js: parseAmount, parseRate, formatMoney, formatRate ----
const oldMoney = await oldModule("src/core/money.js");
const newMoney = await newModule("src/core/money.js");

// Includes a full-width digit, a no-break space, a tab and a newline.
const ALPHABET = [..."0123456789..,-+ eE%abc\u{FF11}\t\n\u{A0}x"];
const strings = new Set(["", " ", "0", ".", "0.", "00.5", "99999.99", "100000", "30", "30.01", "20", "20.01", "6.25"]);
for (let n = 0; n < 300000; n += 1) {
  const kind = int(0, 3);
  let text = "";
  if (kind === 0) for (let k = int(0, 14); k > 0; k -= 1) text += pick(ALPHABET);
  else if (kind === 1) text = "0".repeat(int(0, 12)) + String(int(0, 99999999)) + (rnd() < 0.5 ? "." + String(int(0, 9999)).slice(0, int(0, 4)) : "");
  else if (kind === 2) text = String(int(0, 40)) + "." + String(int(0, 999)).padStart(int(0, 3), "0");
  else text = " ".repeat(int(0, 2)) + "9".repeat(int(1, 30)) + (rnd() < 0.3 ? ".99" : "") + " ".repeat(int(0, 2));
  strings.add(text);
}
for (const huge of ["1" + "0".repeat(400), "0".repeat(1000) + "1", "9".repeat(5000) + "x"]) strings.add(huge);

let compared = 0;
const diffs = [];
for (const text of strings) {
  for (const max of [0, 1, 20, 30, 99, 100, 1000]) {
    const a = JSON.stringify(oldMoney.parseRate(text, max));
    const b = JSON.stringify(newMoney.parseRate(text, max));
    compared += 1;
    if (a !== b) diffs.push(["parseRate", text.slice(0, 40), max, a, b]);
  }
  const a = JSON.stringify(oldMoney.parseAmount(text));
  const b = JSON.stringify(newMoney.parseAmount(text));
  compared += 1;
  if (a !== b) diffs.push(["parseAmount", text.slice(0, 40), a, b]);
}
for (let cents = 0; cents <= 200000; cents += 1) {
  compared += 2;
  if (oldMoney.formatMoney(cents) !== newMoney.formatMoney(cents)) diffs.push(["formatMoney", cents]);
  if (oldMoney.formatRate(cents) !== newMoney.formatRate(cents)) diffs.push(["formatRate", cents]);
}
for (const big of [779999922, 999999999, 2 ** 31, 2 ** 40 + 7, Number.MAX_SAFE_INTEGER, Number.MAX_SAFE_INTEGER - 1]) {
  compared += 2;
  if (oldMoney.formatMoney(big) !== newMoney.formatMoney(big)) diffs.push(["formatMoney", big, oldMoney.formatMoney(big), newMoney.formatMoney(big)]);
  if (oldMoney.formatRate(big) !== newMoney.formatRate(big)) diffs.push(["formatRate", big, oldMoney.formatRate(big), newMoney.formatRate(big)]);
}
console.log(`money.js: ${strings.size} strings, ${compared} comparisons, ${diffs.length} differences`);
for (const d of diffs.slice(0, 10)) console.log("  DIFF", JSON.stringify(d));

// ---- bill.js: a random walk of actions, old against new ----
const oldBill = await oldModule("src/core/bill.js");
const newBill = await newModule("src/core/bill.js");

function step(api, bill, op) {
  switch (op.kind) {
    case "addPerson": return api.addPerson(bill);
    case "removePerson": return api.removePerson(bill, op.id);
    case "setPersonName": return api.setPersonName(bill, op.id, op.text);
    case "addItem": return api.addItem(bill);
    case "removeItem": return api.removeItem(bill, op.id);
    case "setItemName": return api.setItemName(bill, op.id, op.text);
    case "setItemPriceText": return api.setItemPriceText(bill, op.id, op.text);
    case "toggle": return api.toggleItemPerson(bill, op.item, op.person);
    case "mode": return api.setMode(bill, op.text);
    case "sub": return api.setSubtotalText(bill, op.text);
    case "svc": return api.setServiceText(bill, op.text);
    case "sst": return api.setSstText(bill, op.text);
    default: throw new Error(op.kind);
  }
}
let steps = 0;
let sameRefMismatch = 0;
let valueMismatch = 0;
for (let walk = 0; walk < 400; walk += 1) {
  let a = oldBill.newBill();
  let b = newBill.newBill();
  for (let k = 0; k < 300; k += 1) {
    const ids = [...new Set([...a.people.map((p) => p.id), ...a.items.map((i) => i.id), "p99", "i99", ""])];
    const op = {
      kind: pick(["addPerson", "removePerson", "setPersonName", "addItem", "removeItem", "setItemName",
        "setItemPriceText", "toggle", "toggle", "toggle", "mode", "sub", "svc", "sst"]),
      id: pick(ids), item: pick(ids), person: pick(ids), text: pick(["", "x", " y ", "item", "even", "other", "12.50"]),
    };
    const na = step(oldBill, a, op);
    const nb = step(newBill, b, op);
    steps += 1;
    if ((na === a) !== (nb === b)) sameRefMismatch += 1;
    if (JSON.stringify(na) !== JSON.stringify(nb)) valueMismatch += 1;
    a = na;
    b = nb;
    if (valueMismatch + sameRefMismatch > 0) break;
  }
}
console.log(`bill.js: ${steps} action steps, ${valueMismatch} value differences, ${sameRefMismatch} same-reference differences`);
