---
module: split-core
kind: qa
ran_against: running-app
status: green
counts: { pass: 54, fail: 0, blocked: 0 }
---
# QA findings for split-core

**Verdict: PASS.** 54 of 54 qa.md scenarios pass. 0 fail, 0 blocked, 0 untested. Every R1 to R26 has at least one passing scenario and at least one passing tagged test.

Run by the QA finder, read-only on `src/`, `tests/` and `docs/design/`. Date 2026-10-09. Repo `examples/split` at HEAD `bf69ed3`, working tree clean before the run. This module has no UI, so "the running app" is the module exports under Node v24.11.1.

| Level | Pass | Fail | Untested |
|---|---|---|---|
| qa.md scenarios (54, of which 21 are Outlines) | 54 | 0 | 0 |
| Cases (146 Outline example rows plus 33 single scenarios = 179) | 179 | 0 | 0 |
| node tests, `node --test "tests/**/*.test.js"` | 254 | 0 | 0 |
| Independent probe checks, `probe-money.mjs` | 125 | 0 | 0 |

## Evidence
- Suite: `docs/modules/split-core/qa/unit/20261009-142756/node-test.txt`. Exit 0. `tests 254, pass 254, fail 0, cancelled 0, skipped 0, todo 0`. Duration 266.9 ms. Every test title starts with its `@R#` tag.
- Probe: `docs/modules/split-core/qa/qa/20261009-142756/probe-money.mjs`, output in `probe-money.out.txt`. `SUMMARY pass=125 fail=0`. Exit 0.

## Scenario results (qa.md)
The test column gives the title in `node-test.txt`. "xN" means N tests share that title pattern. The probe column gives the section letter in `probe-money.mjs` that checks the same expected values.

