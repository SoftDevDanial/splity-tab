---
module: split-app
kind: qa
ran_against: running-app
status: issues_found
counts: { pass: 165, fail: 1, blocked: 0, not_run: 1 }
date: 2026-10-15
head: d58f4ce
regression_full_2026_10_16: { status: green, head: 64b882c, counts: { pass: 180, fail: 0, blocked: 0, partial: 1 }, node_run: docs/modules/split-core/qa/unit/20261016-031908/node-test.txt, chromium_run: docs/modules/split-app/qa/functional/20261016-031917-chromium/, webkit_run: docs/modules/split-app/qa/functional/20261016-032255-webkit/, fidelity_run: docs/modules/split-app/qa/fidelity/20261016-033155/, live_gate: docs/regression/20261016-032500/cold-boot.md }
node_run: docs/modules/split-core/qa/unit/20261015-204618/node-test.txt
chromium_run: docs/modules/split-app/qa/functional/20261015-204624-chromium/
webkit_run: docs/modules/split-app/qa/functional/20261015-205019-webkit/
live_gate_runs: docs/modules/split-app/qa/live-e2e/20261015-205837-chromium-control/, 20261015-205844-chromium/, 20261015-205925-webkit-control/, 20261015-205931-webkit/, 20261015-205954-chromium/
accessible_description_run: docs/modules/split-app/qa/accessible-description/20261015-205800/
---
# QA findings: split-app (v1.1.0, step 5)

> Newest verdict is the section "v1.1.0 regression --full, 2026-10-16" at the end of this file. It is green for the QA lane and closes QA-S5-1, QA-S5-2 and QA-S5-3. The step 5 text below is kept as the record of that run.

