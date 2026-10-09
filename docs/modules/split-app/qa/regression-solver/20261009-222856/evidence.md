# Evidence: regression solver, split-app (2026-10-09)

Role: dev solver. Start HEAD `9030ce7`. Orders: the ORCH rulings of 2026-10-09 on RG-CR-01 (BLOCKER), RG-CR-02 and RG-CR-04 (WARNING),
plus the scope addition for RG-CR-03 items 2 and 3 in `src/errors.js` and the BUILD.md code map. README.md was not touched.
Python 3.14.0, Node 24.11.1, headless Chromium through the suite's own rig. Every browser context came from `rig.new_context` (recorder on,
`permissions` and `bypass_csp` refused). The system clipboard was never touched (CG-7).

## Commits
| Commit | What |
|---|---|
| `17ac1ed` | test: RG-CR-02, the guard-lifetime tests record the mouse presses as well as the clicks, plus one real-gesture word-select test |
| `e30b015` | fix: RG-CR-01, Add person and Add item arm `swallowRepeatClicks`; `swallowRepeatClicks` JSDoc corrected; 108 new test rows |
| `f0ca022` | docs: spec R6, R7, R12, R30 and the Threat model row, qa.md scenarios |
| `38686c0` | docs: RG-CR-04 (BUILD.md Status, Test counts, call 18, new call 20, `gesture_at` docstring, SEC-01 header comment), `src/errors.js` header comment, BUILD.md code map (`commit`, `errors.js`) |
| (the commit that holds this folder) | the Solver section of `findings/regression-code-review.md`, this evidence, the fidelity run folder |

## How the runs were done
Red runs and mutants ran in `scratch/` (a copy of `index.html`, `CLAUDE.md`, `src/`, `tests/browser/` and `docs/design/`, rebuilt from the project on
every run by `scratch_run.py`), so no mutant was ever applied to the project `src/`. The copy includes `CLAUDE.md`, so `test_R1_harness_serves_the_project_root_over_loopback` passes in it (the
finder's copy lacked it and showed one unrelated failure). The mutants are exact text edits of the current files (each edit must match the
expected number of times or the run stops), so they stay valid after the fix. `scratch/` was deleted at the end.

`scratch_run.py <label> [--mutant NAME] [-k EXPR]`: M1 to M8 are the finder's mutants rebuilt, A1 (Add person arms no guard) and A2 (Add item arms no
guard) are new. Each `run-<label>.txt` is the full pytest output of one run.

## RG-CR-01: red on the unfixed tree, green after (`run-cr01-red.txt`, `run-cr01-green.txt`)
Selection `-k repeat_press_on_add`: the new tests only, 108 rows. Unfixed tree = the working tree at that moment: shipped `src/` plus the new tests.

| Rows | Unfixed tree | After the fix |
|---|---|---|
| `test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it`, press at the right edge (button.right - 22, centre_y): 4 people counts x 3 sizes x 3 gestures = 36 | **36 red**: `assert 2 == (2 + 1)`, `3 == 4`, `4 == 5`, `5 == 6` (9 each): the person was added and removed again | 36 green |
| same test, press at the centre of the button (the control): 36 | 36 green (the repeat press misses the new Remove button) | 36 green |
| `test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page`, 2 item counts x 3 sizes x 3 gestures x 2 places = 36 | **36 red, and only on the recorder check**: the body saw presses and clicks `[1, 2]` (`[1, 2, 3]` for the triple click) where `[1]` is expected; the data and focus checks before it pass, so the bill alone cannot tell a guard from none for Add item | 36 green |
| total | 72 red, 36 green | 108 green |

Sizes 360x640, 390x844, 1280x800. Gestures mouse double click, mouse triple click, touch double tap. People 2, 3, 4, 5 (S2 cut or grown to P1 to Pn).
Items 1 and 4 (S1 cut to its first items).

Independent check with the finder's own probe (`probe_add_double.py`, a copy of the finder's script, logic unchanged; 96 rows per tree, real gestures at
the middle of the overlap and at the button centre; `add-double-unfixed.json` = scratch copy with mutant A1, `add-double-fixed.json` = shipped tree):

