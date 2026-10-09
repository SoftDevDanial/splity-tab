// Counts raw control characters, separators, bidi controls and long dashes in the files of this module.
// A planted bidi control or an em dash would hide in a diff, so this reads the bytes. Run from the project root.
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const ROOTS = ["src", "tests", "docs/modules/split-core/spec.md", "docs/modules/split-core/qa.md",
  "docs/modules/split-core/BUILD.md", "docs/modules/split-core/findings",
  "docs/modules/split-core/qa/code-review/20261009-134620"];
const files = [];
function walk(path) {
  let entries;
  try { entries = readdirSync(path, { withFileTypes: true }); } catch { files.push(path); return; }
  for (const entry of entries) walk(join(path, entry.name));
}
ROOTS.forEach(walk);

const SUSPECT = /[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}\u{FEFF}]/gu;
const DASH = /[\u{2013}\u{2014}]/gu;
let total = 0;
for (const file of files.filter((f) => /\.(js|md|mjs|txt)$/.test(f))) {
  const text = readFileSync(file, "utf8").replace(/[\r\n\t]/g, "");
  const suspect = (text.match(SUSPECT) ?? []).length;
  const dashes = (text.match(DASH) ?? []).length;
  total += suspect + dashes;
  if (suspect + dashes > 0) console.log(file, "controls/separators/bidi:", suspect, "long dashes:", dashes);
}
console.log(`scanned ${files.length} files, ${total} suspect characters (LF, CR and TAB ignored)`);
