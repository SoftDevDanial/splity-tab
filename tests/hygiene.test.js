import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { resolve, join } from "node:path";

const CORE_DIR = resolve(import.meta.dirname, "../src/core");

// Whole-word match, so "Datestamp" would pass but "Date" would not. Comments are scanned too:
// a banned name in a comment is a sign the code was meant to use it.
const BANNED = [
  "window", "document", "globalThis", "localStorage", "sessionStorage", "navigator", "fetch",
  "XMLHttpRequest", "Date", "Math\\.random", "parseFloat", "Number\\.parseFloat", "toFixed",
  // The locale-format and timer non-goals.
  "Intl", "toLocaleString", "toLocaleDateString", "setTimeout", "setInterval", "requestAnimationFrame",
];
const BANNED_PATTERNS = BANNED.map((name) => [name, new RegExp(`\\b${name}\\b`)]);

// import x from "a", export { x } from "a", import "a" and import("a").
const SPECIFIER_PATTERNS = [
  /\b(?:import|export)\b[^"'`;]*?\bfrom\s*["']([^"']+)["']/g,
  /\bimport\s*["']([^"']+)["']/g,
  /\bimport\s*\(\s*["']([^"']+)["']\s*\)/g,
];

function bannedNamesIn(source) {
  return BANNED_PATTERNS.filter(([, pattern]) => pattern.test(source)).map(([name]) => name);
}

function specifiersIn(source) {
  return SPECIFIER_PATTERNS.flatMap((pattern) => [...source.matchAll(pattern)].map((m) => m[1]));
}

/** True when a specifier is relative and resolves inside src/core/. */
function staysInCore(specifier) {
  if (!specifier.startsWith("./") && !specifier.startsWith("../")) return false;
  const target = resolve(CORE_DIR, specifier);
  return target === CORE_DIR || target.startsWith(join(CORE_DIR, "/"));
}

const files = readdirSync(CORE_DIR, { recursive: true }).filter((name) => name.endsWith(".js"));
const sources = files.map((name) => [name, readFileSync(join(CORE_DIR, name), "utf8")]);

test("@R25 the scan sees the core files", () => {
  assert.deepEqual([...files].sort(), ["allocate.js", "bill.js", "money.js", "result.js", "summary.js"]);
});

test("@R25 the scanner catches what it should (negative control)", () => {
  assert.deepEqual(bannedNamesIn("const t = Date.now(); fetch(url); x.toFixed(2)"), ["fetch", "Date", "toFixed"]);
  assert.deepEqual(
    bannedNamesIn("Math.random() + Number.parseFloat(s) + window.document"),
    ["window", "document", "Math\\.random", "parseFloat", "Number\\.parseFloat"],
  );
  assert.deepEqual(
    bannedNamesIn("new Intl.NumberFormat(); n.toLocaleString(); d.toLocaleDateString(); " +
      "setTimeout(f, 0); setInterval(f, 9); requestAnimationFrame(f)"),
    ["Intl", "toLocaleString", "toLocaleDateString", "setTimeout", "setInterval", "requestAnimationFrame"],
  );
  assert.deepEqual(bannedNamesIn("const dateText = 1; const myFetch = 2"), []);
  assert.deepEqual(bannedNamesIn("const localeName = 1; const setTimeoutMs = 2; // locale-independent"), []);
  assert.deepEqual(specifiersIn('import a from "./x.js"; export { b } from "../y.js"; import "z"; import("w")'),
    ["./x.js", "../y.js", "z", "w"]);
  assert.equal(staysInCore("../ui/x.js"), false);
  assert.equal(staysInCore("node:fs"), false);
  assert.equal(staysInCore("./money.js"), true);
});

for (const [name, source] of sources) {
  test(`@R25 ${name} uses no banned name`, () => {
    assert.deepEqual(bannedNamesIn(source), []);
  });

  test(`@R25 ${name} imports only from src/core/`, () => {
    for (const specifier of specifiersIn(source)) {
      assert.ok(staysInCore(specifier), `${name} imports ${specifier}`);
    }
  });
}

test("@R25 the core files do import each other (the import scan is not blind)", () => {
  const all = sources.flatMap(([, source]) => specifiersIn(source));
  assert.ok(all.includes("./money.js") && all.includes("./allocate.js") && all.includes("./bill.js"));
});
