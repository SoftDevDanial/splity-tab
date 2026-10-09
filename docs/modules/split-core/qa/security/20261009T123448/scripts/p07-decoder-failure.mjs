// P07. What the core does when split-app's draft decoder (rules D1 to D12) fails to reject a bad bill.
// Not a core requirement. Recorded so the cross-module contract is explicit.
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { computeResult } from "../../../../../../../src/core/result.js";
import { summaryText } from "../../../../../../../src/core/summary.js";
import { addPerson, addItem, toggleItemPerson, setPersonName } from "../../../../../../../src/core/bill.js";

const base = () => ({
  mode: "item",
  people: [{ id: "p1", name: "A" }, { id: "p2", name: "B" }, { id: "p12", name: "L" }],
  subtotalText: "100.00",
  items: [{ id: "i4", name: "T", priceText: "10.00", who: ["p1"] }],
  serviceText: "10", sstText: "6", nextId: 13,
});
const describe = (f) => {
  try {
    const r = f();
    if (r && typeof r === "object" && "kind" in r) {
      const sums = r.kind === "even" || r.kind === "item" ? ` adds up=${r.check.share === r.charges.total}` : "";
      return `returns ${r.kind}${r.reason ? `/${r.reason}` : ""}${r.count ? ` count=${r.count}` : ""}${sums}${r.rows ? ` rows=${JSON.stringify(r.rows.map((x) => [x.name, x.share]))}` : ""}`;
    }
    return `returns ${JSON.stringify(r)?.slice(0, 160)}`;
  } catch (e) {
    return `THROWS ${e.constructor.name}: ${e.message}`;
  }
};
const with_ = (patch) => ({ ...base(), ...patch });
const CASES = [
  ["D5 mode 'EVEN' (unknown)", () => computeResult(with_({ mode: "EVEN" }))],
  ["D5 mode missing", () => computeResult(with_({ mode: undefined }))],
  ["D5 mode '__proto__'", () => computeResult(with_({ mode: "__proto__" }))],
  ["D6 people [] in even mode", () => computeResult(with_({ mode: "even", people: [] }))],
  ["D6 people [] in item mode", () => computeResult(with_({ people: [] }))],
  ["D6 one person, even", () => computeResult(with_({ mode: "even", people: [{ id: "p1", name: "A" }] }))],
  ["D6 13 people, even", () => computeResult(with_({ mode: "even", people: Array.from({ length: 13 }, (_, i) => ({ id: `p${i + 1}`, name: "" })) }))],
  ["D6 duplicate person id p1 x2, item on p1", () => computeResult(with_({ people: [{ id: "p1", name: "A" }, { id: "p1", name: "A2" }, { id: "p2", name: "B" }] }))],
  ["D6 name is a number", () => computeResult(with_({ people: [{ id: "p1", name: 5 }, { id: "p2", name: "B" }] }))],
  ["D6 name is null", () => computeResult(with_({ people: [{ id: "p1", name: null }, { id: "p2", name: "B" }] }))],
  ["D6 people is an object", () => computeResult(with_({ people: { 0: { id: "p1", name: "A" }, length: 1 } }))],
  ["D7 who has an unknown id only", () => computeResult(with_({ items: [{ id: "i4", name: "", priceText: "10", who: ["p99"] }] }))],
  ["D7 who has p1 twice", () => computeResult(with_({ items: [{ id: "i4", name: "", priceText: "10", who: ["p1", "p1"] }] }))],
  ["D7 who is the STRING 'p12'", () => computeResult(with_({ items: [{ id: "i4", name: "", priceText: "10", who: "p12" }] }))],
  ["D7 who missing", () => computeResult(with_({ items: [{ id: "i4", name: "", priceText: "10" }] }))],
  ["D7 priceText is a number", () => computeResult(with_({ items: [{ id: "i4", name: "", priceText: 10, who: ["p1"] }] }))],
  ["D7 60 items (above 50)", () => computeResult(with_({ items: Array.from({ length: 60 }, (_, i) => ({ id: `i${i + 20}`, name: "", priceText: "99999.99", who: ["p1"] })) }))],
  ["D9 serviceText null", () => computeResult(with_({ serviceText: null }))],
  ["D9 subtotalText number, even", () => computeResult(with_({ mode: "even", subtotalText: 100 }))],
  ["D10 nextId '5' (string), addPerson twice", () => addPerson(addPerson(with_({ nextId: "5" }))).people.map((p) => p.id)],
  ["D10 nextId 1 (stale), addPerson", () => addPerson(with_({ nextId: 1 })).people.map((p) => p.id)],
  ["D10 nextId 1, addItem then tap p1", () => toggleItemPerson(addItem(with_({ nextId: 4 })), "i4", "p2").items.map((i) => [i.id, i.who])],
  ["D10 nextId NaN, addPerson", () => addPerson(with_({ nextId: Number.NaN })).people.map((p) => p.id)],
  ["duplicate ids: setPersonName p1 renames both", () => setPersonName(with_({ people: [{ id: "p1", name: "A" }, { id: "p1", name: "A2" }] }), "p1", "Z").people],
  ["summaryText of a forged result with a non-string name", () => summaryText({ kind: "even", charges: { total: 1, subtotal: 1, service: 0, sst: 0, serviceBp: 0, sstBp: 0 }, rows: [{ name: 7, share: 1 }], check: { share: 1 } })],
];
for (const [title, f] of CASES) console.log(`${title.padEnd(48)} ${describe(f)}`);

// Quadratic cost of holderIndexes (people x items x who) when D6/D7 bounds are not enforced.
console.log("\nholderIndexes cost with P people and one item tapped by all P (child process, hard kill at 30 s):");
const child = fileURLToPath(new URL("./p07-child.mjs", import.meta.url));
const pids = [];
for (const p of [1000, 2000, 4000, 8000, 16000]) {
  const res = spawnSync(process.execPath, [child, String(p)], { timeout: 30000, killSignal: "SIGKILL", encoding: "utf8" });
  pids.push(res.pid);
  console.log(`  P=${p}: ${res.error ? res.error.code : res.stdout.trim()}`);
}
console.log(`child PIDs (exited): ${pids.join(",")}`);
