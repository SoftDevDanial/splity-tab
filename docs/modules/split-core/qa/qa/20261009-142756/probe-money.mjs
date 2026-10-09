// Independent money cross-check for split-core. QA finder, read-only on src/.
// Expected values are typed by hand from docs/modules/split-core/qa.md and spec.md (R1 to R8, R18 to R24).
// Bills are plain literals, not the test helpers. The sweep in section I uses a BigInt reference that
// imports nothing from src/core/.
import { isDeepStrictEqual } from "node:util";

const CORE = "file:///{workspace}/examples/split/src/core/";
const money = await import(new URL("money.js", CORE).href);
const allocate = await import(new URL("allocate.js", CORE).href);
const billMod = await import(new URL("bill.js", CORE).href);
const resultMod = await import(new URL("result.js", CORE).href);
const summaryMod = await import(new URL("summary.js", CORE).href);

const tally = { pass: 0, fail: 0 };
const show = (value) => JSON.stringify(value, (_, v) => (typeof v === "bigint" ? `${v}n` : v));
function check(label, actual, expected) {
  if (isDeepStrictEqual(actual, expected)) {
    tally.pass += 1;
    console.log(`PASS ${label}`);
  } else {
    tally.fail += 1;
    console.log(`FAIL ${label}`);
    console.log(`  expected ${show(expected)}`);
    console.log(`  actual   ${show(actual)}`);
  }
}

// Builders for literal bills and typed expectations.
const P = (id, name) => ({ id, name });
const item = (id, name, priceText, who) => ({ id, name, priceText, who });
const bl = (fields) => ({
  mode: "even", people: [], subtotalText: "", items: [], serviceText: "10", sstText: "6", nextId: 99, ...fields,
});
const ch = (subtotal, serviceBp, service, sstBp, sstBase, sst, total) => ({
  subtotal, serviceBp, service, sstBp, sstBase, sst, total,
});
const irow = (name, items, charges, share) => ({ name, items, charges, share });
const sumOf = (xs) => xs.reduce((a, b) => a + b, 0);
const bigSum = (xs) => xs.reduce((a, b) => a + b, 0n);
const TRIO = [P("p1", "Aisyah"), P("p2", "Ben"), P("p3", "Chen")];
const TWELVE = Array.from({ length: 12 }, (_, k) => P(`p${k + 1}`, `Person ${k + 1}`));

// Does a core result add up (spec R22)? Returns the list of violated invariants, empty when all hold.
function addsUp(r) {
  const problems = [];
  if (r.kind === "even") {
    if (sumOf(r.rows.map((x) => x.share)) !== r.charges.total) problems.push("rows do not sum to total");
    if (r.check.share !== r.charges.total) problems.push("check.share != total");
  } else if (r.kind === "item") {
    if (sumOf(r.rows.map((x) => x.share)) !== r.charges.total) problems.push("share column != total");
    if (sumOf(r.rows.map((x) => x.items)) !== r.charges.subtotal) problems.push("items column != subtotal");
    if (sumOf(r.rows.map((x) => x.charges)) !== r.charges.service + r.charges.sst) problems.push("charges column != service+sst");
    if (r.check.items !== r.charges.subtotal) problems.push("check.items != subtotal");
    if (r.check.charges !== r.charges.service + r.charges.sst) problems.push("check.charges != service+sst");
    if (r.check.share !== r.charges.total) problems.push("check.share != total");
  }
  return problems;
}

