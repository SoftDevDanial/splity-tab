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
