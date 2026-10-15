# Build record: split-core

Built by the backend developer role from `spec.md` and `qa.md`. Pure ES modules under `src/core/`, no
dependencies, no DOM, no I/O. Money is integer cents, rates are integer basis points.

## Tasks to commits
| Task | Requirements | Commit | Files |
|---|---|---|---|
| 1. Parsing | R1, R2, R3 | `bb3fba9` | `src/core/money.js`, `tests/money.test.js`, `tests/support/rng.js` |
| 2. Formatting | R4, R5 | `3399736` | `src/core/money.js`, `tests/money.test.js` |
| 3. Allocation | R7, R8, R9 | `5d98d13` | `src/core/allocate.js`, `tests/allocate.test.js` |
| 4. Bill state rules | R10 to R17, R26 | `8228969` | `src/core/bill.js`, `tests/bill.test.js`, `tests/support/bills.js` |
| 5. Charges and result | R6, R18 to R21, R23, R26 | `e40c171` | `src/core/result.js`, `tests/result.test.js` |
| 6. Invariant sweep | R22 | `50b6a8b` | `tests/invariants.test.js` |
| 7. Summary text | R24, R26 | `27458ba` | `src/core/summary.js`, `tests/summary.test.js` |
| 8. Hygiene scan | R25 | `025e232` | `tests/hygiene.test.js` |