| # | Scenario | R# | Test (node-test.txt) | Probe | Result |
|---|---|---|---|---|---|
| 1 | parseAmount accepts valid amounts (Outline, 12 rows) | R1 | `@R1 parseAmount(...) is N cents` x12 | A (13 inputs, incl. the 1.15 and 4.35 float traps) | PASS |
| 2 | parseAmount rejects invalid text as invalid, not empty (Outline, 17 rows) | R1, R2 | `@R1 @R2 parseAmount(...) is invalid, not empty` x17 | none | PASS |
| 3 | A 401-character amount is rejected without overflow or exception | R1, R2 | `@R1 @R2 a 401-character amount is invalid and does not throw` | none | PASS |
| 4 | A whole part longer than the ceiling's is refused before any numeric conversion | R1, R3 | `@R1 @R3 a whole part longer than the ceiling's is refused before any numeric conversion` (Number spy, with positive controls) | none | PASS |
| 5 | Empty or white-space text is reported as empty (Outline, 2 rows) | R2 | `@R2 "" is reported as empty by both parsers`, `@R2 "   " is reported as empty by both parsers` | none | PASS |
| 6 | The parsers never throw for any string (500 seeded strings) | R2 | `@R2 the parsers never throw and always return a well-formed result` | none | PASS |
| 7 | parseRate reads basis points within its maximum (Outline, 17 rows) | R3 | `@R3 parseRate(...)` x17 | A (12.5, 6.25, 30, 20, 0) | PASS |
| 8 | formatMoney writes RM, a space, ringgit and two sen digits (Outline, 8 rows) | R4 | `@R4 formatMoney(N) is "RM ..."` x8 | B | PASS |
| 9 | formatRate drops trailing zeros and adds a percent sign (Outline, 7 rows) | R5 | `@R5 formatRate(N) is "..."` x7, `@R5 a typed 10.00 round-trips to 10%` | B | PASS |
| 10 | Service and SST round half up to the cent (Outline, 10 rows) | R6 | `@R6 billCharges(...) totals N` x10, each on the whole charges object | D (14 rows), I | PASS |
| 11 | allocateEvenly floors and hands leftover sen to the top (Outline, 7 rows) | R7 | `@R7 allocateEvenly(...)` x7 | C | PASS |
| 12 | allocateByWeight floors exactly and skips zero weights for leftovers (Outline, 7 rows, 3 BigInt trap rows) | R8 | `@R8 allocateByWeight(...)` x4, `@R8 BigInt trap: allocateByWeight(...)` x3 (each also asserts a float allocator misses) | C | PASS |
| 13 | allocateByWeight gives the MAX-I charges split exactly, with products past 2^53 | R8, R23 | `@R8 @R23 allocateByWeight gives the MAX-I charges split exactly, with products past 2^53` | C | PASS |
| 14 | Allocation rejects impossible input (Outline, 9 rows) | R9 | `@R9 allocateEvenly(...) throws RangeError` x5, `@R9 allocateByWeight(...) throws RangeError` x6 (the 9 rows plus 2 extra) | none | PASS |
| 15 | A new bill has two people, even mode and the default rates | R10 | `@R10 a new bill has two people, even mode and the default rates` | none | PASS |
| 16 | Adding a person appends an empty-named person with the next id | R11 | `@R11 adding a person appends an empty-named person with the next id` | none | PASS |
| 17 | A new person's id never reuses a removed id | R11 | `@R11 a new person's id comes from nextId, so it never reuses a removed id` | none | PASS |
| 18 | Adding a 13th person does nothing | R11 | `@R11 the twelfth person is accepted and the thirteenth does nothing` | none | PASS |
| 19 | Removing a person removes them from every item | R12 | `@R12 removing a person removes them from every item` | none | PASS |
| 20 | Removing is refused at 2 people or for an unknown id (Outline, 2 rows) | R12 | `@R12 removing is refused at 2 people or for an unknown id` | none | PASS |
| 21 | Adding an item appends an empty, unassigned item | R13 | `@R13 adding an item appends an empty, unassigned item` | none | PASS |
| 22 | The 51st item is refused and removing works at any time | R13 | `@R13 the 51st item is refused and removing works at any time` | none | PASS |
| 23 | Tapping toggles a person on an item | R14 | `@R14 tapping toggles a person on an item`, `@R14 an unknown item or person id returns the same bill` | none | PASS |
| 24 | Switching modes keeps both sets of input | R15 | `@R15 switching modes keeps both sets of input` | none | PASS |
| 25 | Setters store text exactly as typed | R15 | `@R15 setters store text exactly as typed`, `@R15 each setter changes only its own field` | none | PASS |
| 26 | No action mutates its input (deep-frozen S1) | R16 | `@R16 no action mutates a deep-frozen bill and changes return new objects`, plus 13 `@R16 <action> on a parsed bill builds only known fields` | none | PASS |
| 27 | The other functions that take objects leave them alone | R16 | `@R16 @R17 the labels leave a frozen person or item alone`, `@R16 allocateByWeight leaves frozen weights alone`, `@R16 summaryText leaves a deep-frozen result alone`, `@R16 computeResult leaves a deep-frozen bill alone` | none | PASS |
| 28 | Display names fall back to their position (Outline, 6 rows) | R17 | `@R17 person named ...` x4, `@R17 item named ...` x2 | none | PASS |
| 29 | The first blocking rule wins (Outline, 9 rows) | R18 | `@R18 blocking row 1 is "rates"` to `@R18 blocking row 9 is "prices"` | G (9 rows) | PASS |
| 30 | Even mode ignores broken items | R18, R20 | `@R18 @R20 even mode ignores broken items` | none | PASS |
| 31 | Unassigned items are counted and the charges are still known | R19 | `@R19 unassigned items are counted and the charges are still known` | F (S5) | PASS |
| 32 | Two unassigned items give a count of 2 | R19 | `@R19 two unassigned items give a count of 2` | none | PASS |
| 33 | Even results match the worked examples (Outline: S2, E1, E2, E3, MAX-E) | R20 | `@R20 @R23 even result for S2`, `E1`, `E2`, `E3`, `MAX-E` | E (S2, E1, E2, E3, MAX-E) | PASS |
| 34 | By-item results match the worked examples (Outline: S1, I2, I3, I4, MAX-I) | R21 | `@R21 @R23 by-item result for S1`, `I2`, `I3`, `I4`, `MAX-I` | F (S1, I2, I3, I4, MAX-I) | PASS |
| 35 | A shared item's leftover sen follow the people list, not the tap order | R21 | `@R21 a shared item's leftover sen follow the people list, not the tap order` | F (I3 list order) | PASS |
| 36 | Generated bills always add up (2000 bills, mulberry32 seed 20261008) | R22 | `@R22 generated bills always add up` | E, F and I (400 bills, BigInt reference, seed 4242) | PASS |
| 37 | The largest bills compute exactly (MAX-E and MAX-I) | R23 | `@R20 @R23 even result for MAX-E`, `@R21 @R23 by-item result for MAX-I`, `@R23 MAX-I charges are exact at the bound` | D, E and F (MAX rows) | PASS |
| 38 | Summary text is exact (Outline: S2, S1, E2, E3, I2) | R24 | `@R24 summary text for S2 is exact`, `S1`, `E2 zero rates`, `E3 decimal rates`, `I2 zero share` | H (all five blocks) | PASS |
| 39 | A blank name prints as its position | R24 | `@R24 a blank name prints as its position` | H | PASS |
| 40 | A line break inside a name prints as a space, so it cannot forge a line (Outline, 7 rows) | R24 | `@R24 a LF`, `CR`, `VT`, `FF`, `NEL`, `LS`, `PS` `inside a name prints as a space` x7 | none | PASS |
| 41 | Any other control character in a name prints as a space (Outline, 5 rows) | R24 | `@R24 a NUL`, `FS`, `GS`, `RS`, `ESC` `inside a name prints as a space` x5 | none | PASS |
| 42 | A right-to-left override in a name cannot reorder the share | R24 | `@R24 a right-to-left override in a name cannot reorder the share` | none | PASS |
| 43 | Exactly the R24 class prints as a space, every other code point up to U+2069 as typed | R24 | `@R24 exactly the R24 class prints as a space, every other code point up to U+2069 as typed` | none | PASS |
| 44 | Every code point above U+2069 prints as typed | R24 | `@R24 every code point above U+2069 prints as typed` | none | PASS |
| 45 | Every member of the class in one name is replaced, one space each | R24 | `@R24 every member of the class in one name is replaced, one space each` | none | PASS |
| 46 | A lone surrogate prints as typed | R24 | `@R24 a lone surrogate is not in the class, so it prints as typed` | none | PASS |
| 47 | By-item rows get the same line-break guard | R24 | `@R24 by-item rows get the same line-break guard` | none | PASS |
| 48 | summaryText refuses results without shares (Outline: blocked, unassigned) | R24 | `@R24 results without shares are refused with TypeError` | none | PASS |
| 49 | The core files are pure (source scan) | R25 | `@R25 <file> imports only from src/core/` x5, `@R25 <file> uses no banned name` x5, `@R25 the scan sees the core files`, `@R25 the scanner catches what it should (negative control)`, `@R25 the code-only scan reads code ...`, 11 `@R25 const ... served into each core file goes red as ...`, `@R25 the core files do import each other ...` | none | PASS |
| 50 | The core touches no banned global or method at load or while every export runs (runtime trap) | R25 | `@R25 runtime trap: the core touches no banned global or method ...`, `every trap fires ... (negative control)`, `the trap lists are exactly the pinned ones`, `every name the source scan bans has a trap`, `every trap is put back after a run`, `every run loads its own copy of the core`, `a run whose body throws leaves no hits`, `a stack that cannot be read`, plus 12 `@R25 runtime trap catches the security re-check's F* plant` | none | PASS |
| 51 | Equal names are stored as typed | R26 | `@R26 equal names are stored as typed and nobody is merged` | none | PASS |
| 52 | Tapping and removing address a person by id, not by name | R26 | `@R26 tapping and removing address a person by id, not by name` | none | PASS |
| 53 | Equal names give one row each (Outline: D1 even, D2 item) | R26 | `@R26 D1: two people called Ben give two even rows`, `@R26 D2: two people called Ben give two by-item rows, only the tapped one pays` | E (D1), F (D2) | PASS |
| 54 | Equal names give one summary line each (Outline: D1, D2) | R26 | `@R24 summary text for D1 equal names, even is exact`, `@R24 summary text for D2 equal names, by item is exact`, `@R26 equal names print one line each` | H (D1, D2) | PASS |

