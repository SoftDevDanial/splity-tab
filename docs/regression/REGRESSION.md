# Regression, v1.1.0

| | |
|---|---|
| Project | Split |
| Mode | full, with the step 5 re-check's QA and security halves folded in (CHANGE-LEDGER S7 row 46, ORCH) |
| Opened | 2026-10-16 03:25, at the tail of execute (both modules closed 03:20, row 49) |
| Closed | 2026-10-16 04:25 |
| Run by | the orchestrator, with finder agents. No solver round was needed |
| Code judged | `b0992b4` (HEAD `64b882c`, nothing under `src/`, `tests/` or `index.html` changed after it) |
| Verdict | **PASS** |

The regression of v1.0.0 (PASS 2026-10-10 14:30) is in git history (tag `v1.0.0`).

## Scope per module

| Module | QA and boot | Fidelity | Code review | Security | Why |
|---|---|---|---|---|---|
| split-core | every scenario, Node | n/a (logic) | the fix pass `6b9b093..HEAD`, its earlier delta reviewed at the step 5 re-check | `798f17f..HEAD` | `--full`, with the code review economy of the 1.0 ruling (code already reviewed at the re-check is not reviewed twice) |
| split-app | every scenario, Chromium and WebKit, the cold boot both engines | the pixel gate rerun on the final tree, 40 pairs. The FE checklist half stands from step 5 (row 42), no markup or CSS changed since | the fix pass `6b9b093..HEAD` | `798f17f..HEAD` | the same |
| whole codebase | | | one consistency sweep | | `--full` |

## Finder verdicts

| Finder | Verdict | Record |
|---|---|---|
| QA (Sonnet) | split-core PASS 73 of 73 scenarios, Node 406 of 406. split-app PASS 181 scenarios, Chromium 742 passed, WebKit 739 passed and 3 counted skips, by id 0 differences from the fix pass proofs | both `findings/qa.md`, section "v1.1.0 regression --full, 2026-10-16", ledger row 50 |
| Fidelity pixel gate (Chromium) | 40 of 40 pairs at 0 px, control-self 0 px and control-noseed 56.08 percent, both CONTROL PASS | `docs/modules/split-app/qa/fidelity/20261016-033155/run.log` |
| Security (Opus) | split-app PASS, split-core PASS. SEC-S5-1 and SEC-S5-3 resolved and confirmed against a `798f17f` control in both engines. Every threat row holds. SEC-R1 INFO accepted (an IME composition holding a bidi control is cut short, the name stays plain) | both `findings/security.md`, ledger row 51 |
| Code review (Opus) | split-core CLEAN. split-app 0 BLOCKER, RG-CR-1 WARNING and RG-CR-2 INFO fixed in the README, RG-CR-3 to RG-CR-5 INFO deferred to the v1.2.0 plan | both `findings/code-review.md`, ledger row 52 |
| Consistency sweep (Opus) | 0 BLOCKER. CS-1 WARNING accepted as a residual (a name input bringing only control characters saves the same text and clears the copy status), CS-7 fixed in the README, CS-2 to CS-6 deferred, CS-8 to the publish prep | `docs/regression/20261016-032500/consistency.md`, ledger row 52 |

## Cold boot, the live gate

The shipped `index.html` served by `python -m http.server` with no seed, driven by real gestures, one server per engine, the control first.

| Engine | Control (must stop red at step 1) | Green run |
|---|---|---|
| Chromium 149 | `docs/modules/split-app/qa/live-e2e/20261016-033455-chromium-control/`, red at step 1 | `20261016-033459-chromium/`, 9 of 9 steps, 0 console, page or CSP errors |
| WebKit 26.5 | `20261016-033526-webkit-control/`, red at step 1 | `20261016-033527-webkit/`, 9 of 9 steps, 0 console, page or CSP errors |

Server PIDs and ports are in `docs/regression/20261016-032500/cold-boot.md`.

## Closing checks
- Credential gate, whole tree, exit 0 with both controls (security finder 03:52, the orchestrator at the close).
- Process ledger rows 82 and 83 (and the code reviewer's foreground runs) reconciled, nothing alive but the Streaks UAT server PID 11048 on 8741 (Streaks process row 77).
- CHANGE LEDGER S7 rows 50 to 53.
- Open for the owner's UAT, QA-S5-4 (WebKit glass and the focus ring on Splits after the sheet closes) and the iPhone VoiceOver price case of H-09.