// ---- A. Money text read on the way in (R1, R3), typed from qa.md and the named bills ----
console.log("== A. Money text read on the way in (R1, R3) ==");
const parseCases = [
  ["parseAmount 15.90 (Nasi lemak)", () => money.parseAmount("15.90"), { ok: true, cents: 1590 }],
  ["parseAmount 13.50 (Char kuey teow)", () => money.parseAmount("13.50"), { ok: true, cents: 1350 }],
  ["parseAmount 12.00 (Mee goreng)", () => money.parseAmount("12.00"), { ok: true, cents: 1200 }],
  ["parseAmount 18.00 (Satay)", () => money.parseAmount("18.00"), { ok: true, cents: 1800 }],
  ["parseAmount 10.01 (I3)", () => money.parseAmount("10.01"), { ok: true, cents: 1001 }],
  ["parseAmount 0.10 (I4)", () => money.parseAmount("0.10"), { ok: true, cents: 10 }],
  ["parseAmount 100.00 (S2 subtotal)", () => money.parseAmount("100.00"), { ok: true, cents: 10000 }],
  ["parseAmount 87.65 (E1 subtotal)", () => money.parseAmount("87.65"), { ok: true, cents: 8765 }],
  ["parseAmount 5.01 (I2 Y)", () => money.parseAmount("5.01"), { ok: true, cents: 501 }],
  ["parseAmount 50.00 (E3 subtotal)", () => money.parseAmount("50.00"), { ok: true, cents: 5000 }],
  ["parseAmount 99999.99 (MAX)", () => money.parseAmount("99999.99"), { ok: true, cents: 9999999 }],
  ["parseAmount 1.15 (float trap, naive gives 114)", () => money.parseAmount("1.15"), { ok: true, cents: 115 }],
  ["parseAmount 4.35 (float trap, naive gives 434)", () => money.parseAmount("4.35"), { ok: true, cents: 435 }],
  ["parseRate 12.5 max 30 (E3 service)", () => money.parseRate("12.5", 30), { ok: true, bp: 1250 }],
  ["parseRate 6.25 max 20 (E3 SST)", () => money.parseRate("6.25", 20), { ok: true, bp: 625 }],
  ["parseRate 30 max 30 (MAX service)", () => money.parseRate("30", 30), { ok: true, bp: 3000 }],
  ["parseRate 20 max 20 (MAX SST)", () => money.parseRate("20", 20), { ok: true, bp: 2000 }],
  ["parseRate 0 max 30 (zero is valid)", () => money.parseRate("0", 30), { ok: true, bp: 0 }],
];
for (const [label, run, expected] of parseCases) check(label, run(), expected);

// ---- B. Formatting, typed from R4 and R5 (the summary text is built from these) ----
console.log("== B. Money and rate text written out (R4, R5) ==");
const formatCases = [
  ["formatMoney 0", () => money.formatMoney(0), "RM 0.00"],
  ["formatMoney 1", () => money.formatMoney(1), "RM 0.01"],
  ["formatMoney 10", () => money.formatMoney(10), "RM 0.10"],
  ["formatMoney 100", () => money.formatMoney(100), "RM 1.00"],
  ["formatMoney 3887", () => money.formatMoney(3887), "RM 38.87"],
  ["formatMoney 11660", () => money.formatMoney(11660), "RM 116.60"],
  ["formatMoney 15599999", () => money.formatMoney(15599999), "RM 155999.99"],
  ["formatMoney 779999922", () => money.formatMoney(779999922), "RM 7799999.22"],
  ["formatRate 0", () => money.formatRate(0), "0%"],
  ["formatRate 600", () => money.formatRate(600), "6%"],
  ["formatRate 1000", () => money.formatRate(1000), "10%"],
  ["formatRate 650", () => money.formatRate(650), "6.5%"],
  ["formatRate 625", () => money.formatRate(625), "6.25%"],
  ["formatRate 605", () => money.formatRate(605), "6.05%"],
  ["formatRate 3000", () => money.formatRate(3000), "30%"],
  ["formatRate 1250 (E3 service shows 12.5%)", () => money.formatRate(1250), "12.5%"],
];
for (const [label, run, expected] of formatCases) check(label, run(), expected);