## Independent cross-check (step 4)
`probe-money.mjs` imports `src/core/` directly and does not use the test helpers. Its bills are plain literals. Expected values are typed by hand from qa.md and spec R1 to R8 and R18 to R24. Section I is a sweep of 400 generated bills, checked against a BigInt reference that imports nothing from `src/core/`. Result: 125 of 125 pass.

| Section | Checks | What is typed |
|---|---|---|
| A. Money text read on the way in | 18 | Parse results for every named-bill input, and the 1.15 and 4.35 float traps |
| B. Money and rate text written out | 16 | R4 and R5 rows, and 12.5% for E3 |
| C. Cent allocation | 14 | R7 rows, R8 rows, the three BigInt trap rows, and the MAX-I weights |
| D. Charges | 14 | R6 ten rows, and the charges object of each named bill. The I3 row is derived from R6 because qa.md gives only its parts and total |
| E. Even split | 18 | Full result for S2, E1, E2, E3, MAX-E and D1, each with a typed-table sum check and a core sum check |
| F. By-item split | 20 | Full result for S1, I2, I3, I4, D2 and MAX-I, the S5 unassigned result, and the I3 list-order rule |
| G. Blocking order | 9 | The nine R18 rows |
| H. Summary text | 15 | Exact text for S2, S1, E2, E3, I2, D1 and D2 (with no trailing newline), and the blank-name line |
| I. BigInt reference sweep | 1 | 400 generated bills (200 even, 200 by item), all equal to the reference, down to every row |

