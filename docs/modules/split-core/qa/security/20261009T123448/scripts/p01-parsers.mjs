// P01. Threat row 3: the parsers never throw for any string (R2), always return a well-formed result,
// and never call Number on a whole part longer than the ceiling allows. Fuzz over the full code point
// range including lone surrogates.
import { parseAmount, parseRate } from "../../../../../../../src/core/money.js";
import { rng, randInt, ch } from "./fixtures.mjs";

const r = rng(1);
const SPECIAL = [0x00, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x20, 0x2e, 0x2b, 0x2d, 0x30, 0x31, 0x39, 0x65, 0x85, 0xa0,
  0x1680, 0x2028, 0x2029, 0x202f, 0x3000, 0xfeff, 0xff10, 0x0660, 0xd800, 0xdc00, 0x1d7ce];
const wellFormed = (x, key) => (x.ok === true && Number.isSafeInteger(x[key]) && x[key] >= 0 && Object.keys(x).length === 2)
  || (x.ok === false && typeof x.empty === "boolean" && Object.keys(x).length === 2);
let thrown = 0, malformed = 0, accepted = 0;
for (let n = 0; n < 1000000; n += 1) {
  const len = randInt(r, 0, 14);
  let s = "";
  for (let i = 0; i < len; i += 1) {
    const k = r();
    s += k < 0.6 ? ch(SPECIAL[randInt(r, 0, SPECIAL.length - 1)]) : k < 0.9 ? String(randInt(r, 0, 9)) : ch(randInt(r, 0, 0x10ffff));
  }
  try {
    const a = parseAmount(s), b = parseRate(s, 30), c = parseRate(s, 20);
    if (!wellFormed(a, "cents") || !wellFormed(b, "bp") || !wellFormed(c, "bp")) malformed += 1;
    if (a.ok) {
      accepted += 1;
      if (!/^[0-9]+(\.[0-9]{0,2})?$/.test(s.trim()) || a.cents < 1 || a.cents > 9999999) malformed += 1;
    }
  } catch { thrown += 1; }
}
console.log(`1,000,000 fuzz strings: thrown ${thrown}, malformed or out-of-grammar accepts ${malformed}, accepted ${accepted}`);

// Number spy: long whole parts must be refused before conversion.
const seen = [];
const realNumber = globalThis.Number;
globalThis.Number = new Proxy(realNumber, { apply(t, self, args) { seen.push(String(args[0]).length); return Reflect.apply(t, self, args); } });
parseAmount("9".repeat(1e6)); parseAmount("0".repeat(1e6) + "123456"); parseRate("100", 30); parseRate("999", 20);
const longest = Math.max(0, ...seen);
parseAmount("99999.99");
globalThis.Number = realNumber;
console.log(`Number called with a string longer than 5 characters on refused inputs: ${longest > 5 ? `yes (${longest})` : "no"}; calls on a valid amount seen afterwards: ${seen.length > 0}`);
console.log(`P01 RESULT: ${thrown === 0 && malformed === 0 && longest <= 5 && seen.length > 0 ? "PASS" : "FAIL"}`);
