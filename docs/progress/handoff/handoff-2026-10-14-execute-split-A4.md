# Handoff. Split v1.1.0 execute, task A4 (sections, header rows, folds and the reveal), not started

Written 2026-10-14 21:20 by the frontend developer role. A17 is committed (`22cc845`). The brief said to stop before a new task past about 30 percent context, and this session was at about 30 percent when A17 closed, so A4 goes to a fresh agent. Nothing of A4 is written. The working tree holds only the orchestrator's own modified files (`CLAUDE.md`, `docs/progress/*`, `docs/v1.1.0/CHANGE-LEDGER.md`), the untracked run folders the brief lists as not mine and the untracked handoffs.

## Where it stands
- HEAD `22cc845`. A0 to A3, A17 and C1 to C6 done. Build order A4 next, then A5 to A16, A18 (A19 and A20 are not this builder's).
- Node 379 of 379 (`docs/modules/split-app/qa/unit/20261014-210527/node-test.txt`). Chromium `docs/modules/split-app/qa/functional/20261014-210531-chromium/`, 406 passed, 101 xfailed, 0 failed. WebKit `docs/modules/split-app/qa/functional/20261014-210807-webkit/`, 401 passed, 4 failed, 1 skipped (IME), 101 xfailed. That WebKit run is A4's baseline by id.
- The 4 WebKit failures are the class (b) ids A6 and A16 own (`test_R29_the_dialog_opens_with_the_safe_choice_focused`, `test_R30_leaving_the_dialog_without_starting_over[escape]`, `test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[service-touch]` and `[sst-touch]`). F-A3-1 (`test_R30_leaving_the_dialog_without_starting_over[cancel]`, A16) did not show in that run and may show in a later one.
- No H-04 failure is left. From A4 on any H-04 failure in WebKit is a finding (spec Tasks, the paragraph after the Tasks rule), sorted as A0 sorted.

## What A4 is (spec task A4, one line)
"Sections. Header rows, open on load (CG-P4), toggle by click, Enter and Space, the two summaries with the fitted People text and the Check marker, the reveal through the Web Animations API, restore folds. -> R48, R26". Read R48 in `docs/modules/split-app/spec.md` whole, the eight `@R48` scenarios in `docs/modules/split-app/qa.md`, and the goldens `docs/design/bill-items.html` (folded) and `docs/design/bill-items-open.html` (open) with their `.md` files. The design row (`taste-skill`, `frontend-design`) loads first, A4 draws UI.

## Where things are
- `src/main.js` boot and `render`. `src/ui/people.js`, `src/ui/charges.js` hold the 1.0 People and Charges blocks, wrapped by `block` in `src/ui/dom.js`. A4 builds the `div.blk.sec` wrapper, the header row and the body around them (R48), A5 and A6 rebuild the content.
- `tests/browser/test_app.py`. `open_people_first` (A3 block) clicks `#peopleBtn` only when it exists, is shown and is folded, so from A4 it starts to act (CG-P4 opens both on load, so it should still do nothing on a cold page). `test_R38_code_writes_style_only_to_the_four_allowed_targets` is `xfail(strict=True, reason="task A4")`, the reveal's Web Animations API use is what it waits for. The R3 pair `bill-items-open` waits for A11, not A4.
- `support.py` `card_text`, `reads`, `open_golden` (dark and reduce) for render checks against the goldens.

## Traps worth knowing (measured in A17)
- WebKit sends a tap's mouse events only to content it sees as clickable. A tap on plain text or an empty `li` sends `pointerdown` alone (R59 (3)). A click or mousedown listener on `body` (the test's body recorder) makes everything clickable, so a test that adds the recorder changes what a WebKit tap does. A `window` listener does not (probe in A17's BUILD.md section, judgment call 6).
- `swallowRepeatClicks` now also listens to `keydown` while armed and cancels a keydown with `repeat` true. A header toggled by Enter or Space after a guarded click is not held back, because its first keydown has `repeat` false and ends the guard. Only the repeats of a hold that itself made the guarding click are cancelled (a held Enter on a Remove, Add person, Add item or New bill).
- A click and a tap less than 500 ms apart and within 22 px count as one press when the second is a tap (R57 (b)). A test that clicks with the mouse and then taps the same spot at once gets its tap held back while a guard is armed or on a Remove. Mouse clicks are never held back by time.
- Marks A4 does not remove but should know. `test_R57_a_slow_second_tap_and_a_quick_tap_elsewhere_change_the_draft_as_two_presses` is `xfail` A5 (Add person must stay under the point). `test_R57_after_a_held_enter_on_the_only_remove_the_strip_reads_the_empty_message` is `xfail` A11.

## Open items carried
- Q-A3-1 (BUILD.md A3). The R47 `@static` scan bans "removeItem(", the test bans `.removeItem(`, ruled ORCH, qa wording at the next planner touch.
- F-A3-1 (BUILD.md A3). A16 waits for the `close` event after every R30 close it reads focus from.
- A17 judgment call 1. The qa scenario "A held Enter on New bill leaves the dialog open on Cancel" passes on 1.0 by its end state alone (four repeats close and open the dialog twice). The test counts `close` events and requires 0. Recommended qa wording, "and the dialog never closed while the key was held".
- A17 judgment call 4. "#addItem has focus" is checked by the accessible name "Add item" until A8 gives the button its id.

## Resume here
1. Load the design row and declare what transferred.
2. RED. The `@R48` scenarios as tests, seen failing on their asserted property against `22cc845` in Chromium and WebKit, each run folder recorded. Remove the A4 mark on `test_R38_code_writes_style_only_to_the_four_allowed_targets` only once it passes.
3. Build R48 and the R26 restore of folds, render check against `bill-items.html` and `bill-items-open.html`, then Node, Chromium and WebKit, WebKit compared by id with `20261014-210807-webkit/`.
4. BUILD.md A4 section, tick A4 in spec.md, credential sweep `--staged`, commit `feat(split-app): ... (task A4, R48, R26)`.

## Processes
None alive at writing. Every pytest server and every probe server was stopped by its own `finally` (each printed STOPPED with the port free again). The background WebKit run `bskqfykbk` completed with exit 0.