The probe found no discrepancy between the core and the typed values.

## Coverage table (R1 to R26)
Every R# has at least one passing scenario and at least one passing tagged node test. No R# is without coverage.

| R# | Requirement | qa.md scenarios (row numbers above) | Passing tagged node tests | Probe sections | Covered |
|---|---|---|---|---|---|
| R1 | Amount grammar and range | 1, 2, 3, 4 | 32 | A | yes |
| R2 | Empty versus invalid | 2, 3, 5, 6 | 21 | none | yes |
| R3 | Rate grammar and range | 4, 7 | 18 | A | yes |
| R4 | Money format | 8 | 8 | B | yes |
| R5 | Rate format | 9 | 8 | B | yes |
| R6 | Charges | 10 | 10 | D, I | yes |
| R7 | Even allocation | 11 | 8 | C | yes |
| R8 | Proportional allocation | 12, 13 | 10 | C, I | yes |
| R9 | Allocation preconditions | 14 | 11 | none | yes |
| R10 | New bill | 15 | 3 | none | yes |
| R11 | Add person | 16, 17, 18 | 4 | none | yes |
| R12 | Remove person | 19, 20 | 3 | none | yes |
| R13 | Add and remove item | 21, 22 | 3 | none | yes |
| R14 | Tap a person on an item | 23 | 2 | none | yes |
| R15 | Field setters | 24, 25 | 4 | none | yes |
| R16 | Purity | 26, 27 | 18 | none | yes |
| R17 | Display names | 28 | 8 | none | yes |
| R18 | Blocking order | 29, 30 | 12 | G | yes |
| R19 | Unassigned items | 31, 32 | 2 | F | yes |
| R20 | Even result | 30, 33 | 6 | E | yes |
| R21 | By-item result | 34, 35 | 8 | F | yes |
| R22 | Shares add up | 36 | 1 | E, F, I | yes |
| R23 | Bounds | 13, 37 | 12 | D, E, F | yes |
| R24 | Summary text | 38 to 48 | 27 | H | yes |
| R25 | Pure module | 49, 50 | 45 | none | yes |
| R26 | Duplicate names | 51, 52, 53, 54 | 5 | E, F, H | yes |

## Assertions weaker than their Then line (flagged, none fails the Then)
1. **R25 runtime trap, "every export was called".** The test (`@R25 runtime trap: the core touches no banned global or method while it loads and while every export runs`) records a property read on each export through a Proxy `get` trap. It does not record a call. `runEveryExport` does call every function export, so the Then holds for this code. The assertion alone would still pass if a future workload only read an export.
2. **R16, "each returns what it returns for an unfrozen input".** `@R16 @R17 the labels leave a frozen person or item alone` compares `personLabel` and `itemLabel` on frozen inputs to the literal values "A" and "Satay", not to a call on an unfrozen copy. The literals are the spec outputs, so the Then holds in effect, but the comparison is indirect.
3. **R18 "the result kind is even with the S2 shares"** (`@R18 @R20 even mode ignores broken items`). The test asserts the kind and the row shares only, not `check` or `charges`. It meets the Then as written.
4. **R2 "every result has the shape of R1 or R2"** (`@R2 the parsers never throw ...`). The test checks the key set and the value ranges, and that `empty` is a boolean. It does not check that `empty` is true for blank strings in the generated set. It meets the Then as written.

Notes, not weaknesses:
- **R11 "no item's who changed"** is checked on S1, a bill with items. The Given is a new bill, which has no items, so the Then would be vacuous there. The test is stronger in effect.
- **R26 "after trimming"** is named in the spec's R26 sentence as a matching form. No scenario and no test uses a trim-only twin such as "Ben" and "Ben ". The qa.md Then does not require it, so this is a coverage note for the spec owner.

## Failures
None. There is nothing to route to the Dev Solver and no reproduction to give.

## PROCESSES
- `node --test --test-reporter=spec "tests/**/*.test.js"` (Node v24.11.1): ran to completion under `timeout 300`, exit 0. Its PID was not captured because the run was foreground.
- `node probe-money.mjs`: ran to completion under `timeout 120`, exit 0. Its PID was not captured for the same reason.
- Liveness check: `tasklist` lists no `node.exe`. The `timeout` wrapper of the check itself is the only process from this session still listed.
- No server, browser, watcher or background job was started.
