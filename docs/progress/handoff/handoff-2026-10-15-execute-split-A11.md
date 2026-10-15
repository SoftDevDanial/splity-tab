# Handoff. Split v1.1.0 execute, task A11 (the strip with --strip-h), not started

Written 2026-10-15 by the frontend developer role. A10 is committed (`fb8dbc3`). The brief said to stop after A10, so A11 goes to a fresh agent. Nothing of A11 is written. The working tree holds only the orchestrator's own modified files (`CLAUDE.md`, `README.md`, `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`), the untracked run folders that are not the builder's (`qa/functional/20261014-131624-chromium` to `20261014-153212-chromium`) and the untracked handoffs.

## Where it stands
- HEAD `fb8dbc3`. A0 to A10, A17 and C1 to C6 done. Build order A11 next, then A12 to A16, A18 (A19 and A20 are not this builder's).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261015-120736/node-test.txt`). Chromium `docs/modules/split-app/qa/functional/20261015-120747-chromium/`, 475 passed, 87 xfailed, 0 failed. WebKit `docs/modules/split-app/qa/functional/20261015-121115-webkit/`, 471 passed, 3 failed, 1 skipped (IME), 87 xfailed. That WebKit run is A11's baseline by id.
- The WebKit failures left are A16's. `test_R29_the_dialog_opens_with_the_safe_choice_focused` (R59 (1)), `test_R30_leaving_the_dialog_without_starting_over[escape]` (R59 (2), a timing flake that swaps with F-A3-1 `[cancel]` from run to run) and F-A5-1 `test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[escape]`. Any other new WebKit failure is sorted (a), (b) or (c) as A0 sorted, and any H-04 failure is a finding.
- The commit table in `BUILD.md` ("v1.1.0 commits so far") has no A10 row yet. A11's section adds it, `| A10 | fb8dbc3 | feat(split-app): Copy summary on the card and the strip, one status line in every status paragraph ... (task A10, R22, R23, R24), recorded by the A11 section |`.

## What A11 is (spec task A11)
"The strip with `--strip-h`. -> R49". Read R49 in `docs/modules/split-app/spec.md` whole, the DOM contract's `div.strip.glass.dense#strip` block (the `#stripInfo` forms for even and item, blocked and unassigned, `#stripStatus`, `#splitsBtn`, `#stripCopy [disabled unless even or item]`), R16 to R18's strip lines and the Allowed differences. qa.md `@R49` "The strip for each result" (an outline with the strip's height per state, 111, 108, 128 and 153 px) and "No control the user tabs to is left under the strip", checklist rows K1-57 to K1-59, K2-15, BE-12, RE-08, BU-07, ST-07 to ST-09. Goldens, the strip of every phone golden at 390 and 360 and the S4 strip pieces and "By item, nothing to work out" in `states.html`, with their `.md` files. The design row (`taste-skill`, `frontend-design`) loads first, A11 draws UI.

## Where things are
- `index.html`. `#strip` with the foil, `div.strip-in`, `div.strip-top` holding an empty `#stripInfo` and `p.status#stripStatus`, and `div.strip-acts` with `#splitsBtn` and `#stripCopy`, both always enabled.
- `src/main.js`. The strip's static buttons get their icons at boot. `#stripCopy` calls `copySummary` (A10), which returns before the clipboard for a result without splits, so a click on it today does nothing then. `render` draws `#stripStatus` with `showCopyStatus` (`src/ui/copy-status.js`). Nothing fills `#stripInfo`, sets `disabled` on `#stripCopy` or sets `--strip-h`. `#splitsBtn` is A12's.
- `src/ui/receipt.js`. `hasSplits`, `BLOCKED_MESSAGE` and `unassignedMessage` hold the R17 and R18 texts the strip repeats (the strip's `p.s-msg` has no icon for blocked and the warning circle for unassigned). Reuse them rather than copying the strings (DRY).
- `src/system.css`. `:root` sets `--strip-h: 111px` below 1024 px and `0px` from 1024 px, and `.work`'s bottom padding and `html`'s `scroll-padding-bottom` read it. The app's measured value goes on the root element through the CSSOM (R38 allows `style` on the root, allowed difference 7).
- Tests that wait for A11, each `xfail(strict=True, reason="task A11")`, 29 cases (listed in `skips.txt` of the Chromium proof run). `test_R1_page_works_from_a_sub_path`, `test_R2_cold_boot_is_a_new_bill_with_no_seed`, 18 rows of `test_R3_rendered_markup_matches_its_golden` at 390 and 360, `test_R10_an_empty_rate_leaves_the_strip_reading_check_the_charges`, `test_R7_the_item_left_with_nobody_needs_a_person_on_the_card_and_the_strip`, `test_R12_a_new_item_leaves_the_strip_reading_add_each_item`, `test_R18_the_strip_says_items_still_need_a_person`, `test_R23_a_blocked_copy_grows_the_strip` (A10's, the strip 153 px and `--strip-h` "153px" after a refused copy), the three `test_R28_the_strip_follows_the_bill_without_storage` rows and `test_R57_after_a_held_enter_on_the_only_remove_the_strip_reads_the_empty_message`. `STRIP_MESSAGE_JS` (A9 block of `tests/browser/test_app.py`) reads `#stripMsg` and `#stripCopy`. `test_R17_the_strip_and_the_sheet_say_why_too` is marked A12 and checks the strip too.

## Traps worth knowing
- RED on the 1.0 behaviour. A test that waits on a missing element times out instead of failing on its assertion. Read with one `page.evaluate` that gives null for a missing part. Where a test passes on today's behaviour, its RED is a stub run (a throwaway stub put in and taken out with the Edit tool, never committed, `grep -r STUB src/` empty after).
- Never touch the system clipboard. Every context gets `tests/browser/clipboard/recorder.js` (or `reject.js`, `missing.js`), and copy is asserted on `window.testClipboardText` and `window.testClipboardWrites`. `click_copy` (A10 block) asserts the button's count and waits two frames.
- The strip is not displayed from 1024 px. Measure it at 390 and 360. The status's place beside or under the Total is the CSS's once `#stripInfo` holds the Total (A10 render check, `docs/modules/split-app/qa/status-render/`, shows the status alone on its row today).
- `--strip-h` must follow every size change of the strip (a status that wraps, a message on two lines, a resize). A `ResizeObserver` on the strip is the trigger R56 already uses for the frame. Its callback must change no size, or it can loop.
- A Copy summary that becomes `disabled` while it has focus loses it in some engines. Check focus after a change that blocks the result while `#stripCopy` is focused.
- Do not run a Chromium job while a full suite runs. The R30 Escape and Cancel tests are timing flakes under load.
- No shell redirection of any kind, no heredoc and no pipe after a test runner, not even for a read-only probe (A9 slipped twice and A10 once, see their Process slips). Put probe scripts in the session scratch folder with the Write tool.
- The render check pattern. `docs/modules/split-app/qa/receipt-render/render.py` (A9) and `docs/modules/split-app/qa/status-render/render.py` (A10). A `states.html` piece below the first screen needs `full_page=True` on a clipped screenshot.

## Open items carried
- Q-A10-1 (BUILD.md A10). A clipboard answer that comes after the bill changed shows nothing, as built. Recommended answer, keep it. For the owner.
- F-A10-1 (BUILD.md A10). qa.md ST-12 and states.md say the card's failure line wraps to two lines, which holds for the S4 piece's 282 px card body but not for the app's card at 1280 (410 px), where the golden CSS gives one centred line. For the planner.
- Q-A9-1 (BUILD.md A9). Archive copy of a replaced source module. Recommended answer, no. For the orchestrator.
- Q-A8-1 is ruled (USER, H-06, keep as written).
- F-A8-1, Q-A6-1, F-A4-1, Q-A3-1, F-A5-1, F-A3-1 and the judgment calls of A5 to A10 (see their BUILD.md sections).
- `tests/browser/live_e2e.py` still reads the 1.0 panel and the 1.0 forms in `tests/browser/expected.py` (`EVEN_MESSAGE`, `S1_SUMMARY`, `S1_ROWS`, `S1_CHECK`, `S2_CHECK` and the S2 ones). A20 rewrites the gate.

## Resume here
1. Load the design row and declare what transferred.
2. RED. The A11 scenarios of qa.md (`@R49` and the strip lines A9 and A10 left marked `task A11`) as tests, seen failing on their asserted property in Chromium and WebKit before the build, each run folder recorded.
3. Build R49 (the strip's info for each result, `#stripCopy` disabled unless even or item, `--strip-h` set through the CSSOM and kept current), render check against the phone goldens' strip and the S4 strip pieces, then Node, Chromium and WebKit, WebKit compared by id with `20261015-121115-webkit/`.
4. BUILD.md A11 section (with the A10 row in the commit table), tick A11 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A11, R49)`.

## Processes
None alive at writing. Every pytest server and the render check's server were stopped by their own `finally` (each printed STOPPED with the port free again). Nothing ran in the background.
