# Mutation and probe record, code-review finder, split-app

Run folder 20261009-181036. Every mutant lives in a throwaway copy of the project in the session scratchpad
(`scratchpad/mut/<name>/`, made with the shipped files and one edited file). Nothing under `src/`, `tests/`,
`index.html` or `docs/design/` was touched. The copy was checked equal to the repo before any run
(`diff -r src`, `diff -r tests`, `diff index.html`: same). The browser suite in the copy: **205 passed in 59 s**, the
same as the repo's own record.

Suite = `python -m pytest tests/browser -q` in the copy (205 tests). Node = `node --test "tests/**/*.test.js"` (265 tests).
"Survives" means the whole suite stayed green with the mutant in place.

| Mutant | File and edit | Suite result | Meaning |
|---|---|---|---|
| A1 | `src/errors.js` `typedInto`: clears the flag only when the text is empty (`if (text.trim() === "") setFlag(...)`) | **205 passed. Survives** | QA W2 confirmed. Valid-by-typing is not what the suite distinguishes. |
| A2 | `src/errors.js` `typedInto`: never clears the flag (`export function typedInto() {}`) | **205 passed. Survives** | R10 (c) second half ("does not come back until the field next loses focus") is not pinned. Kill scenario K1. |
| D | `src/draft.js`: (B) D10 compares `nextId` with person ids only, (C) an item name may hold a line break | **Node 265 passed, browser 205 passed. Survives** | D10 against an item id and D8 for item names are not pinned. `kill_decoder.mjs` shows the shipped decoder rejects both and the mutant accepts both. |
| J | `src/ui/dialog.js`: every click whose target is the dialog element closes it (the box test is removed) | **205 passed. Survives** | R30 "a click inside the box keeps it open" is not pinned. Kill scenario K5. |
| CSP | `src/ui/dialog.js`: opening writes `dialog.setAttribute("style", ...)` | **Killed**: `test_R29_the_dialog_opens_with_the_safe_choice_focused` errors with the CSP console line (139 passed, 1 error with `-x`) | QA W3 ruled fine: the suite-wide console rule does work. |
| P1 | `src/ui/field-leave.js`: `endPress` runs `waiting.slice()` and never empties the queue | **205 passed. Survives** | The "run each waiting handler once" guarantee is not pinned. Kill scenario K2. |
| P56 | `src/ui/field-leave.js`: the `pointercancel` and `keydown` ends are removed | **205 passed. Survives** | Two documented branches of the RD-3 helper have no test. Kill scenario K3 (keydown). |
| O | `src/main.js` `copySummary`: the re-check after the `await` is removed | **205 passed. Survives (equivalent)** | `render()` already sets `view.status = null` when no table shows, so the guard is redundant code. |
| RM | `src/main.js` items `onRemove`: `bill = removeItem(bill, id); render();` (no `saveDraft`) | **205 passed. Survives** | R25 for "remove item" is not pinned. Kill scenario K4. |
| LIVE | `src/ui/people.js`: `aria-live="polite"` on the People section | **Killed**: 7 R3 DOM-walk tests fail | W7 is covered for S3, S2, S1 and S5 by the R3 walk. |
| LIVE2 | `src/ui/note.js`: `aria-live="assertive"` on `div.note-wrap` and `aria-pressed` on the dismiss button | **205 passed. Survives** | The S7 note (and the open dialog) have no markup walk. Kill scenario K6. |
| AD | `src/ui/people.js`: Add person gets `aria-disabled` instead of the `disabled` property at 12 people | **Killed**: `test_R6_add_person_until_the_limit` (specimen cursor and border colour differ) | QA W4 ruled fine: the `:disabled` styling check covers "skipped by Tab" transitively. |
| SV | `src/ui/dom.js`: `setValue` always writes (`input.value = text`) | **205 passed. Survives** | The comment in `dom.js` that the guarded setters are what keep R33 is not demonstrable in Chromium. |
| RC | `src/ui/dom.js`: `reconcileChildren` re-inserts every node on every pass | **Killed**: 4 R33 tests and `R24_the_status_lives_as_long_as_the_table` fail (run with `-k "R33 or R34 or R16 or R24"`) | The R33 tests do have teeth against the real mechanism. |
| FIX | `src/ui/dialog.js`: proposal for CR-01, see `02-fix-proposals.md` | 205 passed | Fix works, nothing else breaks. |
| FIX2 | `src/ui/people.js` and `src/ui/items.js`: proposal for WR-01, see `02-fix-proposals.md` | 205 passed | Fix works, nothing else breaks. |

