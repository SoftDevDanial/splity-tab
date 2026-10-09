import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { resolve, join } from "node:path";
import module from "node:module";
import { pathToFileURL } from "node:url";
import { isDeepStrictEqual } from "node:util";

const CORE_DIR = resolve(import.meta.dirname, "../src/core");

// Two R25 guards. The source scan below is best-effort and secondary: no name scan sees through every
// slash, escape or constructor route (security SEC-05). The runtime trap at the end of this file is the
// primary guard, because it watches what the core really touches whatever the syntax.

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

// ---- Runtime trap, the primary R25 guard ----
// Every banned global and method is replaced by a recorder that still returns the real value, the core
// is imported (so module evaluation is watched too) and every export runs. An access counts only when a
// src/core/ frame is on the stack, so the test runner's own use of a global never counts.

const CORE_URL = pathToFileURL(join(CORE_DIR, "/")).href;
const CORE_FILES = ["money.js", "allocate.js", "bill.js", "result.js", "summary.js"];

const TRAPPED_GLOBALS = [
  "eval", "Function", "setTimeout", "setInterval", "requestAnimationFrame", "queueMicrotask", "setImmediate",
  "performance", "crypto", "WebSocket", "process", "require", "fetch", "XMLHttpRequest", "EventSource",
  "localStorage", "sessionStorage", "indexedDB", "Date", "Intl", "window", "document", "navigator", "parseFloat",
  "globalThis",
];
// [label, owner, key, a line of code that reaches it]: banned methods that need no banned global name.
const TRAPPED_METHODS = [
  ["Date.now", Date, "now", "Date.now();"],
  ["Math.random", Math, "random", "Math.random();"],
  ["Number.parseFloat", Number, "parseFloat", "Number.parseFloat(\"1\");"],
  ["toFixed", Number.prototype, "toFixed", "(1).toFixed(1);"],
  ["Number toLocaleString", Number.prototype, "toLocaleString", "(1).toLocaleString();"],
  ["BigInt toLocaleString", BigInt.prototype, "toLocaleString", "(1n).toLocaleString();"],
  ["Array toLocaleString", Array.prototype, "toLocaleString", "[].toLocaleString();"],
  ["Object toLocaleString", Object.prototype, "toLocaleString", "({}).toLocaleString();"],
  ["Date toLocaleString", Date.prototype, "toLocaleString", "new Date(0).toLocaleString();"],
  ["toLocaleDateString", Date.prototype, "toLocaleDateString", "new Date(0).toLocaleDateString();"],
  ["toLocaleTimeString", Date.prototype, "toLocaleTimeString", "new Date(0).toLocaleTimeString();"],
  ["localeCompare", String.prototype, "localeCompare", "\"a\".localeCompare(\"b\");"],
  ["toLocaleUpperCase", String.prototype, "toLocaleUpperCase", "\"a\".toLocaleUpperCase();"],
  ["toLocaleLowerCase", String.prototype, "toLocaleLowerCase", "\"a\".toLocaleLowerCase();"],
];
// [label, prototype, a line of code that reaches it]: building code from any function value, no name used.
const CONSTRUCTOR_ROUTES = [
  ["Function constructor route", Function.prototype, "void (() => 0).constructor;"],
  ["AsyncFunction constructor route", Object.getPrototypeOf(async () => {}), "void (async () => 0).constructor;"],
  ["GeneratorFunction constructor route", Object.getPrototypeOf(function* () {}), "void (function* () {}).constructor;"],
  ["AsyncGeneratorFunction constructor route", Object.getPrototypeOf(async function* () {}),
    "void (async function* () {}).constructor;"],
];

let armed = false;
let recording = false;
const hits = [];
function record(label) {
  if (!armed || recording) return;
  recording = true;
  const limit = Error.stackTraceLimit;
  Error.stackTraceLimit = 50;
  const fromCore = (new Error().stack ?? "").split("\n").some((line) => line.includes(CORE_URL));
  Error.stackTraceLimit = limit;
  recording = false;
  if (fromCore) hits.push(label);
}