8 of 8 tasks done. ~~Last run of `node --test "tests/**/*.test.js"`: tests 185, pass 185, fail 0.~~
[Changed 2026-10-09, solver, code-review WR-01 to WR-10: ~~after the fix batch, tests 212, pass 212, fail 0.~~
The fix commits and their evidence are listed once, in `findings/code-review.md`, section "Solver (2026-10-09)".]
[Changed 2026-10-09, solver, code-review WR-14: the two counts above were true when written and have rotted
with every test added since. The stable effect is `fail 0` on `node --test "tests/**/*.test.js"`. The count is
in the run's own output (`tests`, `pass`), and the count at each round is in the findings files.]

## How to run the tests
From the project root (Node 24): `node --test "tests/**/*.test.js"`. The quotes matter, and a bare
`node --test tests/` fails on Node 24 (CG-6). No install step, no `package.json`: Node 24 detects ES
module syntax in `.js` files by itself.

Test titles start with their tag (`@R8 ...`), so `grep -r "@R8" tests` maps a requirement to its cases.

## Deviations
None architectural. No new dependency, table, service or contract change. Three judgment calls where the
spec is silent, listed so the orchestrator can confirm or overturn them:

1. **Setters with an unknown id.** `setPersonName`, `setItemName` and `setItemPriceText` return the input
   unchanged (same reference) when the id is not in the bill. R15 does not say; this follows R12 to R14.
2. **How `computeResult` finds unassigned items.** It counts an item as unassigned when no person in the
   bill is on it (`holderIndexes` is empty), not when `who` is empty. The two are identical while the
   invariant "every id in `who` is a person of the bill" holds. The difference is that a bill breaking the
   invariant yields `unassigned` instead of a `RangeError` from `allocateEvenly(price, 0)`.
3. **Test helpers.** `tests/support/rng.js` (mulberry32, `randomInt`) and `tests/support/bills.js`
   (`buildBill`, `deepFreeze` and the named example bills of `qa.md`) are shared by several test files, so
   they exist once (DRY). They are not under `src/core/`, and the test glob only picks `*.test.js`.

QA evidence file `docs/modules/split-core/qa/unit/<timestamp>/node-test.txt` was not written. It belongs to
the QA run, and the filesystem rules forbid writing it through a shell redirect.

## Non-goals honoured
No payments or QR, no other currency or locale formatting (no `Intl`, no group separator), no 5-sen
rounding, no tips or discounts or other charges, no history or second bill, no DOM, storage, clipboard,
network or timer code, and no generic helpers beyond what the requirements call. `tests/hygiene.test.js`
~~enforces the purity part mechanically.~~ [Changed 2026-10-09, solver, code-review WR-07: enforces the
spec R25 list, which now also covers the locale-format and timer non-goals. `queueMicrotask` is not on
the list, since the ruling did not add it.] [Changed 2026-10-09, solver, security SEC-04: superseded.
`queueMicrotask` and nine more names (dynamic code and other ambient sources) are now banned in code
only, see spec R25. The code-only reading is `codeOnly` in `tests/hygiene.test.js`.] [Changed 2026-10-09,
solver, security SEC-05: the name scan is best-effort. The primary R25 guard is the runtime trap test in
the same file (`trapped`, `runEveryExport`), see spec R25.]

## Exports (the contract, nothing more)
| File | Exports |
|---|---|
| `src/core/money.js` | `parseAmount`, `parseRate`, `formatMoney`, `formatRate`, `AMOUNT_MIN_CENTS`, `AMOUNT_MAX_CENTS` |
| `src/core/allocate.js` | `allocateEvenly`, `allocateByWeight` |
| `src/core/bill.js` | `LIMITS`, `newBill`, `addPerson`, `removePerson`, `setPersonName`, `setMode`, `setSubtotalText`, `setServiceText`, `setSstText`, `addItem`, `removeItem`, `setItemName`, `setItemPriceText`, `toggleItemPerson`, `personLabel`, `itemLabel` |
| `src/core/result.js` | `billCharges`, `computeResult` |
| `src/core/summary.js` | `summaryText` |

## Internal helpers (module-private, by symbol)
| File | Symbols | Why they exist |
|---|---|---|
| `money.js` | `readHundredths`, `DECIMAL_TEXT`, ~~`MAX_WHOLE_DIGITS`~~ [removed 2026-10-09, solver, WR-06], `EMPTY`, `INVALID`. [Added 2026-10-09, solver, WR-08: `wholePart`.] | One reader for the amount and rate grammar. ~~The digit-count cap runs before any numeric conversion, so a 400-digit string is never converted.~~ [Changed 2026-10-09, WR-06: `readHundredths` takes the caller's ceiling and derives the digit cap from it. The reasoning is its comment.] [Added 2026-10-09, WR-08: `wholePart` is the exact integer division shared by `formatMoney`, `formatRate` and the digit cap.] |
| `allocate.js` | `assertAmount` | The shared amount precondition of both allocators (R9). |
| `bill.js` | `billWith`, `personWith`, `itemWith`, `changeItem`, `labelOf` | Rebuild a bill, person or item from known fields only (no spread of a parsed object), the shared item setter, and the shared label fallback. [Changed 2026-10-09, solver, code-review WR-09: `changeItem` serves all three item actions, `toggleItemPerson` included, and is the only place an item id is looked up.] |
| `result.js` | `applyRate`, `BASIS_POINTS`, `sum`, `blocked`, `evenResult`, `itemResult`, `holderIndexes`, `itemTotals` | Half-up rate application with remainder arithmetic, and the two result builders split by mode. |

## Notes for the README reconcile
- ~~Rounding: `applyRate` stays in `Number` because its products are at most 649,999,935 x 2000 (below 2^53),
  and it uses remainder arithmetic so the division is exact. `allocateByWeight` is the only `BigInt` site,
  as the spec requires (charges x weight reaches about 1.4e16).~~
  [Changed 2026-10-09, solver, code-review WR-02: both numbers were wrong, and the derivation was a copy of
  source comments. Rounding and exact division are explained once, in the comments on `applyRate` and
  `allocateByWeight` (the only `BigInt` site), with the bounds in spec Invariants.]
- ~~`allocateEvenly` subtracts the remainder before dividing, so the division is exact for any safe integer.~~
  [Changed 2026-10-09, solver, WR-02: see the comment in `allocateEvenly`.]
- ~~Parsing caps the whole part at 9 digits after dropping leading zeros. This is an internal safety cap, not
  a rule: the range checks (99,999.99 for amounts, 30 and 20 percent for rates) decide validity.~~
  [Changed 2026-10-09, solver, code-review WR-06: the 9 was a magic number. The cap is now derived from
  the caller's ceiling, and the derivation is stated once, in the comment in `readHundredths`.]
- ~~Actions rebuild every object from known fields, so a `Bill` parsed from JSON loses stray keys and a
  `__proto__` key on its first action (threat model, object integrity). `tests/bill.test.js` covers it.~~
  [Changed 2026-10-09, solver, code-review WR-03: false. Untouched people and items keep their stray keys.
  What is rebuilt and what is shared is stated once, in the `bill.js` module header. The tests titled
  `@R16 <action> on a parsed bill builds only known fields` check each action on a parsed bill directly.]

## Boot
Nothing to boot. This module has no server or UI. `split-app` imports it with relative ES module paths such
as `./core/money.js`.

## v1.1.0 build record
Built by the backend developer role. Each task is one commit, `node --test "tests/**/*.test.js"` green on it.

### C1 (2026-10-14) formatAmount and the thousands comma. R34, R4, R24
- **Commit.** `d9be159`, `feat(split-core): formatAmount and the thousands comma in formatMoney (task C1, R4, R34, R24)`.
- **Files.** `src/core/money.js` (new export `formatAmount`, `formatMoney` is now "RM " plus `formatAmount`, private `THOUSANDS_GAP`), `tests/money.test.js`, `tests/summary.test.js`, `tests/support/bills.js` (fixture W1), `tests/hygiene.test.js`.
- **Tests.** 289 pass, 0 fail (275 before). New or changed cases: the R4 table (four rows with a comma, two new), the R34 table (9 rows), the R34 and R4 seeded equivalence sweep (1000 values, mulberry32 seed 20261013), the R24 W1 summary block.
- **RED first.** Two stubs of `formatAmount` against the 1.0 `formatMoney`. Stub 1 (no comma) failed the 4 R4 rows, 5 R34 rows and the W1 summary. Stub 2 (correct figure, 1.0 `formatMoney`) failed the 4 R4 rows, the sweep and the W1 summary. Output and stub source in `qa/unit/20261014-131203-red/`.
- **R24.** `summaryText` needed no code change, it already prints money through `formatMoney`. The W1 block is the proof (CG-P1, ruled).
- **Deviation, one line.** `tests/hygiene.test.js` `runEveryExport` gained one call, `money.formatAmount(779999922)`. The runtime trap fails on any export the workload does not run, so without it the commit would be red. The rest of C6 (the `spare.js` workload, the negative control) is not started.
- **Comments.** `formatMoney` doc rewritten (the CG-5 text was false now), `formatAmount` doc and the `THOUSANDS_GAP` note added.
- **Non-goals.** No locale API, no other currency, no spare sen line in the summary.

### C2 (2026-10-14) the spare field and sparePeople. R10, R11, R12, R27, R28. NOT COMMITTED, BLOCKED (corrected below, committed)
- **Status.** The code and tests are done and in the working tree, but the commit is held. From C2 on, `newBill()` carries `spare` and the 1.0 draft decoder (`src/draft.js`, split-app, task A1) drops it, so two 1.0 Node cases in `tests/draft.test.js` and 130 Chromium browser cases go red. Both are outside this module. The task asks for a green `node --test` on the commit, so the builder stopped and returned the choice to the orchestrator.
- **Files.** `src/core/bill.js` (`spare` in the `Bill` typedef and `billWith`, `newBill`, `addPerson`, `removePerson`, new export `sparePeople`, private `spareWith` and `spareWithout`), `tests/bill.test.js`, `tests/hygiene.test.js` (one workload call, `bill.sparePeople(b)`, same reason as C1).
- **Tests.** `node --test "tests/**/*.test.js"`: 308 tests, 306 pass, 2 fail. Every `tests/bill.test.js` case passes. The 2 failures are 1.0 cases of split-app, `@R25 encodeDraft and decodeDraft round-trip a new bill and an item bill` and `@R27 loadDraft tells none, ok and unreadable apart, and saveDraft writes the encoded draft`. Both expect the decoded bill to equal `newBill()`, which now has `spare`.
- **Chromium browser suite.** `python -m pytest tests/browser -q --engine chromium` on the working tree: 129 failed, 301 passed, 1 error (the error is counted besides the 430 cases). The same tree with C2 switched off for a probe (no `spare` in `newBill`, `spareWith` and `spareWithout` tolerating a bill without it, probe edits reverted) gave 430 passed, so C2 alone causes all of the reds. Two causes. (1) A reloaded 1.0 draft gives core a bill without `spare`, so `addPerson` and `removePerson` throw (`test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it` 72 cases, `test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing` 24, `test_R7_a_double_click_or_double_tap_on_remove_removes_one_row` 2, `test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it` 2, `test_R7_a_separate_click_on_what_slid_under_the_pointer_is_not_held_back` 1, `test_R7_two_separate_clicks_and_a_key_press_still_remove_a_row_each` 1, `test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word` 1 error). (2) The stored draft now holds `"spare":{"rule":"top"}` while the 1.0 tests expect the old text (`test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note` 24, `test_R25_a_bill_built_by_gestures_is_stored_like_its_seed` 2, `test_R31_start_over` 1). The failure screenshots are in `docs/modules/split-app/qa/functional/20261014-131624-chromium/` and `20261014-131836-chromium/` (the two full runs) and `20261014-131753-chromium/`, `20261014-132019-chromium/` (single-test runs). No browser test was edited.
- **RED first.** Stub 1 `sparePeople` returns `[]` (33 cases red), then stubs 2 and 3 (`sparePeople` returns every id, `removePerson` returns a copy on refusal) for the cases stub 1 passed. Output and stub source in `qa/unit/20261014-131433-red/`.
- **Comments.** `sparePeople` doc, a note on `spareWith` and `spareWithout`, the module header now names the spare choice, `newBill` doc.
- **Non-goals.** No `chooseSpareRule`, `chooseSparePerson`, `pickAgain` (C5), no change to `computeResult` (C4), no decoder change (A1).
- **Status, corrected 2026-10-14 by the frontend developer role. Committed with the reds marked for task A1** (orchestrator's call, the Tasks rule for a test a later task fixes). No assertion and no app source changed. A1 removes every mark.
  - Re-run before the marks. `node --test` 308 tests, 306 pass, 2 fail (the two cases above). Chromium suite 129 failed, 1 teardown error, 300 passed, the same tests as above. Evidence `docs/modules/split-app/qa/functional/20261014-140338-chromium/` (not committed, it waits for the orchestrator's ruling with the four earlier red folders).
  - Node marks. The two `tests/draft.test.js` cases carry `{ todo: "task A1" }`. They still run and report, and the run passes (308 tests, 306 pass, 0 fail, 2 todo).
  - Browser marks in `tests/browser/test_app.py`, each `xfail(strict=True, reason="task A1")`. Whole functions `test_R25_a_bill_built_by_gestures_is_stored_like_its_seed` (2), `test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note` (24), `test_R31_start_over` (1), `test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it` (72), `test_R7_a_separate_click_on_what_slid_under_the_pointer_is_not_held_back` (1). Params `person-2-of-5` of `REMOVE_CASES` (5 cases over `test_R7_a_double_click_or_double_tap_on_remove_removes_one_row`, `test_R7_two_separate_clicks_and_a_key_press_still_remove_a_row_each` and `test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it`), and `S2-person-3-of-3` and `S8-person-12-of-12` of `LAST_ROW_CASES` (24 cases).
  - Deviation, one mark not strict. `test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word` carries `xfail(strict=False, reason="task A1")`. Its call passes and only the teardown's page error check fails, and pytest fails a strict xfail whose call passes, so no strict mark can make the run green. A1 removes it with the others.
  - Run with the marks, `docs/modules/split-app/qa/functional/20261014-140838-chromium/`. Exit 0, 430 call reports (300 passed, 1 xpassed, which is the one above, and 129 xfailed). The 103 teardown reports marked xfail are the page error checks of marked tests, so `junit.xml` reads 533 tests and 232 skipped.

### C3 (2026-10-14) blocking row (c) is "no item has a valid price". R18, PD-24
- **Commit.** See the commit line of this task in `git log` (`feat(split-core): blocking row c ... (task C3, R18)`).
- **Files.** `src/core/result.js` (`itemResult`: reason `no-prices` when no price parses, `prices` when some do and some do not, typedef and doc), `tests/result.test.js` (the R18 table), and under PD-24 the only app files, `src/ui/panel.js` (`BLOCKED_MESSAGE` key `no-items` renamed `no-prices`, its 1.0 text kept) and `tests/browser/test_app.py` (the `item-unpriced` row of `BLOCKED_CASES` and the first message check of `test_R12_add_an_item_remove_one_and_reach_the_limit` now expect "Add an item to see the shares.").
- **Tests.** `node --test "tests/**/*.test.js"`: 316 pass, 0 fail. The R18 table now has 12 rows (rows 7 to 9 changed to `no-prices`, rows 10 to 12 added and pin that "one valid price with one empty is prices" and "a blank rate wins" do not move). Chromium browser suite (`python -m pytest tests/browser -q`): 424 passed, 6 xfailed (the six `task A19` marks), 0 failed. No other browser test went red.
- **RED first.** The 1.0 `itemResult` is the stub (changed R#, no stub file). Rows 7, 8 and 9 failed on their own assertions (actual `no-items`, `prices`, `prices`). Output in `qa/unit/20261014-143300-red/`.
- **Comments.** One why-comment in `itemResult` (one reason for "no items" and "every price invalid"), typedef and `computeResult` doc renamed.
- **Design row.** Not applicable. The key rename keeps the 1.0 text and changes no look, so there is no UI work and no design assignment to load.
- **Non-goals.** No new receipt message (that is app task A9).
- **For the README reconcile.** The blocked reasons are `rates`, `subtotal`, `no-prices`, `prices`. `no-items` no longer exists.

### C4 (2026-10-14) the spare sen divisions and result.spare. R20, R21, R22, R32, R33
- **Commit.** See the commit line of this task in `git log` (`feat(split-core): spare sen divisions and result.spare ... (task C4, R32)`).
- **Files.** `src/core/result.js` (private `floorParts`, `TOP`, `onePerson`, `atRandom`, `spareRule`, `divide`, `nobody`, `spareResult`, `evenResult` and `itemResult` rebuilt on them, `holderIndexes` kept, `itemTotals` removed, `SpareResult` typedef), `tests/result.test.js` (R32 table, One person on an item they did not have, the random walk with a wrap, the fallback and its stored choice, R33), `tests/invariants.test.js` (the R22 sweep, each bill under Top, One person and At random), `tests/summary.test.js` (S2-ONE and S2-RANDOM blocks), `tests/support/bills.js` (`withSpare`, moved out of `tests/bill.test.js` so two files share it).
- **Tests.** `node --test "tests/**/*.test.js"`: 337 pass, 0 fail (316 before). Chromium browser suite: 424 passed, 6 xfailed, 0 failed, so the new `spare` key on a result changes nothing the 1.0 UI reads.
- **How it works.** One step serves all three rules (R32). `divide` gives each member of a division its exact floor part, then hands the division's spare sen (amount less the floors) to whoever the rule names. Even mode is one division, by-item is one per item and then the charges, over the people with items, weighted by items. Top gives the first members, One person gives every spare sen to the chosen person (only when `sparePeople` holds them, else Top and the stored choice stays), At random keeps one cursor over `order` across all divisions.
- **RED first.** The C3 `computeResult` is stub 1 (20 failing cases, mostly the missing `spare` and the One and Random rows). Stub 2 puts a `spare` key on `blocked` and the unassigned return, which the "carry no spare" case needs. Output and stub source in `qa/unit/20261014-144100-red/`. After the build, three mutations were run against the sweep and the tables (One person acts as Top, the random cursor does not advance, Top gives the last members) and each went red, then they were reverted.
- **Judgment call, flagged.** `floorParts` gets the exact floor from `allocateByWeight(amount, [total - weight, weight])[1]`. The spec says the step is written once in `result.js` and the floor is "the exact R8 floor", and allocate.js must export only its two functions. A second BigInt division in `result.js` would duplicate `allocateByWeight`, and a third export would change the contract. `allocateByWeight` gives its leftover to the lowest index with weight, so index 1 of `[total - weight, weight]` is always the exact floor. `allocateEvenly` is now not called by `result.js` (it was the 1.0 Top path). It stays exported with R7 and its tests, and the new tests use both allocators as the oracle for Top. Say if you want the other shape.
- **Comments.** Header line on the divisions, why-comments on `floorParts`, the rule table (`TOP`, `onePerson`, `atRandom`), `spareRule`, `divide` and the payers line in `itemResult`.
- **Non-goals.** No `chooseSpareRule`, `chooseSparePerson` or `pickAgain` (C5), no line about spare sen in the summary (`summaryText` unchanged, the two new blocks only prove it prints the shares as chosen).
- **For the README reconcile.** `computeResult` now returns `spare: { count, rule, personId }` on `even` and `item` results and reads `bill.spare`. `rule` is the rule applied, so it reads `top` when a chosen person cannot take spare sen. A Bill without a `spare` field now throws in `computeResult` (the Bill shape has required it since C2).

### C5 (2026-10-14) chooseSpareRule, chooseSparePerson, pickAgain. R29, R30, R31
- **Commit.** See the commit line of this task in `git log` (`feat(split-core): chooseSpareRule, chooseSparePerson and pickAgain (task C5, R29, R30, R31)`).
- **Files.** `src/core/spare.js` (new, exports exactly the three, private `withSpare`, `drawOrder`, `rowsDiffer`, `MAX_DRAWS` 64), `tests/spare.test.js` (new, 22 cases), `tests/support/rng.js` (`scripted` and `constant` random sources that count their calls), `tests/hygiene.test.js` (two lines only, see the deviation).
- **Tests.** `node --test "tests/**/*.test.js"`: 361 pass, 0 fail (337 before).
- **RED first.** No `spare.js` yet, so two throwaway stubs: every export returns its input (22 cases, 15 red), then every export returns a fresh copy (so the "same bill object" cases go red too, 22 of 22 red). Output and stub source in `qa/unit/20261014-144700-red/`. After the build two mutations were run and went red, then reverted: Pick again comparing only `share` (the equal-share money-moving case), and a bound of 63 draws (two cases).
- **Deviation 1, `tests/hygiene.test.js`.** Two edits the commit needs to stay green, the same reason as C1 and C2. The R25 file-list pin gained `spare.js`, and the runtime-trap workload `runEveryExport` calls the three new exports (the trap fails on an export the workload does not run). The rest of C6 (the Math.random negative control for `spare.js`, the R16 coverage) is not started.
- **Deviation 2, the Bill field list in `spare.js`.** `withSpare` lists the eight Bill fields. `bill.js` has the same list as private `billWith`, and the contract says `bill.js` exports no more than it does, so `spare.js` cannot reuse it. The list is repeated rather than spread, because the threat model forbids spreading a parsed bill. If a ninth Bill field is ever added, both lists change. The alternative is to export `billWith` from `bill.js`, a contract change, so it is left for the orchestrator to decide. C6 pins the keys with a parsed-bill case.
- **Comments.** Module header (why a separate file, why the random source is an argument), `withSpare` (why listed out), `MAX_DRAWS` (CG-P3), a doc on each export.
- **Non-goals.** No random source inside core, no stored record of past draws, no rule beyond the three.
- **For the README reconcile.** `src/core/spare.js` exports `chooseSpareRule(bill, rule, random)`, `chooseSparePerson(bill, personId)` and `pickAgain(bill, random)`, all pure, all returning the same bill object when they change nothing. `random` is a function returning a number from 0 up to but not including 1, passed in by the caller (the app passes `Math.random`, PD-19). Pick again tries at most 64 orders.

### C6 (2026-10-14) the guards cover spare.js and every new export. R16, R25
- **Commit.** See the commit line of this task in `git log` (`test(split-core): R16 and R25 cover spare.js ... (task C6, R16, R25)`).
- **Files.** `tests/bill.test.js` (the R16 deep-freeze test gains the three choice actions, a second frozen-bill case for Pick again, and five parsed-bill cases that the new Bill and spare choice are built from known fields), `tests/hygiene.test.js` (the two Math.random negative controls for `spare.js`). No source file changed.
- **Tests.** `node --test "tests/**/*.test.js"`: 369 pass, 0 fail (361 before). Chromium browser suite (`python -m pytest tests/browser -q`): 424 passed, 6 xfailed, 0 failed, the same as after C3.
- **What covers every new export.** `formatAmount`, `sparePeople` and `computeResult` were covered in C1, C2 and C4 (a number to a string takes no object to freeze, and every C4 case passes a deep-frozen `withSpare` bill, so each checks R16). The three `spare.js` exports are in the runtime-trap workload (added in C5, `runEveryExport`) and now in the R16 deep-freeze and parsed-bill cases.
- **Negative control.** One `Math.random` is planted in `spare.js` in memory, two ways. At load (`void Math.random();`) and inside the draw (`drawOrder` is reassigned to a version that reads it, so only running `chooseSpareRule` reaches it). The scan flags both as exactly `Math.random`, and the runtime trap catches both. The same call on the real file gives no hits, so the hit comes from the plant.
- **RED first.** Four throwaway edits, all reverted: `withSpare` mutating its input and returning it (7 R16 cases red), `withSpare` spreading the bill (5 parsed-bill cases red), a real `Math.random` in `drawOrder` (the scan and the trap red, the `random ?? Math.random` form is seen by the scan only, which is the limit spec R25 states), and a trap blind to `Math.random` (the new control and the 1.0 trap control red). Output and edits in `qa/unit/20261014-145000-red/`.
- **Non-goals.** No source change, no new export.
- **For the README reconcile.** Nothing beyond C5. The hygiene test now pins six core files (`allocate.js`, `bill.js`, `money.js`, `result.js`, `spare.js`, `summary.js`).

## v1.1.0 step 5 solver round (2026-10-15, dev solver)
Findings from `findings/code-review.md`, routed by the orchestrator (ORCH). Each seen failing first, each in its own commit.
- **CR-S5-1 (R21 (4), R8), `042c359`.** `tests/result.test.js` gains "@R21 @R8 a by-item bill whose charges division is an R8 trap row gets the exact charges" with the private helper `itemsWorth`. It builds the reviewer's 38 item trap bill through `buildBill` and asserts the charges column [8246230, 53600495], equal to `allocateByWeight` on the trap row, and that a float floor misses the bill. RED on the reviewer's mutant K02 (a float `floorParts`), applied by the reviewer's `mutate.mjs` to a scratch copy: `qa/unit/20261015-233338-red-CR-S5-1/` (`red.txt`, `node-test-K02.txt`, 379 pass 1 fail, the new test, [8246231, 53600494]).
- **CR-S5-2 (DRY, the threat model's object integrity), `9277412`.** The Bill fields are listed once, by `newBill`. `bill.js` keeps the private `BILL_FIELDS = Object.keys(newBill())` and `billWith` builds its copy from it. `spare.js` imports `newBill` (already in the Contracts) and `withSpare` builds its copy from the same keys. No export added, so no Contracts change, and no spread. Deviation 2 of C5 is closed by this. Behaviour verified on the extraction (constitution, DRY safety): `qa/unit/20261015-233527-dry-CR-S5-2/` holds the Node run of `042c359` before (380 of 380) and of the change after (380 of 380, the same names), and three mutants of the new form, all killed by the existing tests (a spread `withSpare` 5, a dropped `nextId` 7, a spread `billWith` 13, `mutation-summary.json`).
- **Comments written or changed.** `bill.js`: the comment above `BILL_FIELDS` (why the list is read from `newBill` and who copies it) and the JSDoc of `billWith`, which replaces the false "One place that lists the Bill fields". `spare.js`: the comment above its `BILL_FIELDS` and the JSDoc of `withSpare`, which no longer says the fields are listed out. The test's comment says why the result path needs its own trap case.
- **Proof on the committed tree (`4462b4c`).** Node `qa/unit/20261015-234943/node-test.txt`, 380 of 380 (379 at the QA finder's run plus the CR-S5-1 case). The browser suites and the live gate are recorded in `split-app/BUILD.md`, same round.
- **For the README reconcile.** `billWith` and `withSpare` copy the keys of `newBill()` (one field list). No export changed.

## v1.1.0 task C7 (2026-10-16, security solver) plainName and the one class. R35, R24, R25
Ledger H-10 (USER 2026-10-16 00:07, option (1)), security SEC-S5-1 and SEC-S5-3 of split-app. Built with app task A22 in one build, C7 first because A22 imports `plainName`.
- **Commit.** `abfbe3e` (`fix(split-core): SEC-S5-1 and SEC-S5-3, plainName and the one class NAME_CONTROLS ...`).
- **Files.** `src/core/bill.js` gains the exported `NAME_CONTROLS` (`/[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/gu`) and `plainName(text)` (`text.replace(NAME_CONTROLS, "")`). `src/core/summary.js` drops its own `CONTROLS` and imports `NAME_CONTROLS`, its one code line now `row.name.replace(NAME_CONTROLS, " ")`. `tests/bill.test.js` gains the 11 rows of "plainName deletes the class and keeps everything else" and "plainName and summaryText read one class" (`spelled`, `PLAIN_ROWS`). `tests/hygiene.test.js` gains "the class is written once" (`SRC_DIR`, `IMPORTS_THE_CLASS`, `oneClassProblems`), and `runEveryExport` reads `NAME_CONTROLS` and calls `plainName`.
- **RED first.** Three stubs of `plainName` in `bill.js`, each put in and taken out with the Edit tool, `summary.js` on its own class meanwhile. RED 1 returns its input (`qa/unit/20261016-010625-red/`, 9 of the 13 new cases red). RED 2 also deletes `\p{Cf}` (`qa/unit/20261016-010548-red/`, the U+200B and emoji rows and both one-class tests red). RED 3 is added by this build (`qa/unit/20261016-010642-red/`, see Deviation 1). Every new case is red on its own assertion in at least one of the three, none on an import error. `stub.txt` in each folder holds the stub and the reading of the run.
- **DRY safety (constitution, principle 8).** `qa/unit/20261016-010829-dry-before/` is the real `plainName` with `summary.js` still on its literal, 393 tests, 392 pass, the one fail being "the class is written once". `qa/unit/20261016-010848-green/` is after the merge, 393 of 393. The 30 R24 test names have the same outcome in both, and across all names the only difference is that one test (`dry.txt`). The one-line scan has teeth, the same test reports a planted copy of `summary.js` back on a literal of its own, written into a temporary folder under the OS temp folder and removed in its `finally`.
- **Deviation 1, a third stub.** The two stubs C7 names cannot fail two new rows, "the Arabic name U+0639 U+0644 U+064A, a space and Lina stays the same text" and "the empty text gives the empty text", which hold no member of the class and no Cf. The method of `qa.md` (How to run, "RED first") asks that each new case is seen failing in at least one run, so RED 3 is a stub that normalises (NFKC, lower case) and gives an empty result a fallback. Both rows go red on it.
- **Deviation 2, the one-class test corrected after its first runs.** Its first form equated "Chen's row reads A B RM 38.86" with "plainName deleted the code point", as the `qa.md` line words it. For U+0020 the row reads "A B RM 38.86" because a space was typed, which `plainName` keeps, so the test would have failed on correct code (seen in the first stub 2 run, `qa/unit/20261016-010445-red/`, kept as history with the first stub 1 run `20261016-010406-red/`). The test now compares the whole row with "A B RM 38.86" when the code point is deleted and with "A" + the code point + "B RM 38.86" when kept, the oracle of the R24 test in `tests/summary.test.js`, and both stubs were run again on it. For the planner, the `qa.md` line "plainName gives AB exactly when Chen's row of summaryText reads A B RM 38.86" is false by its letter at U+0020.
- **Deviation 3, speed.** The one-class test swaps each name into the row of the one S2 result and calls `summaryText`, in place of working out 1,112,064 bills (every code point but the 2,048 surrogates). It first checks on 8 code points (U+0000, U+0020, U+0041, U+0085, U+200B, U+202E, U+2069, U+1F468) that the swapped row equals the bill with Chen renamed worked out whole. The test takes about 1.8 s.
- **Comments written or changed.** `bill.js`, the comment above `NAME_CONTROLS` (what the class holds, why a reader needs it gone, why it is written once, why the shared `g` flag is safe through `replace`) and the JSDoc of `plainName` (who calls it, that no action does). `summary.js`, the class comment moved to `bill.js` (one home), and the JSDoc names `NAME_CONTROLS` and says the summary does not rely on the app's removal. The tests' comments say why a title is spelled, why 79 is written by hand, why the row is compared whole and why the scan is a text scan.
- **Non-goals honoured.** No core action calls `plainName` (R15), `personLabel` and `itemLabel` are unchanged (R17), no name is trimmed, normalised or folded, nothing outside the class is removed. `\p{Bidi_Control}` appears on one line under `src/`.
- **Proof on the committed tree.** Node `qa/unit/20261016-012221/node-test.txt`, 400 of 400 on `4a19b4d` (C7 and A22). By id against `qa/unit/20261015-234943/`, 380 ids with the same outcome, 20 new (the 13 of C7 and the 7 of A22's decoder outline), 0 missing, 0 changed. The browser proofs are in `split-app/BUILD.md`, task A22.
- **For the README reconcile.** `src/core/bill.js` exports `NAME_CONTROLS` and `plainName(text)`, the text without control, separator and bidi characters (R35). `summaryText` reads that one class, so the names on screen and the copied summary use the same rule. The README line on `summaryText` stays true.
