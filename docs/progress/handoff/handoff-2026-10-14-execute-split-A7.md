# Handoff. Split v1.1.0 execute, task A7 (Split switch and Subtotal), not started

Written 2026-10-14 by the frontend developer role. A6 is committed (`4b806ff`). The brief said to continue past A6 only below about 30 percent context, and this session was at about 39 percent when A6 closed, so A7 goes to a fresh agent. Nothing of A7 is written. The working tree holds only the orchestrator's own modified files (`CLAUDE.md`, `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`), the untracked run folders the brief lists as not mine (`qa/functional/20261014-131624-chromium` to `20261014-153212-chromium`) and the untracked handoffs.

## Where it stands
- HEAD `4b806ff`. A0 to A6, A17 and C1 to C6 done. Build order A7 next, then A8 to A16, A18 (A19 and A20 are not this builder's).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261014-230954/node-test.txt`). Chromium `docs/modules/split-app/qa/functional/20261014-230956-chromium/`, 438 passed, 98 xfailed, 0 failed. WebKit `docs/modules/split-app/qa/functional/20261014-231400-webkit/`, 435 passed, 2 failed, 1 skipped (IME), 98 xfailed. That WebKit run is A7's baseline by id.
- The WebKit failures left are A16's. `test_R29_the_dialog_opens_with_the_safe_choice_focused` (843.984375 against 844, R59 (1)) and `test_R30_leaving_the_dialog_without_starting_over[escape]` (R59 (2)). The two flakes of the R59 (2) class may show, F-A3-1 `test_R30_leaving_the_dialog_without_starting_over[cancel]` and F-A5-1 `test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[escape]`, both A16's. Any other new WebKit failure is sorted (a), (b) or (c) as A0 sorted, and any H-04 failure (a double tap acting twice) is a finding.
- The commit table in `BUILD.md` ("v1.1.0 commits so far") has no A6 row yet. A7's section adds it, `| A6 | 4b806ff | feat(split-app): Charges content in div.charges, the v1.1.0 rate errors with rule 13, and the hint tap per engine (task A6, R15, R10, R59), recorded by the A7 section |`.

## What A7 is (spec task A7, one line)
"Split switch and Subtotal with the error rule. -> R8, R9, R10". Read R8, R9 and R10 in `docs/modules/split-app/spec.md` whole, the DOM contract of `div.blk.split#splitBlk` (`h2.blk-h#splitH`, `div.mode-sw` with `#modeEven` and `#modeItem`, `name="mode"`, each followed by its `label[for]`, no legend) and of `div.blk#evenBlock` (`label.blk-h.solo[for=evenSub]`, `div.field.money.sub-field#evenField` with `span.unit` "RM" and `input#evenSub`, `aria-describedby="evenErr"` at all times, then `p.err#evenErr`). The `@R8` and `@R9` scenarios (qa.md near lines 398 to 426), the Subtotal rows of the `@R10` scenarios (near 428 to 525), `@R59 @per_engine` "Focus after a mouse click is the engine's own" (near 1914, the "By item" label row), checklist rows K1-40 to K1-43, K2-05 to K2-07, BE-07, BE-08, ST-01. Goldens `docs/design/bill-even.html`, `bill-empty.html`, `bill-items.html` with their `.md` files. The design row (`taste-skill`, `frontend-design`) loads first, A7 draws UI.

## Where things are
- `src/ui/mode.js` (1.0, `fieldset.mode` with a hidden legend, ids `mode-even` and `mode-item`) and `src/ui/subtotal.js` (1.0, `section.block`, `span.field.money`, `input#subtotal`, label with a hidden " in RM" ending, `createErrorSlot`). `src/main.js` appends `mode.el` and `subtotal.el` to `#work` after the two sections.
- The v1.1.0 error is `createFieldError(wrapper, input, { id, message, hint })` in `src/ui/field-error.js` (A6). Subtotal uses it with no `hint`, so `aria-describedby` is `evenErr` at all times (CG-P6) and only `hidden`, `is-bad` and `aria-invalid` change. `createErrorSlot` (1.0) then has the prices as its last user, and A8 deletes it.
- `onFieldLeave` (`src/ui/field-leave.js`) and the flags of `src/errors.js` are unchanged by A6 and serve Subtotal as they are.
- Tests. A6 split the R10 outlines by markup (BUILD.md A6, judgment call 2). The v1.1.0 functions carry the qa.md names and the rate rows, `test_R10_an_inline_error_waits_for_the_field_to_be_left` and `test_R10_a_cleared_error_does_not_come_back_until_the_field_is_left_again` (`RATE_ERROR_CASES`), `test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on` (`RATE_PRESS_CASES`). The 1.0 Subtotal and price rows run as `..._in_the_1_0_markup` (`ERROR_CASES`, `PRESS_CASES`). A7 moves its `subtotal` rows across (the press row's target is `#chargesBtn`, mouse and touch, `evenErr`), sees them fail first, and leaves the `item-price` rows for A8.
- Helpers from A6. `field_error(field, error_id)` and `error_state(message, described, shown)` read and give the v1.1.0 error state in one evaluate. `shown_errors(page)` lists every error that shows in either markup, `invalid_fields(page)` counts `aria-invalid="true"`.
- About 21 lines of `tests/browser/test_app.py` read the 1.0 Split and Subtotal (`#mode-even`, `#mode-item`, `#subtotal`, `subtotal-error`, `span.field.money:has(#subtotal)`, `subtotal_field` by the name "Subtotal in RM", which the v1.1.0 `aria-label` keeps). `SNAPSHOT_JS` reads `#subtotal`. `test_R10_a_restored_bad_field_shows_its_error_at_once` keeps its 1.0 Subtotal line for A7. `test_R10_typing_bad_text_in_a_focused_field_shows_no_error_early`, `test_R10_an_error_survives_a_mode_switch` and `test_R10_a_press_that_ends_runs_each_waiting_handler_once` are the Subtotal's 1.0 tests. `R3_STATES` marks `bill-empty` and `bill-unreadable` at 1280 for A7.
- The render check pattern. `docs/modules/split-app/qa/charges-render/render.py` (A6) compares the R3 walk of one block and the box and 28 computed properties of each part against the goldens. A copy for `#splitBlk` and `#evenBlock` against `bill-even.html` and `bill-empty.html` is the cheap render proof.

## Traps worth knowing
- R59. A mouse click on a radio's label focuses the radio in Chromium and leaves `document.activeElement` on `body` in WebKit. The R8 arrow key scenario reaches the radio by Tab, never by a label click.
- The `@R10` Subtotal press row's target is the Charges header row above the field, because nothing sits under the Subtotal since A4. Below 1024 px only.
- A restored bill folds both sections below 1024 px, and a cold boot folds Charges. Every Subtotal test on a seed reaches the field without opening anything (Split and Subtotal are not in a section), but a test that also touches a rate needs `open_charges_first`.
- RED on the 1.0 behaviour. The v1.1.0 Subtotal ids do not exist on the A6 tree, so a test that clicks `#evenSub` there times out. A6 ran its RED against a throwaway stub of the 1.0 block with only the v1.1.0 ids and names (stub S-A, BUILD.md A6, RED first), put in and taken out with the Edit tool, never committed, `grep STUB src/` empty after.
- A test that waits on a missing element times out instead of failing on its assertion. Read with one `page.evaluate` that gives null for a missing part (`field_error`, `CHARGES_BLOCK_JS`).

## Open items carried
- Q-A6-1 (BUILD.md A6). qa.md's hint tap scenario says "a body recorder is added", whose body half makes WebKit send the tap's mouse events. Recommended wording, a window recorder. For the planner.
- F-A5-1 and F-A3-1 (BUILD.md A5, A3). The R30 Escape and Cancel timing flakes, owner A16, which waits for the dialog's `close` event.
- F-A4-1 (BUILD.md A4). qa.md R36 "3 s after load it is empty" cannot hold with the golden CSS. Recommended wording for A18, "no animation is running".
- Q-A3-1 (BUILD.md A3). The R47 `@static` scan bans "removeItem(", the test bans `.removeItem(`, ruled ORCH, qa wording at the next planner touch.
- A17 judgment calls 1 and 4. The held Enter qa wording, and "#addItem has focus" read by the name "Add item" until A8 gives the button its id.
- A5 judgment calls 1 to 7, A6 judgment calls 7 and 8. `tests/browser/live_e2e.py` still reads the 1.0 Charges ids (A20), the R32 tab order names the rates "... in percent" (A18).

## Resume here
1. Load the design row and declare what transferred.
2. RED. The A7 scenarios as tests, seen failing on their asserted property (a throwaway stub where the code of `4b806ff` cannot reach the property, never committed), in Chromium and WebKit, each run folder recorded.
3. Build R8, R9 and the Subtotal rows of R10 (`createFieldError` with no hint), render check against `bill-even.html` and `bill-empty.html`, then Node, Chromium and WebKit, WebKit compared by id with `20261014-231400-webkit/`.
4. BUILD.md A7 section (with the A6 row in the commit table), tick A7 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A7, R8, R9, R10)`.

## Processes
None alive at writing. Every pytest server, the render server and the probe server were stopped by their own `finally` (each printed STOPPED with the port free again). The background suite run (`b43pwpurc`, Node, Chromium then WebKit) completed.
