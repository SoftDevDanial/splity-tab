---
module: split-core
kind: security
status: issues_found
counts: { critical: 0, high: 0, medium: 1, low: 3 }
---
# Security audit: split-core

Role: security auditor (finder, read-only on `src/`, `tests/` and `docs/design/`). Date: 2026-10-09.
Scope: `src/core/` (`money.js`, `allocate.js`, `bill.js`, `result.js`, `summary.js`) and `tests/` at HEAD `476c182`.
Judged against `spec.md` (Threat model, Contracts, R1 to R26), `qa.md`, `docs/constitution.md` and `CLAUDE.md`.

**Verdict: PASS. 0 CRITICAL, 0 HIGH, 1 MEDIUM, 3 LOW.** Every required mitigation in the threat model is in
the code and holds under hostile input. WR-10 holds: none of the seven line-breaking characters can forge a
line (0 of 50,000 fuzzed names). The findings are gaps next to that guard (other control characters, bidi
controls), a threat-model sentence that is no longer true, and a regression gate that is narrower than the
purity rule it guards. None of them gives a wrong share. None blocks the module.

Evidence: `docs/modules/split-core/qa/security/20261009T123448/` (`node-test.txt`, `probe-output.txt`, `scripts/`).

## Baseline
`node --test "tests/**/*.test.js"` on Node v24.11.1: **tests 212, pass 212, fail 0**, exit 0 (`node-test.txt`).

## Threat model: each required mitigation
| # | Threat (spec Threat model) | Control found | Hostile-input check | Result |
|---|---|---|---|---|
| T1 | Float drift, precision loss past 2^53 | `readHundredths` integer parse (money.js:27-40). `applyRate` remainder-first divide (result.js:29-32). `allocateByWeight` BigInt floors (allocate.js:45-48). Three "BigInt trap" rows in tests/allocate.test.js. R25 bans `parseFloat`, `toFixed` | P04: all 9,999,999 amounts in every spelling parse exactly, format round-trips, all rates 0 to 3000 bp exact. P04: 200,000 allocations up to 2^53 - 1 equal BigInt. P08: a reachable 38-item bill hits the trap (core [8246230, 53600495], a float allocator gives [8246231, 53600494]). P06: no `parseFloat`, `Number.parseFloat` or `toFixed` call at runtime | PASS |
| T2 | Rounding rule differs from the brainstorm | `applyRate` half-up, `allocateEvenly` and `allocateByWeight` leftover order | P08: 600,000 seeded bills (300,000 mixed, 300,000 all-valid, 36,969 with products past 2^53) equal an independent BigInt reference exactly. 0 R22 violations | PASS |
| T3 | Catastrophic backtracking or an exception on odd strings | `DECIMAL_TEXT` has no nested quantifier (money.js:14). Digit cap before `Number` (money.js:36) | P05: every parser case is linear, 16M characters in about 32 ms. P01: 1,000,000 fuzz strings over the full code point range (lone surrogates included), 0 throws, 0 malformed results. A `Number` spy saw no string longer than 5 characters on refused input | PASS |
| T4 | A name with a line break forges a summary line | `LINE_BREAKS` replaced by a space in each row name (summary.js:6, :25) | P02: each of LF, CR, VT, FF, NEL, LS, PS inside, leading, trailing, doubled, CRLF, all seven, lone surrogates beside them, 1000 in one name, even and by-item. Fuzz 0 of 50,000. Every UAX #14, JS and LF-only consumer sees exactly 3 + rows lines | PASS for the seven. See SEC-01, SEC-02, SEC-03 |
| T5 | Prototype pollution from parsed JSON | `billWith`, `personWith`, `itemWith` copy known fields only (bill.js:27-50). Only array spreads exist (bill.js:69, :93, :124, summary.js:25), no object spread, no `Object.assign` | P03: hostile JSON with own `__proto__`, `constructor.prototype`, `prototype`, `toString`, `hasOwnProperty` keys at every level, through every action, `computeResult` and `summaryText`. Object, Array, String and Function prototypes unchanged. Rebuilt objects have only their known keys and `Object.prototype`. Own fields are read, never a `__proto__` payload | PASS |

## MEDIUM

