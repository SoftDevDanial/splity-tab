# Evidence: regression code-review re-check, split-app (2026-10-09)

Role: code-review finder, scoped re-check (read-only). Start HEAD `a6cbbf8`. The section for the orchestrator is `recheck-section.md` in
this folder. Project `src/` and `tests/browser/` were never written: `run_mutants.py` prints a SHA-256 of every file under both before and
after each batch, and the three batches all say "unchanged". `git status --short` in the project shows only this folder as new.
Every browser context came from `rig.new_context` (recorder on, `permissions` and `bypass_csp` refused), so the system clipboard was not
touched (CG-7). Every server was the rig's `python -m http.server <free port> --bind 127.0.0.1`, headless Chromium only.

## Suites, run once on the project tree
| Command | Result |
|---|---|
| `node --test "tests/**/*.test.js"` | 275 pass, 0 fail (duration 325 ms) |
| `python -m pytest tests/browser -q -p no:cacheprovider` | **421 passed in 120.74 s** (rig server pid 53972, port 1143, `server STOPPED ... exited True, port free again True`) |

## Scripts and outputs (all in this folder)
| File | What it is | Output |
|---|---|---|
| `probe_add_double.py` | The finder's `probe_add_double.py` of `regression-code-review/20261009-220225/`, unchanged apart from its docstring, run on the project tree: 3 sizes x 4 starting people x 4 gestures x 2 places = 96 rows | `add-double-current.json`. All 96 rows add exactly one person, focus on `Person N+1 name`, `nextId` +1 (the finder's 36 right-edge repeat rows were 0 of 36 on the shipped tree) |
| `probe_hunt.py` | Can the new arming swallow a deliberate action? 40 cases: keyboard Enter and Space on Add person (9 adds) and Add item (6 adds), Tab + Enter on the new Remove, a click of its own on the new name field / the new Remove / the By item label, type then double click a word after Add by mouse and by keyboard, a repeat press on the 12th person and the 50th item, guards left over | `hunt-results.json`: **40 cases, 0 failed** |
| `probe_unarmed.py` | Part A: the whole 44 px "Dismiss note" button (9 points) at widths 320 to 1280 step 20, heights 568 and 844, 2, 3 and 5 people (2646 points). Part B: the two mode labels, 108 repeat-gesture rows against their single click. Part C: a first scan of the field-error layout shift (9 points per control) | `unarmed-results-ABC.json` holds A and B (its C is empty, the first run of C stopped on a strict-mode locator); `unarmed-results-C.json` is C re-run alone |
| `probe_shift.py` | Part C, finer: a point every 4 px across every control, 3, 5, 8 and 12 people, widths 320 and 360 to 1280 step 20, nine fields made bad one at a time. Names every landing and makes the real double click at one example of each destructive one | `shift-results.json`. Landings that matter: a chip pressed, a Remove under the repeat press (`toggle -> REMOVE`) |
| `probe_toggle_remove.py` | RG-CR-08 in full: 3 name sets x 10 people counts (3 to 12) x 8 widths = 240 configurations. Item 1 price holds `abc` with focus. Scan of every 4 px point of every chip, then the REAL double click (and the single click as control) at the first point that lands on a Remove. Run on three trees | `toggle-remove-head.json` (project), `toggle-remove-base.json` (`git archive 61c3cd3`, before the delta), `toggle-remove-fixA.json` (a scratch copy with the candidate fix) |
| `probe_claims.py` | Three small claims measured: a triple click is presses 1, 2, 3 (`gesture_at` docstring); a double click on Dismiss note or a mode label leaves the bill as a single click does and focus on the body (README, Known limits); what is under Dismiss note's centre afterwards | `claims-results.json` |
| `run_mutants.py` | Mutants and the candidate fix, in a scratch copy rebuilt from the project for each run, one string replacement in memory (a replacement that does not match exactly once stops the run). Selection: tests naming R6, R7, R12, R29, R30 or R34 (218 of 421) | `mutant-results-BASE-M1-M2-M9-M10-A1-A2.txt`, `mutant-results-BASE-FIXA-extra.txt`, `mutant-results-FIXA-extra-full.txt` |
| `test_rg_cr_08_candidate.py` | A candidate test for RG-CR-08 (6 rows: 375 and 390 px x mouse double, mouse triple, touch double). Not in the project. `run_mutants.py --extra-test` copies it into the scratch copy | red 6 of 6 on the project tree, green on the candidate fix |
| `scratch-61c3cd3/` | `git archive 61c3cd3 index.html src`, the tree before the delta (the finder used the same baseline) | rebuild with `git archive 61c3cd3 index.html src` |

