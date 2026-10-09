// How long does the shipped decoder take to reject a hostile draft with one huge name? Usage: node time_decoder.mjs <tree>
// Result on the shipped tree: 2 MB of letters rejected in 235 ms, 4 MB in 480 ms, 2 MB of combining marks (one cluster) ACCEPTED in 9 ms.
import { pathToFileURL } from "node:url";
import path from "node:path";

const tree = process.argv[2];
const { decodeDraft } = await import(pathToFileURL(path.join(tree, "src", "draft.js")).href);
const person = (n, name = `P${n}`) => ({ id: `p${n}`, name });
const draft = (name) => JSON.stringify({
  version: 1,
  bill: { mode: "even", people: [person(1, name), person(2)], subtotalText: "", items: [], serviceText: "10", sstText: "6", nextId: 3 },
});

for (const [label, make] of [
  ["2 million plain letters", () => "a".repeat(2_000_000)],
  ["2 million combining marks on one letter (one cluster)", () => "a" + "́".repeat(2_000_000)],
  ["4 million plain letters", () => "a".repeat(4_000_000)],
]) {
  const text = draft(make());
  const started = process.hrtime.bigint();
  const result = decodeDraft(text);
  const ms = Number(process.hrtime.bigint() - started) / 1e6;
  console.log(`${label}: ${(text.length / 1e6).toFixed(1)} MB draft, ok=${result.ok}, ${ms.toFixed(0)} ms`);
}
