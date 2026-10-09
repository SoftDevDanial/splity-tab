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

// Dynamic code and other ambient sources. These are everyday words in prose (and JSDoc types use
// import("./x.js")), so they are matched in code only, after codeOnly blanks comments and literal text.
const BANNED_IN_CODE = [
  ["eval", /\beval\b/],
  ["Function", /\bFunction\s*\(|\bnew\s+Function\b/],
  ["import(", /\bimport\s*\(/],
  ["queueMicrotask", /\bqueueMicrotask\b/],
  ["setImmediate", /\bsetImmediate\b/],
  ["performance", /\bperformance\b/],
  ["crypto", /\bcrypto\b/],
  ["WebSocket", /\bWebSocket\b/],
  ["process", /\bprocess\b/],
  ["require", /\brequire\b/],
];

const REGEX_AFTER = "(,=:[!&|?{};+-*%<>~^";
const REGEX_AFTER_WORD = /\b(?:return|typeof|case|do|else|in|of|new|delete|void|throw|instanceof|yield|await)$/;

/** A slash starts a regex literal when the code before it ends in an operator, a bracket or a keyword. */
function regexMayStart(code) {
  const before = code.trimEnd();
  return before === "" || REGEX_AFTER.includes(before.at(-1)) || REGEX_AFTER_WORD.test(before);
}

/** Index of the delimiter that closes the string or regex literal opened at `open` (or the line end). */
function literalEnd(source, open, delimiter) {
  let inClass = false;
  for (let j = open + 1; j < source.length && source[j] !== "\n"; j += 1) {
    const c = source[j];
    if (c === "\\") j += 1;
    else if (delimiter === "/" && (c === "[" || c === "]")) inClass = c === "[";
    else if (c === delimiter && !inClass) return j;
  }
  const lineEnd = source.indexOf("\n", open);
  return lineEnd === -1 ? source.length : lineEnd;
}

/**
 * The source with comments, string text, template text and regex bodies blanked to spaces, delimiters
 * kept, so a scan sees code only. Code inside a template's ${...} is kept, nested templates included.
 */
function codeOnly(source) {
  let code = "";
  let i = 0;
  let depth = 0;
  const templateDepths = [];
  const take = (end, isCode) => {
    const part = source.slice(i, Math.min(end, source.length));
    code += isCode ? part : part.replace(/[^\n]/g, " ");
    i += part.length;
  };
  const templateText = () => {
    let j = i;
    while (j < source.length && source[j] !== "`" && !source.startsWith("${", j)) j += source[j] === "\\" ? 2 : 1;
    take(j, false);
    if (!source.startsWith("${", i)) return take(i + 1, true);
    take(i + 2, true);
    depth += 1;
    templateDepths.push(depth);
  };
  while (i < source.length) {
    const c = source[i];
    if (source.startsWith("//", i)) {
      const end = source.indexOf("\n", i);
      take(end === -1 ? source.length : end, false);
    } else if (source.startsWith("/*", i)) {
      const end = source.indexOf("*/", i + 2);
      take(end === -1 ? source.length : end + 2, false);
    } else if (c === '"' || c === "'" || (c === "/" && regexMayStart(code))) {
      const end = literalEnd(source, i, c);
      take(i + 1, true);
      take(end, false);
      take(end + 1, true);
    } else if (c === "`") {
      take(i + 1, true);
      templateText();
    } else if (c === "}" && templateDepths.at(-1) === depth) {
      templateDepths.pop();
      depth -= 1;
      take(i + 1, true);
      templateText();
    } else {
      if (c === "{") depth += 1;
      else if (c === "}") depth -= 1;
      take(i + 1, true);
    }
  }
  return code;
}

// import x from "a", export { x } from "a", import "a" and import("a").
const SPECIFIER_PATTERNS = [
  /\b(?:import|export)\b[^"'`;]*?\bfrom\s*["']([^"']+)["']/g,
  /\bimport\s*["']([^"']+)["']/g,
  /\bimport\s*\(\s*["']([^"']+)["']\s*\)/g,
];

function bannedNamesIn(source) {
  const code = codeOnly(source);
  return [
    ...BANNED_PATTERNS.filter(([, pattern]) => pattern.test(source)),
    ...BANNED_IN_CODE.filter(([, pattern]) => pattern.test(code)),
  ].map(([name]) => name);
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

test("@R25 the code-only scan reads code, and skips comments, strings, template text and regex bodies", () => {
  assert.deepEqual(bannedNamesIn("const t = `took ${performance.now()} ms`;"), ["performance"]);
  assert.deepEqual(bannedNamesIn("const t = `a ${`b ${eval(x)}`} c`;"), ["eval"]);
  assert.deepEqual(bannedNamesIn("const half = total / 2; const quote = /'/; require(x);"), ["require"]);
  assert.deepEqual(bannedNamesIn(
    "// eval and process\n/* new Function */ const a = 'crypto'; const b = \"import(x)\"; " +
    "const c = `performance`; const d = /setImmediate|WebSocket|queueMicrotask/u;",
  ), []);
  assert.deepEqual(bannedNamesIn("const evaluate = 1; const processed = 2; myFunction(3); importer(4);"), []);
});

// Each plant is served in memory into every real core file, so the scan is proven on the real sources,
// regex literals and templates included. The same text in a comment or a string must not go red.
const CODE_PLANTS = [
  ["eval", "const run = (text) => eval(text);"],
  ["Function", "const make = (body) => Function(body);"],
  ["Function", "const build = (body) => new Function(body);"],
  ["import(", "const load = (name) => import(name);"],
  ["queueMicrotask", "const soon = (fn) => queueMicrotask(fn);"],
  ["setImmediate", "const later = (fn) => setImmediate(fn);"],
  ["performance", "const now = () => performance.now();"],
  ["crypto", "const pick = () => crypto.getRandomValues(new Uint32Array(1))[0];"],
  ["WebSocket", "const open = (url) => new WebSocket(url);"],
  ["process", "const env = () => process.env.SPLIT;"],
  ["require", "const load = (name) => require(name);"],
];
for (const [banned, plant] of CODE_PLANTS) {
  test(`@R25 ${plant} served into each core file goes red as ${banned}`, () => {
    for (const [file, source] of sources) {
      assert.deepEqual(bannedNamesIn(`${source}\n${plant}\n`), [banned], file);
      assert.deepEqual(bannedNamesIn(`${source}\n// ${plant}\nconst note = ${JSON.stringify(plant)};\n`), [], file);
    }
  });
}

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