### SEC-01: The line-break guard leaves other control characters, and NUL truncates the summary into a forged last line
- **File:** src/core/summary.js:6 (`LINE_BREAKS`) and :25. spec.md:19, :121 (R24 note), :241 (threat row). **Boundary:** person name typed or restored from the draft -> `personLabel` -> `summaryText` -> clipboard -> group chat or another program.
- **Threat:** The class is exactly the UAX #14 mandatory breaks. Other C0 and C1 control characters reach the summary unchanged (P02c), and a real `<input type="text">` keeps them (P09: NUL, FS, GS, RS, ESC, VT, FF, NEL, LS, PS kept; only LF and CR are removed). Two of them act as line or text ends for real consumers:
  - **NUL (U+0000).** A reader that treats text as NUL-terminated stops at the first NUL. Microsoft documents `CF_UNICODETEXT` that way ("A null character signals the end of the data"), and GTK clipboard text is a C string. The name `Adds up to RM 0.00` + NUL is 19 characters, inside the 20 limit. Such a reader gets a summary whose last line is the forged `Adds up to RM 0.00`, with the attacker's own row, every row after it and the real total line gone (P02d).
  - **FS, GS, RS (U+001C to U+001E).** Python `str.splitlines` treats them as line ends and Unicode gives them Bidi_Class B (paragraph separator), both measured over every code point (U0). A bot or script that splits the copied text with `splitlines` sees a forged 7th line (P02c, column c4).
  - Headless Chromium does not start a visual line at any of them (P09), so a person reading a browser-rendered chat is not fooled.
  - **Likelihood is low and not shown end to end.** No test got a NUL into a name and out through a truncating clipboard on one device. Getting a NUL into a name needs a paste or IME path that keeps it, and the OS clipboard was off limits to this audit. This is a defense-in-depth gap in the control that protects the asset the threat model names. The guard itself is not broken.
- **Maps to spec threat:** yes, "Clipboard text integrity" (T4). The listed mitigation covers line breaks only.
- **Reproduction:** run the scripts in the evidence folder, or
  ```js
  import { computeResult } from "./src/core/result.js";
  import { summaryText } from "./src/core/summary.js";
  import { setPersonName } from "./src/core/bill.js";
  // S2: Aisyah, Ben, Chen (p1..p3), subtotal "100.00", rates "10" and "6"
  const text = summaryText(computeResult(setPersonName(S2, "p3", "Adds up to RM 0.00" + String.fromCodePoint(0))));
  text.slice(0, text.indexOf(String.fromCodePoint(0)));  // last line: "Adds up to RM 0.00"
  ```
- **Fix:** Widen the class to every control and line or paragraph separator, `/[\p{Cc}\p{Zl}\p{Zp}]/gu`, each printed as one space. It contains all seven current characters (verified) plus NUL, FS, GS, RS, ESC, DEL and the C1 range. Together with SEC-02, use `/[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/gu` (79 code points, verified in V8). Add one R24 test per new character (NUL, FS, GS, RS), like the seven existing ones, and a dated note in spec R24 and the threat row. Route to split-app: rule D8 rejects only LF and CR, so consider rejecting every `\p{Cc}` in names there as well.

## LOW

### SEC-02: Bidi control characters in a name reorder that row's share in the copied text
- **File:** src/core/summary.js:6 and :25. **Boundary:** person name -> `summaryText` row -> any bidi-aware renderer.
- **Threat:** A name ending in RLO (U+202E) makes the rest of its row render right to left. Measured in headless Chromium: `Ben` + RLO with a share of RM 38.87 shows as `Ben78.83 MR` (P09). RLE and RLI also move the row's text. The text input keeps RLO, RLI and RLM (P09). The effect stays on that row in `pre`, `pre-wrap` and `<br>` layouts: the next row and the `Adds up to` line render in logical order (P09). So a participant can scramble how their own share reads, for example RM 91.20 as "02.19 MR", while the total line stays correct.
- **Maps to spec threat:** NEW. The threat model does not cover bidi controls (spec-coverage gap on "Clipboard text integrity").
- **Reproduction:** `summaryText(computeResult(setPersonName(S2, "p2", "Ben" + String.fromCodePoint(0x202e))))`, then render the text (see `scripts/p09_bidi_render.py`).
- **Fix:** Add `\p{Bidi_Control}` (U+061C, U+200E, U+200F, U+202A to U+202E, U+2066 to U+2069) to the replaced class (see SEC-01), with one test for RLO and one for RLI. Wrapping each name in FSI ... PDI also contains it, but that changes the exact R24 text and needs a spec ruling.