## Results in one table
| Check | Result |
|---|---|
| RG-CR-01 finder's probe, current tree | 96 of 96 rows +1 person, focus on the new name, `nextId` +1 |
| Hunt for a swallowed deliberate action | 40 of 40 pass |
| Dismiss note, whole button | 2646 points: 1038 `div`, 726 `h2`, 648 `section`, 234 `main`, **0 controls**; real double click not needed (no hit) |
| Mode labels | 108 of 108 rows leave the same stored bill as a single click; focus ends on `BODY` |
| Field-error shift, chips (`toggle -> REMOVE`) | **96 of 240 configurations lay a chip point over its own item's Remove; the real double click removed the item in 96 of 96, the single click in 0 of 96.** Before the delta (`61c3cd3`): same 96 layouts, 0 of 96 removed. Candidate fix: 0 of 96 removed |
| M1 (`mousedown` listener never removed) | **4 red** (`test_R7_the_guard_of_a_remove_click_ends_at_the_next_press`, `test_R29_the_guard_of_opening_ends_at_the_next_press`, `test_R30_a_single_click_closes_as_before_and_the_next_double_click_is_not_held_back`, `test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word`) |
| M2 (`click` listener never removed) | 3 red (the first three above) |
| M9 (no `mousedown` listener at all, the press side gone) | 124 red |
| M10 (no `click` listener at all, the click side gone) | 116 red |
| A1 (Add person arms nothing) | 36 red, all of them the right-edge rows of `test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it` |
| A2 (Add item arms nothing) | 36 red, every row of `test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page` |
| Candidate fix `FIXA`, full suite plus the 6 candidate rows | 427 passed in 121.73 s |
| Candidate test on the project tree | 6 failed (the six `[375|390 x mouse-double|mouse-triple|touch-double]` rows) |

## Process notes
- Servers (all started and stopped by the rig, each printed `STOPPED ... exited True, port free again True`): suite pid 53972 port 1143; `probe_add_double` pid 44880 port 32030; `probe_hunt` pid 44988 port 14163 (a first run that stopped on my own wrong button name, `Remove P5` for `Remove Person 5`), pid 47748 port 2426, pid 23792 port 64616; `probe_unarmed` A, B, C pid 8288 port 51697 and C alone pid 35128 port 11299; `probe_shift` pid 7124 port 49209; `probe_toggle_remove` head pid 47956 port 42567, base pid 5304 port 19505, fixA pid 38184 port 4620; `probe_claims` pid 52404 port 52942. The pytest batches of `run_mutants.py` ran the rig inside their own subprocess and each waited for it.
- Two of my scripts were rewritten after a mistake of mine, not of the project: `probe_hunt.py` (the button name above, and Windows Chromium selects the trailing space with a word, `'Siti '`, so selections are compared after `strip()`) and `probe_unarmed.py` (`get_by_label` matched a section as well as the input; `get_by_role("textbox", ...)` fixes it).
- In `probe_unarmed.py` part C and `probe_shift.py` a field label such as "Service charge in percent" is a `label`, so landings on it are listed as `mode-label`; they are field labels, a press on one only focuses its input. `probe_shift.py` names them.
- A `python -m http.server 53410` (pid 44864, started 23:39:22) was running at the end. It serves the Streaks app (title `Streaks`), so it belongs to the sibling project. I did not start it and did not touch it.
