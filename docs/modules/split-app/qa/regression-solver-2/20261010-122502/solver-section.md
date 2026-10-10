## Solver round 2 (2026-10-10)

**RG-CR-08 RESOLVED.** Fixed exactly as the re-check verified it. The 6 new rows are red 6 of 6 on the unfixed `src/` and green 6 of 6 after the fix. The finder's own probe, unchanged, on the fixed tree:
the real double click removes 0 of the 96 affected layouts (it removed 96 of 96 on `a6cbbf8`) and the single click removes 0 of 96. Mutant B1 (items.js Remove drops the count test) turns exactly the 6 new rows red.
Mutant B2 (people.js Remove drops it) is noticed by no test, which is the recorded and expected result. Browser 427 passed, unit 275 passed, fidelity 10 of 10 pairs at 0 px, live gate 7 of 7.
The finder re-run decides the verdict.

Role: dev solver. Start HEAD `856a44e`. Orders: the ORCH ruling of 2026-10-09 (reversible) on RG-CR-08: kept as a BLOCKER and fixed, not accepted. Evidence:
`docs/modules/split-app/qa/regression-solver-2/20261010-122502/` (`evidence.md` indexes every script and output, with the process notes) and the fidelity run
`docs/modules/split-app/qa/fidelity/20261010-123651/`. The finder's sections above, frontmatter included, are as the finder left them. README.md, the ledger, STATE, `findings/*.md` and `docs/design/` were not touched.

### Status per finding
| Id | Status | Commit | Red | Green | Mutants |
|---|---|---|---|---|---|
| RG-CR-08 BLOCKER, a double press on a "who had it" chip under a pending price error removes the item | RESOLVED | `4a36354` (fix and tests), `059f560` (docs and the `swallowRepeatClicks` JSDoc wording) | The 6 new rows on the unfixed `src/`: **6 of 6 red**. `AssertionError: assert ['i4', 'i6', 'i7'] == ['i4', 'i5', 'i6', 'i7']`, `At index 1 diff: 'i6' != 'i5'`, `Right contains one more item: 'i7'` (the same text in every row): item `i5`, "Char kuey teow", was gone from the saved draft | The 6 rows: **6 passed** (4.28 s). Full suite 427 of 427 | B1 killed (6, exactly the new rows). B2 survives, no test notices. M3 and M4 (a Remove arms no guard, count test kept) still killed, 20 each, as in round 1 |

### The fix, in short
Both Remove handlers ignore a repeat press themselves again, as they did before `071577a`, next to the guard: `remove.addEventListener("click", (event) => { swallowRepeatClicks(); if (!isRepeatClick(event)) onRemove(id); })`.
`isRepeatClick` is exported from `src/ui/dom.js` for it. The guard still cancels the repeat press for everything that arms it (it also protects Add person, which has no count test), and the count test at the Remove is the
backstop for a layout move that no click armed, here the error line of a price field pushing the chips down under a double click on a chip. `swallowRepeatClicks` itself did not change.

### What changed, by file and symbol
- `src/ui/dom.js`: `isRepeatClick` is `export const` now (was file-private) and carries a JSDoc line that says why a Remove tests it. `swallowRepeatClicks` JSDoc: "so a new one must (RG-CR-01)" is gone,
  it says that no click can arm the guard for a layout move that is not a click, that a Remove ignores a repeat press itself and that the guard covers everything else, Add person included. "Dismiss note" is kept as a layout mover that arms nothing and lands on no control.
- `src/ui/items.js` `createItems` > `createRow`: `isRepeatClick` added to the import from `./dom.js`; the Remove click handler is the line above; one comment line above it says what the count test is for (the old `// as in people.js` stays true and stays).
- `src/ui/people.js` `createPeople` > `createRow`: the same import and the same handler. The existing comment (a removed row slides the next control under the pointer) is still true and got one more line saying the count test is the backstop for a layout move no click armed.
- `tests/browser/test_app.py`: a new section "Regression RG-CR-08" after the RG-CR-01 rows and before "Security I-1" (not between SEC-01 and RG-CR-01, so the qa.md sentence "up to the RG-CR-01 header" stays true). New names `EIGHT_PEOPLE`, `CHIP_BOXES_JS`,
  `OVER_ITS_OWN_REMOVE_JS` and `test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item` (2 widths x `REPEAT_GESTURES` = 6 rows). It uses the suite's `open_app` (so `rig.new_context`), `gesture_at`, `settle`, `stored` and `REPEAT_GESTURES`.
  The logic is the candidate's (a scout page finds the first point where a chip lies over its own item's Remove once the error shows, a second page presses there with the price field still focused, no item may go). It is named R7 and not R12, as ordered, and the selection `-k "R6 or R7 or R12 or R29 or R30 or R34"` holds it.

