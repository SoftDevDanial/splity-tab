# Handoff. Split v1.1.0 execute, task A5 (People), not started

Written 2026-10-14 22:12 by the frontend developer role. A4 is committed (`7dac4de`). The brief said to stop before a new task past about 30 percent context, and this session was at about 46 percent when A4 closed, so A5 goes to a fresh agent. Nothing of A5 is written. The working tree holds only the orchestrator's own modified files (`CLAUDE.md`, `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`), the untracked run folders the brief lists as not mine and the untracked handoffs.

## Where it stands
- HEAD `7dac4de`. A0 to A4, A17 and C1 to C6 done. Build order A5 next, then A6 to A16, A18 (A19 and A20 are not this builder's).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261014-215728/node-test.txt`). Chromium `docs/modules/split-app/qa/functional/20261014-215658-chromium/`, 431 passed, 102 xfailed, 0 failed. WebKit `docs/modules/split-app/qa/functional/20261014-220149-webkit/`, 426 passed, 4 failed, 1 skipped (IME), 102 xfailed. That WebKit run is A5's baseline by id.
- The 4 WebKit failures are the class (b) ids A6 and A16 own (`test_R29_the_dialog_opens_with_the_safe_choice_focused`, `test_R30_leaving_the_dialog_without_starting_over[escape]`, `test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[service-touch]` and `[sst-touch]`). F-A3-1 (`test_R30_leaving_the_dialog_without_starting_over[cancel]`, A16) did not show in that run and may show in a later one.
- No H-04 failure. Any H-04 failure in WebKit is a finding, sorted as A0 sorted.

## What A5 is (spec task A5, one line)
"People. Rows, live names, Add person and Remove with limits, the disabled look, focus, duplicates, typing keeps focus. It rewrites the two 1.0 `test_R6_*` tests that read `states.html` (B1). -> R4, R5, R6, R7, R33, R34, R42". Read R4 to R7, R33, R34 and R42 in `docs/modules/split-app/spec.md` whole, their `@R4` to `@R7`, `@R33`, `@R34` and `@R42` scenarios in `docs/modules/split-app/qa.md`, the DOM contract of `#peopleBlk` (the `div.blk-head` with `h2.blk-h#peopleH` and `button.btn.btn-ghost#addPerson`, then `ul.people#peopleList`), and the goldens `docs/design/bill-items.html`, `bill-items-open.html` and `bill-twelve.html` with their `.md` files. The design row (`taste-skill`, `frontend-design`) loads first, A5 draws UI.

## Where things are
- `src/ui/sections.js` (A4). `createPeopleSection(content, onToggle)` takes the section's content as an array of nodes and puts it in `div.sec-in.people-in`. Today `src/main.js` passes `[people.el]`, the 1.0 `section.block` from `createPeople` in `src/ui/people.js` (with `h2.block-title#h-people`, `ul.cells` and Add person in the last cell). A5 rebuilds that content to the DOM contract and passes its nodes instead. The CSS puts `.people-in > .blk-head` after the list below 1024 px (`order: 1`). The People summary refits on every render through `update(bill, open)`, so live names reach it with no extra work (R5).
- `tests/browser/test_app.py`. Marked `task A5`, `test_R6_add_person_until_the_limit`, `test_R6_a_restored_twelve_person_bill_shows_the_limit_state` (the two `states.html` readers, B1), `test_R7_a_separate_click_on_what_slid_under_the_pointer_is_not_held_back` and `test_R57_a_slow_second_tap_and_a_quick_tap_elsewhere_change_the_draft_as_two_presses`. `test_R48_on_the_desktop_both_sections_show_their_own_headings` waits for `h2#peopleH` (A5) and `h2#chargesH` (A6), so it stays marked A6.
- Helpers from A4. `open_first(page, key)`, `open_people_first`, `open_charges_first` (qa.md "Open People first"), `opened_rate_field(label)`, `section_state`, `displayed`, `visible_text`, `settled_text`, `start_over`. A restored bill folds People below 1024 px, so every People test on a seed needs `open_people_first`. A4 added it to the 1.0 R6, R7 and R34 families (BUILD.md, A4, Tests).

## Traps worth knowing
- The 1.0 RG-CR-01 premise. `test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it` says the new row's Remove slides under the right 44 px of Add person, because 1.0 Add person sits in the grid cell the new row takes. In v1.1.0 Add person moves to the heading row (below the list on a phone), so read the qa.md v1.1.0 form of that scenario before rewriting, and keep the recorder proof (`assert_only_press_1_and_click_1_reached_the_page`).
- 1.0 selectors that A5 retires. `section[aria-labelledby=h-people] ul.cells` in `test_R6_a_restored_twelve_person_bill_shows_the_limit_state` and in `LAYOUT_JS` (R35, xfail A18), `li.person` (the v1.1.0 rows are `li.field.person`, still matched), `SNAPSHOT_JS` reads `li.person input`.
- WebKit sends a tap's mouse events only to content it sees as clickable (R59 (3)). A body recorder makes everything clickable (A17 judgment call 6).
- The header row click is a mouse click that `watchPointerClicks` records as the previous pointer click. A tap within 22 px and 500 ms of it would count as a repeat by R57 (b). No test hits it today, because the People rows sit more than 22 px below the row.
- With no-preference, the strip foil's finished `CSSAnimation` stays in `document.getAnimations()` (fill `both`), so "getAnimations() is empty" never holds after load (F-A4-1). Read "no animation is running" instead, as `nothing_runs_within` does.

## Open items carried
- F-A4-1 (BUILD.md A4). qa.md R36 "3 s after load it is empty" cannot hold with the golden CSS. Recommended wording for A18, "no animation is running".
- Q-A3-1 (BUILD.md A3). The R47 `@static` scan bans "removeItem(", the test bans `.removeItem(`, ruled ORCH, qa wording at the next planner touch.
- F-A3-1 (BUILD.md A3). A16 waits for the `close` event after every R30 close it reads focus from.
- A17 judgment call 1. Recommended qa wording "and the dialog never closed while the key was held".
- A17 judgment call 4. "#addItem has focus" is checked by the accessible name "Add item" until A8 gives the button its id.

## Resume here
1. Load the design row and declare what transferred.
2. RED. The A5 scenarios as tests, seen failing on their asserted property (throwaway stubs where the code of `7dac4de` cannot reach the property, never committed), in Chromium and WebKit, each run folder recorded. Remove the A5 marks only once each passes.
3. Build R4 to R7, R33, R34 and R42 into the People section content, render check against `bill-items-open.html` and `bill-twelve.html`, then Node, Chromium and WebKit, WebKit compared by id with `20261014-220149-webkit/`.
4. BUILD.md A5 section, tick A5 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A5, R4, R5, R6, R7, R33, R34, R42)`.

## Processes
None alive at writing. Every pytest server, the render server and both probe servers were stopped by their own `finally` (each printed STOPPED with the port free again). The two background suite runs (`bsz57zo5x` Chromium, `bctguh306` WebKit) and the background sorting run (`bx431fz7i`) completed with exit 0.