/** Runs `body` with every trap installed and armed, restores everything, and returns the core's hits. */
async function trapped(body) {
  const saved = [];
  const replace = (owner, key, descriptor) => {
    saved.push([owner, key, Object.getOwnPropertyDescriptor(owner, key)]);
    Object.defineProperty(owner, key, { ...descriptor, configurable: true });
  };
  for (const name of TRAPPED_GLOBALS) {
    const original = Object.getOwnPropertyDescriptor(globalThis, name);
    const read = () => (original?.get ? original.get.call(globalThis) : original?.value);
    replace(globalThis, name, { get() { record(name); return read(); } });
  }
  for (const [label, owner, key] of TRAPPED_METHODS) {
    const real = owner[key];
    replace(owner, key, { writable: true, value: function (...args) { record(label); return real.apply(this, args); } });
  }
  for (const [label, prototype] of CONSTRUCTOR_ROUTES) {
    const real = prototype.constructor;
    replace(prototype, "constructor", { get() { record(label); return real; } });
  }
  armed = true;
  try {
    await body();
  } finally {
    armed = false;
    for (const [owner, key, descriptor] of saved.reverse()) {
      if (descriptor === undefined) delete owner[key];
      else Object.defineProperty(owner, key, descriptor);
    }
  }
  return hits.splice(0);
}

// Each trapped run loads its own copy of the core: a run id rides on every core URL and on every import
// between core files, so module evaluation is always watched, whatever loaded the core before. A plant
// is extra code appended to one file in memory, so the trap is shown red without writing any file.
const plants = new Map();
let runs = 0;
module.registerHooks({
  resolve(specifier, context, next) {
    const out = next(specifier, context);
    const parent = context.parentURL?.startsWith(CORE_URL) ? new URL(context.parentURL) : null;
    const run = parent?.searchParams.get("r25-run");
    if (!run || !out.url.startsWith(CORE_URL)) return out;
    const url = new URL(out.url);
    url.searchParams.set("r25-run", run);
    return { ...out, url: url.href };
  },
  load(url, context, next) {
    const out = next(url, context);
    const plant = url.startsWith(CORE_URL) ? plants.get(new URL(url).searchParams.get("r25-plant")) : undefined;
    if (plant === undefined) return out;
    const text = typeof out.source === "string" ? out.source : new TextDecoder().decode(out.source);
    return { ...out, source: `${text}\n${plant}\n` };
  },
});
function coreUrl(file, run, plantKey) {
  const url = new URL(file, CORE_URL);
  url.searchParams.set("r25-run", run);
  if (plantKey !== undefined) url.searchParams.set("r25-plant", plantKey);
  return url.href;
}
async function importCore() {
  const run = String(runs += 1);
  const loaded = await Promise.all(CORE_FILES.map((file) => import(coreUrl(file, run))));
  return Object.fromEntries(CORE_FILES.map((file, index) => [file.replace(".js", ""), loaded[index]]));
}
function importPlanted(file, plant) {
  const run = String(runs += 1);
  plants.set(run, plant);
  return import(coreUrl(file, run, run));
}

