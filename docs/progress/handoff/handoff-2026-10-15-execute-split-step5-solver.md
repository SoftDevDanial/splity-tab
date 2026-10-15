# Handoff. Split v1.1.0 execute, step 5 solver round, done but CR-S5-9, for the re-check

Written 2026-10-15 by the dev solver at the end of its round. The code commits are `042c359` to `4462b4c` (below), the proofs and records are in the docs commit above them (its message starts `docs: records for the step 5 solver round`, read its hash with `git log`). Nothing under `src/` changed after the proof runs. `git hash-object --no-filters src/system.css` is `bf30ddadb8c756dc5d462243c642c218597ae0ac`. `index.html` and `docs/design/` unchanged.

## Commits
| Commit | Finding | What |
|---|---|---|
| `042c359` | CR-S5-1 (split-core) | Node test, the 38 item trap bill, exact charges column |
| `9277412` | CR-S5-2 (split-core) | one Bill field list, `BILL_FIELDS = Object.keys(newBill())` in `bill.js` and `spare.js`, no export added |
| `2ad022a` | CR-S5-11 | `import re` out of `support.py` |
| `8b7b7d4` | CR-S5-6 | the R41 guard follows the support.py helpers and checks every page script's text |
| `0094f40` | QA-S5-1 | the chromium_only accessible description test |
| `d728076` | CR-S5-7 | `--rows` at 7 to 11 people |
| `6ffecf7` | CR-S5-14 | `evidence_dir` without `exist_ok` |
| `c51d847` | CR-S5-12 | the xfail plumbing gone |
| `4462b4c` | CR-S5-8 | `swallowRepeatClicks` and `isRepeatClick` JSDocs, history to BUILD.md A8 |

Each finding's solver line (in its findings file) names its RED and GREEN folders. The round's sections are `docs/modules/split-core/BUILD.md` and `docs/modules/split-app/BUILD.md`, "v1.1.0 step 5 solver round".

## Proof runs on the committed tree (`4462b4c`)
- Node `docs/modules/split-core/qa/unit/20261015-234943/node-test.txt`, 380 of 380.
- Chromium `docs/modules/split-app/qa/functional/20261015-234948-chromium/`, 716 passed, 0 failed, 0 skipped. By id against the QA finder's `20261015-204624-chromium/`: its 707 ids all present and passed, 9 new ids (5 R20, 2 R41, 1 R58, 1 R9) passed, 0 different.
- WebKit `docs/modules/split-app/qa/functional/20261015-235448-webkit/`, 713 passed, 3 skipped (the R33 IME, the R40 after-load and the new R9 test, each with its reason in `skips.txt`), 0 failed. By id against `20261015-205019-webkit/`: its 707 ids with the same outcome, 9 new ids, 0 different.
- Live gate, one server per engine, control first. Chromium control `docs/modules/split-app/qa/live-e2e/20261016-000355-chromium-control/` red at step 1 on its property, green `20261016-000357-chromium/` 9 of 9. WebKit control `20261016-000424-webkit-control/` red at step 1 on its property, green `20261016-000426-webkit/` 9 of 9. Each green has 0 console errors, 0 page errors, 0 CSP violations, 90 requests with none outside the rule and 3 stand-in writes.

## Resume point (not done)
- **CR-S5-9 (INFO, R48 (3), `revealing?.cancel()` in `createSection`).** Not started, the round stopped at its context limit. The ask: write a test only if one can assert the requirement (read R48 (3) in `docs/modules/split-app/spec.md` first), otherwise say why not in the finding's solver line. Mutant U3 (the line removed) passes all 26 R48 tests (`qa/code-review/20261015-212541/app-mutation-run.txt`).
- For the orchestrator. The qa.md rows the code review routes to the planner (CR-S5-1's trap row, CR-S5-6's helper line and planted copies, CR-S5-7's 7 to 11 row) are not written. QA-S5-1's scenario now has its test. The README reconcile (CR-S5-3, CR-S5-5, and this round's symbols in both BUILD.md sections).
- For the re-check. Re-run the code review (both modules) and QA on split-app (the `@R9 @R11 @chromium_only` scenario). The planner may still prefer CR-S5-2's export form over the `newBill` keys.

## Traps
- A RED that runs a reviewer's mutant goes through the reviewer's own runner in the session scratch folder (`mutate.mjs`, `mutate_app.py`), never in `src/`.
- `docs/progress/STATE.md` was already modified in the working tree by someone else when the round began. It was never staged.
- One slip of process: one command in the round discarded a runner's output with a shell redirection to /dev/null. Nothing was written. Every file was written with the Edit or Write tools or by a runner into its own evidence folder.

## Processes
None alive at writing. The solver started two `python -m http.server` servers, pid 27532 on port 53811 (Chromium gate) and pid 7888 on port 31877 (WebKit gate), and stopped each by exact PID with `taskkill`, after which its port refused a connection (curl exit 7). The two suite runs started and stopped their own servers (pid 13988 logged STOPPED, port free again, for Chromium. The WebKit run's server line was cut by the `tail` of its output, so its pid is not on record, and the sweep below found no python process left). A sweep at 00:04:47 by name (python, node, pytest, webkit, chrome, http.server), by listening port (53811, 31877) and of shells found only the sweep's own two bash processes.
