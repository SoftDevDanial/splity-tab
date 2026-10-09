---
module: split-core
kind: security
status: issues_found
counts: { critical: 0, high: 0, medium: 0, low: 2 }
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

## Re-check (2026-10-09)
Role: security auditor (finder, read-only on `src/`, `tests/` and `docs/design/`). HEAD `c7f9640`, after the
solver commits `b3b43fe` (SEC-01), `a09ce03` (SEC-02), `b5b448d` (SEC-03) and `e56b396` (SEC-04). The verdict
and findings above are the first audit and are kept as written. [Changed 2026-10-09, re-check: the front
matter now counts the findings open after this re-check. It read `medium: 1, low: 3` before.]

**Verdict: PASS. SEC-01 CLOSED, SEC-02 CLOSED, SEC-03 CLOSED, SEC-04 CLOSED. 2 new LOW (SEC-05, SEC-06).
0 CRITICAL, 0 HIGH, 0 MEDIUM open.**
- The forging fixes hold everywhere I could test. All 1,114,112 code points were tried inside a forging name. Exactly the 79 code points of `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]` are replaced, and not one case gave a forged line, a NUL or a bidi control to any of six consumers. Real Python `splitlines`, a NUL-terminated read and Chromium layout agree.
- Both new findings are about regression guards, not about today's behaviour. The new `codeOnly` lexer lets 10 live snippets through the real hygiene test (SEC-05). The new R24 tests pin only 13 of the 79 replaced code points (SEC-06).

Evidence: `docs/modules/split-core/qa/security/20261009T131232/` (`node-test.txt`, `probe-output.txt`, `scripts/`).
The suite is **tests 230, pass 230, fail 0**, exit 0, at the start and at the end of the re-check.

### Per finding
| SEC | Status | What was checked | Evidence |
|---|---|---|---|
| SEC-01 MEDIUM | CLOSED | `CONTROLS` at src/core/summary.js:8, applied at :27. NUL, FS, GS, RS, US, ESC, TAB, DEL, C1, each inside, leading, trailing and tripled, in both modes. The SEC-01 NUL name now gives a text with no NUL, 6 lines and the real last line `Adds up to RM 116.60`. Exhaustive pass over every code point: 0 failures for the LF-only, JS line terminator, UAX #14, Python `splitlines`, Bidi class B and "NUL ends text" consumers. Fuzz: 0 of 100,000 names. Real Python `splitlines` and a NUL read on 89 HEAD texts: 0 of 89 cut or split | R01a, R01b, R01d, R01e, R03 |
| SEC-02 LOW | CLOSED | All 12 bidi controls are replaced. In headless Chromium, RLO, RLE, RLI and LRO, alone or mixed, leave the share `RM 38.87` in reading order, and no other row moves (`pre`, `pre-wrap`, `<br>`). Nothing is over-replaced: Hebrew and Arabic names, a ZWJ emoji family, ZWNJ, a combining accent and NBSP print unchanged, and the share next to a right-to-left name stays in reading order | R01a, R01c, R01f, R03 |
| SEC-03 LOW | CLOSED | spec.md:244-248 strikes "None" and records both residuals. Both behave as written: `Adds up to RM 0.00` gives the row `Adds up to RM 0.00 RM 38.86`. NEL, U+200B, U+2800 and U+3164 alone skip the `Person N` fallback and print no visible name. LRM alone and U+180E behave the same and fall under the note's own wording | R01g |
| SEC-04 LOW | CLOSED (as specified) | The ten names are banned in code. Ordinary call forms go red in the real `tests/hygiene.test.js` in every core file (3 controls). `codeOnly` blanks only string text, template text and regex bodies in the 5 real files (all 42 affected code lines reviewed), so there are no false hits. The lexer has false negatives, filed as SEC-05 | R04 controls and review |

### Threat model and residuals against the code
- The threat row for "Clipboard text integrity" (spec.md:241) matches the code. It names the widened class, the tests for NUL, FS, GS, RS and ESC, and the bidi controls with an RLO test.
- The R24 note lists exactly the replaced set, and the exhaustive pass in R01d reproduces it code point for code point.
- The two accepted residuals at spec.md:247-248 are true as written (R01g).
- Doc precision, routed to code review, not a security finding:
  - The name invariant note (spec.md:19) and the `summaryText` JSDoc (summary.js:11-12) say "every control character and/or separator". That is looser than the code. Space separators such as NBSP and U+3000 are kept (R01f), and the bidi controls are not named.
  - The comment above `CONTROLS` (summary.js:4-7) and R24 are exact.

