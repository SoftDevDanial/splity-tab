# Regression, v1.0.0

| | |
|---|---|
| Project | Split |
| Mode | full, under the ORCH economy ruling of 2026-10-09 (CHANGE-LEDGER row 51), corrected on 2026-10-10 (the fidelity finder gap) |
| Opened | 2026-10-09, at the tail of execute |
| Closed | 2026-10-10 14:30 |
| Run by | the orchestrator, with finder and solver agents |
| Verdict | **PASS** |

## Scope per module
`--full` asks for every finder on every module. The economy ruling keeps a finder's verdict when the code it judged has not
changed since, and re-runs every finder whose code no agent has seen. The QA finder and the cold boot ran on everything.

| Module | Last green | Code since its finders ran | What re-ran | Why the rest stands |
|---|---|---|---|---|
| split-core | `329679e` | none, `src/core/` unchanged | QA finder (179 items), unit suite, cold boot. The app's code review re-read the seam | Code review and security were given on this exact code |
| split-app | `22ac9af` | `61c3cd3..22ac9af` (the repeat-press guard), then the regression's own fixes | Code review on the delta, two solver rounds, a scoped re-check. QA finder (162 items). **Fidelity finder** (the gap below). Cold boot | Security: see the ruling below |

**The fidelity finder gap.** The 2026-10-09 ruling let "the solver's fidelity run" stand as the fidelity result. That run was
the harness pixel gate alone. No fidelity finder had ever judged split-app, so the FE element checklist half of R40 had no
verdict. The regression QA finder reported R40 as untested, the orchestrator traced why, and a fidelity finder ran on
2026-10-10. Recorded in the ledger as an orchestrator gap, not a limit.

**Security on the regression's fixes.** The fixes after `22ac9af` (`e30b015`, `4a36354`, and a comment in `src/errors.js`)
change only which clicks an Add or a Remove acts on. They add no input, storage, rendering or network path, so the security
verdict on `22ac9af` stands (ORCH ruling, ledger).

## Finder verdicts
| Finder | Model | Verdict | Report |
|---|---|---|---|
| Code review, split-app delta | sonnet | RG-CR-01 BLOCKER (a regression: a double click on the right edge of Add person added and removed a person), 3 WARNING, 3 INFO. Solved. Re-check found RG-CR-08 BLOCKER (a second regression: a double press on a chip under a pending price error removed the item). Solved. Closed under the stop rule, status pass | `docs/modules/split-app/findings/regression-code-review.md` |
| QA, both modules | haiku | PASS, 340 of 341 items, R40 checklist half untested (then covered by the fidelity finder). Five everyday flows by hand at 390 x 844, 73 of 73 checks | `docs/modules/split-app/findings/regression-qa.md` |
| Fidelity, split-app | sonnet | 1-to-1, clean, 0 findings. 10 of 10 pairs at 0 px, 157 of 157 checklist rows, 2,242,912 property comparisons across 35 page pairs | `docs/modules/split-app/findings/fidelity.md` |
| Security, both modules | | stands, clean (SEC-04 accepted for v1.0, fixed in v1.1.0) | `docs/modules/*/findings/security.md` |

## Solver rounds
1. **Round 1** (`17ac1ed`, `e30b015`, `f0ca022`, `38686c0`). Add person and Add item arm the repeat-press guard (RG-CR-01, 108 new test rows), the guard's lifetime tests record presses as well as clicks (RG-CR-02), docs. Browser 312 to 421.
2. **Scoped re-check.** RG-CR-01, 02 and 04 hold. New RG-CR-08 BLOCKER. Ruled a fix, not an accepted limit, because it deleted typed data through a gesture that worked before.
3. **Round 2** (`4a36354`, `059f560`). A Remove ignores a repeat press itself as well as arming the guard. The re-check's own probe went from 96 of 96 affected layouts removing the item to 0. 6 new test rows. Browser 421 to 427.

Code review then closed for v1.0.0 under the stop rule.

## Cold boot
Evidence `docs/regression/20261010-142445/` (a copy of the official run `docs/modules/split-app/qa/live-e2e/20261010-142445/`).
The shipped `index.html` on a plain static server, no seed, real `localStorage`, real clicks and keys, Chromium 149, 390 x 844,
the clipboard recorder in place of the system clipboard.

| # | Gesture | What it proves | Result |
|---|---|---|---|
| 1 | open with empty storage | the empty bill (two people, Even, empty Subtotal, 10 and 6 percent), nothing stored | PASS |
| 2 | name Aisyah and Ben, Add person, Chen, Subtotal 100.00 | RM 100.00, 10.00, 6.60, 116.60, shares 38.87, 38.87, 38.86, Adds up to 116.60 | PASS |
| 3 | Copy summary | "Summary copied" and the exact even-split summary | PASS |
| 4 | By item, four items typed with prices, tap who had each, Copy summary | shares 29.04, 15.74, 24.48, Adds up to 69.26, the exact by-item summary | PASS |
| 5 | close the page, open it again, click Even | the bill as left, then the even split | PASS |
| 6 | New bill, Start new bill, reload | a modal dialog with Cancel focused, then the empty bill, still empty after a reload | PASS |
| 7 | read the logs of steps 1 to 6 | 0 console errors, 0 page errors, no CSP violation, only same-origin GETs | PASS |

Server pid 13236 on port 32635, stopped by the gate, port free after.

## Suites on the final tree
| Suite | Command | Result |
|---|---|---|
| Unit | `node --test "tests/**/*.test.js"` | 275 pass, 0 fail (QA finder, 2026-10-10) |
| Browser | `python -m pytest tests/browser -q -p no:cacheprovider` | 427 passed in 109.87 s (QA finder, 2026-10-10) |

No code changed after those runs (`git diff 9420055 HEAD -- src tests index.html` is empty).

## Accepted for v1.0, unchanged by this run
- On a big bill the by-item table is wider than a 360 px phone (H-02). Fixed in v1.1.0.
- Holding Enter on Remove of the only item adds one blank item (SEC-04). Fixed in v1.1.0.
- The rest are in the README, Known limits.

## Close
- CHANGE-LEDGER. A "re-verified, no regression" row in each of C1 to C8, with its proof, plus this run's row.
- README. Reconciled after both solver rounds.
- Process ledger. Reconciled 2026-10-10 (`docs/progress/process-ledger.md`).
- Credential gate. Full sweep from the project root, exit 0.

## Verdict
**PASS.** Every in-scope finder is green or stands on unchanged code, both suites pass, and the app works live from a cold boot.