// ---- C. Allocation, typed from R7 and R8 ----
console.log("== C. Cent allocation (R7, R8) ==");
const eleven = (v) => Array(11).fill(v);
const allocCases = [
  ["allocateEvenly 11660 / 3 (S2)", () => allocate.allocateEvenly(11660, 3), [3887, 3887, 3886]],
  ["allocateEvenly 1800 / 2 (S1 satay)", () => allocate.allocateEvenly(1800, 2), [900, 900]],
  ["allocateEvenly 1001 / 3", () => allocate.allocateEvenly(1001, 3), [334, 334, 333]],
  ["allocateEvenly 1 / 3", () => allocate.allocateEvenly(1, 3), [1, 0, 0]],
  ["allocateEvenly 0 / 2", () => allocate.allocateEvenly(0, 2), [0, 0]],
  ["allocateEvenly 10221 / 4 (E1)", () => allocate.allocateEvenly(10221, 4), [2556, 2555, 2555, 2555]],
  ["allocateEvenly 15599999 / 12 (MAX-E)", () => allocate.allocateEvenly(15599999, 12), [...eleven(1300000), 1299999]],
  ["allocateByWeight 986 S1 charges", () => allocate.allocateByWeight(986, [2490, 1350, 2100]), [414, 224, 348]],
  ["allocateByWeight 10 leftover skips zero", () => allocate.allocateByWeight(10, [0, 1, 1, 1]), [0, 4, 3, 3]],
  ["allocateByWeight 249 (I2 example)", () => allocate.allocateByWeight(249, [0, 1251, 250]), [0, 208, 41]],
  ["allocateByWeight 236419679 BigInt trap", () => allocate.allocateByWeight(236419679, [314963010, 157876348]),
    [157481505, 78938174]],
  ["allocateByWeight 61846725 BigInt trap", () => allocate.allocateByWeight(61846725, [49676084, 322894546]),
    [8246230, 53600495]],
  ["allocateByWeight 178450942 BigInt trap", () => allocate.allocateByWeight(178450942, [111531837, 207130558]),
    [62457829, 115993113]],
  ["allocateByWeight MAX-I charges 279999972", () => allocate.allocateByWeight(279999972,
    [49999995, 49999995, ...Array(10).fill(39999996)]),
  [27999998, 27999998, ...Array(6).fill(22399998), ...Array(4).fill(22399997)]],
];
for (const [label, run, expected] of allocCases) check(label, run(), expected);

// ---- D. Charges, typed from R6 (the ten rows) and from the named bills ----
console.log("== D. Charges (R6) ==");
const chargeCases = [
  ["billCharges S2 (10000, 10%, 6%)", [10000, 1000, 600], ch(10000, 1000, 1000, 600, 11000, 660, 11660)],
  ["billCharges S1 (5940, 10%, 6%) SST 392.04 rounds down", [5940, 1000, 600], ch(5940, 1000, 594, 600, 6534, 392, 6926)],
  ["billCharges E1 (8765, 10%, 6%) service 876.5 rounds up", [8765, 1000, 600], ch(8765, 1000, 877, 600, 9642, 579, 10221)],
  ["billCharges (5, 10%, 0%) half a sen", [5, 1000, 0], ch(5, 1000, 1, 0, 6, 0, 6)],
  ["billCharges (25, 10%, 0%) 2.5 rounds up", [25, 1000, 0], ch(25, 1000, 3, 0, 28, 0, 28)],
  ["billCharges (4, 10%, 0%) 0.4 rounds down", [4, 1000, 0], ch(4, 1000, 0, 0, 4, 0, 4)],
  ["billCharges (1000, 0%, 0%) both off", [1000, 0, 0], ch(1000, 0, 0, 0, 1000, 0, 1000)],
  ["billCharges E3 (5000, 12.5%, 6.25%) SST 351.5625 rounds up", [5000, 1250, 625], ch(5000, 1250, 625, 625, 5625, 352, 5977)],
  ["billCharges MAX-E (9999999, 30%, 20%)", [9999999, 3000, 2000], ch(9999999, 3000, 3000000, 2000, 12999999, 2600000, 15599999)],
  ["billCharges MAX-I (499999950, 30%, 20%)", [499999950, 3000, 2000],
    ch(499999950, 3000, 149999985, 2000, 649999935, 129999987, 779999922)],
  ["billCharges I2 (1501, 10%, 6%) I2 row", [1501, 1000, 600], ch(1501, 1000, 150, 600, 1651, 99, 1750)],
  ["billCharges I3 (1001, 10%, 6%) I3 row, derived from R6", [1001, 1000, 600], ch(1001, 1000, 100, 600, 1101, 66, 1167)],
  ["billCharges I4 (10, 0%, 0%) I4 row", [10, 0, 0], ch(10, 0, 0, 0, 10, 0, 10)],
  ["billCharges D2 (1000, 10%, 6%) D2 row", [1000, 1000, 600], ch(1000, 1000, 100, 600, 1100, 66, 1166)],
];
for (const [label, [a, b, c], expected] of chargeCases) {
  check(label, resultMod.billCharges(a, b, c), expected);
}