/** Calls every export on representative input: both modes, every blocking path and both throws. */
function runEveryExport({ money, allocate, bill, result, summary }) {
  void money.AMOUNT_MIN_CENTS;
  void money.AMOUNT_MAX_CENTS;
  void bill.LIMITS;
  let b = bill.newBill();
  for (let n = 0; n < 10; n += 1) b = bill.addPerson(b);
  b = bill.setPersonName(b, "p1", " A\u{2028}B\u{202E} ");
  b = bill.setSubtotalText(b, "99999.99");
  summary.summaryText(result.computeResult(b));
  result.computeResult(bill.setSubtotalText(b, "0"));
  b = bill.setMode(b, "item");
  result.computeResult(b);
  for (let n = 0; n < 50; n += 1) {
    b = bill.addItem(b);
    const id = b.items.at(-1).id;
    b = bill.setItemName(b, id, "x");
    b = bill.setItemPriceText(b, id, "99999.99");
    b = bill.toggleItemPerson(b, id, b.people[n % 12].id);
  }
  summary.summaryText(result.computeResult(b));
  result.computeResult(bill.setServiceText(b, "31"));
  result.computeResult(bill.setSstText(b, ""));
  result.computeResult(bill.setItemPriceText(b, b.items[0].id, "x"));
  result.computeResult(bill.toggleItemPerson(b, b.items[0].id, b.people[0].id));
  bill.removeItem(b, b.items[0].id);
  bill.removePerson(b, "p3");
  bill.personLabel(b.people[0], 0);
  bill.itemLabel(b.items[0], 0);
  money.parseAmount(" 12.50 ");
  money.parseRate("6.25", 20);
  money.formatMoney(779999922);
  money.formatRate(625);
  allocate.allocateEvenly(10, 3);
  allocate.allocateByWeight(10, [1, 2, 3]);
  result.billCharges(10000, 1000, 600);
  assert.throws(() => summary.summaryText({ kind: "blocked", reason: "rates" }), TypeError);
  assert.throws(() => allocate.allocateByWeight(10, []), RangeError);
}

test("@R25 runtime trap: the core touches no banned global or method while it loads and runs", async () => {
  const used = new Set();
  const watch = (namespace) => new Proxy(namespace, { get: (target, key) => (used.add(key), target[key]) });
  let modules = {};
  const found = await trapped(async () => {
    modules = await importCore();
    runEveryExport(Object.fromEntries(Object.entries(modules).map(([name, ns]) => [name, watch(ns)])));
  });
  assert.deepEqual(found, []);
  const unexercised = Object.values(modules).flatMap((ns) => Object.keys(ns)).filter((name) => !used.has(name));
  assert.deepEqual(unexercised, [], "every export runs under the trap");
});

test("@R25 runtime trap: every trap fires for core code and not for test code (negative control)", async () => {
  const controls = [
    ...TRAPPED_GLOBALS.map((name) => [name, `void ${name};`]),
    ...TRAPPED_METHODS.map(([label, , , line]) => [label, line]),
    ...CONSTRUCTOR_ROUTES.map(([label, , line]) => [label, line]),
  ];
  for (const [label, line] of controls) {
    const found = await trapped(() => importPlanted("money.js", line));
    assert.ok(found.includes(label), `${label}: ${line} gave ${JSON.stringify(found)}`);
  }
  assert.deepEqual(await trapped(async () => { void globalThis.performance; Math.random(); }), []);
});

// The negative control above builds its cases from the same three arrays, so a trap deleted from an array
// would take its own control with it and the suite would stay green. This pin names every trap, so deleting
// one is red. Adding or removing a trap is a deliberate edit of the pin too.
const sorted = (names) => [...names].sort();
test("@R25 runtime trap: the trap lists are exactly the pinned ones, so no trap is dropped unseen", () => {
  assert.deepEqual(sorted(TRAPPED_GLOBALS), sorted([
    "eval", "Function", "setTimeout", "setInterval", "requestAnimationFrame", "queueMicrotask", "setImmediate",
    "performance", "crypto", "WebSocket", "process", "require", "fetch", "XMLHttpRequest", "EventSource",
    "localStorage", "sessionStorage", "indexedDB", "Date", "Intl", "window", "document", "navigator", "parseFloat",
    "globalThis",
  ]), "TRAPPED_GLOBALS");
  assert.deepEqual(sorted(TRAPPED_METHODS.map(([label]) => label)), sorted([
    "Date.now", "Math.random", "Number.parseFloat", "toFixed", "Number toLocaleString", "BigInt toLocaleString",
    "Array toLocaleString", "Object toLocaleString", "Date toLocaleString", "toLocaleDateString",
    "toLocaleTimeString", "localeCompare", "toLocaleUpperCase", "toLocaleLowerCase",
  ]), "TRAPPED_METHODS");
  assert.deepEqual(sorted(CONSTRUCTOR_ROUTES.map(([label]) => label)), sorted([
    "Function constructor route", "AsyncFunction constructor route", "GeneratorFunction constructor route",
    "AsyncGeneratorFunction constructor route",
  ]), "CONSTRUCTOR_ROUTES");
});

