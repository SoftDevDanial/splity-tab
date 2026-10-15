# Handoff. Split v1.1.0 execute, task A17 (the held-key guard and the tap-safe repeat rule R57 (b)), not started

Written 2026-10-14 20:40 by the frontend developer role. A3 is committed (`695bff5`). The brief said not to start a new task past about 30 percent context, and this session was at about 37 percent when A3 closed, so A17 goes to a fresh agent. Nothing of A17 is written. The working tree holds only the orchestrator's own modified files (`CLAUDE.md`, `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`) and the untracked run folders the brief lists as not mine.

## Where it stands
- HEAD `695bff5`, A0 to A3 and C1 to C6 done. Build order A17 next, then A4 to A16, A18 to A20.
- Node 369 of 369. Chromium `docs/modules/split-app/qa/functional/20261014-202551-chromium/`, 402 passed, 99 xfailed. WebKit `docs/modules/split-app/qa/functional/20261014-202809-webkit/`, 366 passed, 35 failed, 1 skipped (IME), 99 xfailed. That WebKit run is A17's RED baseline by id.
- The 35. H-04 class (a) 30, A17's. Class (b) 4, A6 and A16's (`test_R29_the_dialog_opens_with_the_safe_choice_focused`, `test_R30_leaving_the_dialog_without_starting_over[escape]`, `test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[service-touch]` and `[sst-touch]`). F-A3-1, 1, `test_R30_leaving_the_dialog_without_starting_over[cancel]`, a WebKit timing race on the dialog's `close` event under full suite load (0 of 10 failures alone), recorded in BUILD.md A3, not H-04.
- `test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[escape]` (class (b)) passes in WebKit since A3's dark and reduce default.

## The H-04 ids A17 must account for (spec task A17, three groups)
1. The 43 of A0 (`qa/functional/20261014-125604-webkit/`). Still failing at A3, 24. `test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page` touch-double centre and right-edge at 1 and 4 items, three widths (12). `test_R29_a_repeat_press_on_new_bill_leaves_the_dialog_open` touch-double, three widths (3). `test_R30_a_double_click_or_double_tap_on_cancel_changes_nothing[375x667-touch]` and `[412x732-touch]` (2). `test_R30_the_second_click_of_a_double_activation_never_reaches_the_page` Cancel, Start new bill, backdrop touch (3). `test_R7_a_double_click_or_double_tap_on_remove_removes_one_row` item-2-of-4 and person-2-of-5 touch (2). `test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item` 375 and 390 touch-double (2).
2. The 19 that pass in WebKit only by layout (ledger S5 row 7). `test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it` touch-double-right-edge at 2 to 5 people, three widths (12). `test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing` S2 person 3 of 3 and S8 person 12 of 12 touch, three widths (6). `test_R30_a_double_click_or_double_tap_on_cancel_changes_nothing[360x640-touch]` (1). They count only through the body recorder's proof (qa.md Phrases, "A body recorder", every press after the first has `defaultPrevented` true after its dispatch), so A17 adds that check to these 1.0 tests (spec A17, the ORCH change of 2026-10-14).
3. The 6 new at A2. `test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing` touch-double on `S1-item-4-of-4` and `S1-only-item` at 1280x800, 390x844, 360x640.

## Where things are
- `src/ui/dom.js`. `isRepeatClick` (today `event.detail > 1`) and `swallowRepeatClicks` (mousedown and click capture listeners on `document`, no keydown yet, so R57 (a) is not built either).
- `src/main.js`. Boot, where the two `window` capture listeners of R57 (b) go, added once.
- `tests/browser/test_app.py`. The 1.0 body recorder is `RECORD_BODY_CLICKS_JS` (about line 2029, its double tap is two `page.touchscreen.tap` calls), and `RECORD_CLICKS_JS` (about line 1872) for R10. The R30 double tap tests start about line 2066, R7 middle Remove about line 2157.
- Node RED method, `docs/modules/split-core/qa.md`, How to run, "RED first for a new or changed case". The `@R57 @node` table has 10 rows in qa.md, section "Double taps".
- qa.md scenarios A17 adds. The three "Held keys" scenarios (`@R57 @both`), "A slow second tap, or a quick tap elsewhere, is never held back" (`@R57 @both`, has_touch, 600 ms wait, the gap checks), and the `@node` table.

## A trap worth knowing before writing the listeners (from reading R57 (b), not measured)
The window capture listener runs before the document capture guard for the same `click`. If it overwrote "the previous pointer click" with the click being judged, the rule would compare a click with itself and every tap click would be a repeat. "The previous pointer click is the last click ... before this event", so either keep the last two clicks and skip the one whose event is the one being judged, or record a click as previous only once the next event is judged. It must still record a click the guard cancels (R57 (b) 2, "whether it acted or the guard cancelled it"), which is why it sits in the capture phase on `window`. A tap's `click` in WebKit reports `pointerType` "mouse", so the tap flag comes from the last `pointerdown` (R57 (b), the 2 to 3 line "looks wrong but is not" comment belongs there).

## Open items carried from A3 (BUILD.md, A3)
- Q-A3-1. The R47 `@static` scan bans "removeItem(", which also matches split-core's `removeItem(bill, itemId)`. The test bans `.removeItem(`. Recommended, qa.md reads ".removeItem(".
- F-A3-1. Recommended, A16 waits for the `close` event after every R30 close it reads focus from, or `closeByClick` focuses the opener at once.

## Resume here
1. Load the design row (`taste-skill`, `frontend-design`) and declare what transferred.
2. RED. The `@node` table by the stub method, the new `@R57 @both` scenarios and the recorder check on the 19, seen failing in WebKit (the second tap reaches the page) on their asserted property. Record each run folder.
3. Build R57 (a) and (b), run Node, Chromium and WebKit, compare WebKit by id with `20261014-202809-webkit`. No H-04 failure may remain, any left is a finding.
4. BUILD.md A17 section with the three groups by id, tick A17 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A17, R57, R6, R7, R12, R29, R30)`.

## Processes
None alive at writing. Every pytest server and the render check's server were stopped by their own `finally` (each printed STOPPED with the port free again). The background runs `b96v4pj58`, `bird5iq0l` and `biykeyll1` completed.
