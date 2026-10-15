# Handoff, execute v1.1.0, split-app task A0 (2026-10-14)

Written by the frontend developer role, returning blocked. Nothing is committed for A0. HEAD is still `853afe1`.

## Where it stands
- Parts 1 and 2 of A0 are built and verified in the working tree. Part 3 ran in full. The record is `docs/modules/split-app/qa/webkit-baseline/20261014-130011/sorting.md` and the dated A0 section at the end of `docs/modules/split-app/BUILD.md`.
- Chromium suite 430 passed (427 sealed plus 3 A0). WebKit suite 381 passed, 48 failed, 1 counted skip. Live gate 1.0 Chromium PASS, WebKit FAIL at step 7 (tool artefact, Q-A0-3).
- Blocker B-A0-1. 43 touch double activation failures cannot be sorted (a) or tool artefact without an iPhone. Open questions Q-A0-2 (copies of the WebKit run's files in the A0 folder) and Q-A0-3 (the WebKit live gate's screenshot CSP errors). All three are in `sorting.md`.

## Files of the A0 commit, once the ruling allows it (stage by name only)
- `tests/fixtures/design-v1.0.0/.gitattributes`, `system.css`, `bill-empty.html`, `bill-even.html`, `bill-items.html`, `bill-unassigned.html`, `new-bill-dialog.html`, `states.html`
- `tests/browser/rig.py`, `conftest.py`, `support.py`, `test_app.py`, `live_e2e.py`, `probe_webkit.py`
- `docs/modules/split-app/BUILD.md`
- Evidence folders `docs/modules/split-app/qa/functional/20261014-125042/`, `20261014-125053/`, `20261014-125352-chromium/`, `20261014-125604-webkit/`, `docs/modules/split-app/qa/live-e2e/20261014-130326-chromium/`, `20261014-130333-webkit/`, `docs/modules/split-app/qa/webkit-baseline/20261014-130011/`
- Not ours, never stage: `docs/progress/STATE.md`, `STATE-LOG.md`, `process-ledger.md`, `docs/v1.1.0/CHANGE-LEDGER.md`, this handoff unless the orchestrator says so.

## Resume point
1. Get the ruling on B-A0-1 (and Q-A0-2, Q-A0-3). Write it into `sorting.md` as a dated addition.
2. After staging, check that each fixture's index blob equals its `v1.0.0` blob (`git ls-files -s tests/fixtures/design-v1.0.0/`) and that `docs/design/` is unchanged (`git status --short docs/design`).
3. Run `python -B "{sdlc}/harness/credential_sweep.py" --staged` from the project root, exit 0, then commit as `test(split-app): ... (task A0, R58, R59)` with no co-author line.

## Gotchas
- `core.autocrlf` is true. Prove fixture bytes with `git hash-object --no-filters`, never plain `hash-object`.
- `python -I` hides the user site-packages where Playwright lives. Run the probe and the gates with plain `python`.
- In WebKit, `page.screenshot` logs one CSP stylesheet error per call on the app page, with any caret mode.
