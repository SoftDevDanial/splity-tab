// R05 preload: serves src/core/summary.js with its CONTROLS class replaced (in memory only) by the regex
// source in R05_CLASS (base64), so the REAL tests/summary.test.js runs against a mutant. Used as
//   node --import <this file as a file URL> tests/summary.test.js
import module from "node:module";

const replacement = Buffer.from(process.env.R05_CLASS ?? "", "base64").toString("utf8");
const ORIGINAL = "/[\\p{Cc}\\p{Zl}\\p{Zp}\\p{Bidi_Control}]/gu";
module.registerHooks({
  load(url, context, next) {
    const out = next(url, context);
    if (!url.endsWith("/src/core/summary.js") || replacement === "") return out;
    const text = typeof out.source === "string" ? out.source : new TextDecoder().decode(out.source);
    if (!text.includes(ORIGINAL)) throw new Error("R05: original CONTROLS class not found in summary.js");
    return { ...out, source: text.replace(ORIGINAL, replacement) };
  },
});
