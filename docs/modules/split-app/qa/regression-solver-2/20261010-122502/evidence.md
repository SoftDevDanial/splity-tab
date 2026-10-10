# Evidence: regression solver round 2, split-app (2026-10-10)

Role: dev solver. Start HEAD `856a44e` (clean tree). Order: the ORCH ruling of 2026-10-09 on RG-CR-08 (BLOCKER, fixed and not accepted, fix exactly as the re-check verified it).
The section for the orchestrator is `solver-section.md` in this folder. README.md, the ledger, STATE, `findings/*.md` and `docs/design/` were not touched.
Python 3.14.0, Node 24.11.1, Chromium 149.0.7827.55 headless through the suite's own rig. Every browser context came from `rig.new_context` (recorder on, `permissions` and `bypass_csp` refused).
The system clipboard was never touched (CG-7). This folder and the fidelity run folder are left untracked for the orchestrator.

## Commits
| Commit | What |
|---|---|
| `4a36354` | fix: RG-CR-08. `isRepeatClick` exported from `src/ui/dom.js`, both Remove handlers (`items.js`, `people.js`) test it after `swallowRepeatClicks()`, `swallowRepeatClicks` JSDoc, the 6 new test rows. The test was kept uncommitted until the fix because every commit in this suite is green on its own (`e30b015` carries a fix and its tests) |
| `059f560` | docs: BUILD.md (Status, Test counts, code map, judgment call 18), spec.md (R7, Threat model row), qa.md (scenario outline), and a tidier sentence in the `swallowRepeatClicks` JSDoc |
| (the commit that holds this folder) | the orchestrator's: `solver-section.md` merged into `findings/regression-code-review.md`, this evidence, the fidelity run folder |

## How the runs were done
The red run and every mutant ran in `scratch/` (a copy of `index.html`, `CLAUDE.md`, `src/`, `tests/browser/` and `docs/design/`), rebuilt from the project for each run by `scratch_run.py` and deleted by it at the end (it prints `scratch/ exists now: False`).
`scratch_run.py` hashes (SHA-256) every file under the project's `src/` and `tests/browser/` before and after and printed "unchanged" for all 5 runs (the red run, B1, B2, M3, M4). A mutant is an exact text edit that must match exactly once, or the run stops before pytest starts.
The red run used mutant `RED`, which is no edit at all: the scratch copy is the project as it was then, unfixed `src/` plus the new test. It ran in a scratch copy and not in the project because the rig's `conftest.py` writes a failure screenshot per red test into the project's `qa/functional/`.
Everything else ran in the project tree (green, suites, probe, gates), where no test fails and nothing is written.

## RG-CR-08: red on the unfixed `src/`, green after
| Run | File | Result |
|---|---|---|
| New rows, unfixed `src/` (scratch copy) | `run-cr08-red.txt` | **6 failed**, 421 deselected, 5.05 s. Every row: `AssertionError: assert ['i4', 'i6', 'i7'] == ['i4', 'i5', 'i6', 'i7']`, `At index 1 diff: 'i6' != 'i5'`, `Right contains one more item: 'i7'`. The item removed is `i5`, "Char kuey teow", item 2 |
| New rows, fixed project tree | `run-cr08-green.txt` | **6 passed**, 421 deselected, 4.28 s |
| Rows | | `[375\|390]` x `[mouse-double\|mouse-triple\|touch-double]` of `test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item` |

## Probe: the finder's `probe_toggle_remove.py`, unchanged, on the fixed tree
`probe_toggle_remove.py` is a byte-for-byte copy of the re-check's file (same SHA-256 `2f889daa5df7...`, checked with `sha256sum` and `diff`). Run as `python probe_toggle_remove.py <project root> fixed` through `run_logged.py`:
`probe-toggle-remove-fixed.txt` (the printed summary) and `toggle-remove-fixed.json` (all 240 rows). 83.8 s.

| Tree | Layouts where a chip point lands on its own item's Remove | Real double click removed an item | Single click removed an item | Source |
|---|---|---|---|---|
| `61c3cd3` | 96 of 240 | 0 of 96 | 0 of 96 | the re-check, `toggle-remove-base.json` |
| `a6cbbf8` (HEAD before the fix) | 96 of 240 | 96 of 96 | 0 of 96 | the re-check, `toggle-remove-head.json` |
| `4a36354` (fixed) | 96 of 240 | **0 of 96** | **0 of 96** | this folder |

