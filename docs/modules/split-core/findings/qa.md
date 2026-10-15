---
module: split-core
kind: qa
ran_against: running-app
status: green
counts: { pass: 69, fail: 0, blocked: 0 }
date: 2026-10-15
head: d58f4ce
node_run: docs/modules/split-core/qa/unit/20261015-204618/node-test.txt
probe_run: docs/modules/split-core/qa/probe-core/20261015-205500/
---
# QA findings: split-core

**Verdict: PASS.** 69 of 69 qa.md scenarios pass. 0 fail, 0 blocked, 0 not run. `node --test "tests/**/*.test.js"` gives 379 tests, 379 pass, 0 fail, 0 skipped, 0 cancelled (419.9 ms). Every R1 to R34 has at least one scenario and at least one passing tagged test.

Run by the QA finder (read-only) on 2026-10-15 at HEAD `d58f4ce`, working tree clean for `src/`, `tests/`, `index.html` and `docs/design/` (`git diff --stat HEAD` on those paths is empty). This module has no UI, so "the running app" is the module exports under Node v24.11.1. The previous finders ran on 2026-10-09 at `bf69ed3`. The module changed on 2026-10-14 (tasks C1 to C6), so this is a full re-run of the v1.1.0 contract of 2026-10-13, not a delta.

