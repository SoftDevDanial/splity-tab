# Evidence: security solver, split-app, 2026-10-09

Role: Security Solver. Start `06fa151` (the audit commit), tree clean. Orders: the five ORCH rulings of 2026-10-09 (reversible).
This folder holds the red and green runs, the mutants, the regression re-run of the audit's own sweep, the measurements behind the
doc pass, the junit files, the scratch live-gate run and the process notes. Every browser context came from `rig.new_context`
(clipboard recorder on, `permissions` and `bypass_csp` refused; the probes add a second guard that rejects `readText`, `read` and
`write`). The operating system clipboard was never read, written or granted (CG-7). Every file in the project was written with the
Write and Edit tools. Mutants were applied and reverted with Edit and checked with `git diff --quiet` against the index.

## Result at a glance
| Ruling | Result | Commit |
|---|---|---|
| 1. SEC-01 (MEDIUM) | RESOLVED | `071577a` |
| 2. I-1 | RESOLVED, no other behaviour changed | `68ab318` |
| 3. SEC-02 (LOW) | RESOLVED (Publish section, Invariants note) | `314b827` |
| 4. SEC-03 (LOW) | ACCEPTED residual, recorded in `spec.md`, no code | `314b827` |
| 5. Spec gaps, doc pass | DONE (threat-model rows, U+2028 residual, CR and LF row, R7 R29 R30 notes) | `314b827`, `12bc878` (qa.md, BUILD.md) |

Suites. Start: browser 244 passed (86.44 s), unit 275 passed (`junit-browser-baseline.xml`). End: browser 312 passed (113.34 s,
`junit-browser-final.xml`), unit 275 passed (`junit-node-final.xml`). Fidelity 10 of 10 at 0 mismatching pixels
(`docs/modules/split-app/qa/fidelity/20261009-212142/`). Live gate 7 of 7 (`live-gate-check/20261009-212227/`, a scratch folder here, the
official `qa/live-e2e/` was not written).

## Ruling 1: SEC-01, the Remove handlers use the shared guard
Change (`071577a`): `swallowRepeatClicks` moved from `src/ui/dialog.js` to `src/ui/dom.js` (exported), `dialog.js` imports it, and the
Remove handlers of `people.js` and `items.js` call `swallowRepeatClicks(); onRemove(id);` in place of the `isRepeatClick` test.
`isRepeatClick` is now private to `dom.js` (the guard is its only user). The comments that the move made untrue were rewritten in the
same patch (the `isRepeatClick` doc said "the handlers that do either ignore it", the Remove comment named `isRepeatClick`, the
`dialog.js` comment about the guard moved to `dom.js`).

New tests (54), in `tests/browser/test_app.py` under "Security SEC-01":
- `test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing`: 4 bills (S2 remove Chen, S8 remove Mei Ling, S1 remove
  the last of 4 items, S1 with only its last item) x 3 sizes (360x640, 390x844, 1280x800) x 4 gestures (single click as the control,
  mouse double click, mouse triple click, touch double tap) = 48 rows. Each checks the row count, the stored draft equal to the bill one
  click leaves (no blank row, `nextId` unchanged) and where focus is (R34).
- `test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it` (4), `test_R7_a_separate_click_on_what_slid_under_the_pointer_is_not_held_back`
  (1), `test_R7_the_guard_of_a_remove_click_ends_at_the_next_press` (1, asserts both clicks of a later double click reach the page).
- The existing WR-01 (`test_R7_a_double_click_or_double_tap_on_remove_removes_one_row`, `..._two_separate_clicks_and_a_key_press_...`) and
  CR-01 tests stayed green without a change.