`compare_probe.py` reads the two JSON files and writes nothing (`compare-probe.txt`): the 240 configurations have the same layout scan and the same example point as the re-check's HEAD run; on the fixed tree the double click leaves exactly the bill that the single click leaves in 96 of 96; 0 page errors in the 192 affected runs.

## Mutants (all in the scratch copy)
| Label | Mutant | Selection | Result | File |
|---|---|---|---|---|
| `full-B1` | B1: `items.js` Remove back to HEAD's line, no count test | full suite | **6 failed, 421 passed** in 112.32 s. The six: the new test, `[375\|390]` x `[mouse-double\|mouse-triple\|touch-double]` | `run-full-B1.txt` |
| `full-B2` | B2: `people.js` Remove back to HEAD's line | full suite | **427 passed** in 110.20 s. No test notices | `run-full-B2.txt` |
| `sel-M3` | M3: `items.js` Remove arms no guard, count test kept | R6 or R7 or R12 or R29 or R30 or R34 (224) | 20 failed, 204 passed in 65.28 s: 18 rows of `test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing` (`S1-item-4-of-4`, `S1-only-item`) and 2 of `test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it` (`item-2-of-4`) | `run-sel-M3.txt` |
| `sel-M4` | M4: `people.js` Remove arms no guard, count test kept | same | 20 failed, 204 passed in 64.38 s: the same two tests with the people cases (`S2-person-3-of-3`, `S8-person-12-of-12`, `person-2-of-5`) | `run-sel-M4.txt` |

M3 and M4 are round 1's mutants of the same name rebuilt for the new handler line (round 1: 20 red each). The baseline for the full-suite mutants is the project's own full run on the fixed tree, 427 passed (`run-full-fixed.txt`, `run-full-final.txt`).
Not re-run: round 1's other mutants (M1, M2, M5 to M10, A1, A2). They edit the guard's listeners, the dialog opener and the Add handlers, which this change did not touch; the 224-test selection that holds the tests that kill them is green (`run-sel-fixed.txt`).

## Suites and gates
| Check | Result | File |
|---|---|---|
| `node --test "tests/**/*.test.js"` | 275 pass, 0 fail, before the fix commit | `run-node.txt` |
| same, after the comment edit in `dom.js` | 275 pass, 0 fail | `run-node-after-docs.txt` |
| `python -m pytest tests/browser -q -p no:cacheprovider`, fixed tree | **427 passed in 113.75 s** (server pid 3116 port 40211) | `run-full-fixed.txt` |
| same, selection `-k "R6 or R7 or R12 or R29 or R30 or R34"` | **224 passed**, 203 deselected, 77.36 s (pid 3584 port 32035) | `run-sel-fixed.txt` |
| `-k "R37 or R39 or pending_price_error"` after the comment edit (the static scans read `src/` comments) | 19 passed | `run-static-after-docs.txt` |
| same full suite, final tree (after the JSDoc tidy, before the docs commit) | **427 passed in 111.86 s** (pid 11452 port 37101) | `run-full-final.txt` |
| `python tests/browser/fidelity/run.py` | **10 of 10 pairs, 0 mismatching pixels**, dimensions equal, 39.9 s, run folder `docs/modules/split-app/qa/fidelity/20261010-123651/` (pid 6380 port 51222). Run on the tree of `4a36354` | `run-fidelity.txt` |
| live gate through `live_gate_scratch.py` | **7 of 7 PASS**, exit 0, `summary.json` result PASS, 7 steps, `failure` null, `console.log` empty (pid 12852 port 13836). Official `qa/live-e2e/` not written (it still holds `20261009-173415` and `20261009-215416`) | `run-live-gate.txt`, `live-gate-check/20261010-123748/` |
| `credential_sweep.py --staged`, unpiped, from the project root | exit 0 before `4a36354` and before `059f560` ("CLEAN. No secret values found.") | (printed in the session) |

