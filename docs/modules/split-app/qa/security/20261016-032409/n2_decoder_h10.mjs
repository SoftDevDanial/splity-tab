// Security finder (read-only), v1.1.0 regression --full (2026-10-16). D8 as changed by H-10 (R62 (2) and (3), readName in
// src/draft.js): every person and item name is rebuilt without core R35's class after the LF and CR check, and the
// count is of what is left. The oracle here is independent of src/ (its own list of the 79 code points, not plainName).
// For every accepted draft. Every decoded name is the oracle's removal of the stored name, no name holds the class, the
// summary rows are the screen labels (personLabel) followed by the share, and encodeDraft then decodeDraft gives the same
// names. Run from this folder (node n2_decoder_h10.mjs), which writes n2_decoder_h10-results.json here.
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = new URL("../../../../../../", import.meta.url);
if (process.cwd().toLowerCase() !== fileURLToPath(new URL(".", import.meta.url)).slice(0, -1).toLowerCase()) throw new Error("run from this folder");
const { decodeDraft, encodeDraft } = await import(new URL("src/draft.js", root));
const { computeResult } = await import(new URL("src/core/result.js", root));
const { summaryText } = await import(new URL("src/core/summary.js", root));
const { personLabel, itemLabel } = await import(new URL("src/core/bill.js", root));

const cp = (...codes) => String.fromCodePoint(...codes);
const LISTED = new Set([...Array(0x20).keys(), ...Array.from({ length: 0x21 }, (_, i) => 0x7f + i), 0x2028, 0x2029, 0x61c, 0x200e,
  0x200f, 0x202a, 0x202b, 0x202c, 0x202d, 0x202e, 0x2066, 0x2067, 0x2068, 0x2069]);
const oracle = (text) => [...text].filter((ch) => !LISTED.has(ch.codePointAt(0))).join("");
const hasClass = (text) => [...text].some((ch) => LISTED.has(ch.codePointAt(0)));
const RLO = cp(0x202e), NUL = cp(0), LF = cp(10), CR = cp(13), ACUTE = cp(0x301);

const S2 = (names) => ({ mode: "even", people: names.map((name, i) => ({ id: `p${i + 1}`, name })), subtotalText: "100.00", items: [],
  serviceText: "10", sstText: "6", spare: { rule: "top" }, nextId: names.length + 1 });
const S1 = (itemNames) => ({ mode: "item", people: [{ id: "p1", name: "Aisyah" }, { id: "p2", name: "Ben" }], subtotalText: "",
  items: itemNames.map((name, k) => ({ id: `i${k + 3}`, name, priceText: "1.00", who: ["p1"] })), serviceText: "10", sstText: "6",
  spare: { rule: "top" }, nextId: itemNames.length + 3 });
const env = (bill, version = 2) => JSON.stringify(version === 1 ? { version, bill: { ...bill, spare: undefined } } : { version, bill });

