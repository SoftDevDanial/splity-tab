# Handoff. Split v1.1.0 execute, task A10 (copy and status on every status line), not started

Written 2026-10-15 by the frontend developer role. A9 is committed (`386fce1`). The brief said to stop after A9, so A10 goes to a fresh agent. Nothing of A10 is written. The working tree holds only the orchestrator's own modified files (`CLAUDE.md`, `README.md`, `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`), the untracked run folders that are not the builder's (`qa/functional/20261014-131624-chromium` to `20261014-153212-chromium`) and the untracked handoffs.

## Where it stands
- HEAD `386fce1`. A0 to A9, A17 and C1 to C6 done. Build order A10 next, then A11 to A16, A18 (A19 and A20 are not this builder's).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261015-083316/node-test.txt`). Chromium `docs/modules/split-app/qa/functional/20261015-083323-chromium/`, 462 passed, 93 xfailed, 0 failed. WebKit `docs/modules/split-app/qa/functional/20261015-083627-webkit/`, 458 passed, 3 failed, 1 skipped (IME), 93 xfailed. That WebKit run is A10's baseline by id.
- The WebKit failures left are A16's. `test_R29_the_dialog_opens_with_the_safe_choice_focused` (R59 (1)), F-A3-1 `test_R30_leaving_the_dialog_without_starting_over[cancel]` and F-A5-1 `test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[escape]`. `test_R30_leaving_the_dialog_without_starting_over[escape]` (R59 (2)) passed in this run and failed at A8, a timing flake. Any other new WebKit failure is sorted (a), (b) or (c) as A0 sorted, and any H-04 failure is a finding.
- The commit table in `BUILD.md` ("v1.1.0 commits so far") has no A9 row yet. A10's section adds it, `| A9 | 386fce1 | feat(split-app): the receipt renderer and the card, blocked, unassigned, even with many and --rows and by-item forms, the status as its one live element, the 1.0 panel removed (task A9, ...), recorded by the A10 section |`.

## What A10 is (spec task A10)
"Copy and status on every status line, cleared by the next change. -> R22, R23, R24". Read R22 to R24 in `docs/modules/split-app/spec.md` whole, the DOM contract's `p.status [is-fail]` lines (card, sheet and `#stripStatus`), the Copy table row "Copy status" and the Gesture to action row "click Copy summary (card, sheet, strip)". Goldens, the S4 pieces of `states.html` ("S4 on the card, copied and blocked (desktop)", `p.status` with the check icon, and `p.status.is-fail` with the warning circle) and the strip status in the goldens that draw one, with their `.md` files. The design row (`taste-skill`, `frontend-design`) loads first, A10 draws UI.

## Where things are
- `src/ui/receipt.js`. `createReceipt(rbody, { ids, onCopy })` keeps Copy summary and `p.status` made once (so focus and the status survive a render) and writes the status from `COPY_STATUS`, which is still 1.0's form (the text alone, failure class `status status-failure`). R22 and R23 want the check or warning-circle icon before the text and `status` or `status is-fail`. `hasSplits` says when a result has splits.
- `src/main.js`. `copySummary` (writeText of `summaryText(computeResult(bill))`, any refusal is "fail") and `setStatus` (the one writer of `view.status`) are 1.0's. 1.0 kept the status across edits while the splits stayed. v1.1.0 R24 (rule 10) clears it on the next change to the bill, and a focus change, a blur, a fold, a dialog and a resize leave it. `commit` calls `setStatus(view.status)` today.
- `index.html`. `#stripCopy` (copy icon added at boot) and `p.status#stripStatus[role=status]` exist, unwired and empty. The strip's content and `#stripCopy`'s `disabled` are A11's (R49). The sheet's Copy summary and status are A12's.
- At 390 the card is not displayed, so `copy_summary` in the tests (`get_by_role("button", name="Copy summary")`) reaches `#stripCopy` only. The A10 tests that copy at 390 need the strip's button wired, and R24 needs the status in `#stripStatus` too.
- Tests that wait for A10, each `xfail(strict=True, reason="task A10")`. `test_R22_copy_summary_puts_the_exact_text_on_the_clipboard` (`[S2]`, `[S1]`), `test_R23_the_browser_blocks_the_clipboard`, `test_R23_the_clipboard_api_is_missing`, `test_R24_the_status_lives_as_long_as_the_table`, `test_R22_a_failed_copy_is_replaced_by_the_next_attempt`, `test_R24_a_copy_that_finishes_after_the_table_left_sets_no_status`, `test_R5_a_new_name_reaches_the_copied_text`, `test_R42_duplicate_names_through_the_whole_flow`, `test_R24_the_status_is_not_saved`. Several read the 1.0 panel (`table_cells`, `support.panel_text`, `EVEN_MESSAGE`, `status status-failure`) and are A10's to rewrite to their qa.md scenarios with `RECEIPT_JS`, `receipt`, `card_figures` and `card_rows` (A9 block of `tests/browser/test_app.py`). `test_R31_start_over_clears_the_copy_status` (A16) and `test_R37_names_are_shown_as_text_and_never_as_markup` (A18) also read the 1.0 panel and stay with their tasks.
- `test_R39_a_whole_session_makes_only_same_origin_gets` clicks Copy summary at 390, which reaches `#stripCopy`. Once A10 wires it the click writes to the clipboard stand-in.

## Traps worth knowing
- RED on the 1.0 behaviour. A test that waits on a missing element times out instead of failing on its assertion. Read with one `page.evaluate` that gives null for a missing part. Where a test passes on 1.0 behaviour, its RED is a stub run (a throwaway stub put in and taken out with the Edit tool, never committed, `grep -r STUB src/` empty after).
- Never touch the system clipboard. Every context gets `tests/browser/clipboard/recorder.js` (or `reject.js`, `missing.js`), and copy is asserted on `window.testClipboardText` and `window.testClipboardWrites`.
- The card is not displayed below 1024 px but is in the DOM. Measure the card's status at 1280.
- `.status:empty` is not displayed, so an empty status paragraph reads as null in a render check.
- Do not run a Chromium job while a full suite runs. The R30 Escape and Cancel tests are timing flakes under load.
- No shell redirection of any kind and no heredoc, not even for a read-only probe (A9 slipped twice, BUILD.md A9, Process slips). Put probe scripts in the session scratch folder with the Write tool.
- The render check pattern. `docs/modules/split-app/qa/receipt-render/render.py` (A9) compares the R3 walk of `#rbody` and every element of `#card` (box within 0.5 px and 30 computed properties) with a golden, with the golden's `div.r-spare` left out until A13.

## Open items carried
- Q-A9-1 (BUILD.md A9). Should a replaced source module (`src/ui/panel.js`, removed by `git rm` in `386fce1`) also get an archive copy under the house rule, as the fixtures did in Q-A2-2? Recommended answer, no, its bytes stay in git history. For the orchestrator.
- Q-A8-1 (BUILD.md A8). A new blank item carries the amber `needs` bar until someone is tapped, as R18 is written. Recommended answer, keep it. For the owner.
- F-A8-1, Q-A6-1, F-A4-1, Q-A3-1, F-A5-1, F-A3-1 and the judgment calls of A5 to A9 (see their BUILD.md sections).
- `tests/browser/live_e2e.py` still reads the 1.0 panel and the 1.0 forms in `tests/browser/expected.py` (`EVEN_MESSAGE`, `S1_SUMMARY`, `S1_ROWS`, `S1_CHECK` and the S2 ones). A20 rewrites the gate.

## Resume here
1. Load the design row and declare what transferred.
2. RED. The A10 scenarios of qa.md (`@R22` to `@R24`) as tests, seen failing on their asserted property in Chromium and WebKit before the build, each run folder recorded.
3. Build R22 to R24 (the status with its icon in every status paragraph present, cleared by the next change, the strip's Copy summary wired), render check against the `states.html` S4 pieces, then Node, Chromium and WebKit, WebKit compared by id with `20261015-083627-webkit/`.
4. BUILD.md A10 section (with the A9 row in the commit table), tick A10 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A10, R22, R23, R24)`.

## Processes
None alive at writing. Every pytest server, the two render check servers and the copy probe's server were stopped by their own `finally` (each printed STOPPED with the port free again). Nothing ran in the background.
