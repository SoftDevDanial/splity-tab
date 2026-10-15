# Handoff. Split v1.1.0 execute, task A12 (the Splits sheet), not started

Written 2026-10-15 by the frontend developer role. A11 is committed (`7a8dd78`). The brief said to stop after A11, so A12 goes to a fresh agent. Nothing of A12 is written. The working tree holds only the orchestrator's own modified files (`CLAUDE.md`, `README.md`, `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`), the untracked run folders that are not the builder's (`qa/functional/20261014-131624-chromium` to `20261014-153212-chromium`) and the untracked handoffs.

## Where it stands
- HEAD `7a8dd78`. A0 to A11, A17 and C1 to C6 done. Build order A12 next, then A13 to A16, A18 (A19 and A20 are not this builder's).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261015-124313/node-test.txt`). Chromium `docs/modules/split-app/qa/functional/20261015-124316-chromium/`, 514 passed, 56 xfailed, 0 failed. WebKit `docs/modules/split-app/qa/functional/20261015-124632-webkit/`, 509 passed, 4 failed, 1 skipped (IME), 56 xfailed. That WebKit run is A12's baseline by id.
- The WebKit failures left. A16's three, `test_R29_the_dialog_opens_with_the_safe_choice_focused` (R59 (1)), `test_R30_leaving_the_dialog_without_starting_over[escape]` (R59 (2), a timing flake that swaps with F-A3-1 `[cancel]`) and F-A5-1 `test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[escape]`. And A11's F-A11-1, `test_R49_no_control_the_user_tabs_to_is_left_under_the_strip`, sorted (b), open with the owner and the planner as Q-A11-1 (WebKit's focus scroll does not read `scroll-padding-bottom`). Any other new WebKit failure is sorted (a), (b) or (c) as A0 sorted, and any H-04 failure is a finding.
- The commit table in `BUILD.md` ("v1.1.0 commits so far") has no A11 row yet. A12's section adds it, `| A11 | 7a8dd78 | feat(split-app): the strip shows the Total or the reason there is none, Copy summary disabled without splits, and the root's --strip-h kept at the strip's height through the CSSOM (task A11, R49), recorded by the A12 section |`.

## What A12 is (spec task A12)
"The Splits sheet (PD-18, PD-20, PD-21). -> R50". Read R50 in `docs/modules/split-app/spec.md` whole, the DOM contract's `dialog.sheet-dlg#splitsDlg` block and "The receipt is written once (PD-20)" (in the sheet only the heading has an id, `sheetSplitsH`), the Gesture to action rows "click Splits", "Close, Esc or backdrop of the sheet" and "viewport crosses 1024 px", PD-18, PD-20 and PD-21, and the Allowed differences 3 and 6. qa.md, the six `@R50` scenarios (from "The Splits sheet opens with the card's receipt"), the sheet lines other tasks left for A12 (below), and the P2 checklist (`splits-sheet.html`, inventory P2, at 390 x 844 and 360 x 780). Goldens, `splits-sheet.html` and its `.md`. The design row (`taste-skill`, `frontend-design`) loads first, A12 draws UI.

## Where things are
- `index.html`. `dialog.sheet-dlg#splitsDlg[aria-label=Splits]`, empty. `#splitsBtn` in the strip, with its caret added in `src/main.js` and no listener.
- `src/ui/receipt.js`. `createReceipt(rbody, { ids, onCopy })` draws every result into a `div.rbody`, with ids from `ids` (`withId`). The sheet passes only `{ head: "sheetSplitsH" }` (A9 judgment call 5). Copy summary and its status paragraph are kept nodes, so the sheet's own receipt keeps its own pair. `showCopyStatus` (`src/ui/copy-status.js`) draws the sheet's `p.status` through `createReceipt` with no further code (A10).
- `src/ui/strip.js` (A11). `createStrip` owns `#stripInfo`, `#stripStatus` and `#stripCopy`. Splits is not wired there, by A11 judgment call 4.
- `src/ui/dialog.js` (`createDialog`) is the New bill dialog's. `swallowRepeatClicks` and `isRepeatClick` in `src/ui/dom.js` are the guard PD-21 arms on open and close.
- `src/main.js`. `render` calls `card.update`, `strip.update`, `notes.update` and `items.markFrame`. A sheet that is open must update live in `render` (R50 "It updates live while the sheet is open").
- Tests that wait for A12, each `xfail(strict=True, reason="task A12")`. `test_R3_the_walk_sees_every_rendered_element_and_flags_each_kind_of_change`, `test_R16_the_sheet_holds_one_live_element`, the eight rows of `test_R17_the_strip_and_the_sheet_say_why_too`, `test_R20_the_sheet_lists_the_splits_as_the_card_does`, the `[K2-390-sheet]` and `[K1-390-sheet]` rows of `test_R22_copy_summary_puts_the_exact_text_on_the_clipboard` and `test_R24_the_sheet_shows_the_status_while_it_is_open`. The comment of `test_R5_renaming_a_person_updates_every_place_on_each_keystroke` names its sheet line as A12's. `RECEIPT_JS` and `receipt(page, "#splitsDlg .rbody")` read the sheet, `STATUS_JS` reads its `p.status`, `press_escape` waits for the close event (qa.md Phrases, R59 (2)).
- Tests that the R3 rows of the sheet need are A13's (`splits-sheet` at 390 and 360 are marked A13, the spare line inside the sheet).

## Traps worth knowing
- RED on today's behaviour. A test that waits on a missing element times out instead of failing on its assertion. Read with one `page.evaluate` that gives null for a missing part. Where a test passes today, its RED is a stub run (put in and taken out with the Edit tool, never committed, `grep -r STUB src/` empty after).
- Never touch the system clipboard. Every context gets `tests/browser/clipboard/recorder.js` (or `reject.js`, `missing.js`), and copy is asserted on `window.testClipboardText` and `window.testClipboardWrites`. `click_copy` asserts the button's count and waits two frames.
- WebKit closes a dialog in a task after keyup (R59 (2)). Every "press Escape" waits for the close event, at most 2 s. WebKit does not focus a button on a mouse click (R59, "Focus after a mouse click is the engine's own").
- The sheet is a modal dialog, so the strip's `--strip-h` (A11) is unchanged while it is open, and a sheet that holds focus keeps it on `div.sheet[tabindex=-1]` with no ring.
- R38 allows `padding-bottom` on `#sheetScroll` only while P1 and the sheet are both open (A13). A12 writes no style.
- Do not run a Chromium job while a full suite runs. The R30 Escape and Cancel tests are timing flakes under load.
- No shell redirection of any kind, no heredoc and no pipe after a test runner, not even for a read-only probe. Put probe scripts in the session scratch folder with the Write tool. A11 ran its RED and stub runs from an args file (`python -m pytest @<file>`), which pytest 9 reads.
- The render check pattern. `docs/modules/split-app/qa/strip-render/render.py` (A11) compares the walk, every element's box and look, and the page values against the goldens and the `states.html` pieces.

## Open items carried
- Q-A11-1 and F-A11-1 (BUILD.md A11). WebKit leaves a Tab-focused control under the strip. Recommended answer, a spec row for a `focusin` reveal below 1024 px with `scrollIntoView({ block: "nearest" })`. For the owner and the planner.
- Q-A10-1 (H-07, open with the owner). A clipboard answer that comes after the bill changed shows nothing, as built.
- F-A10-1 (BUILD.md A10). qa.md ST-12 and states.md's wording on the card's failure line at 1280. For the planner.
- Q-A9-1 (BUILD.md A9). Archive copy of a replaced source module. Recommended answer, no. For the orchestrator.
- Q-A8-1 is ruled (USER, H-06, keep as written).
- F-A8-1, Q-A6-1, F-A4-1, Q-A3-1, F-A5-1, F-A3-1 and the judgment calls of A5 to A11 (see their BUILD.md sections).
- `tests/browser/live_e2e.py` still reads the 1.0 panel and the 1.0 forms in `tests/browser/expected.py`. A20 rewrites the gate.

## Resume here
1. Load the design row and declare what transferred.
2. RED. The six `@R50` scenarios of qa.md and the sheet lines marked `task A12` as tests, seen failing on their asserted property in Chromium and WebKit before the build, each run folder recorded.
3. Build R50 (Splits fills and opens the sheet with `showModal()`, the receipt by `createReceipt` with `{ head: "sheetSplitsH" }`, live updates while open, focus to `div.sheet` on open and back to Splits on Escape, Close and a backdrop click, `aria-expanded`, the content removed on close, PD-21's guard on open and close, PD-18's close at 1024 px without moving focus), render check against `splits-sheet.html` at 390 and 360, then Node, Chromium and WebKit, WebKit compared by id with `20261015-124632-webkit/`.
4. BUILD.md A12 section (with the A11 row in the commit table), tick A12 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A12, R50)`.

## Processes
None alive at writing. Every pytest server, every probe's server and the render check's server were stopped by their own `finally` (each printed STOPPED with the port free again). Nothing ran in the background.