const cases = [];
for (const c of LISTED) {
  const want = c === 10 || c === 13 ? "R" : "A";
  cases.push([`person name A U+${c.toString(16).padStart(4, "0")} B`, env(S2(["A" + cp(c) + "B", "Ben", "Chen"])), want]);
  cases.push([`item name A U+${c.toString(16).padStart(4, "0")} B`, env(S1(["A" + cp(c) + "B"])), want]);
}
cases.push(
  ["name only class characters becomes empty", env(S2([RLO + cp(0x2066) + NUL + cp(0x9f), "Ben", "Chen"])), "A"],
  ["20 letters and 1000 RLO", env(S2(["x".repeat(20) + RLO.repeat(1000), "Ben", "Chen"])), "A"],
  ["21 letters and one RLO", env(S2(["x".repeat(21) + RLO, "Ben", "Chen"])), "R"],
  ["RLO then LF, LF rejects first", env(S2([RLO + LF, "Ben", "Chen"])), "R"],
  ["CR inside class characters", env(S2([NUL + CR + NUL, "Ben", "Chen"])), "R"],
  ["a NUL acute and 18 x, 21 clusters before, 19 after", env(S2(["a" + NUL + ACUTE + "x".repeat(18), "Ben", "Chen"])), "A"],
  ["lone surrogates around NUL join into one emoji", env(S2(["\ud83d" + NUL + "\ude00", "Ben", "Chen"])), "A"],
  ["markup name ending in RLO", env(S2(["<svg onload=f()>" + RLO, "Ben", "Chen"])), "A"],
  ["two names equal after removal", env(S2(["Ben" + RLO, "B" + cp(0x2067) + "en", "Chen"])), "A"],
  ["LS at both ends, the label trims nothing left", env(S2([cp(0x2028) + "Ben" + cp(0x2028), "B", "C"])), "A"],
  ["version 1 draft with class characters", env(S2(["Aisyah" + RLO, cp(0x85) + "Ben", "Chen" + cp(0x2029)]), 1), "A"],
  ["4.5M NUL person name", env(S2([NUL.repeat(4_500_000), "Ben", "Chen"])), "A"],
  ["x and 4.5M NUL person name", env(S2(["x" + NUL.repeat(4_500_000), "Ben", "Chen"])), "A"],
  ["4.5M RLO item name", env(S1([RLO.repeat(4_500_000)])), "A"],
  ["4.5M x person name (unchanged, D8 rejects)", env(S2(["x".repeat(4_500_000), "Ben", "Chen"])), "R"],
);

const rows = [];
for (const [name, text, expected] of cases) {
  const raw = JSON.parse(text).bill;
  const t0 = performance.now();
  let out, threw = null;
  try { out = decodeDraft(text); } catch (error) { threw = String(error); }
  const ms = Math.round(performance.now() - t0);
  const got = threw ? "THREW" : out.ok ? "A" : "R";
  const row = { name, chars: text.length, expected, got, ms, pass: got === expected };
  if (out?.ok) {
    const people = out.bill.people.map((p) => p.name), items = out.bill.items.map((i) => i.name);
    const wantPeople = raw.people.map((p) => oracle(p.name)), wantItems = raw.items.map((i) => oracle(i.name));
    row.names_as_oracle = JSON.stringify(people) === JSON.stringify(wantPeople) && JSON.stringify(items) === JSON.stringify(wantItems);
    row.class_in_names = [...people, ...items].some(hasClass);
    const result = computeResult(out.bill);
    if (result.kind === "even" || result.kind === "item") {
      const lines = summaryText(result).split("\n");
      const labels = out.bill.people.map(personLabel);
      row.summary_rows_are_labels = lines.slice(2, -1).every((line, i) => line.startsWith(labels[i] + " RM "));
    } else {
      row.summary_rows_are_labels = `no summary, result ${result.kind}`;
    }
    row.item_labels = out.bill.items.map(itemLabel).slice(0, 2).map((l) => (l.length > 40 ? `${l.length} chars` : l));
    row.labels = out.bill.people.map(personLabel).map((l) => (l.length > 40 ? `${l.length} chars` : [...l].map((ch) => (ch.codePointAt(0) > 0x7e ? `U+${ch.codePointAt(0).toString(16)}` : ch)).join("")));
    const again = decodeDraft(encodeDraft(out.bill));
    row.round_trip_same_names = again.ok && JSON.stringify(again.bill.people.map((p) => p.name)) === JSON.stringify(people)
      && JSON.stringify(again.bill.items.map((i) => i.name)) === JSON.stringify(items);
    row.pass = row.pass && row.names_as_oracle && !row.class_in_names && row.summary_rows_are_labels !== false && row.round_trip_same_names;
  }
  rows.push(row);
}
const summary = { node: process.version, cases: rows.length, pass: rows.filter((r) => r.pass).length, fail: rows.filter((r) => !r.pass).map((r) => r.name) };
writeFileSync("n2_decoder_h10-results.json", JSON.stringify({ summary, rows }, null, 1));
console.log(JSON.stringify(summary, null, 1));
for (const r of rows.slice(-15)) console.log(`${r.pass ? "ok  " : "FAIL"} ${r.got} (want ${r.expected}) ${String(r.ms).padStart(5)} ms  ${r.name}  ${r.labels ? JSON.stringify(r.labels) : ""}`);
