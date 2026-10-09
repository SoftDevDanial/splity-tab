// R04 child: proves a planted snippet is real module code that reaches a banned facility. A load hook
// appends the snippet (base64 in R04_PLANT) to src/core/money.js in memory, traps record access to the
// banned globals, and the patched module is imported. Prints one JSON line.
import module from "node:module";

const plant = Buffer.from(process.env.R04_PLANT ?? "", "base64").toString("utf8");
const CORE = new URL("../../../../../../../src/core/", import.meta.url).href;
module.registerHooks({
  load(url, context, next) {
    const out = next(url, context);
    if (url !== `${CORE}money.js`) return out;
    const text = typeof out.source === "string" ? out.source : new TextDecoder().decode(out.source);
    return { ...out, source: `${text}\n${plant}\n` };
  },
});

const hits = [];
let armed = false;
const G = globalThis;
for (const name of ["performance", "process", "eval", "Function", "Date", "fetch", "crypto", "setImmediate", "queueMicrotask"]) {
  const desc = Object.getOwnPropertyDescriptor(G, name);
  const real = desc ? ("value" in desc ? desc.value : desc.get?.call(G)) : undefined;
  Object.defineProperty(G, name, { configurable: true, get() { if (armed) hits.push(name); return real; } });
}
const RealFunction = Function.prototype.constructor;
Object.defineProperty(Function.prototype, "constructor", {
  configurable: true,
  get() { if (armed) hits.push("Function.prototype.constructor"); return RealFunction; },
});

let error = null;
armed = true;
try {
  await import(`${CORE}money.js`);
} catch (e) {
  error = `${e.constructor.name}: ${e.message}`;
}
armed = false;
const out = { reached: [...new Set(hits)], error };
console.log(JSON.stringify(out));