| Level | Pass | Fail | Not run |
|---|---|---|---|
| qa.md scenarios (69, of which 30 are Outlines) | 69 | 0 | 0 |
| Node tests, `node --test "tests/**/*.test.js"` (379, of which 343 are in the eight split-core files and 36 in split-app's `draft`, `errors` and `repeat` files) | 379 | 0 | 0 |
| Independent probe checks, `core_probe.mjs` (written from the qa.md tables, not from `tests/`) | 35 | 0 | 0 |

## Evidence
- `docs/modules/split-core/qa/unit/20261015-204618/node-test.txt`. The full runner output (379 result lines and the summary). The file was written with the Write tool and diffed against the run's scratch capture, identical.
- `docs/modules/split-core/qa/probe-core/20261015-205500/core_probe.mjs` and `probe-out.txt`. 35 checks of S2, S1, W1, MAX-E, the spare rules, Pick again, the parsers, the formatters, the allocators and a line-break name, built through `newBill` and the actions only. My first run of the probe reported 1 fail on "S2 charges". It was my own mistake (the check compared JSON text, so the key order of the object counted). I changed the probe to compare with sorted keys and re-ran. The stored output is the corrected run (35 of 35), and re-running the stored source from its folder gives the same output.
- The 343 and 36 split of the Node count comes from two further runs of the same files (the eight core files, then the three app files), both with 0 failures. Those two outputs stayed in scratch and are not cited as evidence.

## Scenario table
Each scenario is backed by the Node tests named in the last column. Outline rows have one test each, so "12" means 12 rows. All listed tests passed in the run above. A line number is the `Scenario` line of `qa.md`.

| # | line | tag | scenario | tests (title starts) | verdict |
|---|---|---|---|---|---|
| 1 | 71 | @R1 | parseAmount accepts valid amounts as exact cents | 12 `@R1 parseAmount("12") ...` | PASS |
| 2 | 91 | @R1 @R2 | parseAmount rejects invalid text as invalid, not empty | 17 `@R1 @R2 parseAmount("0") ...` (all 17 rows, the full-width "１２" row included) | PASS |
| 3 | 116 | @R1 @R2 | A 401-character amount is rejected without overflow or exception | `@R1 @R2 a 401-character amount is invalid and does not throw` | PASS |
| 4 | 124 | @R1 @R3 | A whole part longer than the ceiling's is refused before any numeric conversion | `@R1 @R3 a whole part longer than the ceiling's ...` (the Number spy) | PASS |
| 5 | 132 | @R2 | Empty or white-space text is reported as empty | 2 `@R2 "" ...`, `@R2 "   " ...` | PASS |
| 6 | 142 | @R2 | The parsers never throw for any string | `@R2 the parsers never throw ...` (500 seeded strings) | PASS |
| 7 | 148 | @R3 | parseRate reads basis points within its maximum | 17 `@R3 parseRate(...)` | PASS |
| 8 | 175 | @R4 | formatMoney writes RM, a space, ringgit with thousands commas and two sen digits | 11 `@R4 formatMoney(...)` | PASS |
| 9 | 194 | @R5 | formatRate drops trailing zeros and adds a percent sign | 7 `@R5 formatRate(...)` | PASS |
| 10 | 209 | @R6 | Service and SST round half up to the cent | 10 `@R6 billCharges(...)` | PASS |
| 11 | 228 | @R7 | allocateEvenly floors and hands leftover sen to the top | 7 `@R7 allocateEvenly(...)` | PASS |
| 12 | 244 | @R8 | allocateByWeight floors exactly and skips zero weights for leftovers | 7 `@R8 allocateByWeight(...)` and `@R8 BigInt trap: ...` | PASS |
| 13 | 265 | @R8 @R23 | allocateByWeight gives the MAX-I charges split exactly, with products past 2^53 | `@R8 @R23 allocateByWeight gives the MAX-I charges split exactly ...` | PASS |
| 14 | 271 | @R9 | Allocation rejects impossible input | 11 `@R9 ... throws RangeError` (the 9 rows and 2 extra) | PASS |
| 15 | 288 | @R10 | A new bill has two people, even mode, the default rates and Top of the list | `@R10 a new bill has two people ...` | PASS |
| 16 | 293 | @R11 | Adding a person appends an empty-named person with the next id | `@R11 adding a person appends an empty-named person with the next id` | PASS |
| 17 | 302 | @R11 | A new person's id never reuses a removed id | `@R11 a new person's id comes from nextId ...` | PASS |
| 18 | 308 | @R11 | Adding a 13th person does nothing | `@R11 the twelfth person is accepted and the thirteenth does nothing` | PASS |
| 19 | 314 | @R12 | Removing a person removes them from every item | `@R12 removing a person removes them from every item` | PASS |
| 20 | 321 | @R12 | Removing is refused at 2 people or for an unknown id | `@R12 removing is refused at 2 people or for an unknown id` | PASS |
| 21 | 331 | @R13 | Adding an item appends an empty, unassigned item | `@R13 adding an item appends an empty, unassigned item` | PASS |
| 22 | 337 | @R13 | The 51st item is refused and removing works at any time | `@R13 the 51st item is refused and removing works at any time` | PASS |
| 23 | 345 | @R14 | Tapping toggles a person on an item | `@R14 tapping toggles a person on an item` | PASS |
| 24 | 354 | @R15 | Switching modes keeps both sets of input | `@R15 switching modes keeps both sets of input` | PASS |
| 25 | 361 | @R15 | Setters store text exactly as typed | `@R15 setters store text exactly as typed`, `@R15 each setter changes only its own field` | PASS |
| 26 | 369 | @R16 | No action mutates its input | `@R16 no action mutates a deep-frozen bill ...` and the 22 `... builds only known fields` cases | PASS |
| 27 | 379 | @R16 | The other functions that take objects leave them alone | `@R16 @R17 the labels leave a frozen person or item alone`, `@R16 allocateByWeight leaves frozen weights alone`, `@R16 summaryText leaves a deep-frozen result alone` | PASS |
| 28 | 386 | @R17 | Display names fall back to their position | 6 `@R17 person named ...` and `@R17 item named ...` | PASS |
| 29 | 400 | @R18 | The first blocking rule wins | 12 `@R18 blocking row N is ...` (the 12 rows, no-prices rows 7 to 9 included) | PASS |
| 30 | 423 | @R18 @R20 | Even mode ignores broken items | `@R18 @R20 even mode ignores broken items` | PASS |
| 31 | 429 | @R19 | Unassigned items are counted and the charges are still known | `@R19 unassigned items are counted ...` | PASS |
| 32 | 435 | @R19 | Two unassigned items give a count of 2 | `@R19 two unassigned items give a count of 2` | PASS |
| 33 | 441 | @R20 | Even results match the worked examples | 5 `@R20 @R23 even result for S2, E1, E2, E3, MAX-E` | PASS |
| 34 | 455 | @R21 | By-item results match the worked examples | 5 `@R21 @R23 by-item result for S1, I2, I3, I4, MAX-I` | PASS |
| 35 | 468 | @R21 | A shared item's leftover sen follow the people list, not the tap order | `@R21 a shared item's leftover sen follow the people list ...` | PASS |
| 36 | 479 | @R22 | Generated bills always add up | `@R22 generated bills always add up, under every spare rule` (2000 bills, three spare rules) | PASS |
| 37 | 493 | @R23 | The largest bills compute exactly | `@R20 @R23 even result for MAX-E`, `@R21 @R23 by-item result for MAX-I`, `@R23 MAX-I charges are exact at the bound` | PASS |
| 38 | 499 | @R24 | Summary text is exact | 5 `@R24 summary text for S2, S1, E2, E3, I2 is exact` | PASS |
| 39 | 512 | @R24 | A blank name prints as its position | `@R24 a blank name prints as its position` | PASS |
| 40 | 519 | @R24 | A line break inside a name prints as a space, so it cannot forge a line | 7 `@R24 a LF, CR, VT, FF, NEL, LS, PS inside a name ...` | PASS |
| 41 | 537 | @R24 | Any other control character in a name prints as a space | 5 `@R24 a NUL, FS, GS, RS, ESC inside a name ...` | PASS |
| 42 | 551 | @R24 | A right-to-left override in a name cannot reorder the share | `@R24 a right-to-left override in a name ...` | PASS |
| 43 | 559 | @R24 | Exactly the R24 class prints as a space, every other code point up to U+2069 as typed | `@R24 exactly the R24 class prints as a space ...` (79 members) | PASS |
| 44 | 567 | @R24 | Every code point above U+2069 prints as typed | `@R24 every code point above U+2069 prints as typed` | PASS |
| 45 | 576 | @R24 | Every member of the class in one name is replaced, one space each | `@R24 every member of the class in one name is replaced, one space each` | PASS |
| 46 | 584 | @R24 | A lone surrogate prints as typed | `@R24 a lone surrogate is not in the class ...` | PASS |
| 47 | 591 | @R24 | By-item rows get the same line-break guard | `@R24 by-item rows get the same line-break guard` | PASS |
| 48 | 597 | @R24 | summaryText refuses results without shares | `@R24 results without shares are refused with TypeError` | PASS |
| 49 | 607 | @R25 | The core files are pure | 27 `@R25` tests: the scan sees the core files, the negative control, the code-only scan, 11 planted names, 6 files by 2 checks, the files import each other | PASS |
| 50 | 627 | @R25 | The core touches no banned global or method at load or while every export runs (runtime trap) | 22 `@R25 runtime trap ...` and `@R25 a Math.random planted ...` tests: F1 to F10 with F4b and F6b plants, the pinned lists, put-back, fresh copy, no stale hits, unreadable stack | PASS |
| 51 | 648 | @R26 | Equal names are stored as typed | `@R26 equal names are stored as typed and nobody is merged` | PASS |
| 52 | 655 | @R26 | Tapping and removing address a person by id, not by name | `@R26 tapping and removing address a person by id, not by name` | PASS |
| 53 | 663 | @R26 | Equal names give one row each | `@R26 D1: ...`, `@R26 D2: ...` | PASS |
| 54 | 675 | @R26 | Equal names give one summary line each | `@R26 equal names print one line each`, `@R24 summary text for D1 ...`, `@R24 summary text for D2 ...` | PASS |
| 55 | 686 | @R27 @R11 | Adding a person extends the drawn order and keeps the people already drawn in place | `@R27 @R11 adding a person extends the drawn order ...` | PASS |
| 56 | 693 | @R27 @R12 | Removing a person keeps the spare choice valid | 4 `@R27 @R12 removing p3 / p2 / p3 / p1 from spare ...` (the 4 rows) | PASS |
| 57 | 705 | @R27 @R15 | A mode switch, the setters and the item actions never touch the spare choice | `@R27 @R15 a mode switch, the setters and the item actions never touch the spare choice` | PASS |
| 58 | 711 | @R28 | Who can take the spare sen | 6 `@R28 sparePeople of S2, S1, I2, I3, I2 switched to even, D2` (plus a new-bill case and a frozen-input case) | PASS |
| 59 | 725 | @R29 | Choosing a rule | 5 `@R29 choosing "one" / "random" / "top" ...` (the 5 rows) | PASS |
| 60 | 741 | @R29 | Choosing the rule already set, or a rule that does not exist, changes nothing | `@R29 choosing the rule already set, an unknown rule or One person with nobody to pick changes nothing` | PASS |
| 61 | 748 | @R30 | Choosing the one person | 3 `@R30 choosing pN on S2 ...` and `@R30 a person who cannot take spare sen, is already chosen or is unknown changes nothing` (the 3 same-bill rows) | PASS |
| 62 | 761 | @R31 | Pick again draws until the splits change | `@R31 Pick again draws until the splits change` (four source calls, two draws) | PASS |
| 63 | 769 | @R31 | Pick again returns the same bill when it cannot or must not draw | `@R31 the S2 bill with spare top ...`, `... spare one p2 ...`, `... empty subtotal (blocked) ...`, `... with no spare sen no order can change the splits: 64 draws ...` | PASS |
| 64 | 782 | @R32 @R20 @R21 | Every spare sen goes where its rule says | 10 `@R32 @R20 @R21 S2 / S1 / I3 / W1 with spare ...` (the 10 rows) | PASS |
| 65 | 801 | @R32 @R33 | One person falls back to Top of the list while the chosen person has nothing, and the choice is kept | `@R32 @R33 One person falls back to Top of the list ...` | PASS |
| 66 | 810 | @R33 | The result names the rule in effect | 4 `@R33 the result of S2 / E2 with spare ... names ...` and `@R33 a blocked result and an unassigned result carry no spare` | PASS |
| 67 | 824 | @R24 @R32 | The summary prints the shares as the spare rule left them | 3 `@R24 summary text for S2-ONE, S2-RANDOM, W1 ... is exact` | PASS |
| 68 | 836 | @R34 | formatAmount writes the figure with thousands commas and no currency | 9 `@R34 formatAmount(...)` | PASS |
| 69 | 853 | @R34 @R4 | formatMoney is RM, a space and formatAmount, for every cents value | `@R34 @R4 formatMoney is RM, a space and formatAmount, for 1000 seeded values` | PASS |

## Findings
None. No scenario fails, and the independent probe agrees with the named tables of `qa.md`.

## Not run
None. The contract has no gate scenario for this module (no UI, no fidelity gate).

## Observations (no verdict impact)
- The Node run is one command for both modules. The 36 tests of `tests/draft.test.js`, `tests/errors.test.js` and `tests/repeat.test.js` (split-app's `@node` scenarios R57 and R61, and the draft and error-flag rules) are in the same 379. They are judged in `docs/modules/split-app/findings/qa.md`, which cites this run folder.