// ---- E. Even split, typed from qa.md (named bills S2, E1, E2, E3, MAX-E, D1) ----
console.log("== E. Even split (R20, R22, R26) ==");
const S2 = bl({ people: TRIO, subtotalText: "100.00" });
const E1 = bl({ people: [P("p1", "A"), P("p2", "B"), P("p3", "C"), P("p4", "D")], subtotalText: "87.65" });
const E2 = bl({ people: TRIO, subtotalText: "10.00", serviceText: "0", sstText: "0" });
const E3 = bl({ people: [P("p1", "Person 1"), P("p2", "Person 2")], subtotalText: "50.00", serviceText: "12.5", sstText: "6.25" });
const MAXE = bl({ people: TWELVE, subtotalText: "99999.99", serviceText: "30", sstText: "20" });
const D1 = bl({ people: [P("p1", "Ben"), P("p2", "Ben"), P("p3", "Chen")], subtotalText: "100.00" });
const evenTyped = [
  ["S2", S2, { kind: "even", charges: ch(10000, 1000, 1000, 600, 11000, 660, 11660),
    rows: [{ name: "Aisyah", share: 3887 }, { name: "Ben", share: 3887 }, { name: "Chen", share: 3886 }], check: { share: 11660 } }],
  ["E1", E1, { kind: "even", charges: ch(8765, 1000, 877, 600, 9642, 579, 10221),
    rows: [{ name: "A", share: 2556 }, { name: "B", share: 2555 }, { name: "C", share: 2555 }, { name: "D", share: 2555 }],
    check: { share: 10221 } }],
  ["E2", E2, { kind: "even", charges: ch(1000, 0, 0, 0, 1000, 0, 1000),
    rows: [{ name: "Aisyah", share: 334 }, { name: "Ben", share: 333 }, { name: "Chen", share: 333 }], check: { share: 1000 } }],
  ["E3", E3, { kind: "even", charges: ch(5000, 1250, 625, 625, 5625, 352, 5977),
    rows: [{ name: "Person 1", share: 2989 }, { name: "Person 2", share: 2988 }], check: { share: 5977 } }],
  ["MAX-E", MAXE, { kind: "even", charges: ch(9999999, 3000, 3000000, 2000, 12999999, 2600000, 15599999),
    rows: TWELVE.map((p, i) => ({ name: p.name, share: i < 11 ? 1300000 : 1299999 })), check: { share: 15599999 } }],
  ["D1", D1, { kind: "even", charges: ch(10000, 1000, 1000, 600, 11000, 660, 11660),
    rows: [{ name: "Ben", share: 3887 }, { name: "Ben", share: 3887 }, { name: "Chen", share: 3886 }], check: { share: 11660 } }],
];
for (const [label, bill, expected] of evenTyped) {
  const got = resultMod.computeResult(bill);
  check(`even ${label} full result`, got, expected);
  check(`even ${label} typed table adds up`, addsUp(expected), []);
  check(`even ${label} core shares add up (R22)`, addsUp(got), []);
}

