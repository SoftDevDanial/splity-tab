// In-memory mutation harness. Loaded with `node --import <this file> <test file>`, with MUT_ID naming
// one entry of mutants-fix.mjs (which re-exports the base mutants of mutants.mjs). It changes source text
// only as it is loaded (a module load hook) or read (fs.readFileSync, which the hygiene scan uses).
// No file under src/ or tests/ is ever written.
import module, { syncBuiltinESMExports } from "node:module";
import fs from "node:fs";
import { relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = process.cwd();
const id = process.env.MUT_ID ?? "";
const { MUTANTS } = await import("./mutants-fix.mjs");
const mutant = MUTANTS.get(id);
if (mutant === undefined) {
  process.stderr.write(`MUT-UNKNOWN ${id}\n`);
  process.exit(3);
}

const SENTINEL = "//MUT-APPLIED";
const announced = new Set();
const relOf = (path) => relative(ROOT, resolve(path)).split("\\").join("/");

function mutate(rel, text, via) {
  const edit = mutant.edits[rel];
  if (edit === undefined || text.includes(SENTINEL)) return text;
  const out = `${edit(text)}\n${SENTINEL}\n`;
  if (!announced.has(`${rel} ${via}`)) {
    announced.add(`${rel} ${via}`);
    process.stderr.write(`MUT-APPLIED ${id} ${rel} via ${via}\n`);
  }
  return out;
}

module.registerHooks({
  load(url, context, next) {
    const out = next(url, context);
    if (!url.startsWith("file:") || out.source == null) return out;
    const rel = relOf(fileURLToPath(url.split("?")[0]));
    if (mutant.edits[rel] === undefined) return out;
    const text = typeof out.source === "string" ? out.source : new TextDecoder().decode(out.source);
    return { ...out, source: mutate(rel, text, "load") };
  },
});

const realRead = fs.readFileSync;
fs.readFileSync = function patchedReadFileSync(path, options) {
  const out = realRead.apply(this, arguments);
  const wantsText = typeof options === "string" || typeof options?.encoding === "string";
  if (!wantsText || typeof out !== "string" || (typeof path !== "string" && !(path instanceof URL))) return out;
  const rel = relOf(path instanceof URL ? fileURLToPath(path) : path);
  return mutant.edits[rel] === undefined ? out : mutate(rel, out, "fs");
};
syncBuiltinESMExports();
