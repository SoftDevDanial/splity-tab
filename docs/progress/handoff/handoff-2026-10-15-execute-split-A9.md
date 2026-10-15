# Handoff. Split v1.1.0 execute, task A9 (the receipt renderer and the card), not started

Written 2026-10-15 by the frontend developer role. A8 is committed (`e1969da`). The brief said to stop after A8, so A9 goes to a fresh agent. Nothing of A9 is written. The working tree holds only the orchestrator's own modified files (`CLAUDE.md`, `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`), the untracked run folders that are not the builder's (`qa/functional/20261014-131624-chromium` to `20261014-153212-chromium`) and the untracked handoffs.

## Where it stands
- HEAD `e1969da`. A0 to A8, A17 and C1 to C6 done. Build order A9 next, then A10 to A16, A18 (A19 and A20 are not this builder's).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261015-080238/node-test.txt`). Chromium `docs/modules/split-app/qa/functional/20261015-080244-chromium/`, 450 passed, 94 xfailed, 0 failed. WebKit `docs/modules/split-app/qa/functional/20261015-080541-webkit/`, 445 passed, 4 failed, 1 skipped (IME), 94 xfailed. That WebKit run is A9's baseline by id.
- The WebKit failures left are A16's. `test_R29_the_dialog_opens_with_the_safe_choice_focused` (R59 (1)), `test_R30_leaving_the_dialog_without_starting_over[escape]` (R59 (2)), F-A5-1 `test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[escape]` and F-A3-1 `test_R30_leaving_the_dialog_without_starting_over[cancel]`, both of which showed in this run. Any other new WebKit failure is sorted (a), (b) or (c) as A0 sorted, and any H-04 failure (a double tap acting twice) is a finding.
- The commit table in `BUILD.md` ("v1.1.0 commits so far") has no A8 row yet. A9's section adds it, `| A8 | e1969da | feat(split-app): Items block in its scrolling frame with data-up and data-down, item rows with the v1.1.0 price error, toggles, the needs marker, Add item and Remove with the limit and focus, absent from the DOM in even mode, 1.0 fixtures and createErrorSlot deleted (task A8, ...), recorded by the A9 section |`.

## What A9 is (spec task A9)
"The receipt renderer and the card. Blocked, unassigned, even (with `many` and `--rows`) and by-item forms, the quiet regions. -> R16, R17, R18, R19, R20, R21". Read R16 to R21 in `docs/modules/split-app/spec.md` whole, the receipt part of the DOM contract (after the body block, "The receipt is written once (PD-20)" and its markup), the Copy table and R51 to R54 only as far as the card's spare line, which is A13's. Goldens `bill-items.html`, `bill-even.html`, `bill-empty.html`, `bill-unassigned.html`, `bill-twelve.html` (`many`, `--rows`), `bill-large.html`, `rate-error.html` and the card pieces of `states.html`, with their `.md` files. The design row (`taste-skill`, `frontend-design`) loads first, A9 draws UI.

## Where things are
- `src/ui/panel.js` is still the 1.0 bill panel (`table.shares`, `dl.sum`, `button.copy`), and `src/ui/receipt.js` holds `blockedReceipt` (A2), which `render` in `src/main.js` uses for a blocked result. R16 says one renderer for the card and the sheet (the sheet is A12's), so A9 writes it once with the card ids and leaves the sheet ids for A12.
- Copy and its status are A10's (R22 to R24). The 1.0 `copySummary`, `setStatus` and `hasShares` in `src/main.js` and `panel.js` still serve the 1.0 panel. Keep their behaviour working through A9, or name what moves.
- Tests that wait for A9. `xfail(strict=True, reason="task A9")` on `test_R16_the_panel_follows_every_keystroke_and_stays_quiet`, `test_R16_the_status_is_the_only_live_element_and_only_while_the_table_is`, `test_R17_when_the_shares_cannot_be_worked_out` (six rows), `test_R18_items_that_still_need_a_person`, `test_R7_removing_a_person_can_leave_an_item_without_anyone`, `R3_STATES` `bill-unassigned` at 1280, and the `card-K1` case near the R3 walk tests. The 1.0 forms that read `table.shares` and `dl.sum` and still pass (`test_R9_a_subtotal_drives_the_even_split`, `test_R19_the_bill_summary_shows_its_working`, `test_R20_the_even_split_from_a_cold_boot`, `test_R21_*`, `test_R13_tapping_a_person_changes_the_shares`, `test_R5_a_blank_name_reads_as_its_position_in_the_shares_row`, `test_R8_the_panel_follows_each_mode`) are A9's to rewrite to their qa.md scenarios.
- Lines left by A8 for A9 (BUILD.md A8 judgment call 8). The card's rows with their working in "Tapping a person on an item" (qa.md `@R13`), and the card's `div.r-msg` in "Items that still need a person" (`@R18`). The marker lines of `@R18` are `test_R18_every_item_with_nobody_carries_the_needs_marker`, done.
- `test_R7_the_item_left_with_nobody_needs_a_person_on_the_card_and_the_strip` is marked A11 and needs A9's `div.r-msg` too.

## Traps worth knowing
- RED on the 1.0 behaviour. A test that waits on a missing element times out instead of failing on its assertion. Read with one `page.evaluate` that gives null for a missing part (`ITEMS_JS`, `field_error`, `SPLIT_MARKUP_JS`). Where the old code cannot reach the property, a throwaway stub put in and taken out with the Edit tool, never committed, `grep -r STUB src/` empty after. Where a test passes on 1.0 behaviour, its RED is a stub run.
- "The card reads" is `support.card_text` (every text node joined with a space, Q-A2-1).
- The card is not displayed below 1024 px but is in the DOM. Measure it at 1280.
- At 1280 the item frame's height depends on the blocks above it, and `render` calls `items.markFrame()` last (A8 judgment call 2). A receipt change does not move the working column, but keep that call last.
- A scout's point on a pill must be checked to hit the pill, rounded corners are not hits (A8 judgment call 5).
- Do not run a Chromium job while a full suite runs. The R30 Escape and Cancel tests are timing flakes under load.
- The render check pattern. `docs/modules/split-app/qa/items-render/render.py` (A8) compares the R3 walk of a block, the box and 28 computed properties of each part, and the pseudo elements, against the goldens.

## Open items carried
- F-A8-1 (BUILD.md A8). qa.md R14 and ST-02 "plus text-align right" cannot hold with the golden CSS. Recommended wording, "plus justify-self end, its right edge at the price field's right edge". For the planner.
- Q-A8-1 (BUILD.md A8). A new blank item carries the amber `needs` bar until someone is tapped, as R18 is written. Recommended answer, keep it. For the owner.
- Q-A6-1, F-A4-1, Q-A3-1, F-A5-1, F-A3-1, A17 judgment calls 1 and 4, A5 judgment calls 1 to 7, A6 judgment calls 7 and 8, A7 judgment calls 1 and 4 (see their BUILD.md sections).
- `tests/browser/live_e2e.py` still reads `p.error`, `fieldset.mode label`, the 1.0 Charges ids and "Item {n} price in RM" (A20).

## Resume here
1. Load the design row and declare what transferred.
2. RED. The A9 scenarios as tests, seen failing on their asserted property in Chromium and WebKit, each run folder recorded.
3. Build R16 to R21 for the card, render check against the card goldens, then Node, Chromium and WebKit, WebKit compared by id with `20261015-080541-webkit/`.
4. BUILD.md A9 section (with the A8 row in the commit table), tick A9 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A9, R16, R17, R18, R19, R20, R21)`.

## Processes
None alive at writing. Every pytest server and the render server were stopped by their own `finally` (each printed STOPPED with the port free again). The background suite run (Chromium then WebKit) completed with exit 0.
