# Solver evidence: split-app, code-review batch of 2026-10-09

Role: Dev Solver. Start: HEAD `044800e`, browser suite 205 passed, unit suite 265 passed (run before any change).
End: HEAD `7edfe0b` plus the docs commit that holds this folder; browser suite 244 passed, unit suite 275 passed
(`junit-browser.xml`, `junit-node.xml` in this folder). Every context came from `rig.new_context` (clipboard recorder on, no
permission, no `bypass_csp`). The operating system clipboard was never touched.

How each proof was made: the new test was run on the shipped code first (red), then the fix was made and the same tests run
again (green). For a finding that is a test gap, the surviving mutant of the review was applied by hand with the Edit tool to the
file named in `01-mutants.md`, the new test was run (red), and the mutant was reverted (checked with `git diff --quiet -- src`
before every commit). Before each commit the full browser suite and the unit suite ran, and the credential gate
(`credential_sweep.py --staged`, unpiped) exited 0.

## CR-01 and QA F-1, commit `d09d8d6`
- Tests added (14): `test_R30_a_double_click_or_double_tap_on_cancel_changes_nothing` (3 phone sizes x mouse and touch),
  `test_R30_the_second_click_of_a_double_activation_never_reaches_the_page` (Cancel, Start new bill, backdrop x mouse and touch),
  `test_R30_a_triple_click_on_cancel_changes_nothing_either`, `test_R30_a_single_click_closes_as_before_and_the_next_double_click_is_not_held_back`.
- RED on the shipped code: 13 failed, 1 passed (the single click guard test). The 6 size cases failed with the draft changed
  (`who` of "Nasi lemak ayam" gained `p3`) and focus on "Chen". The body-click recorder showed `[1, 2]` for all six target cases
  and `[1, 2, 3]` for the triple click. Screenshots of the red state: `red-cr01-screenshots/`.
- The review's guard as ruled, a one-shot capture listener on `click` only: 4 failed, 10 passed. The 3 touch size cases
  still failed (the second press, a `mousedown`, took focus: "Chen" instead of "New bill") and the triple click leaked its third
  click (`[1, 3]`). So the guard cancels the repeat `mousedown` as well, and it stays armed until the first press that is not a
  repeat (`isRepeatClick`, no timer). This extends the ruling slightly; see the report.
- GREEN: 14 passed. Mutant "guard never disarms" fails `..._the_next_double_click_is_not_held_back` (1 failed, 13 passed).
- Wider check on the fixed code, `scan_f1_double_activation.py`: 4 bills x 16 viewports (320x568 to 1280x800) x mouse and touch x
  Cancel, Start new bill and backdrop = 384 cases. Baseline sources (`044800e`): 202 of 384 fail (the draft changed, or focus left
  "New bill"). Fixed code: 0 of 384 fail.
- Full suites: browser 219 passed, unit 265 passed.

## WR-01, commit `9636e84`
- Tests added (6): `test_R7_a_double_click_or_double_tap_on_remove_removes_one_row` (item 2 of 4, person 2 of 5, mouse and touch),
  `test_R7_two_separate_clicks_and_a_key_press_still_remove_a_row_each` (2 cases).
- RED on the shipped code: the 4 double cases failed (`items left 2` instead of 3, `people left 3` instead of 4), the 2 others passed.
- GREEN: 6 passed. Full suites: browser 225, unit 265.

## WR-06, commit `5f5d4d9`
- Tests added (3): press on the dialog text and release on the backdrop keeps the dialog open; press on the backdrop and release
  in the dialog keeps it open; a touch tap on the backdrop still acts as Cancel.
- RED on the shipped code: the first failed (dialog closed), the other two and the existing backdrop tests passed.
- GREEN: 7 passed, and the dialog set (R29, R30, R31, R35) stayed green. Full suites: browser 228, unit 265.

## WR-03, commit `e1d9ee7`
- Tests added or changed: `test_R10_a_press_that_ends_runs_each_waiting_handler_once` (K2), the keyboard-blur test gains a `held`
  case (K3), `test_R10_a_secondary_button_press_does_not_hold_the_error_back`, `test_R10_a_cancelled_press_releases_the_waiting_error`.
- RED: the secondary-button test failed on the shipped code (the error waited for the release). Mutant P1 (`waiting.slice()`, queue
  never emptied): K2 fails. Mutant P56 (`pointercancel` and `keydown` ends removed): the `held` case and the cancelled-press test
  fail. Mutant "only `pointercancel` removed": the cancelled-press test fails.
- GREEN with the `event.button === 0` guard in `field-leave.js`: all pass. Full suites: browser 232, unit 265.

## WR-02, commit `2408d40`
- `tests/errors.test.js` (10 unit tests) and `test_R10_a_cleared_error_does_not_come_back_until_the_field_is_left_again` (K1, 4 rows).
- RED: mutant A1 (clear only on empty): 2 unit tests fail and the 4 K1 rows fail. Mutant A2 (never clear): the same. Further mutants
  of `src/errors.js`: `typedInto` always clears, `visibleErrors` ignoring `isBad` for a price, `forgetPrice` doing nothing: 1 unit
  test fails for each.