RED on the unfixed `src/` (run on `06fa151` sources with the new tests in place, `junit-new-tests-red.xml`, 68 selected: 54 for SEC-01 and 14 for I-1):
52 failed, 16 passed. For SEC-01 40 of 40 rows failed (read from the junit file, first failing assertion of each):
- the 18 people rows (S2 and S8, 3 sizes, 3 gestures) failed on the row count: `3 == (3 - 1)` for S2 and `12 == (12 - 1)` for S8, because Chen or
  Mei Ling went and a blank person came back (the stored draft was not reached, the count check comes first);
- the 18 item rows (S1 last of 4, S1 only item) passed the row count and the stored-draft check, as the audit said (no data change), and failed on the
  focus check: focus ended on the page body instead of `Item 3 name` or `Add item`;
- the 4 R34 rows (mouse and touch, item 2 of 4 and person 2 of 5) failed on focus: it ended on the next row's Remove button (`Remove Mee goreng mamak`,
  `Remove P3`) instead of the name field, which is the audit's "focus drift".
The 16 that passed are the controls: the 12 single-click rows, the separate-click test, the guard-lifetime test, and the two I-1 controls.
GREEN (`junit-new-tests-sec01.xml`): 54 of 54. The full suite on the SEC-01 tree: 298 passed (`junit-browser-sec01.xml`).

Mutants, each applied with Edit on the staged tree, tests run, then reverted and checked equal to the index:
| Mutant | Selection run | Red |
|---|---|---|
| M1: `people.js` Remove handler without the guard | R7 and R34 tests (69) | 20: the 18 people rows (3 sizes x 3 gestures x S2, S8) and the 2 WR-01 person-2-of-5 double rows |
| M2: `items.js` Remove handler without the guard | R7 and R34 tests (69) | 20: the 18 item rows (focus on the body) and the 2 WR-01 item-2-of-4 double rows |
| M3: guard on `click` only (no `mousedown` listener) | R7, R34, R30, R29 | 43: all 36 repeat rows, the 4 R34 rows and the 3 CR-01 touch size rows (the repeat `mousedown` is no longer cancelled; the code-review solver found the same for its click-only variant, the failing assertion was not read row by row here) |
| M4: guard never removes itself | R7, R34, R30, R29 | the lifetime tests: R7 (new) and the existing CR-01 one (2 in the SEC-01 tree, 3 once the I-1 lifetime test existed) |
| M5: guard swallows every press once armed (`if (false && ...)`) | R7, R34, R30, R29 | 4: the separate-click test, the lifetime test, the two WR-01 separate-click rows |
A first version of the lifetime test passed under M5 (a toggle flipped zero times looks like a toggle flipped twice); it now asserts that both clicks
reach the page (`[1, 2]`), and M5 turned red on it.

Regression check, the audit's own sweep re-run unchanged on the fixed tree (`probes/p3_rerun_audit_ghost_sweep.py`, `probes/results-p6-ghost-sweep-after.json`):
123 rows, 21 controls, 3 sizes, double click, triple click, double tap, a single click on a fresh context as the baseline for each.
| | Audit, before | Now |
|---|---|---|
| Rows that differ from a single click in data | 13 (5 toggles, 8 SEC-01) | 5 (the toggles: both clicks of a double click hit the same toggle, so it flips twice, by design) |
| Rows that differ in UI only | 46 | 17 (10 on the two mode labels and 7 on Dismiss note: focus ends on the body, known and accepted, not filed) |
| New bill, Start new bill, Cancel, backdrops, Remove (people, items, middle and last), Add person, Add item, Copy summary | | equal a single click in data and UI, every row |
| Rows with a console error, page error or foreign request | 0 | 0 |

Why the in-handler test could go (BUILD.md judgment call 18). The old handler also ignored a click of count above 1 that reached a Remove
button although no Remove click had armed the guard. The only way in is a repeat press that lands on a Remove button after some other control
moved the rows, and the one candidate is Dismiss note. `probes/p1_dismiss_note.py` (3 sizes x double click, triple click, double tap, with
three people so Remove is enabled): the second press lands on the "People" heading at 360x640 and 390x844 and on a `div` at 1280x800,
people 3 -> 3 in all 9 rows. `probes/p2_dismiss_scan.py`: 291 viewports (widths 320 to 1280 in steps of 10, heights 568, 844 and 1000):
213 land on a heading, 78 on a `div`, 0 on a control.

