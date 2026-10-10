# Evidence index: regression QA, split, 2026-10-10 (run folder 20261010T124914)

The findings report is docs/modules/split-app/findings/regression-qa.md. This folder holds the scripts that produced it,
their outputs and the screenshots. Nothing here was written into src/, tests/, index.html, docs/design/ or any existing doc.

## Run order and what each file is

| Step | Script | Output files | What it did |
|------|--------|--------------|-------------|
| 1 | run_suites.py | node-test.txt | Ran `node --test "tests/**/*.test.js"` once. The script crashed afterwards on its summary regex, before pytest ran. The saved output is the record. |
| 1 | run_browser.py | pytest-collect.txt, pytest.txt, junit.xml, suites-summary.json | Collected the browser tests (427 ids), then ran `python -m pytest tests/browser -q -p no:cacheprovider --junitxml` once. 427 passed in 109.87 s. |
| 2 | (no script) | scenario-table.json, scenario-table.md | The table is built by build_findings.py in step 5, from the rows and citations written there. |
| 3 | driven_checks.py | driven-checks.json, driven-checks-run.txt, driven/*.png | D1 (R5 per keystroke), D2 (R38 strict policy, S1 seed and S2 with the dialog) and D3 (R23 blocked clipboard). 40 of 40 checks pass. |
| 3 | driven_r34.py | driven-r34.json, driven-r34-run.txt | D4 (R34 focus rows b to f on the S1 seed). 15 of 15 checks pass. |
| 3 | probe_chips.py | probe-chips.json, probe-chips-run.txt, probe-chips-after-error.png | Diagnostic for flow 5 part B: chip and Remove positions at 390 x 844. |
| 3 | probe_scout.py | probe-scout.json, probe-scout-run.txt | Diagnostic: the press-point scout on the suite's own bill at 390 x 3000 and 390 x 844, and on the one-item bill. Shows the points come from item 2's Remove. |
| 3 | run_gates.py | gates-run.txt, gates-summary.json, gates/fidelity/20261010-130500/, gates/live-e2e/20261010-130537/ | Ran the R40 fidelity gate (10 pairs) and the R41 live gate (7 steps) with their own code, with only EVIDENCE_ROOT moved into this folder. Both passed the pixel and step checks. |
| 4 | flows.py | flows.json, flows-run.txt, flows/*.png | The five hand-driven flows at 390 x 844 from empty storage. Final run: 73 checks pass, 0 fail, 8 observations. |
| 4 | flows.py (earlier runs) | flows-attempt-1.json, flows-attempt-1-run.txt, flows-attempt-2-one-item.json, flows-attempt-2-one-item-run.txt, flows-attempt-3-stale-scroll.json, flows-attempt-3-stale-scroll-run.txt | The three earlier runs of the same script, kept so the history is visible. See the attempts below. |
| 5 | build_findings.py | scenario-table.json, scenario-table.md, and the findings file | Builds the 341-item table. Each cited test is checked against the saved outputs before its row is written, and the script stops if one is missing. |

Shared helper: harness_common.py (the server and browser helpers, the page readers and the check recorder). It reuses the
suite's own support.py, seeds.py and expected.py, and every browser context is made by rig.new_context, so the clipboard is
always the suite's recorder (CG-7) and no permission is granted.

## The flow attempts

- flows-attempt-1: two defects in the script, not in the app. An expectation ignored that R18 keeps the bill summary on
  screen while an item has no person, and one check had no "what" argument. Both fixed.
- flows-attempt-2-one-item: part B used a one-item bill. An item 2 with a Remove under its own chips does not exist in that
  bill, so the probe found no point. Part B now builds the four-item S1 bill, as the suite's RG-CR-08 test does.
- flows-attempt-3-stale-scroll: part B measured the chips, then clicked the item 1 price, which scrolled the page, so the
  points were stale. Part B now scrolls to the top with the wheel and measures and presses at scrollY 0.
- flows.json is the final run (the one the findings cite). Its screenshots replaced the earlier ones with the same names.

## Screenshots

- flows/: the end state of each flow (flow1 to flow5), plus the mid-flow error and reload shots.
- driven/: the D1 before and after shots, the D2 S1 seed and S2 dialog shots, and the D3 reject shot.
- probe-chips-after-error.png: the 390 x 844 page with the error shown, from the flow 5 diagnostic.
- gates/fidelity/20261010-130500/<screen>-<viewport>/: golden.png, candidate.png, diff.png, styles.json and report.json for
  each of the 10 pairs.
- gates/live-e2e/20261010-130537/: 01 to 07 step screenshots, steps.log, console.log, network.log, clipboard-s1.txt,
  clipboard-s2.txt and summary.json.

## Evidence the orchestrator should know about

- The gate folders in this run sit under gates/ here, because each gate's EVIDENCE_ROOT was moved into this folder. The
  normal folders under docs/modules/split-app/qa/ (fidelity and live-e2e) were not written by this run.
- The R40 checklist half (per-element style review of styles.json) was not judged in this run. R40 is recorded as UNTESTED
  for that reason.
- No file under docs/modules/split-app/qa/functional was written, because SPLIT_EVIDENCE was unset for every suite run.

## Processes

Each script stopped every server and browser it started. The full list, with pids and ports, is section 7 of the findings
report. A final query for Playwright Chromium processes, run after the last script, returned an empty list.
