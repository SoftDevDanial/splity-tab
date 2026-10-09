// R04 preload for the REAL tests/hygiene.test.js: every read of a file under src/core/ returns the file
// with one planted snippet appended (in memory only, nothing on disk changes). Used as
//   node --import <this file> tests/hygiene.test.js
// with R04_PLANT set to the snippet in base64.
import fs from "node:fs";
import { syncBuiltinESMExports } from "node:module";

const plant = Buffer.from(process.env.R04_PLANT ?? "", "base64").toString("utf8");
const realRead = fs.readFileSync;
fs.readFileSync = function patchedRead(file, ...rest) {
  const out = realRead.call(this, file, ...rest);
  const name = String(file).split(String.fromCharCode(92)).join("/");
  if (plant !== "" && /\/src\/core\/[a-z]+\.js$/.test(name) && typeof out === "string") return `${out}\n${plant}\n`;
  return out;
};
syncBuiltinESMExports();
