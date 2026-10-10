---
module: split-app
kind: code-review
run: regression
status: pass
counts: { blocker: 0, warning: 0, info: 0 }
---
# Code review, regression pass: split-app

Role: code-review finder (read-only). Date: 2026-10-09. Head `1e39b83` (no code differs from `22ac9af`).
Scope (ORCH economy ruling): the split-app source delta nobody had reviewed, `git diff 61c3cd3 22ac9af -- src index.html`
(`src/ui/dialog.js`, `dom.js`, `items.js`, `people.js`) with its tests (`tests/browser/test_app.py`, 68 new tests), the
cross-module seam, the new `README.md`, and the doc drift of the security round. Judged against spec R7, R12, R29, R30, R34,
the dated notes of 2026-10-09, the constitution and `CLAUDE.md`. Everything the predecessor reviewed and the solver fixed at
`61c3cd3` was not re-read unless the delta touches it. Accepted limits (H-02, SEC-03, SEC-04, the Dismiss note focus drop, two
tabs) are not findings.

## Verdict
**ISSUES FOUND. 1 BLOCKER, 3 WARNING, 3 INFO.**
- The delta's own logic is sound. `swallowRepeatClicks` arms in the target phase, after the document capture phase of the arming
  click, so the click that arms it is never cancelled. Every non-repeat press passes an older guard first and removes it, so at most
  one guard is outstanding. A key press (count 0) is never held back. It uses `stopPropagation`, not `stopImmediatePropagation`, so the
  `field-leave.js` document listeners still see the presses. No timer, no hook, no banned API.
- **RG-CR-01 is a regression the delta introduced.** Replacing the Remove handlers' own count test by the armed guard removed the
  protection against a repeat press that reaches a Remove button when no Remove click armed the guard. "Add person" is such a case, and
  nobody measured it. A double click on the right edge of "Add person" now adds a person and removes it again. 312 of 312 tests stay
  green because no test double clicks "Add person".
- The tests pin the guard well. Of 8 mutants of the delta, 7 are killed. One plausible slip survives the full suite (RG-CR-02).
- The core seam is clean (`git diff 329679e 22ac9af -- src/core` is empty, only exported functions are imported, no money outside
  split-core). The README is accurate on its symbols and commands, with four wrong or stale lines (RG-CR-03). Doc rot from the
  security round is small (RG-CR-04).
- Suites: `node --test "tests/**/*.test.js"` 275 pass, 0 fail. `python -m pytest tests/browser -q -p no:cacheprovider` 312 passed in
  89.18 s (server pid 44412 port 15052, started and stopped by the rig). The README numbers hold.

## BLOCKER

### RG-CR-01: A double click on the right edge of "Add person" adds a person and removes it again   (bug, regression of 071577a)
- **File and symbol:** `src/ui/people.js`, `createPeople`: `add.addEventListener("click", onAdd)` (line 23) arms no guard, while the Remove
  handler (line 18) now acts on every click that reaches it. Same shape in `src/ui/items.js` line 40, which is safe today (see below).
  Doc claims refuted: `src/ui/dom.js` `swallowRepeatClicks` JSDoc ("it does not matter what slid under the pointer"), spec R7 (SEC-01
  note, "so it no longer matters what slid under the pointer"), the spec Threat model row "The bill, as the user left it" (the repeat
  press is cancelled "before any control sees them"), BUILD.md judgment call 18 ("So no path is left open").
- **Issue:** Before `071577a` each Remove handler ignored any click with a count above 1 (`if (!isRepeatClick(event)) onRemove(id)`),
  whether or not a guard was armed. After it, a Remove button acts on every click and relies on the guard having been armed by an
  earlier Remove click. "Add person" does not arm it. The "Add person" button fills its grid cell, and the new person's row takes that
  cell, so the new row's Remove button (44 px wide at the right of the cell) sits under the right 44 px of the old "Add person"
  button. The first click adds, the repeat press of a double click, triple click or double tap lands on the new Remove and removes the
  blank row. Net result: nothing is added, one id is spent (`nextId` + 1), and focus is on the previous person's name, not on the new
  person's name as R34 says. The overlap exists at every width I tried (320, 360, 375, 390, 412, 600, 768, 1024, 1280) and for every
  people count I tried (2, 3, 4, 5, 11): 45 of 45 rows. "Add item" has no overlap (its button is 123 px wide at the left, its Remove
  button is at the right): 27 of 27 rows clear, so that one is safe today.
- **Proof (run, not read):** `probe_add_double.py` on the shipped tree and on a `git archive` copy of `61c3cd3`. Real gestures
  (`mouse.dblclick`, `mouse.click(click_count=3)`, two `touchscreen.tap`) at the middle of the overlap, at 360x640, 390x844 and
  1280x800, starting from 2, 3, 4 and 5 people:

  | Tree | Repeat gesture at the right edge (36 rows) | Repeat gesture at the button centre (36 rows, control) |
  |---|---|---|
  | `61c3cd3` (before the delta) | 36 of 36 add one person. Focus drifts to `Remove Person N` | 36 of 36 add one person |
  | `22ac9af` / `1e39b83` (shipped) | **0 of 36 add a person. 36 of 36 end with the same people and one id spent.** Focus on the previous last person's name | 36 of 36 add one person |
  | shipped plus the fix below | 36 of 36 add one person, focus on the new person's name | 36 of 36 add one person |

  Mutant view: remove the guard from the Remove handlers and 20 tests fail (M4), so the suite does guard Remove. No test touches a
  repeat press on "Add person", so the shipped tree passes 312 of 312 with this defect.
