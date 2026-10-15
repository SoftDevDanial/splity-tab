# Handoff. Split v1.1.0 execute, task A18 (cross-cutting checks in both engines), not started

Written 2026-10-15 by the frontend developer role at the end of A16. A16 is committed (`3c3d9b0`, tests only, no app file changed), and a second commit records its proof runs on the committed tree and the A16 row of the commit table. A17 was done before A4. The orchestrator runs a planner touch before A18, so read whatever that pass changed in `spec.md`, `qa.md` and `ROADMAP.md` first, then this file. Nothing of A18 is written.

## Where it stands
- A0 to A17 and C1 to C6 done. Build order A18 next (A19 and A20 are not this builder's).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261015-163309/node-test.txt`). Chromium `docs/modules/split-app/qa/functional/20261015-163320-chromium/`, 602 passed, 21 xfailed, 0 failed (623 cases). WebKit `docs/modules/split-app/qa/functional/20261015-163654-webkit/`, 600 passed, 1 failed, 1 skipped (IME), 21 xfailed, on the tree of `3c3d9b0` (proof commit `9bdb9ee`). That WebKit run is A18's baseline by id.
- The one WebKit failure allowed is F-A11-1 `test_R49_no_control_the_user_tabs_to_is_left_under_the_strip` (H-08, open with the owner, build nothing for it until he rules). F-A3-1 and F-A5-1 are closed by A16 (`closing`).
- The 21 xfails. `task A18` 15, `test_R32_tab_order_follows_the_golden_and_every_stop_shows_its_ring` 3, `test_R35_no_horizontal_overflow_and_the_layout_of_each_size` 8, `test_R35_sizes_the_design_gives_at_360_by_780` 1, `test_R35_content_width_of_the_header_and_the_note_at_1280_by_800` 1, `test_R36_motion_follows_the_users_setting` 1, `test_R37_names_are_shown_as_text_and_never_as_markup` 1. `task A19` 6 (the two R40 seed tests, 3 each), not A18's.

## What A18 is
Spec task A18. "Cross-cutting checks in both engines. Tab order and rings, overflow and sizes at 360, 390 and 1280, the desktop layout, large bills at 360, motion, injection, CSSOM targets, network log, per-engine expectations. -> R32, R35, R36, R37, R38, R39, R55, R59, R60". Read R32, R35 to R39, R55, R59 (all four engine differences) and R60 whole, `qa.md` every scenario tagged with those ids, the FE checklist rows they name, and `system.md` (Focus, Motion). The 15 tests above are 1.0 forms marked for A18. Most read 1.0 markup (`table.shares`, `p.dialog-text`, `p.status.status-failure`, the sticky panel), so each is rewritten to its `qa.md` scenario, not unmarked. The design row (`taste-skill`, `frontend-design`, the cache folder `c2bdb427efe8`) loads first if A18 changes any UI.

## Where things are
- Helpers A16 added in `tests/browser/test_app.py`. `closing(page, gesture)` waits for the open dialog's `close` event (2 s, "dialog still open after 2 s") and is what `press_escape` and `start_over` use. Use it for any dialog close before reading focus. `m1_closer`, `bill_empty_screen`, `error_marks`, `NEW_DIALOG_JS`, `scrolled_by_wheel`.
- Tab helpers from A17. `tab_until(page, locator, limit)`, `has_focus`. Section helpers `section_state`, `displayed`, `visible_text`. Focus label `support.active_label`.
- The R3 walk, `support.dom_walk` and `support.first_diff`. Render scripts that compare computed looks and boxes with a golden live beside their runs, the latest `docs/modules/split-app/qa/new-bill-render/render.py`.

## Traps worth knowing
- RED on the asserted property in both engines, each run in its own folder. A timeout on a missing element is not RED. A scenario that already passes gets its RED from a stub put in and taken out with the Edit tool, never committed (`git diff --quiet src/` before the real build, `grep -rn STUB src/` empty before the commit).
- A focus stub must move focus to a live wrong control (in Chromium a dialog's own close step puts focus back on its opener when the app's focus call meets an inert control).
- WebKit does not focus a button, a label or a radio on a mouse click (R59), so assert focus only after a keyboard step or a script focus. Escape closes a dialog a task later in WebKit (R59 (2)), use `closing`.
- WebKit screenshots add an inline style and a CSP violation (R59 (4)). No test takes a screenshot of the app before its console and policy checks.
- Long test names make failure screenshot paths longer than 260 characters. `git add` then fails with "Filename too long". Stage with `git -c core.longpaths=true add <exact paths>` (a per-command setting, the repo config is unchanged), as A16 did.
- No shell redirection of any kind, no heredoc and no pipe after a test runner or git. Keep each pytest run's output in its run folder through a scratch runner written with the Write tool, in a scratch folder of your own. A16's runner `run_pytest.py` (in its own scratch folder `split-a16`) runs pytest with `SPLIT_EVIDENCE=1`, writes `stdout.txt` into the run folder, prints counts, failing ids grouped by test with one message each, and the `test_app.py:<line>: AssertionError` lines, and refuses `-k`.
- The full WebKit suite takes about 7 minutes, so run it as a background job and wait on its exit notice. Do not run a Chromium job while it runs.
- Never touch the system clipboard. Every context gets `tests/browser/clipboard/recorder.js` (or `reject.js`, `missing.js`).
- Another agent works in `examples/streaks` and runs its own browser jobs. Its processes are not yours. A `python -m http.server 4610 --bind 127.0.0.1 --directory .` whose parent is the Claude desktop app belongs to the desktop preview, leave it.

## Open items carried
- F-A16-1 (BUILD.md A16). M1 returns focus only in its `close` event, the sheet and P1 at once on a click close. For the planner.
- F-A15-1, Q-A14-1, F-A13-1, F-A12-1 (BUILD.md). For the planner.
- Q-A11-1 and F-A11-1 (H-08), Q-A10-1 (H-07), both open with the owner. F-A10-1, Q-A9-1, F-A8-1, Q-A6-1, F-A4-1, Q-A3-1 and the judgment calls of A5 to A16 (see their BUILD.md sections). Q-A8-1 is ruled (USER, H-06, keep as written).
- `tests/browser/live_e2e.py` still reads the 1.0 panel (`support.panel_text`, `expected.EVEN_MESSAGE`). A20 rewrites the gate.

## Resume here
1. Read what the planner touch changed, then the A18 sources above. Load the design row if A18 touches UI and declare what transferred.
2. RED. Each `qa.md` scenario of A18's ids not yet written as a test, and each `task A18` test rewritten to its scenario, seen failing on its asserted property in Chromium and WebKit before any app change, each run folder recorded. A scenario that already passes gets its RED from a stub.
3. Build only what fails, then Node, Chromium and WebKit, WebKit compared by id with A16's proof run.
4. BUILD.md A18 section (with the A16 proof commit row), tick A18 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A18, R32, R35, R36, R37, R38, R39, R55, R59, R60)`, proof runs on the committed tree.

## Processes
None of A16's alive at writing, by the closing sweep recorded in A16's return to the orchestrator.

## Added 2026-10-15 18:24 by the frontend developer role at the end of A21. A18's new baseline
A21 (the focus scroll, R49, H-08) is committed, `b8b332e` (build) and a second docs commit with the proof record (`BUILD.md`, A21). The text above stays as written. Where it names the A16 proof run as A18's WebKit baseline, or F-A11-1 as the one WebKit failure allowed, read this section instead (spec A18 line of 2026-10-15).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261015-181242/node-test.txt`).
- Chromium `docs/modules/split-app/qa/functional/20261015-181252-chromium/`, 624 tests, 603 passed, 21 xfailed, 0 failed.
- WebKit `docs/modules/split-app/qa/functional/20261015-181625-webkit/`, 624 tests, 602 passed, 0 failed, 1 skipped (the IME test), 21 xfailed. This run is A18's WebKit baseline by id. No WebKit failure is allowed now, F-A11-1 passes.
- The 21 xfails are the same ids as listed above (`task A18` 15, `task A19` 6). The one new id is `test_R49_the_app_scrolls_a_focused_control_only_below_1024_px_and_only_when_the_strip_covers_it`, passed in both engines.
- New in `src/`. `focusScroll` in `createStrip` (`src/ui/strip.js`) is the document's one `focusin` listener. Below 1024 px it scrolls a control in `div.app` outside `#strip` whose bottom edge is under the strip's top with `scrollIntoView({ block: "nearest" })`. A18 tests that read scroll positions or Tab stops below 1024 px in WebKit now see each covered control end 12 px above the strip (bottom edge 721 at 390 x 844 with the 111 px strip, `qa/focus-scroll-probe/20261015-180501-webkit/result.json`). In Chromium the app makes no call on a Tab walk (`-180503-chromium/`).
- New test helpers in `tests/browser/test_app.py`, `COUNT_SCROLL_INTO_VIEW_JS` (counts the app's `scrollIntoView` calls) and `FOCUSED_AGAINST_STRIP_JS`.
