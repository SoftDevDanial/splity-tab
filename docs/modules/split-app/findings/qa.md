---
module: split-app
kind: qa
ran_against: running-app
status: issues_found
counts: { pass: 165, fail: 1, blocked: 0, not_run: 1 }
date: 2026-10-15
head: d58f4ce
node_run: docs/modules/split-core/qa/unit/20261015-204618/node-test.txt
chromium_run: docs/modules/split-app/qa/functional/20261015-204624-chromium/
webkit_run: docs/modules/split-app/qa/functional/20261015-205019-webkit/
live_gate_runs: docs/modules/split-app/qa/live-e2e/20261015-205837-chromium-control/, 20261015-205844-chromium/, 20261015-205925-webkit-control/, 20261015-205931-webkit/, 20261015-205954-chromium/
accessible_description_run: docs/modules/split-app/qa/accessible-description/20261015-205800/
---
# QA findings: split-app (v1.1.0, step 5)

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
