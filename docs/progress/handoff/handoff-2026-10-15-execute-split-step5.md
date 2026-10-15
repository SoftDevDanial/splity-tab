# Handoff. Split v1.1.0 execute, step 5 finders (QA, code review, security, fidelity checklist), not started

Written 2026-10-15 by the frontend developer role at the end of A20. A20 is committed (`bec655a`, the gate script and its tests, no app file changed) and its proof runs on the committed tree are recorded by the docs commit above it, the one whose message starts `docs(split-app): the proof runs of A20` (read its hash with `git log`). Every app task of v1.1.0 is done. Nothing of step 5 is started. Read `docs/modules/split-app/BUILD.md`, section "v1.1.0 task A20", for the detail of what follows.

## Where it stands
- A0 to A21 and C1 to C6 done and ticked in `spec.md`. No `xfail` is left in the suite.
- Nothing under `src/`, `index.html` or `docs/design/` changed since A21 (`b8b332e`). `git hash-object --no-filters src/system.css` is `bf30ddadb8c756dc5d462243c642c218597ae0ac`.

## Final baselines (all on the committed tree of `bec655a`)
- Node `docs/modules/split-app/qa/unit/20261015-202558/node-test.txt`, 379 of 379.
- Chromium `docs/modules/split-app/qa/functional/20261015-202607-chromium/`, 707 tests, 707 passed, 0 failed, 0 skipped, 215.8 s.
- WebKit `docs/modules/split-app/qa/functional/20261015-202952-webkit/`, 707 tests, 705 passed, 2 skipped (`test_R33_ime_composition_survives_a_render` and `test_R40_an_after_load_script_presses_nothing_without_the_clipboard_stand_in`, both `chromium_only` with their reasons in `skips.txt`), 0 failed, 435.0 s. The WebKit baseline by id for any later run.
- Fidelity gate (Chromium only) `docs/modules/split-app/qa/fidelity/20261015-193738/`, both controls as written and 40 of 40 pairs at 0 mismatching pixels (A19, no app file changed since).
- Cold-boot live gate, one server per engine, control first and green next.
  - Chromium control `docs/modules/split-app/qa/live-e2e/20261015-202120-chromium-control/` (red at step 1 on its property, `control_red_on_its_property` true), green `docs/modules/split-app/qa/live-e2e/20261015-202122-chromium/` (9 of 9, `"control": null`, 0 console errors, 0 page errors, 0 CSP violations, 90 requests and none outside the rule, 3 stand-in writes).
  - WebKit control `docs/modules/split-app/qa/live-e2e/20261015-202153-webkit-control/`, green `docs/modules/split-app/qa/live-e2e/20261015-202154-webkit/`, the same figures. The first v1.1.0 WebKit runs show none of A0's refused stylesheet lines.
  - A bare `python tests/browser/live_e2e.py` run, `docs/modules/split-app/qa/live-e2e/20261015-202220-chromium/` (its own server, 9 of 9), for the `@R58 @R41 @gate` line "run with no option".

## How to run
- `node --test "tests/**/*.test.js"`. `python -m pytest tests/browser -q [--engine webkit]` with `SPLIT_EVIDENCE=1` for the evidence files (WebKit about 7 minutes, run it alone and in the background with a bounded wait).
- `python tests/browser/fidelity/run.py` (Chromium, about 3 minutes, `SDLC_HARNESS` names the harness).
- The live gate per engine (CLAUDE.md, changed in A20). Serve the project root, run `python tests/browser/live_e2e.py --engine <engine> --control seeded --base-url http://127.0.0.1:<port>/` (must stop red at step 1, folder `<stamp>-<engine>-control`), then the same without `--control`, then stop the server. A bare run serves the project root itself. About 2 s a run.

## For each finder
- QA. `qa.md` whole against the running app in both engines, the baselines above, the two `@R41 @gate` scenarios on the four live gate folders (`summary.json`, `steps.log`, the captures), `findings/qa.md`.
- Fidelity. The FE element checklist half of R40 (`qa.md`, "Per-element check") and `findings/fidelity.md`. The pixel half is A19's run above.
- Code review. The v1.1.0 delta, with A20's test-side changes (`live_e2e.py` rewritten, `COLD_BOOT_JS`, `cold_boot_state`, `RECEIPT_JS` and `receipt` moved into `support.py`, `COLD_BOOT` into `expected.py`, the 1.0 panel forms and `support.panel_text` deleted, the guard helpers in `test_app.py`). The module README reconcile for A20 is the orchestrator's first, the reviewer's as fallback.
- Security. R37 to R39 and the threat model. The live gate runs with no `bypass_csp`, no permission and only `recorder.js` and `listener.js` as init scripts, and `test_R41_the_gate_uses_real_gestures_and_reads_only` keeps that true.

## Open items carried
- From A20 (BUILD.md A20, judgment calls 1 to 11). `--base-url` is new in `live_e2e.py` so a control and a green run share one server, and qa.md's How to run names only the plain commands, so a planner line may be wanted there. The A20 observations, the control's strip line reads `'Total\nRM 116.60'` (innerText keeps the line break), and `import re` in `tests/browser/support.py` was already unused before A20.
- From A19, an observation for the fidelity finder and no finding. 38 of the 42 image pairs of the gate run are byte-identical. Three passing pairs differ below the threshold, `bill-unreadable-390x844` (19 pixels, 1 colour level), `new-bill-dialog-390x844` (77 pixels) and `new-bill-dialog-1280x800` (84 pixels), at most 2 levels.
- From A18, two wording observations for the planner (BUILD.md A18 "Findings", BR-02's 44 px and K1-56's line box).
- F-A16-1, Q-A14-1, Q-A10-1 (H-07, open with the owner), F-A10-1, Q-A9-1, F-A8-1, Q-A6-1, F-A4-1, Q-A3-1 and the judgment calls of A5 to A20 (see their BUILD.md sections), as the A20 handoff carried them. Q-A8-1 is ruled (USER, H-06). H-08 is ruled and closed by A21.

## Traps
- RED on the asserted property before any change, each run in its own folder, stubs in and out with the Edit tool and never committed.
- A failing parametrized case with a long id makes the failure screenshot path pass 260 characters (`OSError: [Errno 22]` at teardown beside the real failure). Read the call failure in `junit.xml`, and stage with `git -c core.longpaths=true add <exact paths>`.
- Never touch the system clipboard. Every context gets a stand-in from `tests/browser/clipboard/`. Headless only. Never write into `docs/design/`.
- WebKit screenshots add an inline style and a CSP violation (R59 (4)). The live gate captures screencast frames.
- Another agent works in `examples/streaks` with its own browser jobs. A `python -m http.server 4610` whose parent is the Claude desktop app belongs to the desktop preview.

## Processes
None of A20's alive at writing. Every server port of the task refused a connection after the last run, and the sweep since 20:02 (by name, command line and listening port, shells included) found only its own shell chain. The details are in A20's return to the orchestrator.