## Ruling 2: I-1, a double click on New bill
Change (`68ab318`): the opener handler in `createDialog` calls `swallowRepeatClicks()` before `showModal()`. No other change in `src/`;
the `dom.js` doc comment now names opening as a trigger. New tests (14): `test_R29_a_repeat_press_on_new_bill_leaves_the_dialog_open` (3 gestures x 3
sizes: dialog open, focus on Cancel, only the first click reached the page, draft unchanged), `test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it`
(Cancel, backdrop at (10, 10), Escape: closed, focus on New bill), `test_R29_opening_by_keyboard_and_opening_again_straight_away_is_not_held_back`,
`test_R29_the_guard_of_opening_ends_at_the_next_press`.
RED on the unfixed opener (`junit-i1-red.xml`): 12 failed, 2 passed (the keyboard test and the lifetime test are controls that pass before and after).
GREEN (`junit-i1-green.xml`): the 14 new tests and the existing R29, R30 and R31 tests, 43 of 43. Mutant I1-M1 (opener without the call): 12 red. Mutant M4 (never
disarms): the R29 lifetime test red. Full suite on the I-1 tree: 312 passed (`junit-browser-i1.xml`).
It needed no other behaviour change, so it is done and not left: the dialog stays open after a double click, triple click or double tap, focus is on Cancel
(R29), and a single click on Cancel or the backdrop, Esc and Enter still act.

## Ruling 3: SEC-02, Publish
`CLAUDE.md` has a "## Publish" section modelled on the Streaks one (only `index.html`, `src/` and a `.nojekyll` file are served; `docs/`, `tests/`,
`harness/`, `.claude/`, `CLAUDE.md` and evidence are not; the orchestrator makes the publish copy at release; never point Pages at the repository root, with the
reason), and the Stack line now points to it. `spec.md` has a dated note on the Invariants line with the audit's numbers (3,108 tracked files, 22 are the app, 875
copies of `src/` modules, 143 files with an absolute local path, 142 screenshots, Jekyll without `.nojekyll`). No deploy file was added.

## Ruling 4: SEC-03, accepted
A dated bullet under "Residual risks accepted" in `spec.md`: the reason (only a hand-edited draft or a same-origin page reaches it, and that writer can already
overwrite or delete the draft) and the two options if the owner ever wants a change. No code change.

## Ruling 5: the doc pass, and what was measured for it
- Threat-model rows added: a repeated press (asset: the bill) and what is published. Dated notes on R7, R29 and R30. `qa.md` has scenario rows for the new tests
  (SEC-01: two outlines and a scenario; I-1: two outlines and a scenario). `BUILD.md` code map, judgment calls 18 and 19, and the test counts name the moved helper.
- "Inputs strip CR and LF" measured (`probes/p4_crlf_and_separators.py`, headless Chromium 149, the app running):
  ```
  A1 typed Enter between B and C        field 'ABC'   CR/LF in the field: False   CR/LF in the saved draft: False
  A1 execCommand insertText LF          field 'AX Y'  CR/LF in the field: False   CR/LF in the saved draft: False
  A1 execCommand insertText CRLF        field 'AX Y'  CR/LF in the field: False   CR/LF in the saved draft: False
  A1 script sets .value to S LF T CR U  field 'STU'   CR/LF in the field: False   CR/LF in the saved draft: False
  A2 bare <input type=text>, value set to a LF b CR c: abc
  A3 bare <textarea>,        value set to a LF b CR c: a\nb\nc
  ```
  So the browser's text input does it (the `value` setter strips, inserted text turns a break into a space, a typed Enter inserts nothing), a bare input with no app
  code behaves the same, a `<textarea>` keeps the line feed, and `src/ui/` and `src/main.js` have no code for it (Grep for `\n`, `\r`, `trim(`, `replace(`:
  only `src/draft.js` `nameFits` and `src/core/summary.js` `CONTROLS` touch line breaks). The row now says that.