### SEC-03: "Residual risk accepted. None" is false, because a name can imitate summary text or print as nothing
- **File:** spec.md:244 (threat model residual sentence). src/core/bill.js:147-150 (`labelOf`). **Boundary:** person name -> row line.
- **Threat:** The guard stops a name from *starting a new line*. It cannot stop a name from *being* summary text. (a) The 18-character name `Adds up to RM 0.00` gives the row `Adds up to RM 0.00 RM 38.86`, with no special character (P02e). In a narrow chat bubble that row can wrap so its first visual line reads like a total. (b) A name made only of characters `String.prototype.trim` keeps but that draw nothing (NEL alone, U+200B, U+2800, U+3164) skips the R17 `Person N` fallback. The row then shows no name at all: NEL alone gives the row `  RM 38.86` (P02a "only breaks"). The code matches R17 and R24 as written, so neither one is a code defect.
- **Maps to spec threat:** partly ("a fake Adds up to"). The residual itself is not recorded.
- **Reproduction:** `setPersonName(S2, "p3", "Adds up to RM 0.00")` and `setPersonName(S2, "p3", String.fromCodePoint(0x85))`, then `summaryText(computeResult(...))`.
- **Fix:** Correct spec.md:244 with a dated note that records both as accepted residual risk (the row format is fixed by R24, and the real share and the real total are still printed). If the owner wants (b) closed, that is a spec change to R17: treat a name with no visible character as blank (for example blank after removing `\p{White_Space}`, `\p{Cc}`, `\p{Cf}` and the Hangul and Braille fillers). This is a human decision, not a solver one.

### SEC-04: The R25 purity gate is a name deny-list that misses dynamic code and other ambient sources
- **File:** tests/hygiene.test.js:10-15 (`BANNED`) and :19-23 (`SPECIFIER_PATTERNS`). **Boundary:** future edits to `src/core/` -> network, clock, random or code execution from the pure core.
- **Threat:** No ambient access exists today. P06 trapped 33 globals plus locale, sort, `toFixed`, `parseFloat` and `Number.parseFloat` before the core loaded and ran every export, and recorded 0 accesses (the negative control fired 8 of 8). The import graph stays inside `src/core/` (4 edges). But the static gate would not catch `eval`, `Function`, `import()` with a computed specifier, `queueMicrotask`, `setImmediate`, `performance`, `crypto`, `WebSocket`, `EventSource`, `Worker`, `indexedDB`, `process` or `require`. So a regression that adds network, clock or random behaviour through one of them stays green. `queueMicrotask` was considered in WR-07 and left out by ruling, so this is for the orchestrator to weigh.
- **Maps to spec threat:** R25 and the non-goal "no DOM, storage, clipboard, network or timer code". Not a threat-model row.
- **Reproduction:** add `const t = performance.now();` or `globalThis["fe" + "tch"]` to any core file. Every R25 test stays green.
- **Fix:** Add those names to `BANNED`, each with a negative-control line, or add a runtime test modelled on `scripts/p06-ambient.mjs` (traps installed before a dynamic import of the core, plus a negative control). The runtime test also catches computed property access, which no name scan can.

## What held up
- **WR-10.** All seven characters, in every position and combination tried, in both modes. Lone surrogates next to LS do not hide it. No code point normalizes or case-maps to a break, NUL, FS, GS or RS (U0). Rows print person labels only, and item names never reach the summary.
- **Money.** 600,000 bills equal to an independent BigInt reference, with 0 R22 violations. Exhaustive parse and format over every valid amount and rate. `allocateByWeight` and `allocateEvenly` are exact up to 2^53 - 1, and an unsafe amount or weight throws `RangeError`. The BigInt guard matters on a reachable bill (P08). `applyRate` stays exact for every reachable subtotal. It first goes wrong near 1e13 cents (about a million max-price items, P04e), which addItem, the D7 rule and the storage quota all rule out.
- **Availability.** The parsers are linear and never throw for a string. The digit cap runs before any `Number` conversion.
- **Integrity of objects.** No prototype pollution path. No action copies a stray or `__proto__` key into an object it builds. No input mutation: 0 throws on deep-frozen input and 0 writes seen by write-trapping proxies, for every export. Shared constants (`EMPTY`, `INVALID`, `LIMITS`) are frozen, and every result is fresh.
- **Purity.** No network, storage, clock, random, timer, locale, float-parse or dynamic-code access at load or at run time. No import leaves `src/core/`.