// ---- F. By-item split, typed from qa.md (S1, I2, I3, I4, D2, MAX-I, S5) ----
console.log("== F. By-item split (R19, R21, R22, R26) ==");
const S1 = bl({
  mode: "item", people: TRIO,
  items: [
    item("i4", "Nasi lemak ayam", "15.90", ["p1"]),
    item("i5", "Char kuey teow", "13.50", ["p2"]),
    item("i6", "Mee goreng mamak", "12.00", ["p3"]),
    item("i7", "Satay, 10 sticks", "18.00", ["p1", "p3"]),
  ],
});
const S5 = { ...S1, items: S1.items.map((it) => (it.id === "i6" ? { ...it, who: [] } : it)) };
const I2 = bl({
  mode: "item", people: TRIO,
  items: [item("i4", "X", "10.00", ["p2"]), item("i5", "Y", "5.01", ["p2", "p3"])],
});
const I3 = bl({ mode: "item", people: TRIO, items: [item("i4", "", "10.01", ["p3", "p1"])] });
const I4 = bl({ mode: "item", people: TRIO, serviceText: "0", sstText: "0", items: [item("i4", "", "0.10", ["p1", "p2", "p3"])] });
const D2 = bl({ mode: "item", people: [P("p1", "Ben"), P("p2", "Ben"), P("p3", "Chen")], items: [item("i4", "Tea", "10.00", ["p2"])] });
const MAXI = bl({
  mode: "item", people: TWELVE, serviceText: "30", sstText: "20",
  items: Array.from({ length: 50 }, (_, k) => item(`i${k + 4}`, "", "99999.99", [`p${(k % 12) + 1}`])),
});
const maxItems = [49999995, 49999995, ...Array(10).fill(39999996)];
const maxCharges = [27999998, 27999998, ...Array(6).fill(22399998), ...Array(4).fill(22399997)];
const maxShares = [77999993, 77999993, ...Array(6).fill(62399994), ...Array(4).fill(62399993)];
const itemTyped = [
  ["S1", S1, { kind: "item", charges: ch(5940, 1000, 594, 600, 6534, 392, 6926),
    rows: [irow("Aisyah", 2490, 414, 2904), irow("Ben", 1350, 224, 1574), irow("Chen", 2100, 348, 2448)],
    check: { items: 5940, charges: 986, share: 6926 } }],
  ["I2", I2, { kind: "item", charges: ch(1501, 1000, 150, 600, 1651, 99, 1750),
    rows: [irow("Aisyah", 0, 0, 0), irow("Ben", 1251, 208, 1459), irow("Chen", 250, 41, 291)],
    check: { items: 1501, charges: 249, share: 1750 } }],
  ["I3", I3, { kind: "item", charges: ch(1001, 1000, 100, 600, 1101, 66, 1167),
    rows: [irow("Aisyah", 501, 84, 585), irow("Ben", 0, 0, 0), irow("Chen", 500, 82, 582)],
    check: { items: 1001, charges: 166, share: 1167 } }],
  ["I4", I4, { kind: "item", charges: ch(10, 0, 0, 0, 10, 0, 10),
    rows: [irow("Aisyah", 4, 0, 4), irow("Ben", 3, 0, 3), irow("Chen", 3, 0, 3)],
    check: { items: 10, charges: 0, share: 10 } }],
  ["D2", D2, { kind: "item", charges: ch(1000, 1000, 100, 600, 1100, 66, 1166),
    rows: [irow("Ben", 0, 0, 0), irow("Ben", 1000, 166, 1166), irow("Chen", 0, 0, 0)],
    check: { items: 1000, charges: 166, share: 1166 } }],
  ["MAX-I", MAXI, { kind: "item", charges: ch(499999950, 3000, 149999985, 2000, 649999935, 129999987, 779999922),
    rows: TWELVE.map((p, i) => irow(p.name, maxItems[i], maxCharges[i], maxShares[i])),
    check: { items: 499999950, charges: 279999972, share: 779999922 } }],
];
for (const [label, bill, expected] of itemTyped) {
  const got = resultMod.computeResult(bill);
  check(`item ${label} full result`, got, expected);
  check(`item ${label} typed table adds up`, addsUp(expected), []);
  check(`item ${label} core shares add up (R22)`, addsUp(got), []);
}
check("item S5 one unassigned item (R19) full result", resultMod.computeResult(S5),
  { kind: "unassigned", count: 1, charges: ch(5940, 1000, 594, 600, 6534, 392, 6926) });
check("item I3 leftover follows list order (Aisyah 501, Chen 500)",
  resultMod.computeResult(I3).rows.map((r) => r.items), [501, 0, 500]);

// ---- G. Blocking order, typed from the R18 table ----
console.log("== G. Blocking order (R18) ==");
const blockedTyped = [
  ["row 1 blank service -> rates", bl({ serviceText: "", subtotalText: "100" }), "rates"],
  ["row 2 service 31 -> rates", bl({ serviceText: "31", subtotalText: "" }), "rates"],
  ["row 3 SST 20.01 beats the item rule -> rates", bl({ mode: "item", serviceText: "10", sstText: "20.01" }), "rates"],
  ["row 4 blank subtotal -> subtotal", bl({ subtotalText: "" }), "subtotal"],
  ["row 5 subtotal 0 -> subtotal", bl({ subtotalText: "0" }), "subtotal"],
  ["row 6 subtotal 12.505 -> subtotal", bl({ subtotalText: "12.505" }), "subtotal"],
  ["row 7 item mode, no items -> no-items", bl({ mode: "item", subtotalText: "100" }), "no-items"],
  ["row 8 one blank-priced item -> prices", bl({ mode: "item", items: [item("i4", "", "", [])] }), "prices"],
  ["row 9 one valid and one abc -> prices", bl({
    mode: "item", items: [item("i4", "", "15.90", ["p1"]), item("i5", "", "abc", ["p1"])],
  }), "prices"],
];
for (const [label, bill, reason] of blockedTyped) {
  check(`blocked ${label}`, resultMod.computeResult(bill), { kind: "blocked", reason });
}