- **Fix:** arm the same guard in the Add person click, so the repeat press never reaches whatever slid under the pointer.
  ```js
  // src/ui/people.js, in createPeople
  add.addEventListener("click", () => { swallowRepeatClicks(); onAdd(); });
  ```
  Do the same in `src/ui/items.js` for symmetry (no defect today, and one rule is easier to keep true than a measured exception).
  Verified in a scratch copy (`mutant-files/people.FIX.js`): the 36 right-edge rows give +1 person with focus on the new person's name,
  the centre rows still give +1, the selected R7, R29, R30 and R34 tests pass 106 of 106, and the full suite gives 311 of 312 with the
  one failure the scratch copy has at baseline too (it lacks `CLAUDE.md`, see Evidence). Add the test next to the SEC-01 block:
  parameters people in (2, 3, 4), the three sizes, gestures mouse-double, mouse-triple and touch-double. Press at
  `(button.right - 22, button.centre_y)` of "Add person" through `gesture_at`. Assert one more `li.person` and
  `support.active_label(page) == f"Person {people + 1} name"`. It is red on the shipped tree.
  Update with it: the `swallowRepeatClicks` JSDoc list ("a row removed, the dialog opened or closed" gains "a person added"), spec R6
  (a dated note), the R7 SEC-01 note and the Threat model row ("armed by ... every Remove ... and the opening or closing of the dialog"
  gains "and by Add person"), a qa.md scenario, BUILD.md code map and judgment call 18, the README bullet on `swallowRepeatClicks`.
- **Severity:** BLOCKER because it is incorrect behavior on a path the suite and the spec claim to cover, and it is a regression of
  verified behavior. It is narrow (the rightmost 44 px of the button, 26 percent of its width at 390 px, and a repeat press) and it
  loses no data the user typed (the row that goes is the blank one just added). The orchestrator may rule it down to an accepted limit
  under the stop rule. The fix is one line plus one test and was verified.

## WARNING

### RG-CR-02: A guard that never lets go of its `mousedown` listener passes the whole suite   (test strength, a control that cannot fail)
- **File and symbol:** `src/ui/dom.js` `swallowRepeatClicks` (the removal pair). Tests: `test_R7_the_guard_of_a_remove_click_ends_at_the_next_press`,
  `test_R29_the_guard_of_opening_ends_at_the_next_press`, `test_R30_a_single_click_closes_as_before_and_the_next_double_click_is_not_held_back`.
- **Issue:** Mutant M1 changes the removal pair to remove the `click` listener twice, a copy-paste slip. The `mousedown` guard then stays
  armed for the rest of the page's life, so every later press with a click count above 1 has its mousedown cancelled
  (`preventDefault`). M1 passes every test the baseline passes: 106 of 106 in the R7, R29, R30 and R34 selection, and the full run gives the
  baseline's result (311 passed and the one copy-environment failure described under Evidence, in both). Its mirror, M2 (the `click` listener
  leaks), is killed by 3 tests. The three "guard ends" tests only record `click` events on `document.body`, and a leaked mousedown guard
  does not change any click. The user-visible cost is real: after one Remove click and one ordinary click, a double click on a name no
  longer selects the word (`probe_word_select.py`: the shipped tree selects "Aisyah" before and after, M1 selects "Aisyah" before and
  nothing after).
- **Fix:** make the "guard ends" tests see the press as well as the click. Record `mousedown` details on `document.body` next to the click
  details in `RECORD_BODY_CLICKS_JS` and assert `[1, 2]` for both after `dblclick()` (a swallowed press never reaches the body), or add one
  real-gesture check: after a Remove click and one ordinary click, `dblclick()` on `Person 1 name` leaves `Aisyah` selected. Both kill M1 and
  keep M2 to M8 killed.

### RG-CR-03: Four README lines are wrong or stale   (doc rot, fallback owner)
- **File and symbol:** `README.md`. Ledger row 50 says the README was "verified by symbol". These four lines were not.
- **Issue:**
  1. **Status table, `split-app` row ("gates green, closing").** Ledger row 50 records the module as closed, and `STATE.md` agrees. Stale.
  2. **"`commit`, which runs a core action, saves the draft and calls `render`".** `commit(next)` in `src/main.js` runs no action. The
     caller runs the action (`commit(addPerson(bill))`) and `commit` takes the resulting bill, saves it, restates the copy status and
     renders. The line was copied from BUILD.md's code map, which has the same wording.
  3. **"`src/errors.js` holds the rules ... as pure functions".** `typedInto`, `leftField` and `forgetPrice` mutate the `flags` object they
     are given and return nothing. Only `newErrorFlags`, `flagsFor` and `visibleErrors` are pure. The same wrong claim is in the header comment
     of `src/errors.js` ("Pure view-state rules") and in BUILD.md's code map.
  4. **"Known limits ... The ledger has the reasoning."** The ledger covers four of the six rows (H-02, SEC-04, SEC-03 as row 43, two tabs as
     row 45). It does not carry the "mode label" half of the third row (ledger row 40 names only Dismiss note) and it has no row for the
     same-origin read and framing residuals (those live in `spec.md` Residual risks and `findings/security.md`).