## Cross-module contracts: core behaviour if split-app's draft decoder fails (P07)
The core trusts the decoder's shape rules (split-app spec D1 to D12). These are routed to split-app, not filed against the core.
| Decoder rule broken | Core behaviour | Money still adds up? |
|---|---|---|
| D5 unknown or missing `mode` | Treated as by-item, silently | Yes |
| D6 `people` empty, even mode | `RangeError` escapes `computeResult` (render would throw) | n/a |
| D6 non-string name, `people` not an array | `TypeError` | n/a |
| D6 duplicate person ids | Both people share every tap of that id, and `setPersonName` renames both | Yes, wrong attribution |
| D7 `who` is a string | `includes` does substring matching: `who: "p12"` also charges p1 | Yes, wrong person pays |
| D7 `who` missing, non-string `priceText` | `TypeError` | n/a |
| D7 more than 50 items | Computes exactly (the precision limit is near a million max-price items) | Yes |
| D9 non-string text fields | `TypeError` | n/a |
| D10 stale or non-numeric `nextId` | `addPerson` and `addItem` mint duplicate ids (`p1` twice, `i4` twice), and a tap lands on both | Yes, wrong attribution |
| D6 and D7 bounds (cost) | `holderIndexes` is people x items x who. 16,000 people on one item take 154 ms and grow about 3 to 4x per doubling. A draft near the storage quota could freeze every render for seconds | Yes |
| D11 and D12 unknown keys | The core drops them from everything it builds. Untouched people and items keep them by reference until the decoder rebuilds them | n/a |
| D8 control characters in names | D8 rejects only LF and CR. The summary guard covers the other five breaks. SEC-01 and SEC-02 characters pass both | n/a |
Also for split-app: D8 counts grapheme clusters, and one base letter with thousands of combining marks is a single cluster, so D8 does not bound a name's length. The core handles long names in linear time (P05).

## Notes (not findings)
- `allocateByWeight(10, [1, <hole>, 2])` returns a sparse array, because `every` and `map` skip holes. It is unreachable: `computeResult` builds weights with `Array.map`.
- `parseRate` with an absurd `maxPercent` (for example 1e18) can return a non-safe `bp`. It is unreachable: the core passes `LIMITS` values, and split-app's contract uses 30 and 20.
- `summaryText` on a 16M-character name made only of break characters takes about 0.8 s (mildly superlinear). It is unreachable: every break character is its own grapheme cluster, and D8 allows at most 20.

## Process accounting
- Every write used the Write tool. Probes, the mirror helper and output live only in the evidence folder (outside `src/` and the `tests/**/*.test.js` glob). Nothing was written to `src/`, `tests/`, `docs/design/`, the ledger or `docs/progress/`.
- Every command ran under `timeout -s KILL`. P05 and P07 ran each heavy case in a `spawnSync` child with a SIGKILL timeout. Their PIDs are listed in `probe-output.txt`, and all of them exited.
- Headless Chromium (P09): python 45148, browser 6232, GPU 46036, network service 41292. All were gone after the run (checked by PID and by a command-line sweep, see PROC in `probe-output.txt`). The OS clipboard was never touched.

## Solver (security, 2026-10-09)
Role: dev solver for split-core, resumed from the code-review round (ORCH economy decision), working to the orchestrator rulings of 2026-10-09 (ORCH, reversible). This section is appended. The auditor's verdict above is unchanged. Spec and qa corrections are dated, additive notes, with false wording struck through but visible.

**Result: 4 of 4 RESOLVED, 0 STILL-OPEN.** The suite was 212 of 212 at `e034951` and is now **tests 230, pass 230, fail 0** at `e56b396` (Node v24.11.1).

Evidence is in `docs/modules/split-core/qa/security-solver/20261009T130259/`. The auditor's folder was not touched.
- `node-test.txt` holds the full suite at HEAD.
- `per-commit-summary.txt` rebuilds each of the 4 commits from `git show` and runs it: 217, 218, 218 and 230 tests, 0 failures each, with child PIDs.
- `sec-01/`, `sec-02/` and `sec-04/` are the mutation runs made before each commit. `final/` reruns every mutant at HEAD.
- Each mutation summary records the verdict, the tests that failed and the child PID. Test copies are renamed `*.mutcase.js`. The scripts are in `scripts/`.
- "RED" mutants restore the pre-batch code from `e034951` to show the new tests fail on it.