// ---- H. Summary text, typed from qa.md and spec R24 ----
console.log("== H. Summary text (R24, R26) ==");
const block = (...lines) => lines.join("\n");
const summaryTyped = [
  ["S2", S2, block("Bill split", "Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)",
    "Aisyah RM 38.87", "Ben RM 38.87", "Chen RM 38.86", "Adds up to RM 116.60")],
  ["S1", S1, block("Bill split", "Total RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)",
    "Aisyah RM 29.04", "Ben RM 15.74", "Chen RM 24.48", "Adds up to RM 69.26")],
  ["E2", E2, block("Bill split", "Total RM 10.00 (subtotal RM 10.00, service 0% RM 0.00, SST 0% RM 0.00)",
    "Aisyah RM 3.34", "Ben RM 3.33", "Chen RM 3.33", "Adds up to RM 10.00")],
  ["E3", E3, block("Bill split", "Total RM 59.77 (subtotal RM 50.00, service 12.5% RM 6.25, SST 6.25% RM 3.52)",
    "Person 1 RM 29.89", "Person 2 RM 29.88", "Adds up to RM 59.77")],
  ["I2", I2, block("Bill split", "Total RM 17.50 (subtotal RM 15.01, service 10% RM 1.50, SST 6% RM 0.99)",
    "Aisyah RM 0.00", "Ben RM 14.59", "Chen RM 2.91", "Adds up to RM 17.50")],
  ["D1", D1, block("Bill split", "Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)",
    "Ben RM 38.87", "Ben RM 38.87", "Chen RM 38.86", "Adds up to RM 116.60")],
  ["D2", D2, block("Bill split", "Total RM 11.66 (subtotal RM 10.00, service 10% RM 1.00, SST 6% RM 0.66)",
    "Ben RM 0.00", "Ben RM 11.66", "Chen RM 0.00", "Adds up to RM 11.66")],
];
for (const [label, bill, expected] of summaryTyped) {
  const text = summaryMod.summaryText(resultMod.computeResult(bill));
  check(`summary ${label} exact text`, text, expected);
  check(`summary ${label} no trailing newline`, text.endsWith("\n"), false);
}
const blankBen = billMod.setPersonName(S2, "p2", "   ");
check("summary blank name prints as position (line 4)",
  summaryMod.summaryText(resultMod.computeResult(blankBen)).split("\n")[3], "Person 2 RM 38.87");

// ---- I. BigInt reference sweep over 400 generated bills (R6, R8, R20 to R22), no core code ----
console.log("== I. BigInt reference sweep, 400 generated bills ==");
const MASK = (1n << 64n) - 1n;
let seed = 4242n;
const unit = () => {
  seed = (seed * 6364136223846793005n + 1442695040888963407n) & MASK;
  return Number(seed >> 11n) / 2 ** 53;
};
const between = (lo, hi) => lo + Math.floor(unit() * (hi - lo + 1));
const textOf = (hundredths) => `${Math.floor(hundredths / 100)}.${String(hundredths % 100).padStart(2, "0")}`;
// floor((n x bp + 5000) / 10000), written as (2 n bp + 10000) / 20000 so it is exact in BigInt.
const halfUp = (n, bp) => (2n * (n * bp) + 10000n) / 20000n;
const refCharges = (subtotal, sbp, tbp) => {
  const service = halfUp(subtotal, sbp);
  const sstBase = subtotal + service;
  const sst = halfUp(sstBase, tbp);
  return { subtotal, service, sstBase, sst, total: subtotal + service + sst };
};
// Floors, then one sen each to the lowest indexes with a positive weight until the amount is used up.
const refSplit = (amount, weights) => {
  const total = weights.reduce((a, w) => a + w, 0n);
  const parts = weights.map((w) => (amount * w) / total);
  let left = amount - parts.reduce((a, p) => a + p, 0n);
  return parts.map((p, i) => {
    if (left > 0n && weights[i] > 0n) {
      left -= 1n;
      return p + 1n;
    }
    return p;
  });
};