// The source scan bans these names too, and a name that is banned but not trapped is guarded by the scan
// alone (globalThis was, and an identifier written with a unicode escape reached it unseen). `import(` is
// syntax, not a value, so no recorder can watch it.
test("@R25 runtime trap: every name the source scan bans has a trap", () => {
  const watched = new Set([
    ...TRAPPED_GLOBALS,
    ...TRAPPED_METHODS.flatMap(([label]) => [label, label.split(" ").at(-1)]),
  ]);
  const banned = [...BANNED.map((name) => name.replaceAll("\\", "")), ...BANNED_IN_CODE.map(([name]) => name)];
  assert.deepEqual(banned.filter((name) => name !== "import(" && !watched.has(name)), []);
});

const trapSites = () => [
  ...TRAPPED_GLOBALS.map((name) => [globalThis, name]),
  ...TRAPPED_METHODS.map(([, owner, key]) => [owner, key]),
  ...CONSTRUCTOR_ROUTES.map(([, prototype]) => [prototype, "constructor"]),
];
const describeSites = () => trapSites().map(([owner, key]) => Object.getOwnPropertyDescriptor(owner, key));
/** The keys of the trap sites whose property is not what `snapshot` (from `describeSites`) recorded. */
const changedSince = (snapshot) =>
  trapSites().filter(([owner, key], i) => !isDeepStrictEqual(Object.getOwnPropertyDescriptor(owner, key), snapshot[i]))
    .map(([, key]) => key);

test("@R25 runtime trap: every trap is put back after a run, also after a body that throws", async () => {
  const before = describeSites();
  await trapped(async () => { assert.equal(changedSince(before).length, trapSites().length, "every site is trapped"); });
  assert.deepEqual(changedSince(before), []);
  await assert.rejects(trapped(() => { throw new Error("boom"); }), /boom/);
  assert.deepEqual(changedSince(before), []);
});

test("@R25 runtime trap: every run loads its own copy of the core", async () => {
  const first = await importCore();
  const second = await importCore();
  assert.notEqual(first.money, second.money);
});

// The security re-check's plants (SEC-05, F1 to F10): live code that the source scan above lets through.
const AUDITOR_PLANTS = [
  ["F1", "process", "let r04Hits = 0; const r04Rate = r04Hits++ / process.uptime();"],
  ["F2", "performance", "const r04Range = { in: 2 }; const r04Ratio = r04Range.in / performance.now();"],
  ["F3", "performance", "const r04Q = \"'\"; if (r04Q) /'/.test(r04Q) && performance.now();"],
  ["F4", "process", "const r04K = \"k\"; if (r04K) /`/.test(r04K);\nconst r04Env = process.env.PATH;"],
  ["F4b", "process", "const r04K = \"k\"; if (r04K) /`/.test(r04K) || process.env.PATH; const r04Tick = \"`\";"],
  ["F5", "performance", "const r04U = \"u\"; if (r04U) /\\/\\//.test(r04U) || performance.now();"],
  ["F6", "process", "export function r04Label(n) {\n  return `${n++ / 2} items`;\n}\nconst r04Pid = process.pid;"],
  ["F6b", "process",
    "export function r04Label(n) {\n  return `${n++ / 2} items`;\n}\nconst r04Pid = process.pid; const r04Tick = \"`\";"],
  ["F7", "Function", "const r04F = Function; const r04V = r04F(\"return 1\")();"],
  ["F8", "process", "const r04P = \\u{70}rocess.pid;"],
  ["F9", "Date", "const r04D = \\u{44}ate.now();"],
  ["F10", "Function constructor route", "const r04C = (() => 0).constructor(\"return 1\")();"],
];
for (const [id, label, plant] of AUDITOR_PLANTS) {
  test(`@R25 runtime trap catches the security re-check's ${id} plant in every core file`, async () => {
    for (const file of CORE_FILES) {
      const found = await trapped(() => importPlanted(file, plant));
      assert.ok(found.includes(label), `${id} in ${file} gave ${JSON.stringify(found)}`);
    }
  });
}