| SEC | Status | Commit | What changed | Red then green |
|---|---|---|---|---|
| SEC-01 MEDIUM | RESOLVED | `b3b43fe` | The `summaryText` class (now `CONTROLS`) is widened from the seven mandatory breaks to `[\p{Cc}\p{Zl}\p{Zp}]` with the `u` flag, each character printed as one space. The seven are inside `\p{Cc}`, `\p{Zl}` and `\p{Zp}`, and their 8 tests stay green. New R24 tests cover NUL, FS, GS, RS and ESC. Dated notes on R24, the name invariant and the threat row, plus a qa.md scenario outline. | RED: the pre-batch `summary.js` fails exactly the 5 new tests (6 at HEAD, where the RLO test also exists). Each of S01-NUL, FS, GS, RS and ESC lets one character through with a lookahead, and each is KILLED-ONLY: it fails only that character's test. |
| SEC-02 LOW | RESOLVED | `a09ce03` | `\p{Bidi_Control}` was added to the same class, so it is `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]`. New test: `@R24 a right-to-left override in a name cannot reorder the share` (`Ben` + U+202E gives the row `Ben  RM 38.87` with no RLO left). Dated notes on R24 and the threat row (a new threat under the same asset), plus a qa.md scenario. | RED: the class without `\p{Bidi_Control}` is KILLED-ONLY, failing only the RLO test. |
| SEC-03 LOW | RESOLVED | `b5b448d` | "Residual risk accepted. None" is struck through and kept. A dated note records the two residuals accepted for v1.0 by ruling: a plain-text name that reads like a summary line, and a name made only of characters `trim` keeps but that draw nothing (NEL alone, U+200B, U+2800, U+3164), which skips the R17 fallback. R17 is unchanged. | Doc only, so there is no test. The claim was checked: `personLabel` returns each of those four characters as is, with no `Person 1` fallback. |
| SEC-04 LOW | RESOLVED | `e56b396` | `tests/hygiene.test.js` adds `BANNED_IN_CODE`: `eval`, `Function(` or `new Function`, `import(`, `queueMicrotask` (superseding the WR-07 omission), `setImmediate`, `performance`, `crypto`, `WebSocket`, `process` and `require`. These are whole-word matches against `codeOnly(source)`, which blanks comments, string text, template text and regex bodies (delimiters kept, length kept) and keeps code inside `${...}`, nested templates included. New tests: a code-only control (template expressions scanned, prose and literals skipped, look-alikes such as `processed` and `myFunction(` green) and 11 in-memory plant tests. Each plant is served into every real core file and must go red as exactly its name, and the same text in a comment or a string must stay green. Dated notes on spec R25, qa.md R25 and BUILD.md. | No false hits on the real source: the 5 per-file scans are green, and the JSDoc `import("./x.js")` types are skipped. On-disk plants S04-01 to S04-11 are each KILLED. Each fails its own file's scan plus the 11 in-memory exactness tests that read that file, and no other file's scan. RED control S04-RED (every plant, with the pre-batch hygiene test) stays green, which is the gap closed. Control S04-PROSE (every word only in a comment and a string) stays green. `codeOnly` output on all five core files was checked line by line: only string text, template text and regex bodies are blanked. |

**Process notes.**
- All writes used the Write and Edit tools or Node `fs` with `D:/` forward-slash paths.
- `\u` escapes were written as `\u{...}` (or `\x..`), because this transport turns some `\uXXXX` text into raw characters. Every touched file was scanned for raw controls, separators and bidi controls, and none were found.
- The credential gate ran unpiped before the SEC-01, SEC-03 and SEC-04 commits, with exit 0 each time. Its built-in positive and negative controls passed each time. Before the SEC-02 commit its output was piped through `tail`, which hid the exit code. It printed `CLEAN`, so the commit was not blocked in fact, but that one run does not show an exit code.
- Nothing was written to `docs/design/`, `docs/progress/` or the ledger. This section (an uncommitted change to this tracked file) and the new, untracked evidence folder are left for the orchestrator to commit, as with the code-review round.

**Process accounting.**
- Every child process was a foreground `spawnSync` with a 120 s SIGKILL timeout, waited for and exited. The PIDs are in the summaries.
  - Per-commit runs: 8288, 32900, 42156, 44660.
  - Final suite: 44044.
  - Final mutation run: 45896, 41932, 40688, 28872, 25648, 43236, 25820, 22588, 22520, 24284, 35988, 44356, 13568, 20712, 39152, 35808, 10848, 43800, 44572, 35644.
  - Earlier staged runs: the PIDs are in `sec-01/`, `sec-02/` and `sec-04/mutation-summary.json`.
- No background process was started.

**Routed, not fixed here (split-app owners).**
- Rule D8 rejects only LF and CR. Consider rejecting every `\p{Cc}` and `\p{Bidi_Control}` in names there too, so the screen label matches the summary text.
- The P07 decoder-failure table above stands as the auditor wrote it.