## LOW (re-check)

### SEC-05: `codeOnly` misreads some slashes and escapes, so live banned code passes the R25 gate
- **File:** tests/hygiene.test.js:33-39 (`REGEX_AFTER`, `REGEX_AFTER_WORD`, `regexMayStart`), :43-55 (`literalEnd`), :59-106 (`codeOnly`), :22 (the `Function` pattern). **Boundary:** future edits to `src/core/` -> dynamic code or ambient access from the pure core.
- **Threat:** I appended each snippet in memory to all 5 core files. Each one reaches a banned global when its module is imported (proved with trapped globals). The real, unchanged `tests/hygiene.test.js` still passes 25 of 25 on all 10:
  1. **Postfix `++` or `--` before `/`.** The slash is read as the start of a regex, so the rest of the line is blanked (F1: `let r04Hits = 0; const r04Rate = r04Hits++ / process.uptime();`).
  2. **A member named like a keyword before `/`.** `.in`, `.of`, `.delete` and the like match `REGEX_AFTER_WORD` (F2: `r04Range.in / performance.now()`).
  3. **A regex literal right after `if (...)`, read as division.** Its body is then lexed as code. A quote in it opens a fake string (F3). A `//` opens a fake comment (F5). A backtick opens a fake template that runs to the next backtick (F4b).
  4. **Template desync.** `${n++ / 2}` swallows the template's `}`. The function's closing brace then closes the template, and the code after it is blanked up to the next backtick (F6b).
  5. **Pattern limits outside the lexer.** A bare `Function` reference with no call (F7). An identifier written with a unicode escape, `\u{70}rocess`, which also hides names from the original list, such as `\u{44}ate` (F8, F9). The constructor route, which uses no name at all (F10).
  - F4 and F6 do turn the run red, but only because their hidden region reaches the end of the file and swallows the suite's own in-memory plant lines. The 5 per-file banned-name scans stay green.
  - **Impact:** this is a regression guard only. The core has no ambient access today (P06 re-run: 0 hits).
  - Forms 1 to 4 are valid code an honest edit could write, though uncommon. Form 5 is deliberate obfuscation, which a name scan cannot be expected to stop. The first audit's SEC-04 fix already pointed to a runtime test for that case.
- **Maps to spec threat:** R25, through the SEC-04 fix. Not a threat-model row.
- **Reproduction:** `node docs/modules/split-core/qa/security/20261009T131232/scripts/r04-codeonly.mjs`. It runs the real test through a preload that patches only in-memory reads, so no file is copied or changed. Or add the F1 line above to any core file and run `node --test tests/hygiene.test.js`: it stays green.
- **Fix:**
  - (a) The robust layer: add a runtime test like `scripts/r04-exec-child.mjs` and the first audit's `p06-ambient.mjs`. Install traps on the banned globals and on `Function.prototype.constructor` before a dynamic import of each core module, run the exports, and assert zero hits, with a negative control. That catches all 10 snippets whatever their syntax.
  - (b) If the scan stays, harden it:
    - Read `/` after `++`, `--` or a `.keyword` member as division.
    - For `/` after `)`, scan both readings and keep every hit (fail safe).
    - Decode `\u{...}` and `\uXXXX` escapes in code before matching, for both lists.
    - Match `\bFunction\b` in code, not only the call and `new` forms.
    - Add F1 to F10 as in-memory plant tests.

### SEC-06: The new R24 tests pin 13 of the 79 replaced code points
- **File:** tests/summary.test.js:89-103 (the seven), :107-117 (`OTHER_CONTROLS`), :119-123 (the RLO test). The class is at src/core/summary.js:8. **Boundary:** a future edit to `CONTROLS` -> the SEC-01 and SEC-02 guards.
- **Threat:** I narrowed `CONTROLS` in memory with a load hook and ran the real `tests/summary.test.js` (R05):
  - Narrowing the bidi part to RLO only stays green (25 of 25). It lets 11 bidi controls through again, including RLE and RLI, which the first audit measured moving a row's text (P09).
  - Narrowing the control part to the 12 tested characters stays green. It lets 55 C0 and C1 controls through, BS, BEL, US, DEL and CSI U+009B among them.
  - Narrowing both stays green, with 66 code points through.
  - Dropping the bidi part goes red (the control). Today's code is correct (R01d).
  - My own SEC-01 and SEC-02 fix advice asked for one test per named character, and that is what produced this shape.