- GREEN on the shipped file: 10 of 10 unit tests, 4 of 4 K1 rows. Full suites: browser 236, unit 275.

## WR-04, commit `eae083c`
- Added to `tests/draft.test.js`: D10 against an item id (and the control that `nextId` 4 is accepted), and a line feed and a
  carriage return in an item name (and the control that "Tea" is accepted).
- RED: mutant D(B) (`highest` over people only): the D10 test fails. Mutant D(C) (item name without the line break rule): the D8
  test fails. GREEN on the shipped decoder: 11 of 11 in the file.
- Spec: dated residual note that D8 sets no UTF-16 ceiling.

## WR-05, commit `7bdc368`
- Added: `test_R30_a_click_inside_the_dialog_box_keeps_it_open`, `test_R3_the_note_matches_its_specimen`,
  `test_R3_the_open_dialog_and_the_page_behind_it_match_their_golden`, and the `remove-person` and `remove-item` rows of the R25 table.
  `dom_walk` and `golden_walk` take an optional selector.
- RED: mutant J (no box test): the click-inside test fails. Mutant LIVE2 on the note (`aria-live` on the wrapper, `aria-pressed` on the
  dismiss button): the note walk fails. Mutant LIVE2 on the dialog (`aria-live` set on opening): the dialog walk fails. Mutant RM on
  items (`bill = removeItem(...); render();`): `remove-item` fails. The same for people: `remove-person` fails.
- GREEN on the shipped code. Full suites: browser 241, unit 275.

## WR-09, commit `d0aca98`
- Dead branches of `el` and `setAttr` removed; the re-check after the await in `copySummary` removed; seed S8 kept (qa.md ST-08 names it)
  and booted by `test_R6_a_restored_twelve_person_bill_shows_the_limit_state`. New test
  `test_R24_a_copy_that_finishes_after_the_table_left_sets_no_status` pins the rule the deleted line was thought to guard.
- Proof the deletion changed nothing: the suite is green before and after. The new test has teeth: with the status reset removed from
  `render()` it fails (2 failed: it and `test_R24_the_status_lives_as_long_as_the_table`).
- Full suites: browser 243, unit 275.

## WR-10, commits `842af5a`, `dafeef4`, `138904e`, `14f8d3e`
- `amountTyped` and `amountLeft` replace the six handlers: green before and after (browser 243).
- `setStatus` is the only writer of `view.status`, `render()` no longer writes the view: mutant "commit does not clamp the status"
  fails `test_R24_the_status_lives_as_long_as_the_table`; mutant "copySummary writes `view.status` directly" fails the late-copy test.
- `block()` replaces four copies of the section scaffold: the R3 walks against the goldens stay green.
- `tests/browser/expected.py` replaces the hand-kept copies in `test_app.py` and `live_e2e.py`; the equality test is gone. The live
  gate was run with the refactored script into `live-gate-check/20261009-195308/`: 7 of 7 steps PASS, exit 0.

## WR-11, commit `b73c9fe`
- The press test now compares the error text to the one exact message of its case. Mutant "the subtotal shows the SST text": the 2
  subtotal rows fail (the old test accepted any of the three texts).
- `run.py` takes `SDLC_HARNESS` (blank counts as unset) with the plugin path as default; `test_R40_the_runner_takes_the_harness_from_the_environment_and_has_a_default`
  checks `harness_path` and `DEFAULT_HARNESS`, not a copy of the literal. `SDLC_HARNESS=Z:/nowhere/fidelity.py python tests/browser/fidelity/run.py`
  exits 1 with "harness not found ... (set SDLC_HARNESS ...)" and starts nothing.
- The sub-path test keeps serving the parent folder and now says why.

## WR-07, commit `7edfe0b`
- Comment and record changes only: the `git diff` of `src/` in that commit has no changed line outside a comment. Browser 244, unit 275.

## Fidelity re-run after the refactors
`python tests/browser/fidelity/run.py`: 10 of 10 pairs PASS at 0 mismatching pixels, dimensions equal, evidence
`docs/modules/split-app/qa/fidelity/20261009-200000/` (server pid 28424, stopped).

## Observation, not routed
`probe_dismiss_note.py`: a double click or double tap on "Dismiss note" (360x640 to 1280x800, mouse and touch, 10 cases) never
changed the draft (the second click lands on a heading or a `div`), but the second press moves focus from "Person 1 name" to the page
body, so R27's "focus moves to Person 1 name" does not hold after a double click. No data effect.

## Process note
Once I used a Python heredoc through Bash to apply a throwaway mutant to `src/ui/dialog.js` (against "Write and Edit only"). The edit
was inside the project, was reverted with Edit at once and checked equal to a copy taken before. Every later mutant was applied and
reverted with the Edit tool. Two test runs hung (a test of mine whose `page.evaluate` string evaluated to a function that Playwright
then called and awaited); I killed their process trees by exact PID (pytest 38244 with its server, node and Chromium children; the
scratch script 46148 with its server 51368) and checked that none remained.