| Tree | Repeat gesture at the right edge (36 rows) | Repeat gesture at the centre (36 rows) | Single click (24 rows) |
|---|---|---|---|
| unfixed (A1) | **0 of 36** end with one person added, focus on the new person's name and nextId +1 | 36 of 36 | 24 of 24 |
| fixed | **36 of 36** | 36 of 36 | 24 of 24 |

## RG-CR-02: mutant M1 (`run-cr02-base.txt`, `run-cr02-M1.txt`, `run-full-M1.txt`)
Selection `-k "ends_at_the_next_press or a_single_click_closes_as_before or still_selects_the_word"`: shipped code 4 passed. M1 (the guard never removes its
`mousedown` listener): **4 failed**, `test_R7_the_guard_of_a_remove_click_ends_at_the_next_press`,
`test_R29_the_guard_of_opening_ends_at_the_next_press`,
`test_R30_a_single_click_closes_as_before_and_the_next_double_click_is_not_held_back` (each now compares `{presses, clicks}` seen by the body with
`{[1, 2], [1, 2]}`, the second press is missing under M1) and `test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word` (`'' == 'Aisyah'`).
Full suite with M1 in the scratch copy: 4 failed, 417 passed (the finder's full run with M1 equalled the baseline). Before this change the three lifetime tests recorded clicks only; the
finder's `run_mutants.py` run of them with M1 gave 106 of 106 passed.

## Mutants M1 to M8 and the fix's own (A1, A2) (`run-sel-*.txt`)
Selection `-k "R6 or R7 or R12 or R29 or R30 or R34"` (218 tests, which holds every test the finder's selection held and the new ones). Shipped code: 218 passed.

| Mutant | Change | Result now | Finder's result |
|---|---|---|---|
| M1 | guard never removes its `mousedown` listener | **killed, 4** | survived |
| M2 | guard never removes its `click` listener | killed, 3 | killed, 3 |
| M3 | item Remove arms no guard | killed, 20 | killed, 20 |
| M4 | person Remove arms no guard | killed, 20 | killed, 20 |
| M5 | New bill click arms no guard (I-1) | killed, 12 | killed, 12 |
| M6 | a repeat is a click count above 2 | killed, 137 | killed, 65 |
| M7 | guard does not `preventDefault` | killed, 88 | killed, 52 |
| M8 | guard listens in the bubble phase | killed, 137 | killed, 65 |
| A1 | Add person arms no guard (RG-CR-01) | killed, 36: the right-edge rows of the Add person test, the centre rows stay green | n/a |
| A2 | Add item arms no guard | killed, 36: every row of the Add item test, on the recorder check | n/a |

## Suites, gates
| Check | Result |
|---|---|
| `python -m pytest tests/browser -q -p no:cacheprovider` before `17ac1ed` | 313 passed in 89.45 s (server pid 33724 port 62131) |
| same before `e30b015` | 421 passed in 119.63 s (pid 41364 port 40980) |
| same, final tree (after all four commits' content) | **421 passed in 120.78 s** (pid 41696 port 57384) |
| `node --test "tests/**/*.test.js"` | **275 pass, 0 fail** (run before each commit and at the end) |
| `python tests/browser/fidelity/run.py` | **10 of 10 pairs, 0 mismatching pixels, dimensions equal**, evidence `docs/modules/split-app/qa/fidelity/20261009-225850/` (pid 49992 port 44932) |
| live gate, `live_gate_scratch.py` into `live-gate-check/20261009-225926/` here | **7 of 7 PASS**, exit 0, console.log empty (pid 32580 port 33475). The official `qa/live-e2e/` was not written |
| `credential_sweep.py --staged`, unpiped, from the project root | exit 0 before each of the four commits |

## Process notes
- A slip: one command (the probe run) used shell redirection (`> probe-unfixed.txt.tmp` and `> /dev/null`) against the hard rule. The only file it made was that
  `.tmp` in this folder, which I removed; its content is in `add-double-unfixed.json`. Every other file was made with the Write or Edit tool or by the scripts above.
- Servers started and stopped by the rig or the probes, each with `STOPPED ... exited True, port free again True`: the three project suite runs above, the scratch runs
  (pids and ports are in each `run-*.txt`), the two probe runs (unfixed pid 44528 port 46661, fixed not recorded because its output was discarded), the fidelity run and the live gate.