- **Fix:** (1) set the status to "closed 2026-10-09" once the regression pass ends. (2) "routes every change to the bill through `commit`,
  which takes the bill a core action returned, saves the draft and calls `render`". (3) "as small functions: `flagsFor`, `visibleErrors` and
  `newErrorFlags` build or read the flags, `typedInto`, `leftField` and `forgetPrice` update the flags they are given", and the same in
  the `src/errors.js` header and BUILD.md. (4) either reword to "The ledger, `spec.md` (Residual risks) and `findings/security.md` have the
  reasoning", or have the orchestrator add one ledger row for the mode-label focus drop and one for the same-origin and framing residuals.
  Also touch the `swallowRepeatClicks` bullet when RG-CR-01 is fixed (it says the press "never lands on the control that moved under the
  pointer", which is not true for Add person today).

### RG-CR-04: Counts and claims in qa.md, BUILD.md and a test docstring that the repository refutes   (doc rot)
- **File and symbol:** `docs/modules/split-app/qa.md` (the comment above the SEC-01 outline, "and the four after it"), `docs/modules/split-app/BUILD.md`
  (the Status paragraph, "Test counts (last run, after Task 13)", judgment call 18), `tests/browser/test_app.py` `gesture_at` docstring.
- **Issue:**
  1. qa.md says the SEC-01 tests are `test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing` "and the four after it".
     Three follow it before the I-1 block (`test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it`,
     `test_R7_a_separate_click_on_what_slid_under_the_pointer_is_not_held_back`, `test_R7_the_guard_of_a_remove_click_ends_at_the_next_press`).
     The I-1 comment below it says "the three after it" and is right. A stale absolute count.
  2. BUILD.md Status (top of file) says "The finders, solvers and the official gate runs come next." They have all run. The heading
     "Test counts (last run, after Task 13)" is followed, a few bullets later, by a later run (312). "Last run" is no longer true of its first bullets.
  3. BUILD.md judgment call 18 closes with "So no path is left open." RG-CR-01 refutes it. It measured the Dismiss note only.
  4. `gesture_at` says a triple click is "one press with click count 3, as the operating system sends it". Playwright's
     `Mouse.click(click_count=3)` sends three presses with counts 1, 2 and 3 (`coreBundle.js`, the loop `for (let cc = 1; cc <= clickCount; ++cc)`),
     which is also what the operating system sends. The helper is right, its docstring is not.
- **Fix:** (1) "and the three after it". (2) Replace "come next" by what happened, and rename the heading "Test counts (after Task 13)" with the 312
  and 275 bullet kept as the final line, or state the stable effect instead of a count. (3) Reword with RG-CR-01's fix: "measured for the Dismiss note;
  Add person arms the guard too". (4) "A triple click is three presses with counts 1, 2 and 3."

## INFO

### RG-CR-05: The one guard's derivation is restated in many places   (DRY across the code and docs boundary)
`swallowRepeatClicks` JSDoc in `dom.js` is the home. The same reasoning ("the rest of a double click lands on whatever is drawn
there next") is restated in the call-site comments of `dialog.js` (two) and `people.js` (one), the section header in `test_app.py`, spec R7,
R29, R30 and the Threat model row, and BUILD.md calls 18 and 19. Each is short and true today, and RG-CR-01 shows what happens when a list
inside one of them (which controls arm the guard) goes stale. Suggest the call-site comments say only "arms the guard
(`swallowRepeatClicks`)" plus the one fact that is local, and the lists of arming controls live in the JSDoc and the spec row only. `dom.js`
now also holds an event guard under a header that says "Small DOM helpers", a small cohesion cost the ORCH ruling accepted.

### RG-CR-06: Small README precision points
`applyRate` exists but is private to `src/core/result.js` (the exported one is `billCharges`), so a reader who greps for an export will not
find it. "Every browser context gets a recorder in place of `navigator.clipboard.writeText`" is true of the default. The failure-path tests
give a context a rejecting or a missing stub instead (`rig.new_context(clipboard=...)`), still never the system clipboard. "Only a press that
starts and ends on the backdrop closes it" reads as if nothing else closes the dialog, but Cancel, Esc and Start new bill do. Say "a click
on the backdrop closes it only if the press began there too".

### RG-CR-07: The suite is not portable to a copy without `CLAUDE.md`
`test_R1_harness_serves_the_project_root_over_loopback` fetches `/CLAUDE.md` from the served root, so any copy of the tree that omits it
(mine, for mutant runs) shows one failure unrelated to the code. Not a defect in the project. A comment on the test naming the file as the
probe would save the next reader the detour.

## What I checked and how
1. **Delta code (scope 1).** Read the full diff and the four files at HEAD. Traced event order for the arming click, the repeat presses, a
   keyboard click, a mouse press after a keyboard Remove, and two guards in a row. Cross-read `field-leave.js` and `main.js` (`onRemove`,
   focus rules) for interaction. Reverse audit: every changed line maps to R7 or R12 (SEC-01), R29 (I-1) or R30 (CR-01). No non-goal built.
2. **Layout probes.** `probe_add_geometry.py` measured, for 9 widths and people counts 2, 3, 4, 5, 11 and item counts 1, 2, 4, where the new
   row's Remove button lands against the old Add button (72 rows, 45 overlap, all of them "Add person"). `probe_add_double.py` ran the
   gesture on three trees (shipped, `61c3cd3`, shipped plus fix), 96 rows each.
3. **Tests (scope 1).** Read the 68 new tests. Ran 8 mutants of the delta in a scratch copy with the R7, R29, R30 and R34 selection (106 tests):

   | Mutant | Change | Result |
   |---|---|---|
   | M1 | guard never removes its `mousedown` listener | **survives**: 106 of 106 selected, and the full run equals the baseline's (RG-CR-02) |
   | M2 | guard never removes its `click` listener | killed, 3 tests |
   | M3 | item Remove arms no guard | killed, 20 |
   | M4 | person Remove arms no guard | killed, 20 |
   | M5 | New bill click arms no guard (I-1) | killed, 12 |
   | M6 | a repeat is a count above 2 | killed, 65 |
   | M7 | guard does not `preventDefault` | killed, 52 |
   | M8 | guard listens in the bubble phase | killed, 65 |

   Baseline of the selection: 106 of 106. Controls in the new tests are real: they include the single-click row, and the "guard ends" tests
   record clicks on `document.body`, which the guard cancels before it.
4. **Seam (scope 2).** `git diff --quiet 329679e 22ac9af -- src/core` exits 0 (empty), and `git diff --stat 22ac9af 1e39b83` lists only
   `docs/progress/` and the ledger, so no code moved since. Every import from `core/` in `src/` is an export (`LIMITS`, `newBill` and the
   other actions, `personLabel`, `itemLabel`, `parseAmount`, `parseRate`, `formatMoney`, `formatRate`, `computeResult`, `summaryText`) and
   all are in the spec's import list. A grep of `src/` outside `core/` for rounding, `toFixed`, `BigInt`, `* 100`, `Number(` finds only the id
   number parse in `draft.js`. `panel.js` formats what `computeResult` returns and adds nothing.
5. **README (scope 3).** Every cited symbol was grepped (all exist, `applyRate` is private). `system.css` is the golden's bytes plus
   `\n[hidden] { display: none !important; }\n` (checked byte for byte). The CSP in the README equals the meta in `index.html`. The
   `BigInt` claim holds (only `allocate.js`). The test commands, `SDLC_HARNESS`, the PID and port print, the evidence folders and the failure
   screenshot path were read in `rig.py`, `conftest.py` and `fidelity/run.py`. The unit and browser suites were run once each. The limits table
   was compared row by row with the ledger and H-02 (the RM 650 figure matches RM 653.40).
6. **Doc drift (scope 4).** Spec R7, R12, R29, R30, the Threat model rows, qa.md (SEC-01 and I-1 scenarios), BUILD.md (Status, code map,
   calls 18 and 19) and the test docstrings were checked against the code and the test list. The 54 + 14 test counts in BUILD.md hold
   (48 + 4 + 1 + 1 and 9 + 3 + 1 + 1), and so does "12 of the 14 I-1 tests go red" (M5 = 12).
7. **Not done on purpose.** Fidelity and the live gate were not re-run (the ORCH ruling lets the solver's runs stand, and no code changed).
   Real touch devices were not measured. Em and en dashes were scanned for in the README, CLAUDE.md, spec, BUILD.md, qa.md, ROADMAP, `src/` and
   `test_app.py`: none.

## Evidence
`docs/modules/split-app/qa/regression-code-review/20261009-220225/`
- `probe_add_geometry.py`, `geometry-head.json`: where the new row's Remove button lands (72 rows).
- `probe_add_double.py`, `add-double-head.json`, `add-double-base.json`, `add-double-fix.json`: the RG-CR-01 gesture on three trees.
- `probe_word_select.py`, `word-select-head.json`, `word-select-M1.json`: the user-visible cost of M1.
- `run_mutants.py`, `mutant-results-M1-M2-M3-M4-M5-M6-M7-M8-FIX.txt`: the mutant runs and the failing test ids.
- `scratch-61c3cd3/`: `git archive` of `61c3cd3` (`index.html`, `src/`). `scratch-mutants/`: a copy of `index.html`, `src/`, `tests/browser/` and
  `docs/design/` at HEAD, plus `mutant-files/` (M1 to M8 and the fix). No mutant was ever written to the project `src/`. The scratch copy lacks
  `CLAUDE.md`, so `test_R1_harness_serves_the_project_root_over_loopback` fails in it, at baseline and in every full run alike (full runs:
  baseline, M1, fix: 311 passed, 1 failed each). The 237 failure screenshots the mutant runs left in the scratch copy were removed from it.
- CG-7: every context came from `rig.new_context` (recorder on, `permissions` and `bypass_csp` refused). The system clipboard was not touched.

## Processes
PROCESSES: none alive from me. I started and stopped: the rig static server of the browser suite run (pid 44412, port 15052), of the
probes (for example pid 40916 port 54924 for the `61c3cd3` run, pid 50320 port 50561 and pid 42784 port 59684 for the word-select probes)
and of the scratch pytest runs (for example pid 52644 port 3232). Each printed STARTED and STOPPED with the port free again. Headless
Chromium instances were closed by each script or by the pytest fixture. My four background commands (the suite run, the mutant run, one
bounded wait loop and the scratch full-suite runs) all exited, and my foreground wait loops were capped at 36 or 50 polls. A final sweep with
`Get-CimInstance Win32_Process` by command line (`regression-code-review`, `http.server`, `run_mutants`, `probe_add`, `probe_word`, `pytest`,
`chrome-headless-shell`, `playwright`) found a `run_mutants.py ... test_delete` run with its pytest child under `docs/modules/app/` (the
sibling Streaks project) and, in the same listing, a node driver and three `chrome-headless-shell` processes with none of my paths. A second
query for those PIDs a moment later found them gone, so they were not leaks of mine (a leak would still be there). I did not touch any of them.

---

## Solver (2026-10-09)

Role: dev solver. Start HEAD `9030ce7`. Orders: the ORCH rulings of 2026-10-09 (reversible) on RG-CR-01, RG-CR-02 and RG-CR-04, and the scope
addition for RG-CR-03 items 2 and 3 where they live in `src/errors.js` and the BUILD.md code map. Evidence:
`docs/modules/split-app/qa/regression-solver/20261009-222856/` (`evidence.md` has the red and green runs, the mutant table, the probe results and the process
notes; `run-*.txt` are the full pytest outputs; `live-gate-check/`) and the fidelity run `docs/modules/split-app/qa/fidelity/20261009-225850/`. The finder's
sections above, the frontmatter included, are as the finder left them. The finder re-run decides the verdict.

### Status per finding
| Id | Status | Commit | Red | Green | Mutants |
|---|---|---|---|---|---|
| RG-CR-01 BLOCKER, a double click on the right edge of Add person adds a person and removes it again | RESOLVED | `e30b015` (fix and tests), notes in `f0ca022` and `38686c0` | The 108 new rows on the unfixed tree: **72 red, 36 green**. Red: the 36 Add person rows pressed at `button.right - 22` (`assert 2 == (2 + 1)` and its 3, 4, 5 siblings: the person was added and removed again) and the 36 Add item rows (only on the recorder check: the body saw `[1, 2]`, or `[1, 2, 3]` for the triple click, where `[1]` is expected, because the bill cannot tell a guard from none there). Green: the 36 Add person rows pressed at the centre, the control. The finder's own probe on the unfixed tree: 0 of 36 right-edge rows end with one person added | 108 of 108. The finder's probe on the fixed tree: 36 of 36 right-edge rows add one person with focus on the new person's name and nextId +1, 36 of 36 centre rows and 24 of 24 single clicks as before | A1 (Add person arms no guard): 36 red, exactly the right-edge rows. A2 (Add item arms no guard): 36 red, every Add item row. M3 and M4: 20 red each, M5: 12, still killed |
| RG-CR-02 WARNING, a guard that keeps its `mousedown` listener passes the suite | RESOLVED | `17ac1ed` | M1 on the new tests: **4 red** (the three "guard ends" tests now compare what the body saw of the presses and of the clicks, and the new word-select test: `'' == 'Aisyah'`). Before, M1 passed 106 of 106 | The shipped code: the 4 tests green, full suite 421 of 421 | **M1 killed (4)**, M2 killed (3), M3 (20), M4 (20), M5 (12), M6 (137), M7 (88), M8 (137): all eight killed. The full suite with M1 in the scratch copy: 4 failed, 417 passed |
| RG-CR-04 WARNING, doc rot | RESOLVED | `38686c0` (BUILD.md, `gesture_at`), `f0ca022` (qa.md) | n/a (documents and comments) | Item 1: the qa.md SEC-01 comment now names the range of tests ("the tests after it in the same section of `test_app.py`, up to the RG-CR-01 header") and not a count, because the word-select test is now the fourth after it and a count rots. Item 2: BUILD.md Status says what happened, "Test counts" gives the current counts and keeps the older runs as history. Item 3: judgment call 18 no longer ends with "no path is left open"; a dated correction says it measured the Dismiss note only and that Add person and Add item arm the guard. Item 4: `gesture_at` says a triple click is three presses with counts 1, 2 and 3, as Playwright's `click(click_count=3)` sends them | |
| RG-CR-03 items 2 and 3 (scope addition) | DONE where they live in my files | `38686c0` | n/a (comments) | `src/errors.js` header: only `newErrorFlags`, `flagsFor` and `visibleErrors` are pure, the other three update the flags they are given. BUILD.md code map: `commit` takes the bill a core action returned, saves the draft, restates the copy status and renders; the `errors.js` line corrected the same way. README.md not touched | |
| RG-CR-03 items 1 and 4, RG-CR-06 | NOT MINE | | | README.md and the ledger are the orchestrator's | |
| RG-CR-05, RG-CR-07 | ACCEPTED (ruling) | | | not changed | |

### The fix, in short
`createPeople` and `createItems` register `() => { swallowRepeatClicks(); onAdd(); }` on the Add person and Add item buttons, so the repeat press of a double click,
triple click or double tap is cancelled at the document before it reaches the Remove button that slid under the right end of Add person. `swallowRepeatClicks`
itself did not change. Its JSDoc no longer says "it does not matter what slid under the pointer": it names the armers (every Remove, Add person, Add item, the
opening and closing of the dialog), says the guard protects only what arms it, and names Dismiss note as the measured exception. Spec R6, R7 (a dated correction
of the SEC-01 note), R12 and R30 and the Threat model row carry dated notes, qa.md has an outline for each button, BUILD.md has the code map, call 18 corrected and a new call 20.

### Proof
- Suites: browser 312 to **421 passed** (120.78 s; the 312 plus 72 + 36 Add rows plus 1 word-select test), unit **275 passed**, both run before each commit and at the end. Each commit was green on its own (313 after `17ac1ed`, 421 after `e30b015`).
- Fidelity: `python tests/browser/fidelity/run.py`, **10 of 10 pairs at 0 mismatching pixels**, dimensions equal, evidence `qa/fidelity/20261009-225850/` (server pid 49992 port 44932, stopped).
- Live gate: `tests/browser/live_e2e.py` unchanged, run through `live_gate_scratch.py` into `live-gate-check/20261009-225926/` here: **7 of 7 steps PASS**, exit 0, console.log empty (pid 32580 port 33475, stopped). The official `qa/live-e2e/` folder was not written.
- Credential gate (`credential_sweep.py --staged`, unpiped, from the project root) exit 0 before each of the four code and doc commits.

### What the user will notice
- A double click, triple click or double tap anywhere on "Add person" adds exactly one person, focus is in that person's name field and the draft's id counter moves once. Before, on the right 44 px of the button (about a quarter of its width at 390 px) it added a person and removed it again, and focus stayed on the previous name.
- "Add item" looks and acts the same. A repeat press on it no longer reaches the page, which nothing on screen shows.
- Nothing else on screen changed: the fidelity gate is at 0 pixels. The rest is tests and documents.

### What went beyond the letter of a ruling (reversible, for the orchestrator)
1. **RG-CR-02 got both fixes the finder offered, not one.** The ruling said "or". The three lifetime tests watch the presses as well as the clicks, and a real-gesture word-select test pins the same lifetime from the user's side. Revert: delete `test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word` (M1 stays killed by the other three).
2. **Dated notes on R12 and R30, and a new judgment call 20 in BUILD.md**, none named in the rulings. R30's sentence about who shares the guard became incomplete, and R12 gained the Add item behaviour. Call 20 records why the Add item tests watch the page body.
3. **RG-CR-04 item 1 names a range, not "three".** The finder's fix was "the three after it", which my own new word-select test makes four, and a count in a comment is a claim that rots (constitution 6).
4. **The SEC-01 header comment in `test_app.py`** said the guard cancels the repeat presses "whatever is under them"; it now adds "once the click that moved the layout has armed it".
5. **The fidelity run folder is committed** with this evidence, as the earlier runs' folders are.

### What changed, for the README reconcile (symbols, not lines)
- `src/ui/people.js` `createPeople` and `src/ui/items.js` `createItems`: the Add person and Add item click handlers call `swallowRepeatClicks()` before `onAdd()` (they were `onAdd` itself).
- `src/ui/dom.js` `swallowRepeatClicks`: behaviour unchanged, JSDoc rewritten (armers: every Remove, Add person, Add item, the dialog's open and close; it protects only what arms it; Dismiss note is the measured exception).
- `src/errors.js`: header comment only.
- README lines to touch (the orchestrator's): the test counts (312 browser becomes 421, about 120 s); the `commit` sentence (RG-CR-03 item 2); the `src/errors.js` sentence (item 3); the `swallowRepeatClicks` bullet, which says the press "never lands on the control that moved under the pointer" and lists only the dialog and the Remove buttons as armers: Add person and Add item arm it now, and a control that moves rows without arming it is not covered (Dismiss note is the measured exception).
- Tests (`tests/browser/test_app.py`): `RECORD_BODY_CLICKS_JS` now also records `window.testBodyPresses`; new helpers `seen_by_the_page`, `WHOLE_DOUBLE_CLICK`, `people_bill`, `items_bill`, `bill_after_one_add`, `press_point`; new tests `test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it` (72 rows), `test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page` (36 rows) and `test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word`.

### Observations (not fixed, outside the rulings)
- Two layout-moving controls still do not arm the guard: Dismiss note (measured, its repeat press lands on a heading or a div) and the two mode labels (UI-only focus drop, accepted since the audit). Unchanged.
- RG-CR-05 (the guard's derivation restated in many places) got one more place to keep true: the list of armers is now in the `dom.js` JSDoc, the spec notes of R6, R7, R12, R30 and the Threat model row, BUILD.md (code map, calls 18 and 20), qa.md and the README bullet. Accepted by ruling, so left.
- The browser suite takes about 120 s (it took about 89 s). The 108 Add rows are the cost. One item count instead of two, or the centre rows of the Add item test, could go if the time matters.
- A real mouse's operating-system click count was reasoned about and not measured, as in the audit and the re-check. `gesture_at` says only what Playwright sends.
- The mutants were applied in a scratch copy and rebuilt from the project on every run, so the finder's `mutant-files/` were not reused (they replace whole files and would have dropped the new Add handlers).

### Process note
One command (the probe run) used shell redirection against the hard rule, and made `probe-unfixed.txt.tmp` in the evidence folder; I removed it (the probe's JSON holds the same data). Everything else was made with the Write or Edit tool or by the scripts in the evidence folder. No heredoc, no `sed -i`, nothing written outside my evidence folder except the files the commits name and the fidelity run folder.

PROCESSES: none alive that I started. Every server (the project suite runs, the scratch runs, the probes, the fidelity run and the live gate) was started and stopped by the rig or by its script, each with `STOPPED ... exited True, port free again True`; pids and ports are in `evidence.md` and in each `run-*.txt`.

## Re-check (2026-10-09)

**FAIL. 1 BLOCKER, 0 WARNING, 0 INFO.** RG-CR-01, RG-CR-02, RG-CR-04 and the README hold as fixed. The hunt for a second unarmed path
found one: a double press on a "who had it" chip under a pending price error removes the item (RG-CR-08), the same regression class
as RG-CR-01, so RG-CR-01's fix does not close the class.

Role: code-review finder, scoped re-check (read-only). Start HEAD `a6cbbf8`. Scope as ordered: RG-CR-01 as fixed (`e30b015`) and a hunt
for the fix's own defects, RG-CR-02 (`17ac1ed`), RG-CR-04 and the RG-CR-03 wording (`38686c0`, `f0ca022`), README after `a6cbbf8`.
Accepted and not re-filed: RG-CR-05, RG-CR-07, H-02, SEC-03, SEC-04, two tabs, same-origin read and framing. Evidence:
`docs/modules/split-app/qa/regression-recheck/20261009-230750/` (`evidence.md` indexes every script and output). Project `src/` and
`tests/browser/` were not written (SHA-256 of every file before and after each batch: equal).

### BLOCKER

#### RG-CR-08: A double press on a "who had it" chip under a pending price error removes that item   (bug, regression of 071577a, contract-drift against R7 WR-01)
- **File and symbol:** `src/ui/items.js` `createItems` > `createRow`: `remove.addEventListener("click", () => { swallowRepeatClicks(); onRemove(id); })`.
  Same shape in `src/ui/people.js` `createPeople` > `createRow` (not reachable by this path today, see Reach). The guard's input is
  `src/ui/dom.js` `isRepeatClick`, file-private since `071577a`. The layout move comes from `src/ui/field-error.js` `createErrorSlot`
  (`host.append(paragraph)` inside `div.item-line`), timed by `src/ui/field-leave.js` `onFieldLeave` (RD-3, a blur caused by a press waits for `mouseup`).
- **Issue:** Before `071577a` each Remove handler ignored any click with a count above 1, armed or not (`if (!isRepeatClick(event)) onRemove(id)`).
  Since it, a Remove acts on every click that reaches it and relies on an earlier Remove, Add or dialog click having armed `swallowRepeatClicks`.
  RG-CR-01 closed one unarmed path (Add person). A price error is a second one, and no click can arm for it. With focus in a price field that holds
  invalid text, the first press of a double click, triple click or double tap on a chip blurs the field. RD-3 holds the blur until `mouseup`, the error line
  appears in the item's own `item-line` and pushes the item's chips (and every later item) down by one line, and the click on the chip toggles the person.
  The repeat press then lands on what was a line higher. For a chip in the first chip row whose x range meets the Remove button's, that is the item's own
  Remove, whose handler arms a guard and removes the row. The pressed control was a chip, which arms nothing, so no guard was outstanding. The whole item
  goes (name, price, who), silently, with no undo. R7's WR-01 note says "the second click of a double click or double tap on a remove button is ignored ... One row goes,
  not two" and adds "The same holds for R12". That holds only when something armed the guard.
- **Proof (run, not read):** `probe_toggle_remove.py`, 240 configurations (3 name sets x people 3 to 12 x widths 360, 375, 390, 412, 600, 768, 1024, 1280), by-item
  S1 bill, Item 1 price holds `abc` with focus. Scan of every 4 px point of every chip for what lies under it once the error shows, then the real
  `mouse.dblclick` at the first point that lands on a Remove, and a single click at the same point as control:

  | Tree | Layouts where a chip point lands on its own item's Remove | Real double click removed an item | Single click removed an item |
  |---|---|---|---|
  | `61c3cd3` (before the delta) | 96 of 240 | **0 of 96** | 0 of 96 |
  | `a6cbbf8` (HEAD) | 96 of 240 | **96 of 96** | 0 of 96 |
  | HEAD plus the fix below | 96 of 240 | 0 of 96 | 0 of 96 |

  Concrete repro: viewport 390 x 3000, by-item bill with Aisyah, Ben, Chen, Devi, Farid and the four S1 items, type `abc` in "Item 1 price in RM" and leave focus there,
  `mouse.dblclick(329.5, 577)` (the Farid chip of item 2). Result: "Remove Char kuey teow" gone, 4 items become 3. One click at the same point toggles Farid on item 2 and removes nothing.
  The candidate test `test_rg_cr_08_candidate.py` (6 rows: 375 and 390 px x mouse double, mouse triple, touch double) is **red 6 of 6 on HEAD** and green on the fix.
- **Reach (honest):** it needs a by-item bill, an invalid amount still typed in a price field that has focus, and a repeat press on a chip at the right end of the first
  chip row of an item. In an affected layout the points that land on a Remove are a median 1.4 percent (at most 4.8 percent) of all chip points. Whether a layout is
  affected depends on how wide the chips are:

  | Names | People counts that lay a chip over the Remove, by width |
  |---|---|
  | `P1` to `P12` | 360, 375: 6 or more. 390, 412: 7 or more. 600, 768: 10 or more. 1024: 9 or more. 1280: 10 or more |
  | Aisyah, Ben, Chen, Devi, Farid, Grace, Hafiz, Indra, Jia Hui, Kumar, Lina, Mei Ling | 375, 390: 5 or more. 1024: 7 or more. 1280: 8 or more. None at 360, 412, 600, 768 |
  | 12 longer names (Muhammad Aiman, Nur Aisyah Binti, ...) | 360, 375, 1024: every count from 3. None at 390, 412, 600, 768, 1280 |

  Person Remove buttons are above every price field, so no price error moves them. Dismiss note, the other mover the solver measured, puts no control
  under the pointer (see What held, item 1). The same shift can also put a neighbouring chip under a repeat press (a visible, reversible toggle). That was not
  measured and the fix below does not change it.
- **Fix (verified in a scratch copy, `FIXA` in `run_mutants.py`):** restore the old count test as a backstop at the sink, next to the guard. The guard still cancels the
  repeat press for the armed paths (it also protects Add person, which has no count test).
  ```js
  // src/ui/dom.js
  export const isRepeatClick = (event) => event.detail > 1;   // was file-private
  // src/ui/items.js and src/ui/people.js (createRow), and add isRepeatClick to the import from "./dom.js"
  remove.addEventListener("click", (event) => { swallowRepeatClicks(); if (!isRepeatClick(event)) onRemove(id); });
  ```
  With it: real double click removes 0 of 96, single click 0 of 96, full suite 427 passed (421 plus the 6 candidate rows) in 121.73 s, and the 218-test repeat-press
  selection (R6, R7, R12, R29, R30, R34) is still 218 of 218. The people handler gets the same line for one rule, though no known path reaches it.
  Add the candidate test (it finds the point on a scout page where the price is bad, then presses on a second page) next to the SEC-01 block.
- **Docs this refutes (update with the fix):** BUILD.md judgment call 18 ("The one candidate is a double click on 'Dismiss note'", "'Dismiss note' is the measured exception"),
  spec R7 (the RG-CR-01 correction names "Dismiss note" as the one control that moves rows and does not arm), the spec Threat model row "The bill, as the user left it"
  (same sentence), `swallowRepeatClicks` JSDoc in `src/ui/dom.js` ("a new one must" arm it, which cannot be done for a layout move that is not a click), and the BUILD.md code map
  and call 18 (`isRepeatClick` file-private). Say that a Remove ignores a repeat press itself and that the guard covers everything else.
- **Severity:** BLOCKER by the rule the orchestrator applied to RG-CR-01 (a regression of verified behaviour, `61c3cd3` was safe) and because it destroys typed data.
  It is narrower than RG-CR-01 (the reach table). Under the stop rule the orchestrator may rule it an accepted limit instead. Then the README "Known limits" table, the
  spec Residual risks and the ledger need a row, and the candidate test is not added. I do not recommend it, the fix is two lines and verified.

### What held

1. **RG-CR-01 as fixed (`e30b015`).**
   - The finder's `probe_add_double.py`, unchanged, on HEAD: 96 rows (3 sizes x 4 starting counts x 4 gestures x 2 places). All 96 add exactly one person, focus on `Person N+1 name`,
     `nextId` +1. The 36 right-edge repeat rows that were 0 of 36 on the shipped tree are 36 of 36. Centre rows and single clicks as before.
   - Hunt for a swallowed deliberate action, `probe_hunt.py`, 40 cases, 0 failed. Add person by keyboard (Enter and Space, mixed, 3 to 12 people): 9 of 9 add exactly one with
     focus on the new name. Add item by keyboard x6: 6 of 6. Tab + Enter on the new Remove while guards are outstanding: removes one person (a key click has count 0).
     After the 9 keyboard adds a mouse click on a Remove removes one and a double click on a name selects the word. A click of its own (count 1) on the new name field then typing
     keeps the text, and a click of its own on the new Remove removes that row, for Add person and Add item at the right edge and the centre (12 of 12). A click on the "By item"
     label straight after Add switches the mode. Type then double click the first and the second word after Add by mouse and by keyboard, people and items: 8 of 8 select a word
     (Windows Chromium includes the trailing space, `'Siti '`). A repeat press on the 12th person and the 50th item, three gestures x two places: 12 of 12 add one with focus on the new name.
     Remove, Add, then a double click on Add person adds exactly one (S2, S3).
   - By code: at most one guard is outstanding even for keyboard-only use. A key-activated click (count 0) is not a repeat, so the older guard removes itself in the capture phase before the
     new click arms another. A re-click at the same pixel inside the system double-click time is a repeat press by definition and is cancelled. It has no data effect, the new name field
     is already focused (R34) and empty. Clicks at another pixel have count 1 and pass.
   - Unarmed movers. **Dismiss note**, `probe_unarmed.py` part A: the whole 44 px button (9 points) at widths 320 to 1280 step 20, heights 568 and 844, with 2, 3 and 5 people: 2646 points,
     1038 `div`, 726 `h2`, 648 `section`, 234 `main`, **0 controls**. The solver measured the centre only, the claim holds for the whole button. A real double click leaves the bill as a single click
     does and focus on `BODY` (`probe_claims.py`, 3 sizes). **Mode labels**, part B: 108 repeat-gesture rows (2 bills x 3 sizes x 2 labels x 3 places x 3 gestures), 108 leave the same stored bill
     as one click, focus on `BODY`. Field-error shift: RG-CR-08.
2. **RG-CR-02 as fixed (`17ac1ed`).** Selection R6, R7, R12, R29, R30, R34 (218 tests), scratch copy per run, one in-memory replacement:

   | Mutant | Change | Result |
   |---|---|---|
   | BASE | none | 218 of 218 pass |
   | M1 | the removal pair removes `click` twice, the `mousedown` listener leaks | **4 red**: the R7, R29 and R30 "guard ends" tests and `test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word` |
   | M2 | the `click` listener leaks | 3 red (the three "guard ends" tests) |
   | M9 | no `mousedown` listener registered (press side gone) | 124 red (R6 36, R7 36, R12 36, R29 9, R30 3, R34 4) |
   | M10 | no `click` listener registered (click side gone) | 116 red (R6 36, R7 22, R12 36, R29 9, R30 13) |
   | A1 | Add person arms nothing | 36 red, all of them right-edge rows of the R6 test |
   | A2 | Add item arms nothing | 36 red, every row of the R12 test |

   M1 was 106 of 106 green before and is red now. The tests pin the press side (M9) and the click side (M10) each by more than a hundred rows, and the lifetime of each listener separately (M1, M2).
3. **RG-CR-04 and the RG-CR-03 wording.**
   - `src/errors.js` header: `newErrorFlags`, `flagsFor`, `visibleErrors` are pure, `typedInto`, `leftField`, `forgetPrice` mutate the flags they are given and return nothing. True.
   - `gesture_at` docstring: a triple click is presses 1, 2, 3. Measured (`probe_claims.py`): the document saw `mousedown [1, 2, 3]` and `click [1, 2, 3]`. True.
   - qa.md: the SEC-01 comment names a range ("the tests after it in the same section of `test_app.py`, up to the RG-CR-01 header") and the section holds the four tests the
     solver names (R34 after a double click, a separate click, guard ends, word select). The RG-CR-01 outlines match the tests (people 2 to 5, items 1 and 4, three sizes, three
     gestures, two places: 72 + 36 rows). The I-1 comment "9 rows and the three after it" is still right. True.
   - BUILD.md: Status says what happened. Test counts: 312 + 72 + 36 + 1 = 421, "about 120 s" (120.74 s measured), fidelity `qa/fidelity/20261009-225850/` 10 of 10 at 0 px (`run.log`),
     live gate `live-gate-check/` `summary.json` result PASS, 7 steps, `failure` null. Call 20: A1 reds the right-edge rows only (36), A2 reds all 36 rows of the Add item test, M1 stays killed by the
     other three. Code map: `commit` takes the bill an action returned, saves, restates the status, renders. True. **Call 18 is refuted in part by RG-CR-08** (above).
   - Spec R6 (id counter moves once, focus on the new name), R12 (Add item arms the guard, the body sees press 1 and click 1 only), R30 (the guard is shared with Add person and Add item): true against
     the code and A1, A2. R7 and the Threat model row: the list of armers is true, the statement that Dismiss note is the exception is true but incomplete (RG-CR-08).
4. **README.md after `a6cbbf8`.** Status row "closed 2026-10-09" agrees with ledger row 50 and STATE.md. "At v1.0.0, 421 browser tests and 275 unit tests pass": measured below. The `commit` sentence matches
   `commit(next)` in `src/main.js` (the caller runs `commit(addPerson(bill))`, `commit` saves and renders). The `src/errors.js` sentence matches the code. "Known limits": the reasoning sentence names
   the ledger, `spec.md` (Residual risks, the heading exists) and `findings/security.md` (lines on the mode-label focus drop), and the Dismiss note / mode label row is true (no data change, focus on the body, measured above).
   `billCharges` is the exported function (`applyRate` is private to `result.js`) and "service charge and then SST on top" matches its code. The clipboard sentence matches `rig.new_context(clipboard=...)`
   (recorder, reject, missing). The backdrop sentence matches `createDialog`. The `swallowRepeatClicks` bullet names the armers exactly as the code has them and says it protects only the controls that arm it.
   Commands run once: `node --test "tests/**/*.test.js"` **275 pass, 0 fail**. `python -m pytest tests/browser -q -p no:cacheprovider` **421 passed in 120.74 s** (rig server pid 53972, port 1143, stopped by the rig).
   If RG-CR-08 is fixed the bullet needs one clause (a Remove also ignores a repeat press itself), nothing else in the README changes.

### Processes
PROCESSES: every server was the rig's `python -m http.server` on a free loopback port with headless Chromium, started and stopped by the rig or by the script that started it, each printing `STOPPED ... exited True, port free again True`
(pids and ports are listed in `evidence.md`). My pytest batches ran as subprocesses of `run_mutants.py`, which waited for each. The only thing left running at the end was a `python -m http.server 53410` (pid 44864) that serves the
Streaks app of the sibling project. I did not start it and did not touch it. I checked with `Get-CimInstance Win32_Process` by command line (`http.server`, `chrome-headless-shell`, `pytest`, `probe_`, `run_mutants`, `playwright`), and
the title of that server's page.

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

## ORCH ruling on solver round 2 (2026-10-10)

**Code review closes for v1.0.0, status pass.** Under the stop rule set on 2026-10-09 no further code-review round runs. RG-CR-08 is
closed on the solver's proof, which uses the re-check's own instruments unchanged. The probe `probe_toggle_remove.py` (same SHA-256 as
the re-check's copy) pressed the same 240 configurations and the real double click now removes 0 of 96 affected layouts, against 96 of 96
on `a6cbbf8`. The re-check's candidate test, brought into the suite as six rows, is red 6 of 6 on the unfixed `src/` and green after.
Mutant B1 turns exactly those rows red. B2 (the people Remove without the count test) is noticed by no test, as the re-check said no
known path reaches it. That is recorded, not a gap to fill now. Suites 427 browser and 275 unit, fidelity 10 of 10 at 0 px
(`qa/fidelity/20261010-123651/`), live gate check 7 of 7. The regression QA finder and the official cold boot run next and decide the
regression verdict.