const sweepBad = [];
let evenBills = 0;
let itemBills = 0;
for (let n = 0; n < 400; n += 1) {
  const mode = n % 2 === 0 ? "even" : "item";
  const count = between(2, 12);
  const people = Array.from({ length: count }, (_, i) => P(`p${i + 1}`, `N${i + 1}`));
  const itemCount = between(1, 50);
  const priceCents = Array.from({ length: itemCount }, () => (unit() < 0.1 ? 9999999 : between(1, 9999999)));
  const items = priceCents.map((cents, k) => {
    let who = people.filter(() => unit() < 0.5).map((p) => p.id);
    if (who.length === 0) who = [people[between(0, count - 1)].id];
    for (let i = who.length - 1; i > 0; i -= 1) {
      const j = between(0, i);
      [who[i], who[j]] = [who[j], who[i]];
    }
    return item(`i${k + 1}`, "", textOf(cents), who);
  });
  const subCents = between(1, 9999999);
  const sbp = between(0, 3000);
  const tbp = between(0, 2000);
  const bill = bl({
    mode, people, items, subtotalText: textOf(subCents), serviceText: textOf(sbp), sstText: textOf(tbp),
  });
  const got = resultMod.computeResult(bill);

  let expected;
  if (mode === "even") {
    evenBills += 1;
    const c = refCharges(BigInt(subCents), BigInt(sbp), BigInt(tbp));
    const shares = refSplit(c.total, people.map(() => 1n));
    expected = {
      kind: "even",
      charges: {
        subtotal: subCents, serviceBp: sbp, service: Number(c.service), sstBp: tbp,
        sstBase: Number(c.sstBase), sst: Number(c.sst), total: Number(c.total),
      },
      rows: people.map((p, i) => ({ name: p.name, share: Number(shares[i]) })),
      check: { share: Number(c.total) },
    };
  } else {
    itemBills += 1;
    const totals = people.map(() => 0n);
    items.forEach((it, k) => {
      const holders = people.flatMap((p, i) => (it.who.includes(p.id) ? [i] : []));
      const parts = refSplit(BigInt(priceCents[k]), holders.map(() => 1n));
      holders.forEach((pi, j) => {
        totals[pi] += parts[j];
      });
    });
    const subtotal = BigInt(priceCents.reduce((a, b) => a + b, 0));
    const c = refCharges(subtotal, BigInt(sbp), BigInt(tbp));
    const chargePart = refSplit(c.service + c.sst, totals);
    expected = {
      kind: "item",
      charges: {
        subtotal: Number(subtotal), serviceBp: sbp, service: Number(c.service), sstBp: tbp,
        sstBase: Number(c.sstBase), sst: Number(c.sst), total: Number(c.total),
      },
      rows: people.map((p, i) => ({
        name: p.name, items: Number(totals[i]), charges: Number(chargePart[i]), share: Number(totals[i] + chargePart[i]),
      })),
      check: {
        items: Number(bigSum(totals)), charges: Number(bigSum(chargePart)),
        share: Number(bigSum(totals.map((t, i) => t + chargePart[i]))),
      },
    };
  }
  if (!isDeepStrictEqual(got, expected)) sweepBad.push({ n, mode, got, expected });
}
if (sweepBad.length === 0) {
  tally.pass += 1;
  console.log(`PASS sweep: 400 generated bills (even ${evenBills}, item ${itemBills}) agree with the BigInt reference`);
} else {
  tally.fail += 1;
  const first = sweepBad[0];
  console.log(`FAIL sweep: ${sweepBad.length} of 400 bills differ, first at n=${first.n} (${first.mode})`);
  console.log(`  expected ${show(first.expected)}`);
  console.log(`  actual   ${show(first.got)}`);
}

console.log(`SUMMARY pass=${tally.pass} fail=${tally.fail}`);
process.exitCode = tally.fail === 0 ? 0 : 1;