**Verdict: ISSUES.** 165 of 167 qa.md scenarios pass, 1 fails (QA-S5-1), 1 is not run (the fidelity pixel gate, out of this finder's lane). No browser test failed in either engine. The one fail is a scenario with no test behind it, not an app defect.

Run by the QA finder (read-only) on 2026-10-15 at HEAD `d58f4ce`. `git diff --stat HEAD` on `src/`, `index.html`, `tests/`, `docs/design/` and both `spec.md` and `qa.md` files is empty. `src/system.css` hashes to `bf30ddadb8c756dc5d462243c642c218597ae0ac` (git) and to SHA-256 `66807273...3c08` after CRLF to LF, 33070 bytes, equal to `docs/design/system.css` (qa.md R1). Every run below is fresh, in its own new timestamped folder.

| Run | Result | Against the A20 baseline on the same code |
|---|---|---|
| Node `node --test "tests/**/*.test.js"`, `docs/modules/split-core/qa/unit/20261015-204618/node-test.txt` | 379 of 379, 0 fail, 0 skipped | A20 `qa/unit/20261015-202558/`: 379 of 379 |
| Chromium 149.0.7827.55, `python -m pytest tests/browser -q`, `qa/functional/20261015-204624-chromium/` (`pytest.txt`, `junit.xml`, `skips.txt`, `stdout.txt`, `R50-sheet-closed-at-1024.txt`) | 707 passed, 0 failed, 0 skipped, 219.9 s | A20 `20261015-202607-chromium/`: 707 passed. By id: 707 ids in both, 0 only in one, 0 with a different outcome |
| WebKit 26.5, `python -m pytest tests/browser -q --engine webkit`, `qa/functional/20261015-205019-webkit/` (`pytest.txt`, `junit.xml`, `skips.txt`, `stdout.txt`, `icon-colour.txt`, `R50-sheet-closed-at-1024.txt`) | 705 passed, 2 skipped, 0 failed, 430.6 s. No failure screenshot was written | A20 `20261015-202952-webkit/`: 705 passed, 2 skipped. By id: 707 ids in both, 0 only in one, 0 different. `skips.txt` is identical to the baseline's (R33 IME and R40 after-load, each with its reason) |
| Live gate, Chromium, control then green on one server (port 53462) | control RED at step 1, green 9 of 9 | A20 `20261015-202120-chromium-control/`, `-202122-chromium/`: same figures |
| Live gate, WebKit, control then green on one server (port 31316) | control RED at step 1, green 9 of 9 | A20 `20261015-202153-webkit-control/`, `-202154-webkit/`: same figures |
| Live gate, bare `python tests/browser/live_e2e.py` (serves itself) | 9 of 9, folder ends `-chromium` | A20 `20261015-202220-chromium/` |

Pytest ran with `SPLIT_EVIDENCE=1`. The two runs were one after the other, never together. The by-id comparison used `junit.xml` classname and test name, parametrized ids included.

## Findings
| id | R# | verdict | what I saw | capture |
|---|---|---|---|---|
| QA-S5-1 | R9, R11 | FAIL (Medium, a missing test, not an app defect) | The scenario "The accessible description of the amount fields is measured and reported" (`@chromium_only`, qa.md line 2002) has no test. `grep` for `accessible-description` and `getPartialAXTree` in `tests/` finds nothing, and neither the A20 Chromium run folder nor my own holds `accessible-description.txt`, which the Then line puts in the run's evidence folder. ROADMAP orchestrator action 9 (report CG-P6 to the owner) depends on that file. To close the gap I ran the measurement myself through CDP, see QA-S5-5 for the four lines. Route to the Dev Solver, to add the Chromium test that writes the four lines into the suite's evidence folder. | `docs/modules/split-app/qa/accessible-description/20261015-205800/accessible-description.txt`, `ax_probe.py`, `probe-out.txt` |

**Solver, QA-S5-1, 2026-10-15 (dev solver, step 5 round). RESOLVED in `0094f40`.** New `test_R9_the_accessible_description_of_the_amount_fields_is_measured_and_reported`, marked `chromium_only` with the scenario's reason. It reads the computed description of "Char kuey teow price in RM" (K1) and Subtotal (K2) through CDP `Accessibility.getPartialAXTree`, as loaded and after "13.505" and "0" and Tab, writes the four lines to `accessible-description.txt` in the run's evidence folder and asserts only that the four exist, each naming the field and the error state read from the page. RED on a stub that never left the field: `docs/modules/split-app/qa/functional/20261015-234237-chromium/red.txt`. GREEN `docs/modules/split-app/qa/functional/20261015-234248-chromium/` (the four lines equal this finder's own measurement), and a counted skip with its reason in WebKit, `20261015-234251-webkit/skips.txt`. The full suite runs of the round each write the file again (BUILD.md, "v1.1.0 step 5 solver round").

Observations. They change no verdict and no Then line is broken by them.
- **QA-S5-2.** In both control runs the failing assertion line reads `got 'Total\nRM 116.60'` for the strip (a line break between the two parts, from `innerText`), where the scenario text writes "Total RM 116.60". The green runs pass the same read at step 2. A20 already noted this. Capture: `qa/live-e2e/20261015-205837-chromium-control/steps.log`, `20261015-205925-webkit-control/steps.log`.
- **QA-S5-3.** qa.md writes `browser.version` for `summary.json`. Every gate run (these five, A20's, and the A0 runs of 1.0) records the flat key `browser_version`. Wording only. Capture: `qa/live-e2e/20261015-205844-chromium/summary.json`.
- **QA-S5-4.** WebKit's screencast frames of the Splits sheet show the page behind it faintly through the glass (`20261015-205931-webkit/03-splits-sheet.jpg`, `04-one-person.jpg`), and frame `06-by-item.jpg` shows a focus ring on the Splits button after the sheet closed. The Chromium frames (`20261015-205844-chromium/03-splits-sheet.jpg`, `06-by-item.jpg`) show neither. No scenario asserts either, `system.css` uses `backdrop-filter` for the glass, and the fidelity gate is Chromium only. Worth a look on a real iPhone at UAT.
- **QA-S5-5 (the CG-P6 measurement, for the owner).** Chromium, CDP `Accessibility.getPartialAXTree`: the Char kuey teow price field and the Subtotal both have the computed description "Enter an amount like 12.50" with the error hidden and again after "13.505" or "0" and Tab (the error shown). The hidden error paragraph is named by `aria-describedby` at all times (`ie2`, `evenErr`), as the goldens do, so the hint text is read before any error shows. VoiceOver and TalkBack were not measured (UNVERIFIED, a device check). Capture: `qa/accessible-description/20261015-205800/accessible-description.txt`.

## Not run
- **#86 "Looks right" (`@R40 @gate`, line 1197).** The fidelity pixel gate and the FE element checklist are not this finder's. A19 ran the gate (`docs/modules/split-app/qa/fidelity/20261015-193738/`, per the handoff, not re-run here) and the fidelity finder takes the checklist. No verdict from me.

## The `@R41 @gate` scenarios, judged on the live runs
All five folders below were listed on disk after their runs. Each `summary.json` was read, each `steps.log`, and the frames were viewed.

| Run folder | summary.json | steps.log | Captures |
|---|---|---|---|
| `qa/live-e2e/20261015-205837-chromium-control/` (files `01-cold-boot.jpg`, `console.log`, `network.log`, `steps.log`, `summary.json`) | `control` "seeded", engine chromium, `browser_version` 149.0.7827.55, `pass` false, `steps_run` 1, `first_failing_step` 1, `storage_state` the K2 bill, `bypass_csp` false, `control_red_on_its_property` true | Step 1 FAIL. PASS on the stand-in line ("the clipboard stand-in is in place, writeText is not native and nothing was written"), so the RED comes from the cold boot. FAIL on names, removesDisabled, subtotal, open (got false, false, false), card, totalHolds, emptyIcon, strip, stripCopy and `split.draft is absent` (got the K2 draft). | `01-cold-boot.jpg` shows People and Charges folded, "Aisyah, Ben, Chen", Subtotal 100.00, strip "Total RM 116.60", not bill-empty |
| `qa/live-e2e/20261015-205844-chromium/` | `control` null, `pass` true, 9 of 9, `requests` 90, outside the rule 0, console errors 0, page errors 0, CSP violations 0, `clipboard_writes` 3, `bypass_csp` false, `storage_state` null, the two init scripts only | 9 step lines PASS, 93 assertion lines PASS, 0 FAIL. `console.log` is empty. Every one of the 90 `network.log` lines is a same-origin GET inside the rule (checked by script). `clipboard-s2.txt` is the S2 block and `clipboard-s1.txt` the S1 block, exact | 9 frames `01-cold-boot.jpg` to `09-throughout.jpg`. Viewed 01, 03, 04, 05, 06, 08: bill-empty with People open and the strip "Enter the subtotal to see the splits." (01), the sheet with 38.87, 38.87, 38.86, "2 sen left over", "Adds up to RM 116.60", "Summary copied" (03), P1 with One person, Ben checked and 38.86, 38.88, 38.86 (04), the K1 items and "Total RM 69.26" with "Summary copied" (06), bill-empty again (08) |
| `qa/live-e2e/20261015-205925-webkit-control/` | as the Chromium control, engine webkit, `browser_version` 26.5, `control_red_on_its_property` true | the same 10 FAIL assertion lines and the same PASS on the stand-in | `01-cold-boot.jpg` the K2 screen, not bill-empty |
| `qa/live-e2e/20261015-205931-webkit/` | as the Chromium green, engine webkit, 26.5, 9 of 9, 0 console errors, 0 page errors, 0 CSP violations, 90 requests, 3 writes. No refused-stylesheet line | 9 PASS, 93 assertion PASS, 0 FAIL. `steps.log` equals the Chromium one except the random Pick again draw line. Clipboard texts equal the Chromium ones | Viewed 01, 03, 04, 06, 07, 08, the same screens as Chromium (see QA-S5-4) |
| `qa/live-e2e/20261015-205954-chromium/` (bare run, server pid 3324 port 31423 started and stopped by the script) | `control` null, 9 of 9, `server` "served by this run", same figures | 9 PASS | same frames |

- **#90 Works right.** PASS. Green in both engines, each evidence folder exists and was listed, each green `summary.json` records `"control": null`, and the two control summaries record `"control": "seeded"` with `pass` false, so neither counts as green.
- **#91 control (Outline, 2 rows).** PASS in both engines. Each stopped at step 1 with `pass` false, `steps.log` names the failed assertions, the screen is not bill-empty (data-open false, strip not the empty message) and `split.draft` is present, the stand-in check passed, `summary.json` has `control` "seeded", the engine, the version and `pass` false, the folder ends `-<engine>-control`, holds only its own five files and was never written over.
- **#162 The live gate records its engine.** PASS. `20261015-205931-webkit/summary.json` has engine "webkit" and version 26.5. The bare run's folder `20261015-205954-chromium` is Chromium.
- **#92 and the R41 static tests.** PASS in both engines (test ids in the table).
- Servers. Both shared servers were stopped by exact PID (24688 on 53462, 19616 on 31316) and each port then refused a connection (curl exit 7). The suite runs stopped their own servers (pids 20160 and 22360, each logged "STOPPED ... port free again True").

## Per-scenario evidence notes
- **#161 A Chromium-only test is a counted skip in WebKit.** PASS. The WebKit folder name ends `-webkit`. `skips.txt` lists both skipped tests with their reasons and `count 2`, equal to `junit.xml` `skipped="2"`. The R33 IME test's reason starts "Needs a CDP session". `junit.xml` shows 705 passed and 2 skipped, so no skip counts as a pass. The Chromium folder ends `-chromium`, and its `pytest.txt` has `PASSED` for both `chromium_only` tests (`test_R33_ime_composition_survives_a_render`, `test_R40_an_after_load_script_presses_nothing_without_the_clipboard_stand_in`).
- **#164 The A0 baseline record is complete.** PASS, a record check on disk, no browser run. In `qa/webkit-baseline/20261014-130011/`: `sorting.md` names the WebKit run's own folder `qa/functional/20261014-125604-webkit/` (it holds `pytest.txt`, `junit.xml`, `skips.txt`) and the Chromium folder `20261014-125352-chromium/` (`junit.xml` 430 tests, 0 failures, 427 sealed plus 3 new counted apart), and the 1.0 gate folders `20261014-130326-chromium` and `20261014-130333-webkit`. `probes.json` records `launched_by` "rig.launch", `contexts_by` "rig.new_context", the stand-in before the first gesture, the touch double tap click counts [1, 1], the event order, `isSecureContext` true and `typeof Clipboard` "function", the localStorage redefinition, the CSP and denied-storage console text, `activeElement` after a click on a radio label and on a radio, and the svg `Content-Type` `image/svg+xml`. `sorting.md` accounts for all 48 failed ids of the WebKit `junit.xml` exactly once (5 sorted, 43 touch double taps ruled class (a)), which I recounted from that `junit.xml`.
- **#158, #166, #167 (`@node`).** PASS from the Node run (10 `@R57 b ...` tests, 4 `@R61 D3/D13/D14` tests, 2 save and load tests). The run folder is under split-core's `qa/unit/`.
- **#165.** See QA-S5-1.
- **Counts that match the Examples.** `test_R3_rendered_markup_matches_its_golden` 40 cases (40 pairs), `test_R35_no_horizontal_overflow_in_any_golden_state` 40, `test_R6_a_repeat_press_on_add_person...` 72, `test_R7_a_repeat_press_on_the_last_remove...` 48, `test_R12_a_repeat_press_on_add_item...` 36, `test_R27_an_unreadable_draft...` 32 (B1 to B32). Each is the same in both engines.
- **Static scenarios, my own greps.** No sample name from #4 in `index.html` or `src/`. No `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function`, `srcdoc` or `on*` attribute in either (#79). No `fetch`, `XMLHttpRequest`, `WebSocket`, `sendBeacon`, `EventSource` or absolute URL, except the SVG namespace string `http://www.w3.org/2000/svg` in `src/icon.svg` and `src/ui/icons.js` (#83). All agree with the tests.

## Supporting tests with no scenario row of their own
54 of the 239 test functions (for example `test_R39_clipboard_recorder_keeps_the_text_and_never_reaches_the_system`, `test_R46_the_storage_drivers_do_what_how_to_run_says`, `test_R35_layout_problems_has_teeth`, `test_R48_on_the_desktop_both_sections_show`) back the scenarios above or the harness rules of "How to run". All of them pass in both engines. They are in `junit.xml`.

## Method and limits
A scenario is PASS when the test or tests named for it passed in this run in each engine it names (a `@chromium_only` scenario in Chromium, with the WebKit skip counted), or when I observed the run directly (the gates, the records, the greps, the CDP probe). The scenario to test mapping is by test name (the qa.md rule "functions are named `test_R<n>_<what>`"), checked by similarity and set by hand for 26 scenarios. I did not read each test body against every clause of its Then lines, which is the code review finder's work. `C n/m` means n of m cases passed in Chromium and `W n/m` the same in WebKit.

## Not done
- The fidelity pixel gate and the FE element checklist (not this finder's).
- Any device check (an iPhone or Android phone, a screen reader). See QA-S5-4 and QA-S5-5.
- The README and BUILD.md reconciles (the orchestrator's).

## Scenario table
Columns are the scenario number in order of `qa.md`, the line of its `Scenario`, its tags, its title, the test function (without `test_`) with its cases passed in Chromium (C) and WebKit (W), and the verdict.

| # | line | tags | scenario | tests | verdict |
|---|---|---|---|---|---|
| 1 | 140 | @R1 @both | The entry point loads only its own files | R1_entry_point_loads_only_its_own_files C 1/1 W 1/1 | PASS |
| 2 | 152 | @R1 @both | The page works from a sub-path, as on GitHub Pages | R1_page_works_from_a_sub_path C 1/1 W 1/1 | PASS |
| 3 | 161 | @R2 @both | Cold boot is a new bill with no seed | R2_cold_boot_is_a_new_bill_with_no_seed C 1/1 W 1/1 | PASS |
| 4 | 174 | @R2 @static | No sample data ships | R2_no_sample_data_ships C 1/1 W 1/1 | PASS |
| 5 | 179 | @R3 @both | The rendered markup matches its golden | R3_rendered_markup_matches_its_golden C 40/40 W 40/40 | PASS |
| 6 | 205 | @R3 @both | The walk sees every rendered element and flags each kind of change | R3_the_walk_sees_every_rendered_element_and_flags_each_kind_of_change C 1/1 W 1/1 | PASS |
| 7 | 220 | @R4 @both | Person rows carry their names and labels | R4_person_rows_carry_their_names_and_labels C 1/1 W 1/1 | PASS |
| 8 | 228 | @R4 @R5 @both | A blank name falls back to its position everywhere but the field | R4_a_blank_name_falls_back_to_its_position_everywhere_but_the_field C 1/1 W 1/1 | PASS |
| 9 | 238 | @R5 @both | Renaming a person updates every place on each keystroke | R5_renaming_a_person_updates_every_place_on_each_keystroke C 1/1 W 1/1 | PASS |
| 10 | 252 | @R5 @both | Renaming an item updates its accessible names | R5_renaming_an_item_updates_its_accessible_names C 1/1 W 1/1 | PASS |
| 11 | 259 | @R6 @both | Add person until the limit | R6_add_person_until_the_limit C 1/1 W 1/1 | PASS |
| 12 | 273 | @R6 @both | Removing anyone from twelve turns Add person back on | R6_removing_anyone_from_twelve_turns_add_person_back_on C 1/1 W 1/1 | PASS |
| 13 | 284 | @R7 @both | Remove a person and they leave every item | R7_removing_a_person_takes_them_off_every_item C 1/1 W 1/1; R7_remove_a_person C 1/1 W 1/1; R7_the_item_left_with_nobody_needs_a_person_on_the_card_and_the_strip C 1/1 W 1/1 | PASS |
| 14 | 296 | @R7 @both | A repeat press on the last Remove removes that row and adds nothing | R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing C 48/48 W 48/48 | PASS |
| 15 | 312 | @R34 @both | After a double click or double tap on a middle Remove, focus is where one click puts it | R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it C 4/4 W 4/4; R7_a_double_click_or_double_tap_on_remove_removes_one_row C 4/4 W 4/4 | PASS |
| 16 | 323 | @R7 @both | A press of its own is never held back | R7_two_separate_clicks_and_a_key_press_still_remove_a_row_each C 2/2 W 2/2; R7_a_separate_click_on_the_same_point_is_a_press_of_its_own C 1/1 W 1/1; R7_the_guard_of_a_remove_click_ends_at_the_next_press C 1/1 W 1/1; R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word C 1/1 W 1/1 | PASS |
| 17 | 336 | @R6 @both | A repeat press on Add person adds one person and keeps it | R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it C 72/72 W 72/72 | PASS |
| 18 | 350 | @R12 @both | A repeat press on Add item adds one item and never reaches the page | R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page C 36/36 W 36/36 | PASS |
| 19 | 366 | @R7 @R12 @both | A repeat press on a chip under a pending price error never removes the item | R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item C 6/6 W 6/6 | PASS |
| 20 | 382 | @R42 @both | Two people may have the same name | R42_duplicate_names_are_accepted_and_act_on_their_own_row C 1/1 W 1/1; R42_duplicate_names_through_the_whole_flow C 1/1 W 1/1; R42_the_draft_keeps_both_people_with_the_same_name C 1/1 W 1/1 | PASS |
| 21 | 401 | @R8 @both | Switching modes keeps both sets of input | R8_switching_modes_keeps_both_sets_of_input C 1/1 W 1/1 | PASS |
| 22 | 415 | @R8 @both | Arrow keys move between the modes | R8_arrow_keys_move_between_the_modes C 1/1 W 1/1 | PASS |
| 23 | 422 | @R9 @both | The subtotal field drives the even split | R9_the_subtotal_field_drives_the_even_split C 1/1 W 1/1 | PASS |
| 24 | 431 | @R10 @both | An inline error waits for the field to be left | R10_an_inline_error_waits_for_the_field_to_be_left C 4/4 W 4/4 | PASS |
| 25 | 448 | @R10 @both | An empty field never shows an error | R10_an_empty_field_never_shows_an_error C 1/1 W 1/1 | PASS |
| 26 | 459 | @R10 @both | Typing invalid text in a focused field does not show the error early | R10_typing_bad_text_in_a_focused_field_shows_no_error_early C 1/1 W 1/1 | PASS |
| 27 | 466 | @R10 @both | A restored invalid field shows its error at once | R10_a_restored_bad_field_shows_its_error_at_once C 1/1 W 1/1 | PASS |
| 28 | 473 | @R10 @both | An error survives a mode switch | R10_an_error_survives_a_mode_switch C 1/1 W 1/1 | PASS |
| 29 | 481 | @R10 @R13 @both | A press below an invalid field lands on the control it started on | R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on C 6/6 W 6/6 | PASS |
| 30 | 498 | @R10 @R59 @per_engine | A touch tap on the charges hint below an invalid rate | R10_a_touch_tap_on_the_charges_hint_below_an_invalid_rate C 2/2 W 2/2 | PASS |
| 31 | 512 | @R13 @both | A tap on a person below an invalid, unflagged price toggles them and then shows the error | R13_a_tap_below_an_invalid_price_toggles_that_person_and_then_shows_the_error C 2/2 W 2/2 | PASS |
| 32 | 520 | @R10 @both | The error waits for the release, and only a press holds it back | R10_the_error_waits_for_the_mouse_button_to_come_up C 1/1 W 1/1; R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press C 3/3 W 3/3; R10_pressing_empty_space_also_waits_for_the_release C 1/1 W 1/1; R10_a_press_that_ends_runs_each_waiting_handler_once C 1/1 W 1/1; R10_a_secondary_button_press_does_not_hold_the_error_back C 1/1 W 1/1; R10_a_cancelled_press_releases_the_waiting_error C 1/1 W 1/1 | PASS |
| 33 | 532 | @R11 @both | Item rows carry their names and labels | R11_item_rows_carry_their_names_and_labels C 1/1 W 1/1 | PASS |
| 34 | 542 | @R12 @both | Add an item, remove one, and reach the limit | R12_add_an_item_remove_one_and_reach_the_limit C 1/1 W 1/1 | PASS |
| 35 | 555 | @R13 @both | Tapping a person on an item | R13_tapping_a_person_on_an_item C 1/1 W 1/1 | PASS |
| 36 | 566 | @R14 @both | A price error sits in the item row | R14_a_price_error_sits_in_the_item_row C 1/1 W 1/1 | PASS |
| 37 | 578 | @R15 @both | The Charges block and its defaults | R15_the_charges_block_and_its_defaults C 1/1 W 1/1 | PASS |
| 38 | 588 | @R15 @both | A rate error names the hint first and then its error | R15_a_rate_error_names_the_hint_first_and_then_its_error C 1/1 W 1/1 | PASS |
| 39 | 596 | @R15 @R19 @both | A charge of 0 is allowed and still shown | R19_a_charge_of_zero_is_allowed_and_still_shown C 1/1 W 1/1 | PASS |
| 40 | 605 | @R16 @both | The receipt follows every keystroke and stays quiet | R16_the_receipt_follows_every_keystroke_and_stays_quiet C 1/1 W 1/1 | PASS |
| 41 | 617 | @R17 @both | When the splits cannot be worked out | R17_when_the_splits_cannot_be_worked_out C 8/8 W 8/8 | PASS |
| 42 | 636 | @R18 @both | Items that still need a person | R18_items_that_still_need_a_person C 1/1 W 1/1 | PASS |
| 43 | 649 | @R19 @both | Total and bill lines | R19_total_and_bill_lines C 2/2 W 2/2 | PASS |
| 44 | 661 | @R20 @both | The even split from a cold boot (key flow 1) | R20_the_even_split_from_a_cold_boot C 1/1 W 1/1 | PASS |
| 45 | 673 | @R20 @both | More than six people list in two columns on the desktop | R20_more_than_six_people_list_in_two_columns_on_the_desktop C 1/1 W 1/1 | PASS |
| 46 | 683 | @R21 @both | The by-item split from gestures (key flow 2) | R21_the_by_item_split_from_gestures C 1/1 W 1/1 | PASS |
| 47 | 693 | @R21 @both | Someone who had nothing is still listed | R21_someone_who_had_nothing_is_still_listed C 1/1 W 1/1 | PASS |
| 48 | 701 | @R22 @both | Copy summary puts the exact text on the clipboard | R22_copy_summary_puts_the_exact_text_on_the_clipboard C 6/6 W 6/6 | PASS |
| 49 | 717 | @R22 @both | A bill from RM 1,000 copies with thousands commas | R22_a_bill_from_rm_1000_copies_with_thousands_commas C 1/1 W 1/1 | PASS |
| 50 | 724 | @R23 @both | The browser blocks the clipboard | R23_the_browser_blocks_the_clipboard C 1/1 W 1/1 | PASS |
| 51 | 733 | @R23 @both | The clipboard API is missing | R23_the_clipboard_api_is_missing C 1/1 W 1/1 | PASS |
| 52 | 740 | @R24 @both | The status lasts until the next change to the bill | R24_the_status_lasts_until_the_next_change_to_the_bill C 1/1 W 1/1 | PASS |
| 53 | 755 | @R25 @both | Every change is saved | R25_every_change_is_saved C 9/9 W 9/9 | PASS |
| 54 | 771 | @R25 @both | Leaving a field, copying, folding and the sheet do not save | R25_leaving_a_field_copying_folding_and_the_sheet_do_not_save C 1/1 W 1/1 | PASS |
| 55 | 778 | @R26 @both | Come back later (key flow 3) | R26_come_back_later C 1/1 W 1/1 | PASS |
| 56 | 788 | @R26 @both | A drawn order comes back after a reload | R26_a_drawn_order_comes_back_after_a_reload C 1/1 W 1/1 | PASS |
| 57 | 796 | @R26 @R61 @both | Odd but readable drafts load | R26_odd_but_readable_drafts_load C 7/7 W 7/7 | PASS |
| 58 | 813 | @R27 @R61 @both | An unreadable draft starts a new bill with a note | R27_an_unreadable_draft_starts_a_new_bill_with_a_note C 32/32 W 32/32 | PASS |
| 59 | 858 | @R27 @both | Dismissing the note | R27_dismissing_the_note C 1/1 W 1/1 | PASS |
| 60 | 868 | @R28 @both | The app works without storage | R28_the_app_works_without_storage C 3/3 W 3/3 | PASS |
| 61 | 882 | @R29 @both | The dialog opens with the safe choice focused | R29_the_dialog_opens_with_the_safe_choice_focused C 1/1 W 1/1 | PASS |
| 62 | 899 | @R30 @both | Leaving the dialog without starting over | R30_leaving_the_dialog_without_starting_over C 4/4 W 4/4 | PASS |
| 63 | 916 | @R29 @both | A repeat press on New bill leaves the dialog open | R29_a_repeat_press_on_new_bill_leaves_the_dialog_open C 9/9 W 9/9 | PASS |
| 64 | 926 | @R30 @both | After a double click on New bill one deliberate click still closes it | R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it C 3/3 W 3/3 | PASS |
| 65 | 939 | @R30 @both | The second press of a double activation that closed the dialog never reaches the page | R30_the_second_press_of_a_double_activation_that_closed_the_dialog_never_reaches_the_page C 13/13 W 13/13 | PASS |
| 66 | 953 | @R29 @both | The keyboard and the next press are not held back | R29_the_keyboard_and_the_next_press_are_not_held_back C 1/1 W 1/1 | PASS |
| 67 | 962 | @R31 @both | Start over (key flow 4) | R31_start_over C 1/1 W 1/1 | PASS |
| 68 | 973 | @R31 @both | Start over clears the copy status and the spare choice | R31_start_over_clears_the_copy_status_and_the_spare_choice C 1/1 W 1/1 | PASS |
| 69 | 985 | @R31 @both | Start over clears the error flags | R31_start_over_clears_the_error_flags C 4/4 W 4/4 | PASS |
| 70 | 1005 | @R32 @both | Tab order follows the golden | R32_tab_order_follows_the_golden C 9/9 W 9/9 | PASS |
| 71 | 1024 | @R32 @both | Every focused control shows the one ring | R32_every_focused_control_shows_the_one_ring C 2/2 W 2/2 | PASS |
| 72 | 1033 | @R33 @both | Typing never loses its place | R33_typing_in_a_person_name_keeps_focus_and_caret C 1/1 W 1/1; R33_typing_in_an_item_field_keeps_focus_and_caret C 2/2 W 2/2; R33_typing_in_an_amount_or_a_rate_keeps_focus_and_caret C 2/2 W 2/2 | PASS |
| 73 | 1050 | @R33 @chromium_only | IME composition survives a render | R33_ime_composition_survives_a_render C 1/1, W 0 pass 1 skip (counted, reason in skips.txt) | PASS |
| 74 | 1057 | @R34 @both | Focus after adding or removing | R34_focus_after_adding_or_removing_a_person C 3/3 W 3/3; R34_focus_after_adding_or_removing_an_item C 4/4 W 4/4 | PASS |
| 75 | 1073 | @R35 @both | No horizontal overflow in any golden state | R35_no_horizontal_overflow_in_any_golden_state C 40/40 W 40/40 | PASS |
| 76 | 1097 | @R36 @both | Reduced motion moves nothing | R36_reduced_motion_moves_nothing C 1/1 W 1/1 | PASS |
| 77 | 1104 | @R36 @both | With motion allowed nothing loops | R36_with_motion_allowed_nothing_loops C 1/1 W 1/1 | PASS |
| 78 | 1117 | @R37 @both | Names are shown as text, never as markup | R37_names_are_shown_as_text_and_never_as_markup C 1/1 W 1/1 | PASS |
| 79 | 1133 | @R37 @static | No HTML sink in the source | R37_no_banned_api_in_the_shipped_files C 1/1 W 1/1; R37_the_banned_api_scan_has_teeth C 1/1 W 1/1 | PASS |
| 80 | 1139 | @R38 @both | The Content Security Policy is exact and never violated | R38_policy_is_exact_and_nothing_inline C 1/1 W 1/1 | PASS |
| 81 | 1146 | @R38 @both | The strict policy blocks nothing the app needs | R38_strict_policy_blocks_nothing_the_app_needs C 5/5 W 5/5 | PASS |
| 82 | 1162 | @R38 @static | Code writes style only to the four allowed targets | R38_code_writes_style_only_to_the_four_allowed_targets C 1/1 W 1/1 | PASS |
| 83 | 1172 | @R39 @static | Nothing leaves the device | R39_nothing_leaves_the_device_by_the_static_scan C 1/1 W 1/1; R39_the_network_scan_has_teeth C 1/1 W 1/1 | PASS |
| 84 | 1182 | @R39 @both | Every request stays on the device | R39_a_whole_session_makes_only_same_origin_gets C 1/1 W 1/1; R39_the_request_log_flags_anything_but_same_origin_gets C 1/1 W 1/1 | PASS |
| 85 | 1188 | @R39 @R44 @both | The run-time icons come from createElementNS | R39_the_run_time_icons_come_from_createElementNS C 1/1 W 1/1 | PASS |
| 86 | 1197 | @R40 @gate | Looks right | fidelity pixel gate, not this finder's (A19 ran it) | NOT RUN |
| 87 | 1203 | @R40 @static | The runner uses the Python that runs pytest and stays Chromium only | R40_the_runner_uses_the_python_that_runs_pytest C 1/1 W 1/1; R40_the_runner_takes_the_harness_from_the_environment_and_has_a_default C 1/1 W 1/1; R40_the_runner_builds_the_documented_command C 1/1 W 1/1; R40_the_runner_runs_its_controls_first_and_passes_only_a_clean_pair C 4/4 W 4/4 | PASS |
| 88 | 1212 | @R40 @static | The fidelity seeds equal seeds.py and carry the clipboard stand-in | R40_fidelity_seeds_match C 9/9 W 9/9; R40_there_is_one_seed_script_per_seed_and_a_planted_fault_is_reported C 1/1 W 1/1; R40_a_seed_script_boots_the_app_through_its_own_load_path C 3/3 W 3/3; R40_the_open_new_bill_script_leaves_the_dialog_open_without_a_ring C 1/1 W 1/1 | PASS |
| 89 | 1223 | @R40 @chromium_only | An after-load script presses nothing without the clipboard stand-in | R40_an_after_load_script_presses_nothing_without_the_clipboard_stand_in C 1/1, W 0 pass 1 skip (counted, reason in skips.txt) | PASS |
| 90 | 1233 | @R41 @gate | Works right | live gate runs 20261015-205844-chromium and 20261015-205931-webkit (9 of 9 each, control null), see the gate section | PASS |
| 91 | 1242 | @R41 @gate | The live gate fails when the app starts from a saved bill (control) | 20261015-205837-chromium-control and 20261015-205925-webkit-control, red at step 1 | PASS |
| 92 | 1256 | @R41 @static | The gate script makes a cold context except on its control path | R41_the_step_log_puts_gesture_and_assertion_in_their_own_fields C 1/1 W 1/1; R41_the_gate_installs_the_clipboard_recorder_and_the_csp_listener_and_nothing_else C 1/1 W 1/1; R41_the_gate_uses_real_gestures_and_reads_only C 1/1 W 1/1; R41_a_planted_copy_of_the_gate_script_is_reported C 4/4 W 4/4 | PASS |
| 93 | 1273 | @R43 @both | The name in the title and the top bar | R43_the_name_in_the_title_and_the_top_bar C 1/1 W 1/1 | PASS |
| 94 | 1280 | @R44 @static | The sprite and the mark are the golden's bytes | R44_the_sprite_and_the_mark_are_the_goldens_bytes C 1/1 W 1/1 | PASS |
| 95 | 1287 | @R44 @both | The sprite comes first and the empty receipt uses the mark | R44_the_sprite_comes_first_and_the_empty_receipt_uses_the_mark C 1/1 W 1/1 | PASS |
| 96 | 1294 | @R45 @static | The tab icon file is the golden's icon | R45_the_tab_icon_file_is_the_goldens_icon C 1/1 W 1/1 | PASS |
| 97 | 1302 | @R45 @both | The tab icon loads under the live policy | R45_the_tab_icon_loads_under_the_live_policy C 1/1 W 1/1 | PASS |
| 98 | 1309 | @R45 @per_engine | The tab icon's colour follows the colour scheme | R45_the_tab_icon_colour_follows_the_colour_scheme C 1/1 W 1/1 (WebKit `icon-colour.txt` equals the baseline's) | PASS |
| 99 | 1318 | @R46 @both | (a) A cold boot with working storage shows no warning | R46_a_cold_boot_with_working_storage_shows_no_warning C 1/1 W 1/1 | PASS |
| 100 | 1324 | @R46 @both | (b) The first failed save shows the warning | R46_the_first_failed_save_shows_the_warning C 1/1 W 1/1 | PASS |
| 101 | 1333 | @R46 @both | (c) The warning stays while saves fail, and a reload starts without it | R46_the_warning_stays_while_saves_fail_and_a_reload_starts_without_it C 1/1 W 1/1 | PASS |
| 102 | 1342 | @R47 @both | (d) The first save that works removes the warning | R47_the_first_save_that_works_removes_the_warning C 1/1 W 1/1 | PASS |
| 103 | 1350 | @R46 @both | (e) A failed boot read shows the warning in the first render | R46_a_failed_boot_read_shows_the_warning_in_the_first_render C 2/2 W 2/2 | PASS |
| 104 | 1362 | @R46 @R27 @both | (f) An unreadable draft whose reset save fails shows both notes, the warning first | R46_an_unreadable_draft_whose_reset_save_fails_shows_both_notes_the_warning_first C 1/1 W 1/1 | PASS |
| 105 | 1371 | @R47 @both | SW6. A storage object that comes back clears the warning without a reload | R47_a_storage_object_that_comes_back_clears_the_warning_without_a_reload C 1/1 W 1/1 | PASS |
| 106 | 1379 | @R47 @both | SW4. Only a save attempt decides, so a change that writes nothing leaves the warning | R47_a_change_that_writes_nothing_leaves_the_warning C 1/1 W 1/1 | PASS |
| 107 | 1388 | @R46 @both | SW7. The warning's live region is not touched on every keystroke | R46_the_warnings_live_region_is_not_touched_on_every_keystroke C 1/1 W 1/1 | PASS |
| 108 | 1395 | @R46 @R47 @both | D-d. A real full storage shows the warning, and room again clears it | R46_a_real_full_storage_shows_the_warning_and_room_again_clears_it C 1/1 W 1/1 | PASS |
| 109 | 1405 | @R47 @static | The app reads no error name and probes nothing | R47_the_app_reads_no_error_name_and_probes_nothing C 1/1 W 1/1 | PASS |
| 110 | 1415 | @R48 @both | Which section is open on load | R48_which_section_is_open_on_load C 7/7 W 7/7 | PASS |
| 111 | 1429 | @R48 @both | A header row toggles by click, Enter and Space | R48_a_header_row_toggles_by_click_enter_and_space C 1/1 W 1/1 | PASS |
| 112 | 1441 | @R48 @both | The People summary fits its row | R48_the_people_summary_fits_its_row C 4/4 W 4/4 | PASS |
| 113 | 1452 | @R48 @both | The People summary refits when its row's width changes | R48_the_people_summary_refits_when_its_rows_width_changes C 1/1 W 1/1 | PASS |
| 114 | 1458 | @R48 @both | The Charges summary names a rate that blocks | R48_the_charges_summary_names_a_rate_that_blocks C 5/5 W 5/5 | PASS |
| 115 | 1472 | @R48 @both | The Charges summary follows each keystroke, not the error timing | R48_the_charges_summary_follows_each_keystroke_not_the_error_timing C 1/1 W 1/1 | PASS |
| 116 | 1480 | @R48 @both | Only the header row and Start new bill open or fold a section | R48_only_the_header_row_and_start_new_bill_open_or_fold_a_section C 1/1 W 1/1 | PASS |
| 117 | 1488 | @R48 @both | On the desktop both sections show with their own headings | R48_on_the_desktop_both_sections_show_their_own_headings C 1/1 W 1/1 | PASS |
| 118 | 1494 | @R49 @both | The strip for each result | R49_the_strip_for_each_result C 7/7 W 7/7 | PASS |
| 119 | 1510 | @R49 @both | No control the user tabs to is left under the strip | R49_no_control_the_user_tabs_to_is_left_under_the_strip C 1/1 W 1/1 | PASS |
| 120 | 1518 | @R49 @both | The app scrolls a focused control only below 1024 px and only when the strip covers it | R49_the_app_scrolls_a_focused_control_only_below_1024_px_and_only_when_the_strip_covers_it C 1/1 W 1/1 | PASS |
| 121 | 1531 | @R50 @both | The Splits sheet opens with the card's receipt | R50_the_splits_sheet_opens_with_the_cards_receipt C 1/1 W 1/1 | PASS |
| 122 | 1541 | @R50 @both | Closing the sheet returns focus to Splits | R50_closing_the_sheet_returns_focus_to_splits C 4/4 W 4/4 | PASS |
| 123 | 1554 | @R50 @both | A press that starts in the sheet and ends on the backdrop does not close it | R50_a_press_that_starts_in_the_sheet_and_ends_on_the_backdrop_does_not_close_it C 1/1 W 1/1 | PASS |
| 124 | 1560 | @R50 @both | A repeat press on Splits leaves the sheet open and copies nothing | R50_a_repeat_press_on_splits_leaves_the_sheet_open_and_copies_nothing C 4/4 W 4/4 | PASS |
| 125 | 1570 | @R50 @both | The second press of a double activation that closed the sheet never reaches the page | R50_the_second_press_of_a_double_activation_that_closed_the_sheet_never_reaches_the_page C 4/4 W 4/4 | PASS |
| 126 | 1583 | @R50 @both | The sheet closes itself when the window reaches 1024 px | R50_the_sheet_closes_itself_when_the_window_reaches_1024_px C 1/1 W 1/1 | PASS |
| 127 | 1591 | @R50 @both | The sheet follows the bill while it is open | R50_the_sheet_follows_the_bill_while_it_is_open C 1/1 W 1/1 | PASS |
| 128 | 1597 | @R55 @both | The desktop layout at 1280 and at 1024 | R55_the_desktop_layout_at_1280_and_at_1024 C 1/1 W 1/1 | PASS |
| 129 | 1606 | @R55 @both | The page never scrolls at 1280 x 800 | R55_the_page_never_scrolls_at_1280_by_800 C 12/12 W 12/12 | PASS |
| 130 | 1625 | @R56 @both | The item frame marks what lies above and below | R56_the_item_frame_marks_what_lies_above_and_below C 4/4 W 4/4 | PASS |
| 131 | 1636 | @R56 @both | Scrolling the frame moves the marks | R56_scrolling_the_frame_moves_the_marks C 1/1 W 1/1 | PASS |
| 132 | 1647 | @R51 @both | The spare sen line and chip | R51_the_spare_sen_line_and_chip C 5/5 W 5/5 | PASS |
| 133 | 1660 | @R51 @both | No spare sen, no line | R51_no_spare_sen_no_line C 1/1 W 1/1 | PASS |
| 134 | 1668 | @R52 @both | P1 opens from either chip with focus on the chosen rule | R52_p1_opens_from_either_chip_with_focus_on_the_chosen_rule C 2/2 W 2/2 | PASS |
| 135 | 1680 | @R52 @both | A choice applies at once and P1 stays open | R52_a_choice_applies_at_once_and_p1_stays_open C 1/1 W 1/1 | PASS |
| 136 | 1689 | @R52 @both | Arrow keys move between the three choices and focus stays on the radio | R52_arrow_keys_move_between_the_three_choices_and_focus_stays_on_the_radio C 1/1 W 1/1 | PASS |
| 137 | 1701 | @R52 @both | P1 sits beside the card on the desktop | R52_p1_sits_beside_the_card_on_the_desktop C 4/4 W 4/4 | PASS |
| 138 | 1712 | @R52 @both | On a phone P1 is a bottom sheet over the Splits sheet, and the sheet makes room | R52_on_a_phone_p1_is_a_bottom_sheet_over_the_splits_sheet_and_the_sheet_makes_room C 4/4 W 4/4 | PASS |
| 139 | 1726 | @R52 @both | The sheet scrolls so the splits stay in view above P1 | R52_the_sheet_scrolls_so_the_splits_stay_in_view_above_p1 C 1/1 W 1/1 | PASS |
| 140 | 1733 | @R52 @both | Closing P1 returns focus to the chip shown at that moment | R52_closing_p1_returns_focus_to_the_chip_shown_at_that_moment C 7/7 W 7/7 | PASS |
| 141 | 1749 | @R52 @both | A repeat click on the desktop chip leaves P1 open | R52_a_repeat_click_on_the_desktop_chip_leaves_p1_open C 1/1 W 1/1 | PASS |
| 142 | 1756 | @R52 @both | The second press of a double activation that closed P1 never reaches the page | R52_the_second_press_of_a_double_activation_that_closed_p1_never_reaches_the_page C 8/8 W 8/8 | PASS |
| 143 | 1771 | @R52 @both | P1 follows the width when it crosses 1024 px | R52_p1_follows_the_width_when_it_crosses_1024_px C 1/1 W 1/1 | PASS |
| 144 | 1780 | @R52 @both | P1 opened on the desktop and closed below 1024 px | R52_p1_opened_on_the_desktop_and_closed_below_1024_px C 1/1 W 1/1 | PASS |
| 145 | 1790 | @R53 @both | One person picks the first eligible person at once, and a pill changes it | R53_one_person_picks_the_first_eligible_person_at_once_and_a_pill_changes_it C 1/1 W 1/1 | PASS |
| 146 | 1802 | @R53 @both | Only people on an item can be chosen in By item | R53_only_people_on_an_item_can_be_chosen_in_by_item C 1/1 W 1/1 | PASS |
| 147 | 1812 | @R53 @both | A chosen person who has nothing falls back to Top of the list and stays chosen | R53_a_chosen_person_who_has_nothing_falls_back_to_top_of_the_list_and_stays_chosen C 1/1 W 1/1 | PASS |
| 148 | 1824 | @R53 @both | Removing the chosen person sets the rule back to Top of the list | R53_removing_the_chosen_person_sets_the_rule_back_to_top_of_the_list C 1/1 W 1/1 | PASS |
| 149 | 1831 | @R54 @both | At random gives the spare sen to different people, and Pick again draws again | R54_at_random_gives_the_spare_sen_to_different_people_and_pick_again_draws_again C 1/1 W 1/1 | PASS |
| 150 | 1847 | @R54 @both | Pick again that can change nothing does nothing | R54_pick_again_that_can_change_nothing_does_nothing C 1/1 W 1/1 | PASS |
| 151 | 1854 | @R54 @both | Pick again in the Splits sheet draws again | R54_pick_again_in_the_splits_sheet_draws_again C 1/1 W 1/1 | PASS |
| 152 | 1863 | @R54 @static | Math.random goes only to the two draws | R54_math_random_goes_only_to_the_two_draws C 1/1 W 1/1 | PASS |
| 153 | 1872 | @R60 @both | Large bills fit a 360 px phone | R60_large_bills_fit_a_360_px_phone C 3/3 W 3/3 | PASS |
| 154 | 1885 | @R60 @both | The large price shows whole | R60_the_large_price_shows_whole C 1/1 W 1/1 | PASS |
| 155 | 1892 | @R57 @both | A held Enter on the only item's Remove removes that item only | R57_a_held_enter_on_the_only_items_remove_removes_that_item_only C 1/1 W 1/1 | PASS |
| 156 | 1900 | @R57 @both | A held Enter on New bill leaves the dialog open on Cancel | R57_a_held_enter_on_new_bill_leaves_the_dialog_open_on_cancel C 1/1 W 1/1 | PASS |
| 157 | 1908 | @R57 @both | Separate presses still act, and a held letter still types | R57_separate_presses_still_act_and_a_held_letter_still_types C 1/1 W 1/1 | PASS |
| 158 | 1921 | @R57 @node | The repeat rule reads the click count, the pointer, the time and the place | Node run 20261015-204618, 10 of 10 `@R57 b ...` tests (tests/repeat.test.js) | PASS |
| 159 | 1940 | @R57 @both | A slow second tap, or a quick tap elsewhere, is never held back | R57_a_slow_second_tap_or_a_quick_tap_elsewhere_is_never_held_back C 1/1 W 1/1 | PASS |
| 160 | 1950 | @R58 @static | The engine option and the one launch place | R58_the_engine_option_and_the_one_launch_place C 1/1 W 1/1 | PASS |
| 161 | 1960 | @R58 @gate | A Chromium-only test is a counted skip in WebKit | run folders checked on disk (notes above) | PASS |
| 162 | 1968 | @R58 @R41 @gate | The live gate records its engine | live gate summary.json and folder names (gate section) | PASS |
| 163 | 1974 | @R59 @per_engine | Focus after a mouse click is the engine's own | R59_focus_after_a_mouse_click_is_the_engines_own C 1/1 W 1/1 | PASS |
| 164 | 1986 | @R59 @gate | The A0 baseline record is complete | `qa/webkit-baseline/20261014-130011/` checked on disk (notes above) | PASS |
| 165 | 2002 | @R9 @R11 @chromium_only | The accessible description of the amount fields is measured and reported | no test, no `accessible-description.txt` in a run folder. QA-S5-1. My own measurement in `qa/accessible-description/20261015-205800/` | FAIL |
| 166 | 2011 | @R61 @node | The decoder accepts versions 1 and 2 and checks the spare choice | Node run 20261015-204618, 4 `@R61 D3/D13/D14` tests (tests/draft.test.js) | PASS |
| 167 | 2025 | @R61 @node | Saving writes version 2, and load and save report failures | Node run 20261015-204618, `@R61 encodeDraft writes version 2 ...` and `@R27 loadDraft tells none ...` (tests/draft.test.js) | PASS |

---

## v1.1.0 regression --full, 2026-10-16

**Verdict: PASS for the QA lane, with one half scenario outside it.** 181 qa.md scenarios. 180 pass, 0 fail, 0 blocked, 0 not run, and 1 is partial. The partial one is #87 "Looks right" (`@R40 @gate`), whose Then line has two halves. The pixel gate half is observed and green (both controls as written, 40 of 40 pairs at 0 px). The FE element checklist half belongs to the fidelity finder and was not run here. No browser test failed in either engine, no id differs from the fix pass proofs, and every pair of the fidelity gate is at 0 px.

Run by the QA finder (read-only) on 2026-10-16 at HEAD `64b882c` (last green code `b0992b4`). `git diff --stat HEAD` on `src/`, `index.html`, `tests/` and `docs/design/` is empty. The only modified tracked file at the time was `docs/progress/STATE.md`, which is the orchestrator's. This section is appended under the step 5 verdict above and no existing line was removed. It was appended with `sed -i '$r'` on this one file, and the front matter gains one line, `regression_full_2026_10_16`. Every run below made its own new timestamped folder and every folder was listed on disk after its run. This section is also the QA half of the step 5 re-check (ledger S7 row 46).

| Run | Result | Against the proofs of the fix pass on `b0992b4` |
|---|---|---|
| Node `node --test "tests/**/*.test.js"`, `docs/modules/split-core/qa/unit/20261016-031908/node-test.txt` | 406 of 406, 0 fail, 0 skipped | `qa/unit/20261016-030139/` 406 of 406. The same 406 titles in the same order |
| Chromium 149.0.7827.55, `SPLIT_EVIDENCE=1 python -m pytest tests/browser -q -p no:cacheprovider`, `docs/modules/split-app/qa/functional/20261016-031917-chromium/` (`pytest.txt`, `junit.xml`, `skips.txt`, `accessible-description.txt`, `R50-sheet-closed-at-1024.txt`) | 742 passed, 0 failed, 0 skipped, 216.63 s, junit timestamp 2026-10-16T03:19:17 | `20261016-030148-chromium/` 742 passed. By id (classname and name, parametrized ids included) 742 ids in both, 0 only in one, 0 with a different outcome |
| WebKit 26.5, `SPLIT_EVIDENCE=1 python -m pytest tests/browser -q -p no:cacheprovider --engine webkit`, `docs/modules/split-app/qa/functional/20261016-032255-webkit/` (`pytest.txt`, `junit.xml`, `skips.txt`, `icon-colour.txt`, `R50-sheet-closed-at-1024.txt`) | 739 passed, 3 skipped, 0 failed, 472.05 s. No failure screenshot was written | `20261016-030547-webkit/` 739 passed, 3 skipped. By id 742 in both, 0 only in one, 0 different. `skips.txt` is identical (R33 IME, R9 accessible description, R40 after-load, each with its reason, count 3) and so is `icon-colour.txt` |
| Fidelity pixel gate, Chromium, `python tests/browser/fidelity/run.py`, `docs/modules/split-app/qa/fidelity/20261016-033155/` (42 report folders and `run.log`) | 40 of 40 pairs at 0 px with equal sizes. Control `control-self-390x844` 0 px and sizes 390 x 950 both sides, `CONTROL PASS`. Control `control-noseed-390x844` 184588 px (56.0785%) with sizes 390 x 950 and 390 x 844, `CONTROL PASS` (it wants more than 0). Server pid 20876 port 28423, `server STOPPED ... port free again True` | A19 `qa/fidelity/20261015-193738/`. The 40 PASS lines of its `run.log` are identical to this run's and both controls give the same pixel counts (0 and 184588). This run's `run.log` has 40 PASS lines and 0 FAIL lines, and a script over the 42 `report.json` files found `mismatch_pixels` 0 and `dimensions_match` true for the 40 pairs and the self control, and 184588 and false for the no-seed control |
| Live gate, Chromium, control then green on one server (pid 4760 port 7237) | control RED at step 1, green 9 of 9 | `docs/regression/20261016-032500/cold-boot.md` lists the folders, the figures and the PIDs. The same figures as the step 5 runs |
| Live gate, WebKit, control then green on one server (pid 20580 port 15809) | control RED at step 1, green 9 of 9 | the same |
| Live gate, bare `python tests/browser/live_e2e.py` (serves itself, pid 14340 port 5461) | 9 of 9, folder ends `-chromium` | `20261015-205954-chromium/` 9 of 9 |

The two suite runs were one after the other. The by-id comparison used `junit.xml` classname and test name, and the two outputs hold no duplicate id.

### Findings
None. No scenario fails and no scenario is without a test.

| id | R# | verdict | what I saw | capture |
|---|---|---|---|---|
| (none) | | | | |

### The step 5 open items
- **QA-S5-1 (R9, R11, a missing test). Closed.** `test_R9_the_accessible_description_of_the_amount_fields_is_measured_and_reported` runs and passes in Chromium (`20261016-031917-chromium/pytest.txt`, `PASSED`), and is a counted skip with its reason in WebKit (`20261016-032255-webkit/skips.txt`). It wrote `accessible-description.txt` into the Chromium run's folder. Its four lines name the field and the error state and equal my step 5 measurement (`qa/accessible-description/20261015-205800/accessible-description.txt`) in content. Both fields read the description "Enter an amount like 12.50" with the error hidden and shown, and `aria-describedby` is `ie2` and `evenErr`. The scenario is #167.
- **QA-S5-2 (the strip text). Closed.** qa.md no longer names it as open. The Phrases section says "The strip reads" is `innerText` with every run of white space made one space, and a failing line may print the raw text. Both control runs print `got 'Total\nRM 116.60'` for the strip and the green runs pass the same read at step 2.
- **QA-S5-3 (`browser.version`). Closed.** qa.md now writes `browser_version` (the live gate section, the control scenario and "The live gate records its engine"). All five runs of today record the flat key `browser_version` (149.0.7827.55 and 26.5).
- **QA-S5-4 (WebKit frames). Still observed, unchanged, no scenario asserts it.** `20261016-033527-webkit/03-splits-sheet.jpg` shows the page behind the sheet faintly through the glass, and `06-by-item.jpg` shows a focus ring on the Splits button after the sheet closed. The Chromium `03-splits-sheet.jpg` shows less of the page behind the sheet. A real iPhone check at UAT stays the open item.
- **QA-S5-5 (the CG-P6 measurement). Unchanged.** See QA-S5-1. VoiceOver and TalkBack were not measured (UNVERIFIED, a device check).

### New scenarios, judged
- `@R62` (rows 170 to 179). 8 browser scenarios, 12 ids in each engine (5 for the control or bidi outline, 1 each for the other seven), all pass in Chromium and in WebKit. The two `@node` ones pass in the Node run, 7 `@R62 @R61 decodeDraft ...` (tests/draft.test.js) and 6 `@R62 @R33 plainNameField ...` (tests/dom.test.js).
- `@R27 @R7` "A repeat press on Dismiss note acts as one press at every width" (#180). 12 of 12 ids pass in each engine, the single click rows as the control and the double click, triple click and touch double tap rows at 390, 360 and 1280.
- `@R27 @R57` "A held Enter on Dismiss note reaches nothing" (#181). 2 of 2 ids pass in each engine.
- `@R62 @R33 @node` "plainNameField puts the caret where the text went in" (#179). 6 of 6 pass.
- The R9 accessible description test (#167). See QA-S5-1.
- Also new since step 5, `@R20` "Seven to eleven people list in two columns on the desktop" (#46, 5 of 5 per engine) and `@R58 @static` "A suite run never writes into an evidence folder it did not make" (#163, 1 of 1 per engine). The step 5 scenario #6 gained the suffix "(the walk's control)" and maps to the same test.

### Gate scenarios, judged on the runs of today
- **#87 Looks right (`@R40 @gate`). PARTIAL.** The pixel half is PASS as above. The FE element checklist half is not this finder's, so there is no verdict from me on it.
- **#91 Works right. PASS.** Green in both engines (`20261016-033459-chromium`, `20261016-033527-webkit`, 9 of 9, 93 assertion lines PASS, 0 FAIL, 90 requests all same-origin GETs inside the rule, 0 console errors, 0 page errors, 0 CSP violations, 3 clipboard writes, `bypass_csp` false, `storage_state` null). Each `summary.json` records `"control": null`. Frames viewed (Chromium 01, 03, webkit 03 and 06) show bill-empty with People open and the strip "Enter the subtotal to see the splits.", the sheet with 38.87, 38.87, 38.86 and "Summary copied", and the K1 items with "Total RM 69.26".
- **#92 control (Outline, 2 rows). PASS.** Both control runs stopped at step 1 with `pass` false. The stand-in line passed (so the RED comes from the cold boot), 10 assertion lines failed (names, removesDisabled, subtotal, open, card, totalHolds, emptyIcon, strip, stripCopy and `split.draft is absent`, got the K2 draft), `summary.json` records `"control": "seeded"`, the engine, the version and `control_red_on_its_property` true, the folder ends `-<engine>-control`, and each holds only its own five files. The frame `20261016-033455-chromium-control/01-cold-boot.jpg` shows the K2 bill, not bill-empty.
- **#162 A Chromium-only test is a counted skip in WebKit. PASS.** The WebKit folder ends `-webkit`, `skips.txt` lists 3 skipped tests with their reasons and `count 3`, equal to `junit.xml` `skipped="3"`, and the R33 IME reason starts "Needs a CDP session". 739 passed and 3 skipped, so no skip counts as a pass. In the Chromium `pytest.txt` the three `chromium_only` tests are `PASSED`.
- **#164 The live gate records its engine. PASS.** `20261016-033527-webkit/summary.json` has engine webkit and `browser_version` 26.5. The bare run's folder `20261016-033656-chromium` is Chromium.
- **#166 The A0 baseline record is complete. PASS**, a record check on disk. `qa/webkit-baseline/20261014-130011/` still holds `sorting.md`, `probes.json` (`launched_by` "rig.launch", `contexts_by` "rig.new_context", the seven probe keys) and `diagnostics/`. The folders it names exist (`qa/functional/20261014-125604-webkit/`, `20261014-125352-chromium/`, `qa/live-e2e/20261014-130326-chromium` and `20261014-130333-webkit`), and the WebKit `junit.xml` has the 48 failed ids that `sorting.md` says. I did not re-sort them.
- Servers. Both shared servers were stopped by exact PID (4760 on 7237, 20580 on 15809), each pid is gone from the process list and each port then refused a connection (curl exit 7). The suite runs and the fidelity run stopped their own servers (pids 5324, 24028 and 20876, each logged `STOPPED ... port free again True`), and so did the bare gate run (pid 14340).

### Process slips of this run (none changes a verdict)
- I ran `python tests/browser/fidelity/run.py --help` to read its options. The script has no argument parser, so it started a real gate (server pid 25420 port 60969), and my `| head -30` closed the pipe after 14 folders. The run stopped, there is no `run.log`, and the server was gone when I swept (no process, no listener). That folder is `docs/modules/split-app/qa/fidelity/20261016-031935/` (2 controls and 12 pairs). It is an aborted capture of mine, it counts for nothing, and it is not deleted. The verdict run is `20261016-033155/`. The aborted run overlapped the first minute of the Chromium suite, which still passed 742 of 742.
- Banned shell forms I wrote by habit, all printing or refused, none wrote a file. One `> <path> 2>/dev/null` to a path I had not meant to use (the shell answered "Permission denied", no file exists), one `> /dev/null 2>&1`, and one heredoc with `2>&1` that only printed a string.
- `-p no:cacheprovider` was added to both pytest commands so that no `.pytest_cache` lands in the project root. It does not change which tests run.

### Supporting tests with no scenario row of their own
54 of the 253 test functions (74 of the 742 ids) back the scenarios above or the harness rules of "How to run". Examples are `test_R39_clipboard_recorder_keeps_the_text_and_never_reaches_the_system`, `test_R46_the_storage_drivers_do_what_how_to_run_says`, `test_R35_layout_problems_has_teeth` and `test_R48_on_the_desktop_both_sections_show`. All pass in both engines. They are in `junit.xml`. The step 5 count was 54 of 239, and the 14 functions added since (R20, R58, R9, R62 by 8, R27 by 2, and the R41 helper guard, which is a clause of #93) are all mapped to a scenario.

### Scenario table
Columns are the scenario number in order of `qa.md`, the line of its `Scenario`, its tags, its title, the test function (without `test_`) with its cases passed in Chromium (C) and WebKit (W), and the verdict. The scenario to test names are the step 5 finder's for the scenarios that existed then (by title), set by hand for the new ones. A script checked that each named function exists in both `junit.xml` files and that every case of it passed (a skip counts only where the scenario is `@chromium_only`).

| # | line | tags | scenario | tests | verdict |
|---|---|---|---|---|---|
| 1 | 147 | @R1 @both | The entry point loads only its own files | R1_entry_point_loads_only_its_own_files C 1/1 W 1/1 | PASS |
| 2 | 159 | @R1 @both | The page works from a sub-path, as on GitHub Pages | R1_page_works_from_a_sub_path C 1/1 W 1/1 | PASS |
| 3 | 168 | @R2 @both | Cold boot is a new bill with no seed | R2_cold_boot_is_a_new_bill_with_no_seed C 1/1 W 1/1 | PASS |
| 4 | 181 | @R2 @static | No sample data ships | R2_no_sample_data_ships C 1/1 W 1/1 | PASS |
| 5 | 186 | @R3 @both | The rendered markup matches its golden | R3_rendered_markup_matches_its_golden C 40/40 W 40/40 | PASS |
| 6 | 212 | @R3 @both | The walk sees every rendered element and flags each kind of change (the walk's control) | R3_the_walk_sees_every_rendered_element_and_flags_each_kind_of_change C 1/1 W 1/1 | PASS |
| 7 | 227 | @R4 @both | Person rows carry their names and labels | R4_person_rows_carry_their_names_and_labels C 1/1 W 1/1 | PASS |
| 8 | 235 | @R4 @R5 @both | A blank name falls back to its position everywhere but the field | R4_a_blank_name_falls_back_to_its_position_everywhere_but_the_field C 1/1 W 1/1 | PASS |
| 9 | 245 | @R5 @both | Renaming a person updates every place on each keystroke | R5_renaming_a_person_updates_every_place_on_each_keystroke C 1/1 W 1/1 | PASS |
| 10 | 259 | @R5 @both | Renaming an item updates its accessible names | R5_renaming_an_item_updates_its_accessible_names C 1/1 W 1/1 | PASS |
| 11 | 266 | @R6 @both | Add person until the limit | R6_add_person_until_the_limit C 1/1 W 1/1 | PASS |
| 12 | 280 | @R6 @both | Removing anyone from twelve turns Add person back on | R6_removing_anyone_from_twelve_turns_add_person_back_on C 1/1 W 1/1 | PASS |
| 13 | 291 | @R7 @both | Remove a person and they leave every item | R7_removing_a_person_takes_them_off_every_item C 1/1 W 1/1, R7_remove_a_person C 1/1 W 1/1, R7_the_item_left_with_nobody_needs_a_person_on_the_card_and_the_strip C 1/1 W 1/1 | PASS |
| 14 | 303 | @R7 @both | A repeat press on the last Remove removes that row and adds nothing | R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing C 48/48 W 48/48 | PASS |
| 15 | 319 | @R34 @both | After a double click or double tap on a middle Remove, focus is where one click puts it | R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it C 4/4 W 4/4, R7_a_double_click_or_double_tap_on_remove_removes_one_row C 4/4 W 4/4 | PASS |
| 16 | 330 | @R7 @both | A press of its own is never held back | R7_two_separate_clicks_and_a_key_press_still_remove_a_row_each C 2/2 W 2/2, R7_a_separate_click_on_the_same_point_is_a_press_of_its_own C 1/1 W 1/1, R7_the_guard_of_a_remove_click_ends_at_the_next_press C 1/1 W 1/1, R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word C 1/1 W 1/1 | PASS |
| 17 | 343 | @R6 @both | A repeat press on Add person adds one person and keeps it | R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it C 72/72 W 72/72 | PASS |
| 18 | 357 | @R12 @both | A repeat press on Add item adds one item and never reaches the page | R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page C 36/36 W 36/36 | PASS |
| 19 | 373 | @R7 @R12 @both | A repeat press on a chip under a pending price error never removes the item | R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item C 6/6 W 6/6 | PASS |
| 20 | 389 | @R42 @both | Two people may have the same name | R42_duplicate_names_are_accepted_and_act_on_their_own_row C 1/1 W 1/1, R42_duplicate_names_through_the_whole_flow C 1/1 W 1/1, R42_the_draft_keeps_both_people_with_the_same_name C 1/1 W 1/1 | PASS |
| 21 | 408 | @R8 @both | Switching modes keeps both sets of input | R8_switching_modes_keeps_both_sets_of_input C 1/1 W 1/1 | PASS |
| 22 | 422 | @R8 @both | Arrow keys move between the modes | R8_arrow_keys_move_between_the_modes C 1/1 W 1/1 | PASS |
| 23 | 429 | @R9 @both | The subtotal field drives the even split | R9_the_subtotal_field_drives_the_even_split C 1/1 W 1/1 | PASS |
| 24 | 438 | @R10 @both | An inline error waits for the field to be left | R10_an_inline_error_waits_for_the_field_to_be_left C 4/4 W 4/4 | PASS |
| 25 | 455 | @R10 @both | An empty field never shows an error | R10_an_empty_field_never_shows_an_error C 1/1 W 1/1 | PASS |
| 26 | 466 | @R10 @both | Typing invalid text in a focused field does not show the error early | R10_typing_bad_text_in_a_focused_field_shows_no_error_early C 1/1 W 1/1 | PASS |
| 27 | 473 | @R10 @both | A restored invalid field shows its error at once | R10_a_restored_bad_field_shows_its_error_at_once C 1/1 W 1/1 | PASS |
| 28 | 480 | @R10 @both | An error survives a mode switch | R10_an_error_survives_a_mode_switch C 1/1 W 1/1 | PASS |
| 29 | 488 | @R10 @R13 @both | A press below an invalid field lands on the control it started on | R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on C 6/6 W 6/6 | PASS |
| 30 | 505 | @R10 @R59 @per_engine | A touch tap on the charges hint below an invalid rate | R10_a_touch_tap_on_the_charges_hint_below_an_invalid_rate C 2/2 W 2/2 | PASS |
| 31 | 519 | @R13 @both | A tap on a person below an invalid, unflagged price toggles them and then shows the error | R13_a_tap_below_an_invalid_price_toggles_that_person_and_then_shows_the_error C 2/2 W 2/2 | PASS |
| 32 | 527 | @R10 @both | The error waits for the release, and only a press holds it back | R10_the_error_waits_for_the_mouse_button_to_come_up C 1/1 W 1/1, R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press C 3/3 W 3/3, R10_pressing_empty_space_also_waits_for_the_release C 1/1 W 1/1, R10_a_press_that_ends_runs_each_waiting_handler_once C 1/1 W 1/1, R10_a_secondary_button_press_does_not_hold_the_error_back C 1/1 W 1/1, R10_a_cancelled_press_releases_the_waiting_error C 1/1 W 1/1 | PASS |
| 33 | 539 | @R11 @both | Item rows carry their names and labels | R11_item_rows_carry_their_names_and_labels C 1/1 W 1/1 | PASS |
| 34 | 549 | @R12 @both | Add an item, remove one, and reach the limit | R12_add_an_item_remove_one_and_reach_the_limit C 1/1 W 1/1 | PASS |
| 35 | 562 | @R13 @both | Tapping a person on an item | R13_tapping_a_person_on_an_item C 1/1 W 1/1 | PASS |
| 36 | 573 | @R14 @both | A price error sits in the item row | R14_a_price_error_sits_in_the_item_row C 1/1 W 1/1 | PASS |
| 37 | 585 | @R15 @both | The Charges block and its defaults | R15_the_charges_block_and_its_defaults C 1/1 W 1/1 | PASS |
| 38 | 595 | @R15 @both | A rate error names the hint first and then its error | R15_a_rate_error_names_the_hint_first_and_then_its_error C 1/1 W 1/1 | PASS |
| 39 | 603 | @R15 @R19 @both | A charge of 0 is allowed and still shown | R19_a_charge_of_zero_is_allowed_and_still_shown C 1/1 W 1/1 | PASS |
| 40 | 612 | @R16 @both | The receipt follows every keystroke and stays quiet | R16_the_receipt_follows_every_keystroke_and_stays_quiet C 1/1 W 1/1 | PASS |
| 41 | 624 | @R17 @both | When the splits cannot be worked out | R17_when_the_splits_cannot_be_worked_out C 8/8 W 8/8 | PASS |
| 42 | 643 | @R18 @both | Items that still need a person | R18_items_that_still_need_a_person C 1/1 W 1/1 | PASS |
| 43 | 656 | @R19 @both | Total and bill lines | R19_total_and_bill_lines C 2/2 W 2/2 | PASS |
| 44 | 668 | @R20 @both | The even split from a cold boot (key flow 1) | R20_the_even_split_from_a_cold_boot C 1/1 W 1/1 | PASS |
| 45 | 680 | @R20 @both | More than six people list in two columns on the desktop | R20_more_than_six_people_list_in_two_columns_on_the_desktop C 1/1 W 1/1 | PASS |
| 46 | 693 | @R20 @both | Seven to eleven people list in two columns on the desktop (new since step 5) | R20_seven_to_eleven_people_list_in_two_columns_on_the_desktop C 5/5 W 5/5 | PASS |
| 47 | 706 | @R21 @both | The by-item split from gestures (key flow 2) | R21_the_by_item_split_from_gestures C 1/1 W 1/1 | PASS |
| 48 | 716 | @R21 @both | Someone who had nothing is still listed | R21_someone_who_had_nothing_is_still_listed C 1/1 W 1/1 | PASS |
| 49 | 724 | @R22 @both | Copy summary puts the exact text on the clipboard | R22_copy_summary_puts_the_exact_text_on_the_clipboard C 6/6 W 6/6 | PASS |
| 50 | 740 | @R22 @both | A bill from RM 1,000 copies with thousands commas | R22_a_bill_from_rm_1000_copies_with_thousands_commas C 1/1 W 1/1 | PASS |
| 51 | 747 | @R23 @both | The browser blocks the clipboard | R23_the_browser_blocks_the_clipboard C 1/1 W 1/1 | PASS |
| 52 | 756 | @R23 @both | The clipboard API is missing | R23_the_clipboard_api_is_missing C 1/1 W 1/1 | PASS |
| 53 | 763 | @R24 @both | The status lasts until the next change to the bill | R24_the_status_lasts_until_the_next_change_to_the_bill C 1/1 W 1/1 | PASS |
| 54 | 778 | @R25 @both | Every change is saved | R25_every_change_is_saved C 9/9 W 9/9 | PASS |
| 55 | 794 | @R25 @both | Leaving a field, copying, folding and the sheet do not save | R25_leaving_a_field_copying_folding_and_the_sheet_do_not_save C 1/1 W 1/1 | PASS |
| 56 | 801 | @R26 @both | Come back later (key flow 3) | R26_come_back_later C 1/1 W 1/1 | PASS |
| 57 | 811 | @R26 @both | A drawn order comes back after a reload | R26_a_drawn_order_comes_back_after_a_reload C 1/1 W 1/1 | PASS |
| 58 | 819 | @R26 @R61 @both | Odd but readable drafts load | R26_odd_but_readable_drafts_load C 7/7 W 7/7 | PASS |
| 59 | 836 | @R27 @R61 @both | An unreadable draft starts a new bill with a note | R27_an_unreadable_draft_starts_a_new_bill_with_a_note C 32/32 W 32/32 | PASS |
| 60 | 881 | @R27 @both | Dismissing the note | R27_dismissing_the_note C 1/1 W 1/1 | PASS |
| 61 | 892 | @R28 @both | The app works without storage | R28_the_app_works_without_storage C 3/3 W 3/3 | PASS |
| 62 | 906 | @R29 @both | The dialog opens with the safe choice focused | R29_the_dialog_opens_with_the_safe_choice_focused C 1/1 W 1/1 | PASS |
| 63 | 923 | @R30 @both | Leaving the dialog without starting over | R30_leaving_the_dialog_without_starting_over C 4/4 W 4/4 | PASS |
| 64 | 940 | @R29 @both | A repeat press on New bill leaves the dialog open | R29_a_repeat_press_on_new_bill_leaves_the_dialog_open C 9/9 W 9/9 | PASS |
| 65 | 950 | @R30 @both | After a double click on New bill one deliberate click still closes it | R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it C 3/3 W 3/3 | PASS |
| 66 | 963 | @R30 @both | The second press of a double activation that closed the dialog never reaches the page | R30_the_second_press_of_a_double_activation_that_closed_the_dialog_never_reaches_the_page C 13/13 W 13/13 | PASS |
| 67 | 977 | @R29 @both | The keyboard and the next press are not held back | R29_the_keyboard_and_the_next_press_are_not_held_back C 1/1 W 1/1 | PASS |
| 68 | 986 | @R31 @both | Start over (key flow 4) | R31_start_over C 1/1 W 1/1 | PASS |
| 69 | 997 | @R31 @both | Start over clears the copy status and the spare choice | R31_start_over_clears_the_copy_status_and_the_spare_choice C 1/1 W 1/1 | PASS |
| 70 | 1009 | @R31 @both | Start over clears the error flags | R31_start_over_clears_the_error_flags C 4/4 W 4/4 | PASS |
| 71 | 1029 | @R32 @both | Tab order follows the golden | R32_tab_order_follows_the_golden C 9/9 W 9/9 | PASS |
| 72 | 1048 | @R32 @both | Every focused control shows the one ring | R32_every_focused_control_shows_the_one_ring C 2/2 W 2/2 | PASS |
| 73 | 1057 | @R33 @both | Typing never loses its place | R33_typing_in_a_person_name_keeps_focus_and_caret C 1/1 W 1/1, R33_typing_in_an_item_field_keeps_focus_and_caret C 2/2 W 2/2, R33_typing_in_an_amount_or_a_rate_keeps_focus_and_caret C 2/2 W 2/2 | PASS |
| 74 | 1074 | @R33 @chromium_only | IME composition survives a render | R33_ime_composition_survives_a_render C 1/1 W 0 pass 1 skip (counted, reason in skips.txt) | PASS |
| 75 | 1081 | @R34 @both | Focus after adding or removing | R34_focus_after_adding_or_removing_a_person C 3/3 W 3/3, R34_focus_after_adding_or_removing_an_item C 4/4 W 4/4 | PASS |
| 76 | 1097 | @R35 @both | No horizontal overflow in any golden state | R35_no_horizontal_overflow_in_any_golden_state C 40/40 W 40/40 | PASS |
| 77 | 1121 | @R36 @both | Reduced motion moves nothing | R36_reduced_motion_moves_nothing C 1/1 W 1/1 | PASS |
| 78 | 1128 | @R36 @both | With motion allowed nothing loops | R36_with_motion_allowed_nothing_loops C 1/1 W 1/1 | PASS |
| 79 | 1141 | @R37 @both | Names are shown as text, never as markup | R37_names_are_shown_as_text_and_never_as_markup C 1/1 W 1/1 | PASS |
| 80 | 1157 | @R37 @static | No HTML sink in the source | R37_no_banned_api_in_the_shipped_files C 1/1 W 1/1, R37_the_banned_api_scan_has_teeth C 1/1 W 1/1 | PASS |
| 81 | 1163 | @R38 @both | The Content Security Policy is exact and never violated | R38_policy_is_exact_and_nothing_inline C 1/1 W 1/1 | PASS |
| 82 | 1170 | @R38 @both | The strict policy blocks nothing the app needs | R38_strict_policy_blocks_nothing_the_app_needs C 5/5 W 5/5 | PASS |
| 83 | 1186 | @R38 @static | Code writes style only to the four allowed targets | R38_code_writes_style_only_to_the_four_allowed_targets C 1/1 W 1/1 | PASS |
| 84 | 1196 | @R39 @static | Nothing leaves the device | R39_nothing_leaves_the_device_by_the_static_scan C 1/1 W 1/1, R39_the_network_scan_has_teeth C 1/1 W 1/1 | PASS |
| 85 | 1206 | @R39 @both | Every request stays on the device | R39_a_whole_session_makes_only_same_origin_gets C 1/1 W 1/1, R39_the_request_log_flags_anything_but_same_origin_gets C 1/1 W 1/1 | PASS |
| 86 | 1212 | @R39 @R44 @both | The run-time icons come from createElementNS | R39_the_run_time_icons_come_from_createElementNS C 1/1 W 1/1 | PASS |
| 87 | 1221 | @R40 @gate | Looks right | fidelity pixel gate `qa/fidelity/20261016-033155/`, both controls as written and 40 of 40 pairs at 0 px. The FE element checklist half is the fidelity finder's and was not run here | PARTIAL |
| 88 | 1227 | @R40 @static | The runner uses the Python that runs pytest and stays Chromium only | R40_the_runner_uses_the_python_that_runs_pytest C 1/1 W 1/1, R40_the_runner_takes_the_harness_from_the_environment_and_has_a_default C 1/1 W 1/1, R40_the_runner_builds_the_documented_command C 1/1 W 1/1, R40_the_runner_runs_its_controls_first_and_passes_only_a_clean_pair C 4/4 W 4/4 | PASS |
| 89 | 1236 | @R40 @static | The fidelity seeds equal seeds.py and carry the clipboard stand-in | R40_fidelity_seeds_match C 9/9 W 9/9, R40_there_is_one_seed_script_per_seed_and_a_planted_fault_is_reported C 1/1 W 1/1, R40_a_seed_script_boots_the_app_through_its_own_load_path C 3/3 W 3/3, R40_the_open_new_bill_script_leaves_the_dialog_open_without_a_ring C 1/1 W 1/1 | PASS |
| 90 | 1247 | @R40 @chromium_only | An after-load script presses nothing without the clipboard stand-in | R40_an_after_load_script_presses_nothing_without_the_clipboard_stand_in C 1/1 W 0 pass 1 skip (counted, reason in skips.txt) | PASS |
| 91 | 1257 | @R41 @gate | Works right | live gate `20261016-033459-chromium` and `20261016-033527-webkit`, 9 of 9 each, `control` null | PASS |
| 92 | 1266 | @R41 @gate | The live gate fails when the app starts from a saved bill (control) | `20261016-033455-chromium-control` and `20261016-033526-webkit-control`, RED at step 1, `control` seeded | PASS |
| 93 | 1280 | @R41 @static | The gate script makes a cold context except on its control path | R41_the_step_log_puts_gesture_and_assertion_in_their_own_fields C 1/1 W 1/1, R41_the_gate_installs_the_clipboard_recorder_and_the_csp_listener_and_nothing_else C 1/1 W 1/1, R41_the_gate_uses_real_gestures_and_reads_only C 1/1 W 1/1, R41_a_planted_copy_of_the_gate_script_is_reported C 4/4 W 4/4, R41_a_planted_copy_of_a_helper_the_gate_runs_is_reported C 2/2 W 2/2 | PASS |
| 94 | 1301 | @R43 @both | The name in the title and the top bar | R43_the_name_in_the_title_and_the_top_bar C 1/1 W 1/1 | PASS |
| 95 | 1308 | @R44 @static | The sprite and the mark are the golden's bytes | R44_the_sprite_and_the_mark_are_the_goldens_bytes C 1/1 W 1/1 | PASS |
| 96 | 1315 | @R44 @both | The sprite comes first and the empty receipt uses the mark | R44_the_sprite_comes_first_and_the_empty_receipt_uses_the_mark C 1/1 W 1/1 | PASS |
| 97 | 1322 | @R45 @static | The tab icon file is the golden's icon | R45_the_tab_icon_file_is_the_goldens_icon C 1/1 W 1/1 | PASS |
| 98 | 1330 | @R45 @both | The tab icon loads under the live policy | R45_the_tab_icon_loads_under_the_live_policy C 1/1 W 1/1 | PASS |
| 99 | 1337 | @R45 @per_engine | The tab icon's colour follows the colour scheme | R45_the_tab_icon_colour_follows_the_colour_scheme C 1/1 W 1/1 (WebKit `icon-colour.txt` equals the baseline's) | PASS |
| 100 | 1346 | @R46 @both | (a) A cold boot with working storage shows no warning | R46_a_cold_boot_with_working_storage_shows_no_warning C 1/1 W 1/1 | PASS |
| 101 | 1352 | @R46 @both | (b) The first failed save shows the warning | R46_the_first_failed_save_shows_the_warning C 1/1 W 1/1 | PASS |
| 102 | 1361 | @R46 @both | (c) The warning stays while saves fail, and a reload starts without it | R46_the_warning_stays_while_saves_fail_and_a_reload_starts_without_it C 1/1 W 1/1 | PASS |
| 103 | 1370 | @R47 @both | (d) The first save that works removes the warning | R47_the_first_save_that_works_removes_the_warning C 1/1 W 1/1 | PASS |
| 104 | 1378 | @R46 @both | (e) A failed boot read shows the warning in the first render | R46_a_failed_boot_read_shows_the_warning_in_the_first_render C 2/2 W 2/2 | PASS |
| 105 | 1390 | @R46 @R27 @both | (f) An unreadable draft whose reset save fails shows both notes, the warning first | R46_an_unreadable_draft_whose_reset_save_fails_shows_both_notes_the_warning_first C 1/1 W 1/1 | PASS |
| 106 | 1399 | @R47 @both | SW6. A storage object that comes back clears the warning without a reload | R47_a_storage_object_that_comes_back_clears_the_warning_without_a_reload C 1/1 W 1/1 | PASS |
| 107 | 1407 | @R47 @both | SW4. Only a save attempt decides, so a change that writes nothing leaves the warning | R47_a_change_that_writes_nothing_leaves_the_warning C 1/1 W 1/1 | PASS |
| 108 | 1416 | @R46 @both | SW7. The warning's live region is not touched on every keystroke | R46_the_warnings_live_region_is_not_touched_on_every_keystroke C 1/1 W 1/1 | PASS |
| 109 | 1423 | @R46 @R47 @both | D-d. A real full storage shows the warning, and room again clears it | R46_a_real_full_storage_shows_the_warning_and_room_again_clears_it C 1/1 W 1/1 | PASS |
| 110 | 1433 | @R47 @static | The app reads no error name and probes nothing | R47_the_app_reads_no_error_name_and_probes_nothing C 1/1 W 1/1 | PASS |
| 111 | 1443 | @R48 @both | Which section is open on load | R48_which_section_is_open_on_load C 7/7 W 7/7 | PASS |
| 112 | 1457 | @R48 @both | A header row toggles by click, Enter and Space | R48_a_header_row_toggles_by_click_enter_and_space C 1/1 W 1/1 | PASS |
| 113 | 1469 | @R48 @both | The People summary fits its row | R48_the_people_summary_fits_its_row C 4/4 W 4/4 | PASS |
| 114 | 1480 | @R48 @both | The People summary refits when its row's width changes | R48_the_people_summary_refits_when_its_rows_width_changes C 1/1 W 1/1 | PASS |
| 115 | 1486 | @R48 @both | The Charges summary names a rate that blocks | R48_the_charges_summary_names_a_rate_that_blocks C 5/5 W 5/5 | PASS |
| 116 | 1500 | @R48 @both | The Charges summary follows each keystroke, not the error timing | R48_the_charges_summary_follows_each_keystroke_not_the_error_timing C 1/1 W 1/1 | PASS |
| 117 | 1508 | @R48 @both | Only the header row and Start new bill open or fold a section | R48_only_the_header_row_and_start_new_bill_open_or_fold_a_section C 1/1 W 1/1 | PASS |
| 118 | 1516 | @R48 @both | On the desktop both sections show with their own headings | R48_on_the_desktop_both_sections_show_their_own_headings C 1/1 W 1/1 | PASS |
| 119 | 1522 | @R49 @both | The strip for each result | R49_the_strip_for_each_result C 7/7 W 7/7 | PASS |
| 120 | 1538 | @R49 @both | No control the user tabs to is left under the strip | R49_no_control_the_user_tabs_to_is_left_under_the_strip C 1/1 W 1/1 | PASS |
| 121 | 1546 | @R49 @both | The app scrolls a focused control only below 1024 px and only when the strip covers it | R49_the_app_scrolls_a_focused_control_only_below_1024_px_and_only_when_the_strip_covers_it C 1/1 W 1/1 | PASS |
| 122 | 1559 | @R50 @both | The Splits sheet opens with the card's receipt | R50_the_splits_sheet_opens_with_the_cards_receipt C 1/1 W 1/1 | PASS |
| 123 | 1569 | @R50 @both | Closing the sheet returns focus to Splits | R50_closing_the_sheet_returns_focus_to_splits C 4/4 W 4/4 | PASS |
| 124 | 1582 | @R50 @both | A press that starts in the sheet and ends on the backdrop does not close it | R50_a_press_that_starts_in_the_sheet_and_ends_on_the_backdrop_does_not_close_it C 1/1 W 1/1 | PASS |
| 125 | 1588 | @R50 @both | A repeat press on Splits leaves the sheet open and copies nothing | R50_a_repeat_press_on_splits_leaves_the_sheet_open_and_copies_nothing C 4/4 W 4/4 | PASS |
| 126 | 1598 | @R50 @both | The second press of a double activation that closed the sheet never reaches the page | R50_the_second_press_of_a_double_activation_that_closed_the_sheet_never_reaches_the_page C 4/4 W 4/4 | PASS |
| 127 | 1611 | @R50 @both | The sheet closes itself when the window reaches 1024 px | R50_the_sheet_closes_itself_when_the_window_reaches_1024_px C 1/1 W 1/1 | PASS |
| 128 | 1619 | @R50 @both | The sheet follows the bill while it is open | R50_the_sheet_follows_the_bill_while_it_is_open C 1/1 W 1/1 | PASS |
| 129 | 1625 | @R55 @both | The desktop layout at 1280 and at 1024 | R55_the_desktop_layout_at_1280_and_at_1024 C 1/1 W 1/1 | PASS |
| 130 | 1634 | @R55 @both | The page never scrolls at 1280 x 800 | R55_the_page_never_scrolls_at_1280_by_800 C 12/12 W 12/12 | PASS |
| 131 | 1653 | @R56 @both | The item frame marks what lies above and below | R56_the_item_frame_marks_what_lies_above_and_below C 4/4 W 4/4 | PASS |
| 132 | 1664 | @R56 @both | Scrolling the frame moves the marks | R56_scrolling_the_frame_moves_the_marks C 1/1 W 1/1 | PASS |
| 133 | 1675 | @R51 @both | The spare sen line and chip | R51_the_spare_sen_line_and_chip C 5/5 W 5/5 | PASS |
| 134 | 1688 | @R51 @both | No spare sen, no line | R51_no_spare_sen_no_line C 1/1 W 1/1 | PASS |
| 135 | 1696 | @R52 @both | P1 opens from either chip with focus on the chosen rule | R52_p1_opens_from_either_chip_with_focus_on_the_chosen_rule C 2/2 W 2/2 | PASS |
| 136 | 1708 | @R52 @both | A choice applies at once and P1 stays open | R52_a_choice_applies_at_once_and_p1_stays_open C 1/1 W 1/1 | PASS |
| 137 | 1717 | @R52 @both | Arrow keys move between the three choices and focus stays on the radio | R52_arrow_keys_move_between_the_three_choices_and_focus_stays_on_the_radio C 1/1 W 1/1 | PASS |
| 138 | 1729 | @R52 @both | P1 sits beside the card on the desktop | R52_p1_sits_beside_the_card_on_the_desktop C 4/4 W 4/4 | PASS |
| 139 | 1740 | @R52 @both | On a phone P1 is a bottom sheet over the Splits sheet, and the sheet makes room | R52_on_a_phone_p1_is_a_bottom_sheet_over_the_splits_sheet_and_the_sheet_makes_room C 4/4 W 4/4 | PASS |
| 140 | 1754 | @R52 @both | The sheet scrolls so the splits stay in view above P1 | R52_the_sheet_scrolls_so_the_splits_stay_in_view_above_p1 C 1/1 W 1/1 | PASS |
| 141 | 1761 | @R52 @both | Closing P1 returns focus to the chip shown at that moment | R52_closing_p1_returns_focus_to_the_chip_shown_at_that_moment C 7/7 W 7/7 | PASS |
| 142 | 1777 | @R52 @both | A repeat click on the desktop chip leaves P1 open | R52_a_repeat_click_on_the_desktop_chip_leaves_p1_open C 1/1 W 1/1 | PASS |
| 143 | 1784 | @R52 @both | The second press of a double activation that closed P1 never reaches the page | R52_the_second_press_of_a_double_activation_that_closed_p1_never_reaches_the_page C 8/8 W 8/8 | PASS |
| 144 | 1799 | @R52 @both | P1 follows the width when it crosses 1024 px | R52_p1_follows_the_width_when_it_crosses_1024_px C 1/1 W 1/1 | PASS |
| 145 | 1808 | @R52 @both | P1 opened on the desktop and closed below 1024 px | R52_p1_opened_on_the_desktop_and_closed_below_1024_px C 1/1 W 1/1 | PASS |
| 146 | 1818 | @R53 @both | One person picks the first eligible person at once, and a pill changes it | R53_one_person_picks_the_first_eligible_person_at_once_and_a_pill_changes_it C 1/1 W 1/1 | PASS |
| 147 | 1830 | @R53 @both | Only people on an item can be chosen in By item | R53_only_people_on_an_item_can_be_chosen_in_by_item C 1/1 W 1/1 | PASS |
| 148 | 1840 | @R53 @both | A chosen person who has nothing falls back to Top of the list and stays chosen | R53_a_chosen_person_who_has_nothing_falls_back_to_top_of_the_list_and_stays_chosen C 1/1 W 1/1 | PASS |
| 149 | 1852 | @R53 @both | Removing the chosen person sets the rule back to Top of the list | R53_removing_the_chosen_person_sets_the_rule_back_to_top_of_the_list C 1/1 W 1/1 | PASS |
| 150 | 1859 | @R54 @both | At random gives the spare sen to different people, and Pick again draws again | R54_at_random_gives_the_spare_sen_to_different_people_and_pick_again_draws_again C 1/1 W 1/1 | PASS |
| 151 | 1875 | @R54 @both | Pick again that can change nothing does nothing | R54_pick_again_that_can_change_nothing_does_nothing C 1/1 W 1/1 | PASS |
| 152 | 1882 | @R54 @both | Pick again in the Splits sheet draws again | R54_pick_again_in_the_splits_sheet_draws_again C 1/1 W 1/1 | PASS |
| 153 | 1891 | @R54 @static | Math.random goes only to the two draws | R54_math_random_goes_only_to_the_two_draws C 1/1 W 1/1 | PASS |
| 154 | 1900 | @R60 @both | Large bills fit a 360 px phone | R60_large_bills_fit_a_360_px_phone C 3/3 W 3/3 | PASS |
| 155 | 1913 | @R60 @both | The large price shows whole | R60_the_large_price_shows_whole C 1/1 W 1/1 | PASS |
| 156 | 1921 | @R57 @both | A held Enter on the only item's Remove removes that item only | R57_a_held_enter_on_the_only_items_remove_removes_that_item_only C 1/1 W 1/1 | PASS |
| 157 | 1929 | @R57 @both | A held Enter on New bill leaves the dialog open on Cancel | R57_a_held_enter_on_new_bill_leaves_the_dialog_open_on_cancel C 1/1 W 1/1 | PASS |
| 158 | 1937 | @R57 @both | Separate presses still act, and a held letter still types | R57_separate_presses_still_act_and_a_held_letter_still_types C 1/1 W 1/1 | PASS |
| 159 | 1950 | @R57 @node | The repeat rule reads the click count, the pointer, the time and the place | Node run `20261016-031908`, 10 of 10 `@R57 b ...` (tests/repeat.test.js) | PASS |
| 160 | 1969 | @R57 @both | A slow second tap, or a quick tap elsewhere, is never held back | R57_a_slow_second_tap_or_a_quick_tap_elsewhere_is_never_held_back C 1/1 W 1/1 | PASS |
| 161 | 1979 | @R58 @static | The engine option and the one launch place | R58_the_engine_option_and_the_one_launch_place C 1/1 W 1/1 | PASS |
| 162 | 1989 | @R58 @gate | A Chromium-only test is a counted skip in WebKit | `20261016-032255-webkit/skips.txt` count 3 equals junit skipped 3, `20261016-031917-chromium/pytest.txt` PASSED for the three chromium_only tests | PASS |
| 163 | 1999 | @R58 @static | A suite run never writes into an evidence folder it did not make (new since step 5) | R58_a_run_never_writes_into_an_evidence_folder_it_did_not_make C 1/1 W 1/1 | PASS |
| 164 | 2005 | @R58 @R41 @gate | The live gate records its engine | `20261016-033527-webkit/summary.json` engine webkit, 26.5, and the bare run `20261016-033656-chromium` | PASS |
| 165 | 2011 | @R59 @per_engine | Focus after a mouse click is the engine's own | R59_focus_after_a_mouse_click_is_the_engines_own C 1/1 W 1/1 | PASS |
| 166 | 2023 | @R59 @gate | The A0 baseline record is complete | `qa/webkit-baseline/20261014-130011/` checked on disk | PASS |
| 167 | 2039 | @R9 @R11 @chromium_only | The accessible description of the amount fields is measured and reported (QA-S5-1, now has its test) | R9_the_accessible_description_of_the_amount_fields_is_measured_and_reported C 1/1 W 0 pass 1 skip (counted, reason in skips.txt) | PASS |
| 168 | 2048 | @R61 @node | The decoder accepts versions 1 and 2 and checks the spare choice | Node run `20261016-031908`, 4 `@R61 D3/D13/D14` tests (tests/draft.test.js) | PASS |
| 169 | 2062 | @R61 @node | Saving writes version 2, and load and save report failures | Node run `20261016-031908`, `@R61 encodeDraft writes version 2 ...` and `@R27 loadDraft tells none ...` | PASS |
| 170 | 2078 | @R62 @R5 @both | A control or bidi character put into a person's name is removed at once (new) | R62_a_control_or_bidi_character_put_into_a_persons_name_is_removed_at_once C 5/5 W 5/5 | PASS |
| 171 | 2094 | @R62 @R33 @both | A removal in the middle of a name keeps the caret where the text went in (new) | R62_a_removal_in_the_middle_of_a_name_keeps_the_caret_where_the_text_went_in C 1/1 W 1/1 | PASS |
| 172 | 2102 | @R62 @both | Each kind of character in the class is removed from a name field (new) | R62_each_kind_of_character_in_the_class_is_removed_from_a_name_field C 1/1 W 1/1 | PASS |
| 173 | 2111 | @R62 @both | Characters outside the class stay in a name (new) | R62_characters_outside_the_class_stay_in_a_name C 1/1 W 1/1 | PASS |
| 174 | 2119 | @R62 @R33 @both | Typing that brings no character of the class writes nothing into the field (new) | R62_typing_that_brings_no_character_of_the_class_writes_nothing_into_the_field C 1/1 W 1/1 | PASS |
| 175 | 2126 | @R62 @R11 @both | An item name loses the class too (new) | R62_an_item_name_loses_the_class_too C 1/1 W 1/1 | PASS |
| 176 | 2133 | @R62 @R4 @both | A name made only of removed characters falls back to its position (new) | R62_a_name_made_only_of_removed_characters_falls_back_to_its_position C 1/1 W 1/1 | PASS |
| 177 | 2140 | @R62 @R26 @R48 @both | A saved name with bidi controls loads plain and the People line reads left to right (new) | R62_a_saved_name_with_bidi_controls_loads_plain_and_the_people_line_reads_left_to_right C 1/1 W 1/1 | PASS |
| 178 | 2152 | @R62 @R61 @node | The decoder rebuilds names without the class (new) | Node run `20261016-031908`, 7 `@R62 @R61 decodeDraft ...` (tests/draft.test.js) | PASS |
| 179 | 2168 | @R62 @R33 @node | plainNameField puts the caret where the text went in (new) | Node run `20261016-031908`, 6 `@R62 @R33 plainNameField ...` (tests/dom.test.js) | PASS |
| 180 | 2190 | @R27 @R7 @both | A repeat press on Dismiss note acts as one press at every width (new) | R27_a_repeat_press_on_dismiss_note_acts_as_one_press_at_every_width C 12/12 W 12/12 | PASS |
| 181 | 2215 | @R27 @R57 @both | A held Enter on Dismiss note reaches nothing (new) | R27_a_held_enter_on_dismiss_note_reaches_nothing C 2/2 W 2/2 | PASS |

### Verdict per R#
A scenario counts for every R# in its tags. R40 is PASS for this lane, with the checklist half of #87 outside it.

| R# | scenarios | verdict |
|---|---|---|
| R1 | 1, 2 | PASS |
| R2 | 3, 4 | PASS |
| R3 | 5, 6 | PASS |
| R4 | 7, 8, 176 | PASS |
| R5 | 8, 9, 10, 170 | PASS |
| R6 | 11, 12, 17 | PASS |
| R7 | 13, 14, 16, 19, 180 | PASS |
| R8 | 21, 22 | PASS |
| R9 | 23, 167 | PASS |
| R10 | 24, 25, 26, 27, 28, 29, 30, 32 | PASS |
| R11 | 33, 167, 175 | PASS |
| R12 | 18, 19, 34 | PASS |
| R13 | 29, 31, 35 | PASS |
| R14 | 36 | PASS |
| R15 | 37, 38, 39 | PASS |
| R16 | 40 | PASS |
| R17 | 41 | PASS |
| R18 | 42 | PASS |
| R19 | 39, 43 | PASS |
| R20 | 44, 45, 46 | PASS |
| R21 | 47, 48 | PASS |
| R22 | 49, 50 | PASS |
| R23 | 51, 52 | PASS |
| R24 | 53 | PASS |
| R25 | 54, 55 | PASS |
| R26 | 56, 57, 58, 177 | PASS |
| R27 | 59, 60, 105, 180, 181 | PASS |
| R28 | 61 | PASS |
| R29 | 62, 64, 67 | PASS |
| R30 | 63, 65, 66 | PASS |
| R31 | 68, 69, 70 | PASS |
| R32 | 71, 72 | PASS |
| R33 | 73, 74, 171, 174, 179 | PASS |
| R34 | 15, 75 | PASS |
| R35 | 76 | PASS |
| R36 | 77, 78 | PASS |
| R37 | 79, 80 | PASS |
| R38 | 81, 82, 83 | PASS |
| R39 | 84, 85, 86 | PASS |
| R40 | 87 (pixel half PASS, checklist half not run here), 88, 89, 90 | PASS for this lane |
| R41 | 91, 92, 93, 164 | PASS |
| R42 | 20 | PASS |
| R43 | 94 | PASS |
| R44 | 86, 95, 96 | PASS |
| R45 | 97, 98, 99 | PASS |
| R46 | 100, 101, 102, 104, 105, 108, 109 | PASS |
| R47 | 103, 106, 107, 109, 110 | PASS |
| R48 | 111, 112, 113, 114, 115, 116, 117, 118, 177 | PASS |
| R49 | 119, 120, 121 | PASS |
| R50 | 122, 123, 124, 125, 126, 127, 128 | PASS |
| R51 | 133, 134 | PASS |
| R52 | 135 to 145 | PASS |
| R53 | 146, 147, 148, 149 | PASS |
| R54 | 150, 151, 152, 153 | PASS |
| R55 | 129, 130 | PASS |
| R56 | 131, 132 | PASS |
| R57 | 156, 157, 158, 159, 160, 181 | PASS |
| R58 | 161, 162, 163, 164 | PASS |
| R59 | 30, 165, 166 | PASS |
| R60 | 154, 155 | PASS |
| R61 | 58, 59, 168, 169, 178 | PASS |
| R62 | 170 to 179 | PASS |

### Not done
- The FE element checklist (the second half of #87), the fidelity finder's.
- Any device check (an iPhone or Android phone, a screen reader). See QA-S5-4 and QA-S5-5.
- The README and BUILD.md reconciles (the orchestrator's).
- I did not read each test body against every clause of its Then lines, which is the code review finder's work. A scenario is PASS when the tests named for it passed in this run in each engine it names (a `@chromium_only` scenario in Chromium with the WebKit skip counted), or when I observed the run directly (the gates and the records).
