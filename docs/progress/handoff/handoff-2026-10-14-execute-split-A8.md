# Handoff. Split v1.1.0 execute, task A8 (Items and the frame), not started

Written 2026-10-14 at 23.44 by the frontend developer role. A7 is committed (`0180d36`). The brief said to stop after A7 because the usage windows are near their limit tonight, so A8 goes to a fresh agent. Nothing of A8 is written. The working tree holds only the orchestrator's own modified files (`CLAUDE.md`, `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`), the untracked run folders the brief lists as not mine (`qa/functional/20261014-131624-chromium` to `20261014-153212-chromium`) and the untracked handoffs.

## Where it stands
- HEAD `0180d36`. A0 to A7, A17 and C1 to C6 done. Build order A8 next, then A9 to A16, A18 (A19 and A20 are not this builder's).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261014-233306/node-test.txt`). Chromium `docs/modules/split-app/qa/functional/20261014-233206-chromium/`, 441 passed, 96 xfailed, 0 failed. WebKit `docs/modules/split-app/qa/functional/20261014-233538-webkit/`, 437 passed, 3 failed, 1 skipped (IME), 96 xfailed. That WebKit run is A8's baseline by id.
- The WebKit failures left are A16's. `test_R29_the_dialog_opens_with_the_safe_choice_focused` (843.984375 against 844, R59 (1)), `test_R30_leaving_the_dialog_without_starting_over[escape]` (R59 (2)) and the flake F-A5-1 `test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[escape]`, which showed in this run with its known signature. F-A3-1 `test_R30_leaving_the_dialog_without_starting_over[cancel]` may show too. Any other new WebKit failure is sorted (a), (b) or (c) as A0 sorted, and any H-04 failure (a double tap acting twice) is a finding.
- The commit table in `BUILD.md` ("v1.1.0 commits so far") has no A7 row yet. A8's section adds it, `| A7 | 0180d36 | feat(split-app): Split block with the mode switch, the Subtotal block with its v1.1.0 error, absent from the DOM in by-item mode (task A7, R8, R9, R10), recorded by the A8 section |`.

## What A8 is (spec task A8)
"Items and the frame. Rows, toggles, the `needs` marker, price errors, Add item and Remove with the limit, `data-up` and `data-down`, focus. It rewrites `test_R12_add_an_item_remove_one_and_reach_the_limit` and `test_R14_a_price_error_sits_in_the_item_line`, the last readers of the fixture `states.html`, and deletes `tests/fixtures/design-v1.0.0/` with them (B1). -> R11, R12, R13, R14, R56, R10, R34". Read R11 to R14, R56, R10 and R34 in `docs/modules/split-app/spec.md` whole, with the DOM contract of `#itemsBlock`. Goldens `bill-items.html`, `bill-items-open.html`, `bill-unassigned.html`, `rate-error.html` and the item frames of `states.html` in `docs/design/`, with their `.md` files. The design row (`taste-skill`, `frontend-design`) loads first, A8 draws UI.

## Where things are
- `src/ui/items.js` is still 1.0 (`section` hidden by its own `update` when `bill.mode !== "item"`). R8 says the block of the other mode is absent from the DOM. A7 did that for Subtotal with `placeSubtotal` in `src/main.js` (put back after `#splitBlk` only when missing, because moving the block that holds the focused field drops its focus). The Items block needs the same.
- Price errors. `createErrorSlot` in `src/ui/field-error.js` (the 1.0 form) has the prices as its last user. A8 moves them to `createFieldError(wrapper, input, { id: "ie{j}", message: AMOUNT_ERROR })` with no hint (CG-P6, the price names `ie{j}` at all times) and deletes `createErrorSlot` with its doc and the module header lines about it.
- Tests that wait for A8.
  - The `[item-price]` rows of the 1.0 functions `test_R10_an_inline_error_waits_for_the_field_to_be_left_in_the_1_0_markup`, `test_R10_a_cleared_error_does_not_come_back_until_the_field_is_left_again_in_the_1_0_markup` (`ERROR_CASES`) and `test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on_in_the_1_0_markup` (`PRESS_CASES`, mouse and touch). Move each row to the v1.1.0 function (`RATE_ERROR_CASES` and `RATE_PRESS_CASES`, which since A7 take the field, both `aria-describedby` values and the press target per row), see it fail first, and delete the 1.0 functions and lists with the last row.
  - `shown_errors` reads both markups (`p.err` without `hidden`, or a 1.0 `p.error`). After A8 the `p.error` half can go.
  - The `#itemsBlock` lines of the two `@R8` scenarios (A7 judgment call 1). `test_R8_arrow_keys_move_between_the_modes` ("#itemsBlock is in the DOM") and `test_R8_switching_modes_keeps_both_sets_of_input` ("#evenBlock is not in the DOM and #itemsBlock is", then not after Even). Both still read `ol.items` or nothing for the Items side. `split_state` (`SPLIT_STATE_JS`) can gain an `itemsBlocks` count.
  - `R3_STATES` marks `rate-error` at 1280 for A8. `R3_PAIRS` takes `None` for a complete pair (A7).
  - `support.active_label` returns the id "addItem" before the text "Add item" (A5 note), and A17 reads "#addItem has focus" by the name "Add item" until A8 gives the button its id (A17 judgment call 4).
  - Lines in many tests read the 1.0 item markup (`li.item`, `ol.items`, `price-error-i5`, `p.error#price-error-i5`, `item_name`, `item_price` by "Item {n} price in RM"). qa.md v1.1.0 names a price by its item, for example "Char kuey teow price in RM".
- RED on the 1.0 behaviour. A test that waits on a missing element times out instead of failing on its assertion. Read with one `page.evaluate` that gives null for a missing part (`field_error`, `SPLIT_MARKUP_JS`, `CHARGES_BLOCK_JS`). Where the old code cannot reach the property, a throwaway stub put in and taken out with the Edit tool, never committed, `grep STUB src/` empty after (A6 S-A, A7 S-A7).
- The render check pattern. `docs/modules/split-app/qa/split-render/render.py` (A7) and `qa/charges-render/render.py` (A6) compare the R3 walk of a block and the box and 28 computed properties of each part against the goldens.

## Traps worth knowing
- R59. A mouse click on a radio's label focuses the radio in Chromium and leaves `document.activeElement` on `body` in WebKit (`test_R59_focus_after_a_mouse_click_is_the_engines_own[by-item-label]`). Reach a control by Tab when focus matters.
- A restored bill folds both sections below 1024 px, and a cold boot folds Charges. A test that touches a rate needs `open_charges_first`.
- Do not run a Chromium job while a full suite runs. The R30 Escape and Cancel tests are timing flakes under load.

## Open items carried
- Q-A6-1 (BUILD.md A6). qa.md's hint tap scenario says "a body recorder is added". Recommended wording, a window recorder. For the planner.
- F-A5-1 and F-A3-1 (BUILD.md A5, A3). The R30 Escape and Cancel timing flakes, owner A16, which waits for the dialog's `close` event.
- F-A4-1 (BUILD.md A4). qa.md R36 "3 s after load it is empty" cannot hold with the golden CSS. Recommended wording for A18, "no animation is running".
- Q-A3-1 (BUILD.md A3). The R47 `@static` scan bans "removeItem(", the test bans `.removeItem(`, ruled ORCH, qa wording at the next planner touch.
- A17 judgment calls 1 and 4, A5 judgment calls 1 to 7, A6 judgment calls 7 and 8.
- A7 judgment calls 1 and 4. The strip lines of the `@R8` scenarios ("Total RM 116.60", "Total RM 5.83") wait for A11. `tests/browser/live_e2e.py` still reads `fieldset.mode label` and the 1.0 Charges ids (A20).

## Resume here
1. Load the design row and declare what transferred.
2. RED. The A8 scenarios as tests, seen failing on their asserted property in Chromium and WebKit, each run folder recorded.
3. Build R11 to R14, R56, the price rows of R10 and R34, delete `createErrorSlot` and `tests/fixtures/design-v1.0.0/` as the task line says, render check against the item goldens, then Node, Chromium and WebKit, WebKit compared by id with `20261014-233538-webkit/`.
4. BUILD.md A8 section (with the A7 row in the commit table), tick A8 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A8, R11, R12, R13, R14, R56, R10, R34)`.

## Processes
None alive at writing. Every pytest server and the render server were stopped by their own `finally` (the render server printed STOPPED with the port free again). The background suite run (Chromium then WebKit) completed with exit 0.