- The U+2028 residual measured on the copy path (same probe, part B, names `Q` + character + `Z`, then Copy summary and the recorded clipboard text):
  ```
  U+2028 U+2029 U+0085 tab NUL U+202E  ->  copied line 'Q Z RM 38.87'  (6 lines in the copied text)
  U+200B U+FEFF U+00A0                 ->  copied line keeps the character  (6 lines in the copied text)
  ```
  The audit measured 15 characters, 30 of 30 clean. The residual now says what `summaryText` replaces and what still passes.
- Spec gap 6 (two tabs of one browser, last writer wins) was not in the rulings and is left (see the Observations in `findings/security.md`, section "Solver").

## Probes in this folder (all print only, except the one results file)
`probes/common.py` (rig contexts, the CG-7 guard, a click log), `p1_dismiss_note.py`, `p2_dismiss_scan.py`, `p3_rerun_audit_ghost_sweep.py` (imports the audit's script
read-only, writes `results-p6-ghost-sweep-after.json` here), `p4_crlf_and_separators.py`, `p5_live_gate_scratch.py` (runs `tests/browser/live_e2e.py` unchanged with
its evidence root pointed at `live-gate-check/`). The special characters in `p4` are built with `chr()`, because the Write tool turned backslash-u escapes in my
first version into raw characters (found by counting them, fixed by rewriting the file).

## Process notes
- The Write tool converted the escapes in my first `p4` into raw characters; I replaced them with `chr()`. No escape text was written into any spec or doc line (U+2028
  is written as "U+2028"). The added doc lines were checked for em and en dashes and for raw invisible characters (U+2028, U+2029, U+200B, U+FEFF, U+202E, U+00A0): none.
- Failed test runs (the red runs and the mutants) leave screenshots under `docs/modules/split-app/qa/functional/<ts>/`. They were my own scratch outputs and I deleted
  them by exact folder name each time (13 folders in three batches, none left; `git status` showed no `functional/` before any commit).
- Each commit was preceded by the unpiped credential gate, exit 0 ("CLEAN. No secret values found"): `071577a` (5 files), `68ab318` (3), `314b827` (2), `12bc878` (2).
- Servers (all `python -m http.server <port> --bind 127.0.0.1` through `rig.StaticServer`, each printed `STOPPED ... exited True, port free again True`).
  Recorded: baseline pytest pid 40612 port 47711; `p1` pid 35232 port 3919; `p2` pid 44504 port 8872; I-1 green run pid 30076 port 55164; I-1 full suite pid 51112 port 63662;
  ghost sweep pid 25336 port 47292; `p4` pid 36116 port 11087; fidelity runner pid 40216 port 12414; live gate pid 47116 port 48889; final browser suite pid 50360 port 47850.
  The red runs, mutant runs and SEC-01 runs were filtered through `tail` or `grep`, so their pids were not kept; each of those runs also ended with the same STOPPED line.
- Headless Chromium and the Playwright driver were closed by each script or by pytest's fixtures. No background shell, no watcher, no poll loop.
- Final sweep at 21:27 by Win32_Process (name: python, node, chrome, headless, playwright; command line: `http.server`, `playwright`, `ms-playwright`, the two evidence folder
  names, `credential_sweep`, `pytest`) and by netstat on the ports above: nothing of mine is alive and no recorded port listens. The sweep did list processes that are not mine, and I left
  them alone: a `python -B -m pytest tests/browser` (pid 37548, started through `timeout.exe`, flags I never use) with its Playwright node 47668 and `chrome-headless-shell` children,
  and two `http.server` processes started with `--directory` (ports 7627 and 8791, the Streaks example and its parent folder).
