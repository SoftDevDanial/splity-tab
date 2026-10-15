# Handoff. Split v1.1.0 execute, task A20 (the cold-boot live gate in both engines), not started

Written 2026-10-15 by the frontend developer role at the end of A19. A19 is committed (`af782d0`, tooling and tests, no app file changed) and its proof runs on the committed tree are recorded by the docs commit above it, the one whose message starts `docs(split-app): the proof runs of A19` (read its hash with `git log`). The orchestrator may run a planner touch before A20, so read whatever it changed in `spec.md`, `qa.md` and `ROADMAP.md` first, then this file. Nothing of A20 is written.

## Where it stands
- A0 to A19, A21 and C1 to C6 done. A20 is the last app task in the build order, then the QA phase (none of it this role's until the orchestrator says).
- Baselines of A19's proof, all on the committed tree (`git diff --quiet HEAD -- src/ tests/ index.html docs/design/` exit 0 before and after).
  - Node `docs/modules/split-app/qa/unit/20261015-194336/node-test.txt`, 379 of 379.
  - Chromium `docs/modules/split-app/qa/functional/20261015-194344-chromium/`, 703 tests, 703 passed, 0 xfailed, 0 failed, 0 skipped, 207.3 s.
  - WebKit `docs/modules/split-app/qa/functional/20261015-194724-webkit/`, 703 tests, 701 passed, 2 skipped (the IME test and `test_R40_an_after_load_script_presses_nothing_without_the_clipboard_stand_in`, both `chromium_only`), 0 xfailed, 0 failed, 409.3 s. A20's WebKit baseline by id.
  - Fidelity gate `docs/modules/split-app/qa/fidelity/20261015-193738/`, both controls as written (self-compare 0 px, no-seed 184588 px) and 40 of 40 pairs at 0 mismatching pixels, harness the sdlc 2.6.0 cache copy through `SDLC_HARNESS`, about 160 s.
- No xfail is left in the suite. By id against A18's runs, the 6 `task A19` xfails passed, the 5 cases of the 1.0 `test_R40_the_runner_builds_the_documented_command` are gone and 13 ids are new (BUILD.md, A19).
- Nothing in `src/`, `index.html` or `docs/design/` changed in A19. `git hash-object --no-filters src/system.css` is `bf30ddadb8c756dc5d462243c642c218597ae0ac`.

## What A20 is
Spec task A20 with its items 1 to 4, R41, R58, R59 (4), and `qa.md` "Cold-boot live-e2e gate" whole (Control and baseline, Control mode, Rules, Flow steps 1 to 9, Evidence artifact) with the `@R41` scenarios ("Works right", the control scenario "The live gate fails when the app starts from a saved bill", the `@R41 @static` "The gate script makes a cold context except on its control path", and the `@R58 @R41 @gate` row). The script is `tests/browser/live_e2e.py`, still the 1.0 flow with A0's `--engine`, reading the 1.0 panel through `support.panel_text` and `expected.EVEN_MESSAGE`.
- Per engine a control run with `--control seeded` must stop at step 1 on its asserted property (the cold boot), into `qa/live-e2e/<stamp>-<engine>-control/`, and then the green run into `qa/live-e2e/<stamp>-<engine>/` with `summary.json` holding `"control": null`. The task counts only once both control captures exist.
- Each step's capture is a screencast frame, never `page.screenshot` or `locator.screenshot` (R41, R59 (4), A20 item 4). The RED of the capture is A0's WebKit run of the 1.0 gate, `qa/live-e2e/20261014-130333-webkit/` (seven refused stylesheet lines at step 7). A0's Chromium run is `qa/live-e2e/20261014-130326-chromium/`.
- Three sealed 1.0 tests are rewritten (A20 items 1 to 3), `test_R41_the_gate_uses_real_gestures_and_reads_only`, `test_R41_the_step_log_puts_gesture_and_assertion_in_their_own_fields` and `test_R41_the_gate_installs_the_clipboard_recorder_and_nothing_else` (renamed for its two scripts). Each passes today against the 1.0 script, so each is seen failing first against the script of that moment once rewritten (the Tasks rule).

## Where things are
- Scratch runners from A19 in `{temp}/claude/{project-id}/34019cfb-f1a7-415f-a7eb-c47e4619e819/scratchpad/split-a19/`. `run_pytest.py <engine> [@file | node ids]` (no `-k`, writes `stdout.txt` into the run folder, prints counts and failing ids, `A19_ALL_MESSAGES=1` prints every failing case), `run_node.py`, `compare_runs.py <old> <new>`, `wait_for_run.py <engine> <after stamp>` (540 s cap), `run_fidelity.py` (the fidelity gate with the 2.6.0 harness, 1800 s cap), `sweep.ps1 -Since "<time>"` (read only). A fresh builder copies them into a folder of its own if that one is gone.
- Test helpers an A20 test may reuse in `tests/browser/test_app.py`. `FakeServer` (stands in for `rig.StaticServer`), `RECORD_BODY_CLICKS_JS`, `seen_by_the_page`, `presses_and_clicks`, `closing`, `live_gate_steps`. The A19 tests check planted copies through one helper that takes a path (`seed_script_problems`), the shape A20 item 1 asks of the gate guard.

## Traps
- RED on the asserted property before any change, each run in its own folder. A stub goes in and out with the Edit or Write tool and is never committed (`grep -rn STUB tests/ src/ index.html` empty before the commit).
- A failing parametrized case with a long id makes the failure screenshot of `open_app` in `tests/browser/conftest.py` pass 260 characters, and teardown adds `OSError: [Errno 22]` beside the real call failure (seen in A19's RED-1). Read the call failure in `junit.xml`. Stage with `git -c core.longpaths=true add <exact paths>`.
- Never touch the system clipboard. Every context gets `tests/browser/clipboard/recorder.js` (or `reject.js`, `missing.js`), and the live gate proves the stand-in is not native before its first gesture.
- Headless only. Never write into `docs/design/`.
- No shell redirection of any kind (`>`, `>>`, `2>&1`, `| tee`, heredoc, `cat >`, `python open(..., 'w')`), not even to `/dev/null` (A19 slipped once that way on a read-only `sed`), and no pipe after a test runner or git.
- WebKit computes some px values with a tail, so compare within 0.5 px (R59 (1)). WebKit does not focus a button, a label or a radio on a mouse click (R59). Escape and M1's click closes close a task later in WebKit (R59 (2), use `closing`). A WebKit screenshot adds an inline style and a CSP violation (R59 (4)).
- The full WebKit suite takes about 7 minutes. Run it in the background and wait on its exit notice with a bounded wait, never beside a Chromium job. The fidelity gate is a Chromium job of about 3 minutes.
- Another agent works in `examples/streaks` and runs its own browser jobs. Its processes are not yours. A `python -m http.server 4610 --bind 127.0.0.1 --directory .` whose parent is the Claude desktop app belongs to the desktop preview, leave it.
- The commit table in `docs/modules/split-app/BUILD.md` ("v1.1.0 commits so far") has the A19 row (`af782d0`). Add the row of A19's proof commit (the docs commit named above) with the A20 section.

## Open items carried
- From A19, an observation for the fidelity finder and no finding. 38 of the 42 image pairs of the gate run are byte-identical. Three passing pairs differ below the threshold, `bill-unreadable-390x844` (19 pixels, 1 colour level), `new-bill-dialog-390x844` (77 pixels) and `new-bill-dialog-1280x800` (84 pixels), at most 2 levels.
- The FE element checklist half of R40 and `findings/fidelity.md` are the fidelity finder's (qa.md, "Per-element check").
- Two wording observations for the planner, BUILD.md A18 "Findings" (BR-02's 44 px, K1-56's line box).
- F-A16-1, Q-A14-1, Q-A10-1 (H-07, open with the owner), F-A10-1, Q-A9-1, F-A8-1, Q-A6-1, F-A4-1, Q-A3-1 and the judgment calls of A5 to A19 (see their BUILD.md sections). Q-A8-1 is ruled (USER, H-06). H-08 is ruled and closed by A21.

## Resume here
1. Read what the planner touch changed (if any), then spec A20, R41, the qa.md live gate section and its `@R41` scenarios, and `tests/browser/live_e2e.py`.
2. RED. The three rewritten R41 tests and the new `@R41 @static` scenario with its planted copies, each against the script of that moment, in both engines, each run in its own folder.
3. Build the gate. Per engine, the control run seen failing at step 1, then the green run. Then Node, Chromium and WebKit on the committed tree, compared by id with A19's proof runs above.
4. BUILD.md A20 section (with the A19 proofs row), tick A20 in `spec.md`, credential sweep `--staged`, commit `feat(split-app): ... (task A20, R41, ...)`, the proof runs and a docs commit.

## Processes
None of A19's alive at writing. The fidelity gate and the WebKit suite ran as background jobs bounded by their runners (1800 s), and both exited (0) before the record was written. The sweep at the end (by name, command line and listening port since 19:29, shells included) found only its own shell chain. The details are in A19's return to the orchestrator.