## Scripts and outputs in this folder
| File | What it is |
|---|---|
| `run_logged.py` | Runs one command from a folder with a time limit and keeps its whole output in a file here (header line with the command, exit status and wall time, then the output unchanged). Needed because shell redirection is not allowed. Used for every `run-*.txt` except the scratch runs |
| `scratch_run.py` | Builds the scratch copy, applies at most one mutant (`RED`, `B1`, `B2`, `M3`, `M4`), runs pytest in it, writes `run-<label>.txt`, hashes the project's `src/` and `tests/browser` before and after, deletes the scratch copy |
| `probe_toggle_remove.py`, `toggle-remove-fixed.json`, `probe-toggle-remove-fixed.txt` | The finder's probe, byte for byte, and its two outputs |
| `compare_probe.py`, `compare-probe.txt` | Reads `toggle-remove-fixed.json` and the re-check's `toggle-remove-head.json`; prints the comparison above |
| `live_gate_scratch.py`, `live-gate-check/` | Runs `tests/browser/live_e2e.py` unchanged with its one `EVIDENCE_ROOT` variable pointed at `live-gate-check/` here; the gate's seven screenshots, two clipboard texts, logs and `summary.json` |
| `run-cr08-red.txt`, `run-cr08-green.txt` | The new rows on the unfixed `src/` (scratch) and on the fixed tree |
| `run-full-B1.txt`, `run-full-B2.txt`, `run-sel-M3.txt`, `run-sel-M4.txt` | The four mutant runs |
| `run-node.txt`, `run-node-after-docs.txt`, `run-full-fixed.txt`, `run-sel-fixed.txt`, `run-static-after-docs.txt`, `run-full-final.txt`, `run-fidelity.txt`, `run-live-gate.txt` | The suites and gates above |
| `solver-section.md` | The section the orchestrator merges into `findings/regression-code-review.md` |

## Process notes
- Servers (all the rig's `python -m http.server` on a free loopback port with headless Chromium, each printed `STOPPED ... exited True, port free again True`): red run pid 4164 port 40504; green rows pid 22512 port 12158; full suite pid 3116 port 40211; selection pid 3584 port 32035;
  probe pid 20764 port 31259; B1 pid 9276 port 56155; B2 pid 24396 port 1242; fidelity pid 6380 port 51222; live gate pid 12852 port 13836; static scans pid 23484 port 13289; final full suite pid 11452 port 37101; M3 pid 1492 port 62354; M4 pid 9420 port 64260.
  The two node runs start no server. A last `Get-CimInstance Win32_Process` search by command line (`http.server`, `chrome-headless-shell`, `pytest`, `probe_`, `scratch_run`, `run_logged`, `playwright`, `live_gate`) matched only the shell running the search.
- The probe ran as a background command (about 84 s) and finished by itself.
- The shell's PATH was the Windows one at first, so `git` and `head` were not found; every later command began with an `export PATH=...` line. Not a rule breach.
- `run_logged.py` crashed once, on its first node run: the final `print` of node's reporter symbol failed on the Windows code page (`UnicodeEncodeError`). The output file had been written before the print. I made stdout UTF-8 in the script and ran the same command again; the first run's file was overwritten by the second, same result (275 pass).
- Before `compare_probe.py` existed I ran the same comparison once as an inline `python -B -c "..."`. It read two JSON files and wrote nothing. `compare_probe.py` and its saved output replace it.
- `2>&1` was on several commands to show error output in the tool result, never into a file. `sed` was used for display in one `grep | sed | cut` line, never with `-i`. No heredoc, no `tee`, no `>` or `>>`. Files were made with Write or Edit, or by the scripts above. `git add` named its paths, never `-A`. Commit messages used several `-m` arguments and carry no co-author or tool line.
- The red run was in a scratch copy and not in the project tree (see How the runs were done). That is a small deviation from "run it against the unfixed `src/`": the `src/` in the copy was the unfixed one.
- The fidelity run and the live gate ran on the tree of `4a36354`. `059f560` changed one JSDoc block in `dom.js` and documents, after which the full browser suite (427) and the unit tests ran again.
- `docs/brand/` (an empty `screens/` folder, made at 12:30) appeared as untracked in the project during the round. Not mine, not touched, not staged.
- A hook note after two `src/` edits suggested starting a preview server. I did not: the app is checked by the Playwright runs above, and no server of mine was left running.