### Proof
- **Test first.** The test was written, then run against the unfixed `src/` in a scratch copy of the project (`scratch_run.py cr08-red`, mutant `RED` = no mutation), so the 6 failure screenshots the rig writes on a red run did not land in the project's `qa/functional/`.
  `run-cr08-red.txt`: 6 failed, 421 deselected. The suite's convention is that every commit is green on its own (round 1: `e30b015` carries a fix and its tests, 421 green), so the test was **kept uncommitted** until the fix and went in with it in `4a36354`.
- **Fix, green.** `run-cr08-green.txt`: 6 passed, 421 deselected, project tree.
- **Probe**, `probe_toggle_remove.py` copied byte for byte from the re-check (same SHA-256), run on the fixed project tree (`probe-toggle-remove-fixed.txt`, `toggle-remove-fixed.json`, 83.8 s):

  | Tree | Layouts where a chip point lands on its own item's Remove | Real double click removed an item | Single click removed an item |
  |---|---|---|---|
  | `61c3cd3` (before the delta; the re-check's run) | 96 of 240 | 0 of 96 | 0 of 96 |
  | `a6cbbf8` (HEAD before the fix; the re-check's run) | 96 of 240 | **96 of 96** | 0 of 96 |
  | `4a36354` (fixed; this round's run) | 96 of 240 | **0 of 96** | 0 of 96 |

  `compare_probe.py` (`compare-probe.txt`): all 240 configurations have the same layout scan and the same example point as the re-check's run on HEAD, so both runs pressed the same pixels. On the fixed tree the double click leaves exactly the bill that the single click leaves in 96 of 96
  (so at that point the repeat press toggled nothing either), and the page raised no error in any of the 192 runs.
- **Mutants**, each in a scratch copy rebuilt from the project for that run (`scratch_run.py`), one exact text edit that must match once, project `src/` and `tests/browser` hashed before and after (unchanged every time), the scratch copy deleted after each run:

  | Mutant | Change | Selection | Result |
  |---|---|---|---|
  | B1 | `items.js` Remove drops the count test (HEAD's line `() => { swallowRepeatClicks(); onRemove(id); }`) | full suite | **6 failed, 421 passed**: exactly the 6 rows of the new test |
  | B2 | `people.js` Remove drops the count test (the same) | full suite | **427 passed, no test notices.** Expected: the re-check found no path that puts a repeat press on a person's Remove that no click armed for (the person Removes sit above every price field), so nothing can pin that line. It is there for one rule |
  | M3 | `items.js` Remove arms no guard, keeps the count test | R6 or R7 or R12 or R29 or R30 or R34 (224) | killed, 20 (18 rows of the SEC-01 last-Remove test, 2 of the R34 focus test), the same count as round 1 |
  | M4 | `people.js` Remove arms no guard, keeps the count test | same | killed, 20 (the same shape for people) |

  M3 and M4 are round 1's mutants rebuilt for the new line (their old edit text no longer exists). They show that the count test did not make the arming at the Remove redundant.

### Suites and gates
| Check | Result |
|---|---|
| `node --test "tests/**/*.test.js"` | **275 pass, 0 fail** (265 ms), run before the fix commit and again after the comment edit |
| `python -m pytest tests/browser -q -p no:cacheprovider`, fixed tree before the JSDoc tidy | **427 passed in 113.75 s** (421 + 6) |
| same, final tree (after the JSDoc tidy, before the docs commit) | **427 passed in 111.86 s** |
| repeat-press selection `-k "R6 or R7 or R12 or R29 or R30 or R34"`, fixed tree | **224 passed**, 203 deselected, 77.36 s (the 218 of before plus the 6 new rows) |
| `python tests/browser/fidelity/run.py` | **10 of 10 pairs, 0 mismatching pixels**, dimensions equal, 39.9 s, evidence `qa/fidelity/20261010-123651/` (run on the tree of `4a36354`; `059f560` changed one JSDoc block and documents) |
| live gate, `live_gate_scratch.py` into `live-gate-check/20261010-123748/` here | **7 of 7 PASS**, `failure` null, console.log empty, exit 0. The official `qa/live-e2e/` was not written |
| `credential_sweep.py --staged`, unpiped, from the project root | exit 0 before `4a36354` and before `059f560` |

### Docs changed (commit `059f560`, and the JSDoc in `4a36354`)
- `docs/modules/split-app/BUILD.md`: Status (one sentence, call 18 corrected twice); Test counts (current 427, the 421 line kept as history); Code map (`dom.js` exports `isRepeatClick`, "the one guard" became "the guard", the Remove handlers also test the count; the people and items line);
  judgment call 18 (heading and tenses, the RG-CR-01 sentences put in the past, and a dated correction 2026-10-10 with the mechanism, the measurements, the fix and how to revert it).
- `docs/modules/split-app/spec.md`: R7 (a dated correction after the RG-CR-01 one: a Remove ignores a repeat press itself, the guard covers the rest) and the Threat model row "The bill, as the user left it" (the Seen list gains the chip, then its own Remove; the mitigation sentence no longer says a layout-moving control has to arm the guard; a dated change note).
- `src/ui/dom.js`: the `swallowRepeatClicks` JSDoc and the new `isRepeatClick` JSDoc (above).
- `docs/modules/split-app/qa.md`: a scenario outline for the 6 rows after the Add item outline, with the same kind of dated comment as the RG-CR-01 outlines. It names the grid (widths 375 and 390, three gestures) and not a count.

### What the user will notice
- With a bad amount still in a price field, a double click, triple click or double tap on a "who had it" chip toggles that person and nothing else. Before, in the layouts where a chip's right end sits over its item's Remove (96 of the 240 the probe tried), the whole item (name, price, who) disappeared with no undo.
- Nothing else on screen changed: the fidelity gate is at 0 pixels.

### What went beyond the letter of the order (reversible, for the orchestrator)
1. The red run was in a scratch copy of the project, not in the project tree, to keep failure screenshots out of `qa/functional/`. The `src/` in it was the unfixed `src/` (the project was unchanged by the run, SHA-256 checked).
2. The `dom.js` JSDoc is in two commits: the first wording in `4a36354`, a tidier sentence in `059f560` (the first said "a layout move that is not a click cannot arm anything", which reads oddly).
3. BUILD.md says "the guard" where it said "the one guard against a repeat press", because the Remove count test is a second line now. The Status sentence is the one more place the order did not list but a stale claim would have sat.
4. M3 and M4 were run although the order asked for B1 and B2: nothing else shows that the arming at a Remove is still pinned once the count test is back.

### What changed, for the README reconcile (symbols, not lines)
- `src/ui/dom.js` exports `isRepeatClick`; `src/ui/items.js` and `src/ui/people.js` `createRow` Remove handlers test it. The README `swallowRepeatClicks` bullet needs the clause the re-check named: a Remove also ignores a repeat press itself, and a layout move that is not a click (the error line of a price field) cannot arm the guard.
- Test counts: browser 421 becomes 427 (about 114 s measured; the earlier line said about 120 s), unit 275. Fidelity 10 of 10, live gate 7 of 7 as before.
- Nothing else in the README changes.

### Observations (not fixed, outside the order)
- B2 survives. There is no known user path to build a real-gesture test on for the people handler, and the suite's header allows real gestures only (`test_app.py`), so the line is pinned by the rule and not by a test. Left.
- The re-check noted that the same shift can put a neighbouring chip under the repeat press (a visible, reversible toggle). Not measured by anyone and not changed by this fix. In the 96 probe runs the double click left the single-click bill at the one point pressed, which is not a measurement of every point.
- `docs/brand/` (an empty `screens/` folder) appeared as untracked in the project while this round ran, at 12:30. It is not mine and I did not touch it.
- The fidelity run folder `qa/fidelity/20261010-123651/` is untracked, like this folder. Earlier rounds committed theirs with the evidence.

### Process note
No heredoc, no `sed -i`, no `>` redirection and no `tee`. Files were made with Write or Edit, or by the scripts in the evidence folder (`run_logged.py` keeps the output of a run, since redirection is not allowed). `2>&1` was used on several commands only to show a command's error output
in the tool result, never into a file. `git commit -m` took the message as several `-m` arguments. Slips and script errors are in `evidence.md`, "Process notes".

PROCESSES: none alive that I started. Every server (the project suite runs, the scratch runs, the probe, the fidelity run and the live gate) was the rig's `python -m http.server` on a free loopback port with headless Chromium, started and stopped by the rig or by its script,
each with `STOPPED ... exited True, port free again True`; pids and ports are in `evidence.md`. A final `Get-CimInstance Win32_Process` search by command line (`http.server`, `chrome-headless-shell`, `pytest`, `probe_`, `scratch_run`, `playwright`) found only the shell running the search itself.
