# Handoff. Split v1.1.0 execute, task A23 and the step 5 re-check items, done, for the regression

Written 2026-10-16 by the dev solver at the end of its pass. Ledger S7 rows 45 to 47 (row 46 routed the items, ORCH). Planner commits `4e3267a` and `a084b14`. Base `6b9b093`. The records are in the docs commit above the four item commits (its message starts `docs: records for task A23`, read its hash with `git log`). Nothing under `src/` or `tests/` changed after the proof runs. `git hash-object --no-filters src/system.css` is `bf30ddadb8c756dc5d462243c642c218597ae0ac`. `index.html`, `src/system.css` and `docs/design/` are unchanged against `6b9b093`.

## Commits
| Commit | Item | What |
|---|---|---|
| `1f1eb97` | A23 (app CR-R1) | `createNotes` calls `swallowRepeatClicks()` before `onDismiss`, 14 browser ids, the false JSDoc line on Dismiss note dropped |
| `d989d32` | app CR-R6 | `tests/dom.test.js`, six `plainNameField` cases with a stand-in input |
| `62cf3c5` | app CR-R3 | 16 literal characters in `seeds.py` and `test_app.py` written as `\u` escapes |
| `b0992b4` | comments | core CR-R1, CR-R2, app CR-R2, CR-R4 code parts, CR-R5, comments and docstrings only |

## Where the record is
- `docs/modules/split-app/BUILD.md`, "v1.1.0 task A23 and the step 5 re-check items", with the RED, GREEN and proof tables and the readings.
- `docs/modules/split-core/BUILD.md`, "v1.1.0 step 5 re-check, comment items".
- Solver lines under each routed item of both `findings/code-review.md`, section "v1.1.0 step 5 re-check, 2026-10-16".
- A23 ticked in `split-app/spec.md`, and a dated "Built" note on R7, R27 (the held Enter sentence) and the threat row of the bill as the user left it.

## RED and GREEN
- A23 browser RED on the tree before it, `docs/modules/split-app/qa/functional/20261016-024218-chromium/` and `20261016-024258-webkit/` (`red.txt`), 11 of 14 fail on the asserted property in each engine, only the 3 single click controls pass. GREEN `20261016-024404-chromium/` and `20261016-024426-webkit/`, 15 of 15.
- CR-R6 Node RED on scratch copies, `docs/modules/split-app/qa/unit/20261016-024701-red/` (UC1 4 of 6, UC2 5 of 6, UC3 6 of 6 fail). GREEN `20261016-024714-green/`, 406 of 406.
- CR-R3 check, the 12 R62 ids in `docs/modules/split-app/qa/functional/20261016-025245-chromium/` and `20261016-025252-webkit/` (`green.txt`), the same ids and outcome as the A22 GREEN runs.

## Proofs on the committed tree (`b0992b4`)
- Node `docs/modules/split-core/qa/unit/20261016-030139/node-test.txt`, 406 of 406. By id against `20261016-012221/`, 6 new, 0 missing, 0 changed.
- Chromium `docs/modules/split-app/qa/functional/20261016-030148-chromium/`, 742 passed. By id against `20261016-012252-chromium/`, 14 new (A23), 0 missing, 0 changed.
- WebKit `docs/modules/split-app/qa/functional/20261016-030547-webkit/`, 739 passed, 3 skipped (the counted skips of `skips.txt`). By id against `20261016-012652-webkit/`, 14 new (A23), 0 missing, 0 changed.
- The fidelity gate and the live gate were not re-run (task A23), the regression covers both.

## Resume point
Nothing of A23 or of the routed re-check items is left to build. The next actions are the orchestrator's. The ledger row for this pass, the README reconcile (CR-R4 (a), (c), (d), (e), (f) and the Known limits row on double clicks), the process ledger, then module close and `sdlc:regression --full`, whose QA and security runs cover this pass (ledger S7 row 46).

## Open, for the orchestrator
- README Known limits row, as the solver would state it after A23 (the orchestrator decides the words). "A double click on a mode label acts as one click. It leaves the same mode and changes no other data. Focus stays on the radio in Chromium and is on the page in WebKit, after a click and after a double click alike." Dismiss note leaves the row, since a double click, triple click, double tap or held Enter on it acts as one press at every width in both engines.
- For the planner (qa.md wording). The held Enter scenario's closing note says four repeats that reached New bill would open, close, open and close M1. Measured on the tree before A23, only the first repeat reached New bill (its own click arms the guard, which cancelled the rest), so M1 stayed open. The scenario's assertions are right as written.
- For the planner (qa.md wording). The CR-R6 outline says its RED is three stubs put in with the Edit tool. The routing asked for scratch copies, which is what ran.
- Older comments outside the review's 21 lines still use a prose colon (for example `D13:` in `draft.js`, the headers of `draft.js` and `spare.js`). Not routed, not touched.

## Traps
- The Edit tool decodes a `\uXXXX` written in its strings into the character, and writes `\\` as two backslashes. To write the six characters `‮` into a file, spell the backslash as `\` and check the bytes after (`cat -A` or `od`). Its compare step treats an escape and its character as equal, and it trims a trailing space of the new text.
- A python `http.server` on 127.0.0.1:8741 (PID 11048, started 01:25:42) is the orchestrator's and was left alone.
- Process slip, disclosed. The first A23 RED command in Chromium carried a `2>&1` into a pipe to `tail`. Nothing was written by it.