## Kill scenarios (`scripts/probe_kill.py`, one process per tree)
Shipped code (`base`): all 9 checks PASS. Each surviving mutant fails exactly the check meant for it:

| Check | Fails on |
|---|---|
| K1 error shown on blur, gone at valid text; bad text typed again does NOT bring the error back before blur; returns on the next blur | A1, A2 |
| K2 a press on blank space waits then shows the error; a click inside the focused field afterwards shows no stale error | A1, A2, P1 |
| K3 mouse down inside the focused field, then Tab: the error is shown at once | P56 |
| K4 removing an item is saved | RM |
| K5 a click on the dialog padding keeps the dialog open | J |
| K6 the note carries no stray aria attribute | LIVE2 |

Results per tree: `probe-kill-base.json`, `probe-kill-A1.json`, `probe-kill-A2.json`, `probe-kill-P1.json`,
`probe-kill-P56.json`, `probe-kill-RM.json`, `probe-kill-J.json`, `probe-kill-LIVE2.json`.

## Behaviour probes on the shipped code
| File | What | Result |
|---|---|---|
| `probe-dialog.json` | double click and double tap on Cancel with the S1 bill at 375x667, 360x640, 412x732 | **Draft changed in 6 of 6.** QA F-1 reproduced. |
| `probe-dialog.json` | press on the dialog title, drag to the backdrop, release | Dialog closes (it should stay open or at least not count as a backdrop click) |
| `probe-dialog.json` | click on the dialog padding; Tab and Shift+Tab after a click on the title | Stays open; focus stays on the two buttons |
| `probe-detail.json`, `probe-detail-dblclick.json` | `MouseEvent.detail` of the second click | `mouse.dblclick`: 1 then 2. Double tap within 200 ms: 1 then 2. Two taps 400 ms apart: 1 and 1. So `detail > 1` marks the second click of a double click or double tap. (`mouse.click()` twice sends 1 and 1, so the first rows of `probe-detail.json` show 1.) |
| `probe-double.json` | double click and double tap on `Remove Char kuey teow` (item 2 of 4) and `Remove P2` (person 2 of 5) | Two rows removed in both mouse and touch. |
| `probe-overflow.json` | S1 prices scaled up | 360 px: no overflow up to a total of RM 692.60, **5 px at RM 761.86**, 23 px at RM 1385.21. 390 px: first overflow at RM 69260.40. QA O-1 confirmed. |
| `probe-zalgo.json` | a person name of one letter plus 20,000 / 200,000 / 1,000,000 combining marks in the draft | Accepted by D8 (one grapheme cluster). The page loads in 0.08 / 0.12 / 0.37 s and stays responsive. |
| `fuzz-seed-{1..4}.json` | 720 random real-gesture steps (type, Tab, click, add and remove, toggle, mode, copy, dialog 4 ways, reload) with invariants: no page or console error, draft equals screen, focus after add and remove (R34), error count equals `aria-invalid` count, dialog closes with focus on New bill | 0 failures |
| (terminal) `time_decoder.mjs` | decoder on a 4 MB hostile name | 480 ms in Node, rejected |

CG-7: every context was made by the project's `rig.new_context` (recorder installed, `permissions` and `bypass_csp` refused)
plus a guard script that rejects `Clipboard.readText`, `read` and `write`. No permission was granted. The OS clipboard
was never read or written.