- **Maps to spec threat:** "Clipboard text integrity". This is a regression guard for the SEC-01 and SEC-02 mitigations.
- **Reproduction:** `node docs/modules/split-core/qa/security/20261009T131232/scripts/r05-class-mutants.mjs`.
- **Fix:** Add one property test that walks U+0000 to U+2069 (no class member lies above it). It asserts that every member of `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]` in a name prints as one space and every other code point prints unchanged. It kills all three narrowing mutants and keeps the named-character tests as readable examples.

### Re-check: what still holds
- The first audit's probes, re-run unchanged at HEAD, all pass:
  - P01: 1,000,000 strings, 0 throws.
  - P02: 0 of 50,000 forging names, and every lookalike line count is now 6.
  - P03: no pollution, no mutation.
  - P04: exhaustive exactness.
  - P06: 0 ambient accesses, and the negative control fired 8 of 8.
  - P08: 600,000 bills, 0 differences.
- `src/` changed only in `summary.js` between `e034951` and `c7f9640`, so T1, T2, T3 and T5 are unaffected.
- P02's NUL line now prints the text minus one character. That is a probe artifact (`indexOf` returns -1), not a truncation.

### Re-check: process accounting
- Every write used the Write tool. Scripts and output are only in the new evidence folder. Nothing was written to `src/`, `tests/`, `docs/design/`, the ledger or `docs/progress/`. The mutation and plant runs patch in-memory module loads and file reads only, and no source or test file was copied or changed.
- One command sent a probe's output to `/dev/null` to read its exit code. It wrote no file.
- Headless Chromium (R03): python 44640, browser 13212, GPU 46028. All three were gone afterwards (checked by PID).
- R04 and R05 children were `spawnSync` with SIGKILL timeouts, each waited for and exited. Their PIDs are in `probe-output.txt`.
- Final sweep by name (node, python, chrome) at 13:25: none alive. The OS clipboard was never touched.

## Solver (security round 2, 2026-10-09)
Role: dev solver for split-core, resumed again for this round, working to the orchestrator rulings of 2026-10-09 (ORCH, reversible). This section is appended. The auditor's re-check above is unchanged. By ORCH's stop rule there is no third security round. The split-core code-review re-check verifies these commits.

**Result: SEC-05 RESOLVED, SEC-06 RESOLVED, and the wording item RESOLVED. 0 STILL-OPEN.** The suite was 230 of 230 at `a47bcb7` and is now **tests 246, pass 246, fail 0** at `4e2740b` (Node v24.11.1).

Evidence is in `docs/modules/split-core/qa/security-solver/20261009T133744/`. The auditor's folders were not touched.
- `node-test.txt` holds the full suite at HEAD.
- `per-commit-summary.txt` rebuilds each commit from `git show` and runs it: 244, 246 and 246 tests, 0 failures each, with child PIDs.
- `sec-05/`, `sec-05-run/` and `sec-06/` were run before each commit. `final/` reruns every mutant at HEAD.
- `scripts/mutate.mjs` reads the F1 to F10 plants from `tests/hygiene.test.js` at run time, so the evidence cannot drift from the suite. "RED" controls put back the test file from `a47bcb7`.
- The first `S05-RUN` and `S05-RUN-RED` rows in `sec-05/` are superseded by `sec-05-run/`. That first mutant spelled `fetch` inside a string, which the old whole-source list also catches, so it was not a run-time-only access.

| Item | Status | Commit | What changed | Red then green |
|---|---|---|---|---|
| SEC-05 LOW | RESOLVED | `fedaa7a` | Per the ruling, the lexer is not hardened. A runtime trap at the end of `tests/hygiene.test.js` is now the primary R25 guard, and the scan stays as a secondary guard. See "How the SEC-05 trap works" below. | Each of the 12 plants (F1, F2, F3, F4, F4b, F5, F6, F6b, F7, F8, F9, F10), written on disk into a core file, is KILLED by the clean-run test. The one extra failure in each is that plant's own served test, which collides with the same declarations already on disk. F4 and F6 also hide the rest of the file from the scan. Every RED control (the 10 plants the scan missed, with the `a47bcb7` hygiene test) stays green, which is the gap. S05-RUN is KILLED-ONLY: `formatRate` reaches the constructor route with the name split as `"f" + "etch"`, which only the trap sees, and its RED control stays green. S05-EXPORT (an export the workload never calls) is KILLED-ONLY. |
| SEC-06 LOW | RESOLVED | `5d5d02a` | Two property tests were added to `tests/summary.test.js`. (1) Every code point U+0000 to U+2069, each in a name of its own: exactly the members of `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]` print as one space, every other code point prints as typed, and exactly 79 code points match. (2) Every code point U+206A to U+10FFFF (surrogate halves left out, as adjacent halves would pair) in one name prints unchanged. The runs take 27 ms and 102 ms. A dated qa.md scenario was added. | KILLED-ONLY: RLO only, the 12 named controls, both together, over-replacing `\p{Zs}` (NBSP, U+3000), and an astral addition (U+1F600). RED controls: RLO only and the 12 controls with the `a47bcb7` summary tests stay green, reproducing the auditor's R05. |
| Wording | RESOLVED | `4e2740b` | spec.md line 19 (the name invariant note) and the `summaryText` JSDoc now give the exact class `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]` and say that space separators such as NBSP are kept. The spec's loose phrase is struck through, with a dated note. | No code change. The SEC-06 property tests pin exactly this class, and NBSP and U+3000 are kept. |

**How the SEC-05 trap works.**
- **What it traps.** Every banned global gets a recorder that still returns the real value: `eval`, `Function`, the timers, `queueMicrotask`, `setImmediate`, `performance`, `crypto`, `WebSocket`, `process`, `require`, `fetch`, `XMLHttpRequest`, `EventSource`, storage, `Date`, `Intl`, `window`, `document`, `navigator` and `parseFloat`. So do `Date.now`, `Math.random`, `Number.parseFloat`, `toFixed`, the locale methods, and the function-constructor route on the Function, AsyncFunction, GeneratorFunction and AsyncGeneratorFunction prototypes.
- **What counts.** An access counts only when a `src/core/` frame is on the stack, so the test runner's own use of a global never counts.
- **A fresh core each run.** A `module.registerHooks` resolve hook carries a run id onto every core import, so each trapped run evaluates a fresh copy of the whole core whatever loaded it before. A load hook serves plants appended in memory, so no file is written.
- **Three test groups:**
  - The clean run loads the core, calls every export (both modes, every blocking path, both throws), requires zero accesses, and requires every export to have run.
  - A negative control shows each trap fires for one served line of core code, and that test-code access is not counted.
  - 12 tests serve the auditor's F1 to F10 plants into every core file. The plant texts were checked byte-identical to the auditor's `r04-codeonly.mjs`.
- **Docs.** Spec R25 has a dated note naming the scan's known limits and the trap as primary. qa.md and BUILD.md are updated.

**Process notes.**
- All writes used the Write and Edit tools, or Node `fs` with `D:/` forward-slash paths.
- `\u` escapes were written as `\u{...}` or `\x..`, and every touched file was byte-scanned for raw controls, separators and bidi controls. None were found.
- The credential gate ran unpiped before each of the 3 commits, with the exit code echoed (0, 0, 0). Its built-in positive and negative controls passed each time.
- No redirect or heredoc was used. Nothing was written to `docs/design/`, `docs/progress/` or the ledger.
- This section (an uncommitted change to this tracked file) and the untracked evidence folder are left for the orchestrator to commit.

**Process accounting.**
- Every child process was a foreground `spawnSync` with a SIGKILL timeout, waited for and exited.
  - Per-commit runs: 25820, 22608, 11284.
  - Final suite: 45428.
  - Final mutation run: 37164, 39152, 45428, 508, 29988, 45104, 44160, 31824, 28488, 43800, 43996, 44692, 1444, 41360, 37736, 25456, 32552, 44508, 35040, 33532, 22608, 43848, 33440, 18028, 13288, 23748, 42612, 37804, 44556, 36780, 26416, 43220.
  - Earlier staged runs: the PIDs are in `sec-05/`, `sec-05-run/` and `sec-06/mutation-summary.json`.
- Windows reuses PIDs, so a few numbers repeat across runs.
- No background process was started.
