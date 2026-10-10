# CHANGE LEDGER - v1.0.0

> The version's ONE attribution record and the human's only complete view of what happened.
> `STATE.md` is *situation*, handoffs are *resume points*, `findings/` are *evidence*. **None of them is
> the record.** `sdlc:uat` derives its cases from the **scope sections** below and its handover from
> **Needs the human**, so an item that is not here never reaches the human.
>
> **Rules (constitution, The CHANGE LEDGER):** updated at **every close** (round, fix batch, module, live
> gate, finder loop, decision, deferral) · corrections are **additive and dated**, never a silent
> rewrite · **staleness check** at every phase boundary: newest dated entry here vs newest file in
> `./docs/progress/handoff/`. Handoff newer means this file is stale.

**Version:** v1.0.0 · **Opened:** 2026-10-08 by `sdlc:plan` as ~~v0.1.0~~ · **Relabelled:** 2026-10-09 to
v1.0.0 on the owner's word (see Off-scope, the USER row of that date). Same version, same scope. Plan-phase
documents written before that date still say v0.1.0. · **Sealed:** 2026-10-10 on the owner's word, "Seal both apps" (see `SEAL.md`, tag `v1.0.0`)

> **This run was delegated.** The owner asked for the whole lifecycle to be created ("Auto create with
> lifecycles for 2 projects", 2026-10-08). Every decision an agent or the orchestrator took in his place is
> tagged **ORCH** and is reversible. The human UAT verdicts and the seal are his alone.

## At a glance

| scope | title | status | tag | open items |
|---|---|---|---|---|
| C1 | People | SHIPPED | IN SCOPE | 0 |
| C2 | Even split | SHIPPED | IN SCOPE | 0 |
| C3 | Split by item | SHIPPED | IN SCOPE | 0 |
| C4 | Charges | SHIPPED | IN SCOPE | 0 |
| C5 | Shares that add up | SHIPPED | IN SCOPE | 0 |
| C6 | Copy summary | SHIPPED | IN SCOPE | 0 |
| C7 | Draft kept | SHIPPED | IN SCOPE | 0 |
| C8 | New bill | SHIPPED | IN SCOPE | 0 |

---

## Scope sections

### C1 - People
**Status:** SHIPPED · **Opened:** 2026-10-08 · **Closed:** 2026-10-09 · **Tag:** IN SCOPE
**Implemented by:** core R10, R11, R12, R17 · app R4, R5, R6, R7, R34, core R26, app R42 (duplicate names allowed, added 2026-10-09 after the plan check)
**Proof:** split-app live gate `docs/modules/split-app/qa/live-e2e/20261009-215416/` 7 of 7, 312 browser and 275 unit tests, fidelity 10 of 10 at 0 px. Regression --full to follow

A list of 2 to 12 people they can add, remove and rename.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |
| 2 | sdlc:regression --full | 2026-10-10 regression | Re-verified, no regression. Proof: regression-qa.md (every C1 item PASS, flow F5 Add person double click adds one), cold boot `docs/regression/20261010-142445/` step 2 | ORCH | Re-verified |

### C2 - Even split
**Status:** SHIPPED · **Opened:** 2026-10-08 · **Closed:** 2026-10-09 · **Tag:** IN SCOPE
**Implemented by:** core R1, R7, R18, R20 · app R8, R9, R20
**Proof:** split-app live gate `docs/modules/split-app/qa/live-e2e/20261009-215416/` 7 of 7, 312 browser and 275 unit tests, fidelity 10 of 10 at 0 px. Regression --full to follow

Type the subtotal once and everyone pays the same share, to the cent.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |
| 2 | sdlc:regression --full | 2026-10-10 regression | Re-verified, no regression. Proof: regression-qa.md (every C2 item PASS, flow F1), cold boot `docs/regression/20261010-142445/` steps 2 and 5 | ORCH | Re-verified |

### C3 - Split by item
**Status:** SHIPPED · **Opened:** 2026-10-08 · **Closed:** 2026-10-09 · **Tag:** IN SCOPE
**Implemented by:** core R13, R14, R19, R21 · app R11, R12, R13, R14, R18, R21
**Proof:** split-app live gate `docs/modules/split-app/qa/live-e2e/20261009-215416/` 7 of 7, 312 browser and 275 unit tests, fidelity 10 of 10 at 0 px. Accepted v1.0 limit H-02 (360 px overflow on big bills), fixed in v1.1.0. Regression --full to follow

List each item, tap who had it, and shared items are split between those people.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |
| 2 | sdlc:regression --full | 2026-10-10 regression | Re-verified, no regression. Proof: regression-qa.md (every C3 item PASS, flows F2 and F5, RG-CR-08 holds), cold boot `docs/regression/20261010-142445/` step 4 | ORCH | Re-verified |

### C4 - Charges
**Status:** SHIPPED · **Opened:** 2026-10-08 · **Closed:** 2026-10-09 · **Tag:** IN SCOPE
**Implemented by:** core R3, R5, R6 · app R15, R19
**Proof:** split-app live gate `docs/modules/split-app/qa/live-e2e/20261009-215416/` 7 of 7, 312 browser and 275 unit tests, fidelity 10 of 10 at 0 px. Regression --full to follow

10% service and 6% SST by default, both editable, with SST on subtotal plus service.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |
| 2 | sdlc:regression --full | 2026-10-10 regression | Re-verified, no regression. Proof: regression-qa.md (every C4 item PASS), cold boot `docs/regression/20261010-142445/` steps 2 and 4 (service charge then SST on top) | ORCH | Re-verified |

### C5 - Shares that add up
**Status:** SHIPPED · **Opened:** 2026-10-08 · **Closed:** 2026-10-09 · **Tag:** IN SCOPE
**Implemented by:** core R7, R8, R9, R22, R23 · app R20, R21
**Proof:** split-app live gate `docs/modules/split-app/qa/live-e2e/20261009-215416/` 7 of 7, 312 browser and 275 unit tests, fidelity 10 of 10 at 0 px. Regression --full to follow

Every share is in whole cents and the shares always add up to the total, with the sum shown.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |
| 2 | sdlc:regression --full | 2026-10-10 regression | Re-verified, no regression. Proof: regression-qa.md (every C5 item PASS), fidelity finder clean (the Adds up to row 1-to-1), cold boot `docs/regression/20261010-142445/` steps 2 and 4 | ORCH | Re-verified |

### C6 - Copy summary
**Status:** SHIPPED · **Opened:** 2026-10-08 · **Closed:** 2026-10-09 · **Tag:** IN SCOPE
**Implemented by:** core R24 · app R22, R23, R24
**Proof:** split-app live gate `docs/modules/split-app/qa/live-e2e/20261009-215416/` 7 of 7, 312 browser and 275 unit tests, fidelity 10 of 10 at 0 px. Regression --full to follow

One tap copies a plain-text summary for the group chat.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |
| 2 | Line-break characters in a name could fake an extra line in the copied summary (WR-10) | 2026-10-09 execute | R24 amended, dated: the seven Unicode mandatory line breaks print as one space. Commits `db3bd35`, `46f5670` | LANE (sdlc-dev-solver), ruled ORCH | Solved, security re-check pending |
| 3 | sdlc:regression --full | 2026-10-10 regression | Re-verified, no regression. Proof: regression-qa.md (every C6 item PASS), cold boot `docs/regression/20261010-142445/` steps 3 and 4 (exact summaries in the recorder) | ORCH | Re-verified |

### C7 - Draft kept
**Status:** SHIPPED · **Opened:** 2026-10-08 · **Closed:** 2026-10-09 · **Tag:** IN SCOPE
**Implemented by:** app R2, R25, R26, R27, R28
**Proof:** split-app live gate `docs/modules/split-app/qa/live-e2e/20261009-215416/` 7 of 7, 312 browser and 275 unit tests, fidelity 10 of 10 at 0 px. Regression --full to follow

The bill survives a reload or a closed tab on the same device.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |
| 2 | sdlc:regression --full | 2026-10-10 regression | Re-verified, no regression. Proof: regression-qa.md (every C7 item PASS, flow F4), cold boot `docs/regression/20261010-142445/` steps 5 and 6 | ORCH | Re-verified |

### C8 - New bill
**Status:** SHIPPED · **Opened:** 2026-10-08 · **Closed:** 2026-10-09 · **Tag:** IN SCOPE
**Implemented by:** core R10 · app R29, R30, R31
**Proof:** split-app live gate `docs/modules/split-app/qa/live-e2e/20261009-215416/` 7 of 7, 312 browser and 275 unit tests, fidelity 10 of 10 at 0 px. Regression --full to follow

Clears everything after a confirmation.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |
| 2 | sdlc:regression --full | 2026-10-10 regression | Re-verified, no regression. Proof: regression-qa.md (every C8 item PASS, flow F4), fidelity finder clean (the dialog), cold boot `docs/regression/20261010-142445/` step 6 | ORCH | Re-verified |

---

## Clarify-gate rulings (plan, 2026-10-08)

| # | Question | Ruling | Who | Outcome |
|---|---|---|---|---|
| CG-1 | What is a newly added person called? | Empty field with placeholder "Person N"; "Person N" everywhere else | ORCH | Ruled 2026-10-08, reversible |
| CG-2 | Where does focus go after add and remove? | The new row's name field; after a remove, the field now at that position (or the one above); after the last item, Add item | ORCH | Ruled 2026-10-08, reversible |
| CG-3 | When does an inline error appear? | When the field is left (and at load for restored bad text); it clears while typing once the text is valid or empty | ORCH | Ruled 2026-10-08, reversible |
| CG-4 | Exact number grammar | Trim, ASCII digits, optional dot, 0 to 2 decimals; "12." is 12.00; ".5", "1,000", signs and exponents are errors | ORCH | Ruled 2026-10-08, reversible |
| CG-5 | Thousands separator? | None ("RM 1234.56") | ORCH | Ruled 2026-10-08, reversible |
| CG-6 | Broken unit test command | Fixed in CLAUDE.md (see Off-scope 4) | ORCH | Ruled 2026-10-08, reversible |
| CG-7 | May tests touch the system clipboard? | Never, not even to save and restore it. Tests replace `navigator.clipboard.writeText` in the page with a recorder or a rejecter | ORCH | Ruled 2026-10-08, reversible |
| CG-8 | What does a backdrop click do? | Acts as Cancel, including focus return. **Supersedes** the line in the approved `docs/design/new-bill-dialog.md` that says a backdrop click does nothing (the visual golden is unchanged); matches the design flow check | ORCH | Ruled 2026-10-08, reversible |
| PD-8 | Content Security Policy | Strict policy kept (`style-src 'self'`), after the harness gained `bypass_csp` in sdlc 2.1.2 | ORCH | Ruled 2026-10-08, reversible |
| CG-9 | R37 attack payloads did not fit the field limits | Person payload `<svg onload=f()>` (16 chars), the long payload moved to an item name | ORCH | Ruled 2026-10-09, reversible |
| CG-10 | How the icons are built without failing the no-URL scan | `createElementNS` with exactly the SVG namespace string; `innerHTML`, `insertAdjacentHTML`, `createContextualFragment`, `DOMParser` and `<template` are banned (the last three accepted 2026-10-09 as the planner's extension) | ORCH | Ruled 2026-10-09, reversible |
| CG-11 | Which Python runs the fidelity harness | `run.py` uses `sys.executable`; the README venv is optional | ORCH | Ruled 2026-10-09, reversible |
| RC-5 | `hidden` does not hide an element whose class sets `display` (measured) | `src/system.css` ends with `[hidden] { display: none !important; }`; the R3 walk skips computed `display: none` | ORCH | Ruled 2026-10-09, reversible |

---

## Off-scope and new

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | The plugin fidelity harness could only load a URL, so an app with saved data, a date or a dialog could not reach a golden's state without a test hook in the app | 2026-10-08 plan | sdlc 2.1.0 adds `--candidate-init-script`, `--candidate-after-load`, `--fixed-time`, `--browser-arg`. Control: seeded candidate 0.0%, unseeded 5.1% | ORCH (plugin) | Solved in the plugin |
| 2 | The harness freeze script was an uninvoked arrow function, so `Date.now` and `Math.random` were never pinned (measured) | 2026-10-08 plan | sdlc 2.1.1 invokes it and pins time through Playwright's clock. Verified 0.0% self-diff on a page that prints the time | ORCH (plugin) | Solved in the plugin |
| 3 | A strict CSP (`style-src 'self'`) crashed the harness, which had pushed the Split plan to loosen its own policy | 2026-10-08 plan | sdlc 2.1.2 renders with `bypass_csp`; QA and the live gate still enforce the policy. Control: 2.1.1 crashed, 2.1.2 0.0% | ORCH (plugin) | Solved in the plugin |
| 4 | `node --test tests/` in CLAUDE.md exits 1 on Node 24.11.1 (measured by the planner) | 2026-10-08 plan | CLAUDE.md now uses `node --test "tests/**/*.test.js"` and adds `python -m pytest tests/browser -q` | ORCH | Solved |
| 5 | A planning probe wrote "a" and "b" to the owner's real system clipboard, replacing what was there (headless Chromium on Windows writes the OS clipboard) | 2026-10-08 plan | Ruling CG-7: tests never touch the system clipboard. The previous clipboard content could not be restored | LANE (sdlc-planner) | Solved going forward; the lost clipboard content is reported to the owner |
| 6 | Plan coverage gate, first run (sdlc-plan-checker) | 2026-10-08 plan | BLOCK: 3 block (S5 checklist rows, R37 payload longer than the field, R39 scan vs icon building), 9 flag | LANE (sdlc-plan-checker) | Routed to a fresh planner |
| 7 | All 12 items fixed as ruled | 2026-10-09 plan | PLAN-CHECK.md, Fixes (2026-10-08) | LANE (sdlc-planner, sonnet) | Solved |
| 8 | Plan coverage gate, re-check | 2026-10-09 plan | PASS, 0 block, 1 flag (hidden attribute, ruled RC-5). 68 R#, 108 scenarios, 21 tasks | LANE (sdlc-plan-checker) | Solved |
| 9 | split-core builder judgment calls where the spec is silent: unknown-id setters return the same reference; unassigned counted by people present; shared test helpers in tests/support/; no package.json | 2026-10-09 execute | Accepted as written (BUILD.md, Judgment calls) | LANE (sdlc-backend-dev) proposed, ORCH accepted | Ruled, reversible |
| 10 | split-core code review round 1: PASS, 0 blocker, 10 warning. No wrong money result (S1 and S2 recomputed independently with BigInt). 16 mutants, 5 survived, each tied to a warning | 2026-10-09 execute | Routed to sdlc-dev-solver with rulings. WR-10 ruled (security): the summary replaces every line-breaking character in a label (CR, LF, VT, FF, U+0085, U+2028, U+2029) with a space, so a name cannot fake an Adds up to line in a chat client | LANE (sdlc-code-reviewer) found, ORCH ruled | Open, solver running |
| 11 | The split-core reviewer wrote its baseline node-test.txt with a shell redirect, against the filesystem rule (reported by the reviewer) | 2026-10-09 execute | File verified at the intended path; no strays in the project root or at D:/c, D:/d | LANE (sdlc-code-reviewer) | No damage. Recorded as a process breach |
| 12 | Agents fell back to shell writes because their definitions lacked the tool: sdlc-plan-checker had no Write (it must write PLAN-CHECK.md), sdlc-planner had no Edit (it fixes specs after a BLOCK) | 2026-10-09 execute | sdlc 2.1.3 adds Write to the plan-checker and Edit to the planner | ORCH (plugin) | Solved in the plugin, applies to agents spawned in a new session |
| 13 | split-core code-review solver round: all 10 warnings resolved in 12 commits (`170a293` to `46f5670`). Suite 185 to 212 tests, all pass, each commit green on its own. 28 of 28 planted mutants killed, one control survives as designed. No exported name or signature changed | 2026-10-09 execute | findings/code-review.md, Solver (2026-10-09). Evidence `qa/solver/20261009-121000/` | LANE (sdlc-dev-solver) | Solved, re-check by code-review and security finders pending |
| 14 | The Edit tool turned the escape text `\u2028` and `\u2029` into raw line-separator characters, which broke one uncommitted test run | 2026-10-09 execute | Rewritten as `\u{2028}` and `\u{2029}`. Every touched file scanned, no raw line terminators remain | LANE (sdlc-dev-solver) | Worked around. Agents writing these escapes check the bytes |
| 15 | Contracts the split-app decoder must honour, found by the core solver: reject an unknown `mode`; rebuild or reject people and items carrying unknown or `__proto__` keys (core shares untouched ones by reference); `personLabel` shows VT, FF, U+0085, U+2028, U+2029 as typed while the summary prints a space | 2026-10-09 execute | Carried into the split-app builder brief | LANE (sdlc-dev-solver) found, ORCH routed | Open until split-app ships |
| 16 | split-core security audit: PASS, 0 critical, 0 high, 1 MEDIUM, 3 LOW. All 5 threat-model mitigations held. WR-10 holds (0 of 50,000 fuzzed names forged a line). 600,000 seeded bills match an independent BigInt implementation exactly | 2026-10-09 execute | findings/security.md, evidence `qa/security/20261009T123448/`, commit `e034951` | LANE (sdlc-security-auditor) | Routed to a solver |
| 17 | SEC-01 MEDIUM other control characters (NUL, FS, GS, RS, ESC) pass into the summary; a reader that stops at NUL sees a fake total line. SEC-02 LOW bidi controls reorder one row's share. SEC-03 LOW spec says no residual risk, but a plain name can read like a summary line and an invisible-only name prints blank. SEC-04 LOW purity scan misses eval, Function, dynamic import and other globals | 2026-10-09 execute | Ruled: guard widened to `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]` printed as a space; both SEC-03 cases accepted as residual risk for v1.0 with R17 unchanged; scan list extended, `queueMicrotask` included (supersedes the WR-07 omission) | ORCH | Ruled, reversible |
| 18 | Who fixes the split-core security findings | 2026-10-09 execute | The split-core dev solver was resumed instead of a cold security solver, because it holds the module context and wrote the WR-10 guard. Economy choice | ORCH | Ruled, reversible |
| 19 | split-core security re-check: SEC-01 to SEC-04 CLOSED (all 1,114,112 code points tried, exactly the 79 in the class replaced; bidi checked in headless Chromium). Two new LOW findings about regression guards: SEC-05 the `codeOnly` lexer misses 10 crafted plants, SEC-06 the R24 tests pin 13 of 79 code points | 2026-10-09 execute | Re-check section in findings/security.md, evidence `qa/security/20261009T131232/`, commit `a47bcb7` | LANE (sdlc-security-auditor) | Routed to the solver |
| 20 | How far to chase the hygiene scan | 2026-10-09 execute | Ruled: no lexer hardening. A runtime trap test becomes the primary R25 guard, the source scan stays as best effort with its limits noted. One property test over the code point range for R24. Stop rule: no third security round, the code-review re-check verifies the batch | ORCH | Ruled, reversible |
| 21 | split-core code-review re-check: PASS, 0 blocker, 5 warning, all test or doc (WR-11 property tests pin membership only, a dropped `g` flag survives; WR-12 trap lists unpinned and `globalThis` untrapped; WR-13 trap only sees code that runs; WR-14 BUILD.md test counts rot; WR-15 small items incl. a hit leak in `trapped`). WR-01 to WR-10 resolved, differential 1.77M money and 120,000 action comparisons with 0 differences | 2026-10-09 execute | Re-check section in findings/code-review.md, evidence `qa/code-review/20261009-134620/`, commit `bd7282c` | LANE (sdlc-code-reviewer, sonnet) | Routed to sdlc-dev-solver (sonnet) |
| 22 | Rulings on the re-check warnings | 2026-10-09 execute | All five fixed as the reviewer suggests. Stop rule: no further code-review round, the QA finder runs next | ORCH | Ruled, reversible |
| 23 | split-core re-check warnings solved: WR-11 `28c67ed`, WR-12 `6ec63fb` (`globalThis` trapped, trap lists pinned), WR-13 `7c4e896`, WR-14 `93b9c48`, WR-15 `6edc1b6` (hit leak fixed). Suite 254 of 254, 81 of 85 mutants killed (survivors: 2 identity controls, the documented untaken-branch limit, one equivalent mutant) | 2026-10-09 execute | Solver section in findings/code-review.md, evidence `qa/solver/20261009-141136/` | LANE (sdlc-dev-solver, sonnet) | Solved |
| 24 | B7 equivalent mutant (run id not carried on core-to-core imports) and the unbuilt single banned-names table | 2026-10-09 execute | Both left as is: no input tells B7 apart, and the pin plus the derived test already stop the lists drifting | ORCH | Ruled, reversible |
| 25 | split-core QA finder: PASS. 54 scenarios (179 cases) pass, 0 fail, 0 untested; every R1 to R26 covered; 125 independent money checks and a 400-bill BigInt reference sweep agree. Four assertions noted as weaker than their Then line in form, none failing | 2026-10-09 execute | findings/qa.md, evidence `qa/qa/20261009-142756/`, commit `329679e` | LANE (sdlc-qa-tester, haiku) | Solved |
| 26 | split-core module close: code review PASS (round 1 plus re-check, stop rule), security PASS (audit plus two fix rounds and a re-check, stop rule), QA PASS. Credential gate CLEAN over 2,991 files (controls pass). Suite 254 of 254. Last green `329679e` | 2026-10-09 execute | README reconcile deferred to the split-app close, where the project README is written | ORCH | Module closed |
| 27 | Version label for this run | 2026-10-09 execute | Relabelled v0.1.0 to v1.0.0. Owner's words: "Make sure both app reach a stable 1.0 version. Then i will test it out." Folder moved to `docs/v1.0.0/`, STATE `version: 1.0.0`, plan documents keep their historical label | USER | Done |
| 28 | split-app builder part 1: Tasks 1 to 10, commits `17a95c2` to `4b11bfb`, build record and handoff `a3e7d04`. 149 browser and 265 unit tests pass (11 new decoder tests). Stopped at about 40% context as the role rule requires | 2026-10-09 execute | docs/modules/split-app/BUILD.md, Handoff: resume at Task 11 | LANE (sdlc-frontend-dev, sonnet) | Partial, resumed by a fresh builder |
| 29 | Spec says `src/system.css` hashes equal to the golden (R1, qa) while RC-5 appends the `[hidden]` rule; qa R16 says no live element in the tape while the contract puts the status there | 2026-10-09 execute | Ruled RD-1: RC-5 wins, dated notes in R1 and qa. RD-2: the status is the only live element in the tape, dated note and an exact test | ORCH | Ruled, reversible |
| 30 | A tap just below an invalid price field is lost once: the error inserted on blur shifts the layout about 28 px before the pointer is released (measured with mouse and touch) | 2026-10-09 execute | Ruled RD-3: a defect, not a residual. When a pointer press causes the blur, the error renders after the press is released, through one shared helper for every blur-error field; keyboard blurs unchanged. CG-3 kept | LANE (sdlc-frontend-dev) found, ORCH ruled | Fix in progress |
| 31 | The split-app builder used a Python heredoc to patch four calls in a test file, against the Write and Edit rule (reported by the builder) | 2026-10-09 execute | Verified by grep, inside the project | LANE (sdlc-frontend-dev) | No damage. Recorded as a process breach |
| 32 | split-app builder part 2 (resumed after the owner's stop): reviewed the stopped run's uncommitted work, kept it, finished RD-1 to RD-3 and Tasks 11 to 13. Commits `4a544c3` (RD-1, RD-2), `fceae5f` (RD-3), `84f6422`, `c55f9a4`, `dbab928`, `c40140e`. 205 browser and 265 unit tests pass. Fidelity 10 of 10 pairs at 0 mismatching pixels (5 screens, 390x844 and 1280x800). Live gate 7 of 7 | 2026-10-09 execute | BUILD.md, evidence `qa/fidelity/20261009-172737/`, `qa/live-e2e/20261009-173415/` | LANE (sdlc-frontend-dev, sonnet) | Built, finders next |
| 33 | RD-3 waits for `mouseup` instead of the ruled `pointerup`: a touch tap sends `pointerup` before the focus change, so `pointerup` left every touch case broken (measured) | 2026-10-09 execute | Accepted. Noted in spec R10 | LANE (sdlc-frontend-dev) proposed, ORCH accepted | Ruled, reversible |
| 34 | split-app QA finder: PASS, 145 of 145 qa.md cases, R1 to R42 covered, 515 independent driver checks, 90-bill differential against split-core with 0 mismatches, fidelity re-run 10 of 10 at 0 px. Outside the contract: F-1 MEDIUM a double click or double tap on the dialog's Cancel lands its second click on a toggle beneath and changes the bill (10 of 64 by-item cases on phones). A double click on New bill never wipes the bill. O-1 LOW the by-item table overflows 360 px once a bill is bigger than the sample | 2026-10-09 execute | findings/qa.md, evidence `qa/qa/20261009-174214/`, commit `fcd5a78` | LANE (sdlc-qa-tester, sonnet) | F-1 batched for the solver after code review and security |
| 35 | F-1 and O-1 | 2026-10-09 execute | F-1 ruled a defect: after the dialog closes from a pointer press, the page swallows clicks for about 500 ms (one shared helper). O-1 is a design call on the immutable golden CSS, so it goes to Needs the human (H-02) and is accepted for v1.0 until he rules | ORCH | Ruled, reversible |
| 36 | split-app code review: 1 BLOCKER, 12 WARNING. CR-01 confirms QA F-1 (double click on Cancel changes the saved draft, 6 of 6 cases). WR-01 a double click on Remove deletes two rows. WR-02 to WR-05 test holes (10 mutants survive). WR-06 a press from the dialog text released on the backdrop closes it. WR-07 doc rot, WR-08 README, WR-09 dead code, WR-10 smells, WR-11 rig hygiene, WR-12 the 360 px overflow (H-02). No money outside split-core, CSS is golden plus RC-5 only, 720 random gesture steps broke no invariant | 2026-10-09 execute | findings/code-review.md, evidence `qa/code-review/20261009-181036/`, commit `044800e` | LANE (sdlc-code-reviewer, sonnet) | Routed to sdlc-dev-solver (sonnet) |
| 37 | Rulings on the split-app review | 2026-10-09 execute | CR-01 and F-1 fixed with the reviewer's `event.detail > 1` one-shot listener (supersedes the 500 ms window ruling for F-1). WR-01 treated as the same ghost-click class and fixed. WR-02 to WR-07, WR-09 to WR-11 fixed as suggested; D8 UTF-16 ceiling accepted as a residual; the parent-folder test server kept with a comment. WR-08 README at module close. Stop rule: security, fidelity re-run and the live gate next | ORCH | Ruled, reversible |
| 38 | split-app review solver: CR-01 and QA F-1 `d09d8d6` (double click or tap on Cancel, Start new bill or the backdrop no longer changes the bill: 384 gesture cases, 202 failed on `044800e`, 0 after), WR-01 `9636e84` (double click on Remove removes one row), WR-06 `5f5d4d9` (press from dialog text to backdrop keeps it open), WR-02 to WR-05 test holes closed with mutants shown red, WR-09 to WR-11 dead code, smells and rig hygiene, WR-07 doc rot. Browser 205 to 244, unit 265 to 275, fidelity re-run 10 of 10 at 0 px, live gate 7 of 7 (solver's own run) | 2026-10-09 execute | Solver section in findings/code-review.md, evidence `qa/solver/20261009-190119/` and `qa/fidelity/20261009-200000/`, final `61c3cd3` | LANE (sdlc-dev-solver, sonnet) | Solved |
| 39 | Solver went past the ruled one-shot click listener: `swallowRepeatClicks` also cancels repeat mousedown, because the click-only listener left 3 touch cases failing (second press moved focus off New bill, R30) and a triple click leaked its third click | 2026-10-09 execute | Accepted. Still timer free, removes itself at the first non-repeat press. Revert path is the 6-line listener in 02-fix-proposals.md (4 tests then go red) | LANE (sdlc-dev-solver) found, ORCH ruled | Accepted, reversible |
| 40 | Observation: a double click or tap on Dismiss note moves focus from Person 1 name to the page body. The draft never changed in 10 cases | 2026-10-09 execute | Accepted residual for v1.0 (no data effect, same class as CR-01). Listed for the owner's UAT pass. Security finder checks the ghost-click class across every control | LANE (sdlc-dev-solver) found, ORCH ruled | Accepted residual |
| 41 | Left for module close: README from BUILD.md (WR-08), qa.md scenarios for double click and tap, backdrop press and right click, ROADMAP PD-14 still repeats the Tab-wrap measurement | 2026-10-09 execute | Routed to the module-close step | ORCH | Open, module close |
| 42 | split-app security audit: 0 critical, 0 high, 1 MEDIUM, 2 LOW. SEC-01 a double click, triple click or double tap on Remove of the LAST person removes it, then the repeat lands on Add person (it slides into the freed cell) and saves a blank person (16 of 16 rows). SEC-02 publish scope undefined: serving the repo root would expose 3,086 files incl. 875 mutant copies of src, 143 files with local paths, no .nojekyll. SEC-03 D10 accepts nextId 1000000000, one add saves a draft the decoder then rejects. All 7 threat rows and R37 to R39 held with the CSP live, ghost sweep of 21 controls clean apart from SEC-01. Baseline 244 browser, 275 unit | 2026-10-09 execute | findings/security.md, evidence `qa/security/20261009-201702/` | LANE (sdlc-security-auditor, sonnet) | Routed to the security solver |
| 43 | Rulings on the split-app security audit | 2026-10-09 execute | SEC-01 fixed the general way: `swallowRepeatClicks` moves to dom.js and guards the Remove handlers of people and items in place of `isRepeatClick`. I-1 (a double click on New bill flashes the dialog open then shut) fixed with the same helper if it needs no other change. SEC-02 fixed with a Publish section in CLAUDE.md (serve only index.html, src/ and .nojekyll), same as Streaks SEC-04. SEC-03 accepted residual: only a hand-edited draft or a same-origin page reaches it, and such a page can already overwrite the draft outright, so it adds no capability. Spec gaps closed in the solver's doc pass: threat rows for a repeated press and for the publish scope, the stale U+2028 residual, the CR and LF wording. Stop rule: one scoped re-check, then no further security round | ORCH | Ruled, reversible |
| 44 | split-app security solver: SEC-01 `071577a` (swallowRepeatClicks moved to dom.js and guards every Remove: 40 of 40 defect rows red before, 54 of 54 green, 5 mutants red), I-1 `68ab318` (the New bill opener arms the guard, the dialog stays open after a double click or tap: 12 of 14 red before, 14 of 14 green), SEC-02 `314b827` (Publish section in CLAUDE.md), SEC-03 accepted residual in spec.md, doc pass `314b827` and `12bc878` (threat rows for a repeated press and the publish scope, U+2028 and CR LF wording measured). Browser 244 to 312, unit 275, fidelity 10 of 10 at 0 px, live gate 7 of 7 (solver's own run). The audit's 123-row ghost sweep re-run: data differences only on the toggles that flip twice by design | 2026-10-09 execute | Solver section in findings/security.md, evidence `qa/security-solver/20261009-205629/` and `qa/fidelity/20261009-212142/`, final `b02386b` | LANE (sdlc-security-solver, sonnet) | Solved, scoped re-check pending |
| 45 | Two tabs of one browser editing the bill: last writer wins (audit spec gap 6, not modelled) | 2026-10-09 execute | Accepted as known behaviour for v1.0. The brainstorm keeps one draft in one browser on purpose, and each tab only overwrites the user's own draft | ORCH | Accepted residual |
| 46 | Versioning is part of the showcase: the owner said "Part of the showcase is to show the versioning as well" and chose "Second version per app" and "Fix the v1.0 limits" | 2026-10-09 execute | After the owner seals v1.0.0, Split runs v1.1.0 with one scope item: H-02, the by-item table fits a 360 px phone (small design pass on the table, then plan, execute, finders, regression, review, UAT). H-02 ruled: shipped in v1.0.0 as an accepted limit | USER | Ruled |
| 47 | split-app security re-check (scoped): SEC-01 closed (36 of 36 rows one removal, no blank row, nextId unchanged, 3 of 3 control rows show the old defect), I-1 closed (24 of 24), no over-swallow found, the 123-row ghost sweep differs from a single click only on the 5 toggles that flip twice by design, CSP live 0 violations. New LOW SEC-04: a held Enter on Remove of the only item adds a blank item (auto-repeat presses Add item after focus moves there), keyboard only, also on the pre-fix tree. Suites 312 browser, 275 unit | 2026-10-09 execute | Re-check section and ORCH ruling in findings/security.md, evidence `qa/security-recheck/20261009-213133/` | LANE (sdlc-security-auditor, sonnet) | Closed with one accepted limit |
| 48 | Ruling on SEC-04 | 2026-10-09 execute | Accepted v1.0 limit under the stop rule (one click undoes it, keyboard held only). Goes into v1.1.0 with H-02, per the owner's choice that v1.1.0 fixes the v1.0 limits. Fix in hand from the re-check: a capture keydown listener in swallowRepeatClicks that cancels event.repeat | ORCH | Accepted for v1.0, scoped to v1.1.0 |
| 49 | split-app official cold-boot live gate on the final code: 7 of 7 steps PASS (empty storage, even split, copy, by item, come back, start over, logs clean: 0 console errors, 0 CSP violations, only same-origin GETs) | 2026-10-09 execute | Evidence `qa/live-e2e/20261009-215416/`, commit `341d990` | ORCH | PASS |
| 50 | split-app module close: QA PASS (F-1 fixed), code review solved (CR-01, WR-01 to WR-11) with WR-08 closed by the project README, security clean after audit, solver and one re-check (stop rule, SEC-04 accepted for v1.0 and scoped to v1.1.0), fidelity 10 of 10 at 0 px on the final code, live gate 7 of 7. README reconciled from BUILD.md and verified by symbol. ROADMAP PD-14 fixed. Credential gate CLEAN over the whole tree (3,448 files, controls pass). Browser 312, unit 275. Last green `22ac9af` | 2026-10-09 execute | README.md, ROADMAP.md, findings/*.md | ORCH | Module closed |
| 51 | How to run sdlc:regression --full at the tail of execute without re-burning finders on code they already passed | 2026-10-09 regression | ORCH economy, measured: split-core src is unchanged since its last green `329679e` (git diff empty). split-app src at `22ac9af` is byte-identical to what the security re-check (`b02386b`) and the solver's fidelity run (`qa/fidelity/20261009-212142/`, 10 of 10 at 0 px) saw, so their verdicts stand as the regression's security and fidelity results. Re-run: a code-review finder on the split-app delta no reviewer has seen (`61c3cd3..22ac9af`, the repeat-press guard) plus the README and the core seam, and a QA finder (haiku) on both modules on the final code. Cold-boot gate run by the orchestrator into `docs/regression/<ts>/` | ORCH | Ruled, reversible |
| 52 | Regression code review of the split-app delta `61c3cd3..22ac9af`: 1 BLOCKER, 3 WARNING, 3 INFO. RG-CR-01 a regression introduced by `071577a`: a double click, triple click or double tap on the right 44 px of Add person adds a person and removes it again (the new row's Remove slides under the pointer, and the Remove handler no longer ignores a repeat press unless a Remove click armed the guard). 61c3cd3 +1 in 36 of 36 rows, shipped tree +0 in 36 of 36, focus lands on the wrong name. No test double clicks Add person, so all 312 stayed green. RG-CR-02 mutant M1 (mousedown listener never removed) survives the suite. RG-CR-03 four stale README lines. RG-CR-04 doc rot in qa.md, BUILD.md and a test docstring. Core seam clean. Suites 312 and 275 | 2026-10-09 regression | findings/regression-code-review.md, evidence `qa/regression-code-review/20261009-220225/` | LANE (sdlc-code-reviewer, sonnet) | Routed to the dev solver |
| 53 | Rulings on the regression code review | 2026-10-09 regression | RG-CR-01 kept as a BLOCKER (a regression of verified behaviour is what regression exists to catch): Add person and Add item arm swallowRepeatClicks on their click, as the finder verified in a scratch copy, with tests at the right edge of the button and the refuted claims corrected (dom.js JSDoc, spec R7 and the threat row, BUILD.md call 18). RG-CR-02 fixed by making the guard-lifetime tests see mousedown too. RG-CR-04 fixed by the solver. RG-CR-03 and RG-CR-06 README lines are the orchestrator's, reconciled after the tree settles. RG-CR-05 accepted (the derivation is restated, not wrong). RG-CR-07 accepted (only a copy without CLAUDE.md fails one test, and the publish copy ships no tests). Then one scoped code-review re-check (stop rule) | ORCH | Ruled, reversible |
| 54 | Regression dev solver: RG-CR-01 `e30b015` (Add person and Add item arm swallowRepeatClicks: the 36 right-edge Add person rows red before, 108 of 108 green after, focus on the new name, nextId +1), RG-CR-02 `17ac1ed` (the guard-lifetime tests see presses too, mutant M1 red in 4), RG-CR-04 and the errors.js and BUILD.md wording `38686c0` and `f0ca022`, section and evidence `677d719`. Mutants M1 to M8, A1 and A2 all killed. Browser 312 to 421, unit 275, fidelity 10 of 10 at 0 px, live gate 7 of 7 (solver's own run) | 2026-10-09 regression | Solver section in findings/regression-code-review.md, evidence `qa/regression-solver/20261009-222856/` and `qa/fidelity/20261009-225850/` | LANE (sdlc-dev-solver, sonnet) | Solved, scoped re-check pending |
| 55 | README reconcile after the regression solver (RG-CR-03, RG-CR-06) | 2026-10-09 regression | Status closed, counts at v1.0.0, `commit` takes the bill an action returned, errors.js is not all pure, swallowRepeatClicks names every armer and says it protects only them, the backdrop sentence, billCharges in place of the private applyRate, the clipboard stand-in wording, and where the limits' reasoning lives | ORCH | Done |
| 56 | Regression code-review re-check (scoped): RG-CR-01, RG-CR-02, RG-CR-04 and the README hold (Add rows 96 of 96, 40 deliberate-action cases unharmed, mutants M1, M2, M9, M10, A1, A2 red). New RG-CR-08 BLOCKER, a second regression of `071577a`: with an invalid price field focused, a double press on a who-had-it chip removes the whole item, because the RD-3 error line pushes the chips down and the repeat press lands on that item's Remove, which since `071577a` acts on every click. 96 of 96 overlap layouts remove the item on HEAD, 0 on `61c3cd3`, 0 with the fix. Narrow reach (median 1.4 percent of chip area). Suites 421 and 275 | 2026-10-09 regression | Re-check section in findings/regression-code-review.md, evidence `qa/regression-recheck/20261009-230750/` (probe_toggle_remove.py, candidate test test_rg_cr_08_candidate.py red 6 of 6 on HEAD, green on the fix) | LANE (sdlc-code-reviewer, sonnet) | Routed to the dev solver |
| 57 | Ruling on RG-CR-08 | 2026-10-09 regression | Kept as a BLOCKER and fixed, not accepted: it deletes data the user typed, through a gesture that worked before today. Fix as the re-check verified in a scratch copy: the Remove handlers of items and people again ignore a click with a count above 1 (`isRepeatClick` exported from dom.js) as well as arming swallowRepeatClicks, plus the candidate test rows, plus corrections to BUILD.md call 18, spec R7, the Threat model row and the swallowRepeatClicks JSDoc. The stop rule holds for code review: the solver proves it red and green with the re-check's own probe and candidate test, and the regression QA finder and cold boot run after it. Queued for the next session (owner asked to wrap up at 23:40) | ORCH | Ruled, reversible |
| 58 | Regression dev solver round 2 on RG-CR-08: `4a36354` (dom.js exports `isRepeatClick`, the item and person Remove handlers ignore a click with a count above 1 as well as arming the guard, plus 6 test rows), `059f560` (BUILD.md call 18 and code map, spec R7 and the Threat model row, qa.md scenario, JSDoc). New rows red 6 of 6 on the unfixed src, green 6 of 6 after. The re-check's probe, unchanged: real double click removes 0 of 96 affected layouts (96 of 96 before). Mutant B1 reds exactly the 6 rows, B2 (person Remove) is noticed by no test, as expected. Suites 427 browser and 275 unit, fidelity 10 of 10 at 0 px, live gate check 7 of 7 | 2026-10-10 regression | Solver round 2 section in findings/regression-code-review.md, evidence `qa/regression-solver-2/20261010-122502/`, fidelity `qa/fidelity/20261010-123651/` | LANE (sdlc-dev-solver, sonnet) | Solved |
| 59 | Close of code review for v1.0.0 after solver round 2 | 2026-10-10 regression | Stop rule: no further code-review round. RG-CR-08 closed on the solver's proof with the re-check's own probe and candidate test. findings/regression-code-review.md status pass. README reconciled (427 browser tests, the swallowRepeatClicks bullet says a Remove also ignores a repeat press itself). The regression QA finder and the official cold boot decide the regression verdict | ORCH | Code review closed |
| 60 | Regression QA on the final code (haiku): PASS, 340 of 341 items (split-core 179, split-app 162), 0 fail, 1 untested (R40 Looks right, the FE element checklist half). Suites 275 and 427. Driven checks D1 to D4 pass, pixel gate 10 of 10 at 0 px, live gate 7 of 7. Five flows by hand at 390 x 844, 73 of 73 checks, including F5: a double click on a chip over its own Remove under a pending price error removes no item (RG-CR-08 holds) | 2026-10-10 regression | findings/regression-qa.md, evidence `qa/regression-qa/20261010T124914/` | LANE (sdlc-qa-tester, haiku) | PASS, 1 untested |
| 61 | Gap found by the orchestrator: the split-app fidelity finder (sdlc-fidelity-tester, the FE element checklist plus its judgement of the pixel gate) never ran. Execute closed the module on harness pixel runs alone (10 of 10 at 0 px), so R40's checklist half has no verdict. Streaks ran its fidelity finder (71 of 71 rows), Split did not | 2026-10-10 regression | Not accepted as a limit: regression --full runs every finder on every FE module. Routed to sdlc-fidelity-tester on split-app in the next free agent slot. The regression verdict waits for it | ORCH | Routed |
| 62 | Owner asked for READMEs that look good and a simple logo per example app (2026-10-09 23:40), and on 2026-10-10 for the logo to live in each project where needed | 2026-10-10 regression | Logo files in docs/brand (the logo stays out of v1.0 screens). The favicon goes into the app in v1.1.0 through the design phase, next to H-02 and SEC-04. No header mark inside the app (the goldens have none) | USER | Ruled |
| 63 | Logo: an equals sign whose top bar is cut once, two to one, over one whole bar, ink only | 2026-10-10 regression | logo-qa PASS 21 of 24, no gate failed, contrast verified. The orchestrator applied QA's two pre-release fixes (wordmark width locked with textLength, the description's arithmetic) plus caption contrast and one comment. docs/brand/BRAND.md records the decisions and the usage rules | LANE (logo-designer, logo-qa), ORCH | Done |
| 64 | README redesign | 2026-10-10 regression | Lockup header for light and dark, static badges in the app's tokens (facts at 1.0.0, never live status), a showcase image composed from two real pixel-gate captures, a Mermaid lifecycle, a table of what the reviews caught, a versions table, the technical detail folded in details blocks | ORCH | Done |
| 65 | split-app fidelity finder (sonnet), the gap routed at 13:16: 1-to-1, status clean, 0 findings, 12 observations. Pixel gate 10 of 10 at 0 mismatching pixels (8 byte-identical, the 2 dialog pairs differ by at most 2 of 255 on rounded corners only), extra runs at 360, 600 and 1024 15 of 15. FE element checklist 131 of 131 qa.md rows plus 26 finder rows, 157 of 157. Whole-page comparison 35 pairs, 2,242,912 property comparisons, 0 differences outside native-modal properties. 13 one-thing mutants all caught. R40 now fully verified | 2026-10-10 regression | findings/fidelity.md, evidence `qa/fidelity/20261010-133017/` and `qa/fidelity-checklist/20261010-133500/` | LANE (sdlc-fidelity-tester, sonnet) | PASS |
| 66 | Fidelity observation O-01: new-bill-dialog.md says a backdrop click does nothing, the app closes the dialog as Cancel | 2026-10-10 regression | Not a finding: the clarify-gate ruling CG-8 names and overrides that golden sentence. Listed for the owner in the UAT handover (H-01, delegated choices) | ORCH | Ruled, CG-8 stands |
| 67 | Process slip declared by the fidelity finder: one Python heredoc changed a constant in its own scratch helper, and about a dozen stdin heredocs read its own JSON | 2026-10-10 regression | No product, test or doc file touched by them. Recorded against the Write-and-Edit-only rule | LANE (sdlc-fidelity-tester) | Recorded |
| 68 | Security on the regression's fixes after `22ac9af` (`e30b015`, `4a36354`, a comment in src/errors.js) | 2026-10-10 regression | Not re-audited: the fixes change only which clicks an Add or a Remove acts on, with no new input, storage, rendering or network path. The security verdict on `22ac9af` stands | ORCH | Ruled, reversible |
| 69 | sdlc:regression --full closed | 2026-10-10 regression | Cold boot 7 of 7 PASS into `docs/regression/20261010-142445/` (0 console or page errors, no CSP violation, same-origin GETs only). Suites on the final tree 275 unit and 427 browser. Fidelity finder clean. docs/regression/REGRESSION.md written. Process ledger reconciled. Full credential gate exit 0 | ORCH | PASS |
| 70 | sdlc:review, stakeholder seat | 2026-10-10 review | Precondition: regression PASS at 14:30 and no code change since (git diff of src, index.html and tests against `dc180ad` is empty), so it stands. Drove the brainstorm on a cold boot with real gestures, no seed, clipboard recorder only (CG-7): 80 of 80 checks (4 key flows, the brainstorm's summary example copied word for word, amount grammar, rate ranges, half-up rounding, leftover cents, 2 to 12 people, 50 items, blank and duplicate names, removing a person from every item, blocked clipboard, unreadable draft, keyboard and focus ring, 360 and 1280 px, reduced motion, non-goals, same-origin only, 0 console errors). Money figures worked out by the script from the brainstorm's rules. H-02 measured again as a known limit (383 px at a RM 1,058.40 item total). Evidence `docs/review/20261010-144746/`. Verdict: shippable for UAT. Deviations named with cause in docs/lifecycle.md. No requirement dropped, nothing invented. Compliance skipped (personal). No out-of-project artifacts logged. docs/lifecycle.md and docs/init/repo-summary.md written | ORCH | Shippable for UAT |
| 71 | Review observation: if storage is blocked or full, a change is not saved and no message says so | 2026-10-10 review | Accepted for v1.0. The brainstorm asks for a note only when a saved draft cannot be read. Listed for the owner under H-01 in the UAT handover | ORCH | Accepted, reversible |
| 72 | sdlc:uat sitting 1 of 1 written: 8 cases, one per scope (C1, C2, C5, C4, C6, C3, C7, C8 in the order a person meets them), with the two handover sections (OPEN: H-01 delegated choices with the backdrop ruling CG-8 inside UAT-08, D-01 limits accepted for 1.0; SOLVED: seven items in plain language, including the clipboard overwritten during planning). Preconditions held: regression PASS, review done, ledger current (handoff folder empty), credential gate clean over 4,102 files | 2026-10-10 uat | docs/v1.0.0/user-test-2026-10-10/TEST-CASES.md. App served by the orchestrator on 127.0.0.1:8732 (pid 9084), served index.html and src/main.js verified | ORCH | Written |
| 73 | UAT pre-run by sdlc-uat-tester (sonnet) on the orchestrator's server: 8 of 8 PASS at 1280 x 800 and again at 390 x 844, 235 of 235 checks each. UAT-05's paste step not driven (CG-7), the copied text verified on the recorder instead. No case blocked. Its own first run marked UAT-06 FAIL on an instrument error (innerText drops the CSS gap in "+ Charges"), fixed and re-run from a fresh context. Nine wordings flagged: the satay split is not printed on its own, the tab-close and address pitfalls in UAT-07, the faint Person 3 hint, the column heads, 10% and 6%, the Tab into SST, a paste target's own trailing line, where to click outside the box, where Add person sits | 2026-10-10 uat | Script wording repaired from those notes (no step changed its action), the tester's verdicts copied beside the empty human column. Evidence `docs/v1.0.0/user-test-2026-10-10/pre-run/20261010-145359/` | LANE (sdlc-uat-tester, sonnet), ORCH | Ready for the owner |
| 74 | Owner's UAT verdicts, sitting 1: UAT-01 to UAT-08 all PASS, in his words "Pass" on each, with notes on UAT-03 and UAT-06. Tester and owner agree on every verdict | 2026-10-10 uat | Recorded word for word with the date in TEST-CASES.md. Findings keyed by case in docs/v1.0.0/user-test-2026-10-10/findings.md | USER | PASS 8 of 8 |
| 75 | UAT-F1 on UAT-03, owner: "Pass but i prefer if it cannot be evenly split, the number in summary should show the extras then let the user decide to put to who or have a button or random split. So user can split manually or randomly or even have 1 person pay the extras" | 2026-10-10 uat | Routed FULL as a new scope for 1.1.0 (brainstorm row, design, plan, build, finders). It changes the brainstorm's leftover-cents rule, which was an ORCH call | USER | Proposed for v1.1.0, waiting for his yes |
| 76 | UAT-F2 and UAT-F3 on UAT-06, owner: "You did not include what the service charge and sst. Be as accurate and precise as possible when doing test cases. Also the shares number is correct but the charges for ben is 2.25 and aiyah is 4.13 when in test cases ben is 2.24 and aisyah is 4.14 ( check if this is a bug or a simple logic mistake)" | 2026-10-10 uat | F2: script rule taken, every expected result lists every figure and line on screen. F3: re-run in Chromium 149, Chrome 154 and Edge 154 gives Aisyah 4.14 and Ben 2.24 as scripted. His figures appear exactly when Ben is above Aisyah in the list, and then the shares read 15.75 and 29.03. A row's share is always its items plus its charges, so no screen shows the scripted shares beside those charges. Evidence `docs/v1.0.0/user-test-2026-10-10/evidence-uat-f3/` | ORCH | No bug found, cause unconfirmed, asked him |
| 77 | H-01 ruling, owner: "i am happy with the choices made." | 2026-10-10 uat | Every choice taken under delegation stands, including CG-8 (a click outside the New bill box cancels) | USER | Ruled |
| 78 | D-01, owner: "Discuss each item" | 2026-10-10 uat | Each accepted 1.0 limit discussed with him one by one. Each keeps its status until he rules | USER | In discussion |
| 79 | Owner comments on both apps: (1) "Wheres the logo. I dont see it being used for both" (2) "Both designs are great but is just that its so dull. Need to spice it up so it looks nicer" (3) "Test cases, i want steps and expected result in a table. Much easier to read. Bigger fonts for UAT number. I think scope, problem, precond, steps and result should be in a table. Steps and result can be side by side. If theres any extra notes, have a row for notes as well. Overall make it nicer to read the whole test cases. Its hard for a human to find a read properly. Present it better. Also include some sort of verdict selection examples so people will know if its pass or fail or any other option with its explanation somewhere at the top. i think the best is to run the design phase with me. Propose 5 designs for both app. Doesnt need to be working, i just want the design part." (4) "I also want this part to be displayed in the showcase. What else besides test cases can be shown. We dont need to show all, just bits or parts of it so people can know what it is." | 2026-10-10 uat | Correction to row 62, dated: "no header mark inside the app" was the orchestrator's reading of "where needed", not his words. He expects to see the logo in the app, so it goes into the app in 1.1.0 through the design phase with him. Comments 2 and 3 go to a design round run with him, comment 4 to the showcase plan. Routing agreed in the conversation | USER | Recorded, routing with him |
| 80 | UAT-F3 answered, owner: "UAT 06 probably is because of ben was above or something." and "Most likely. I think i deleted aisyah and addedf later so yes" | 2026-10-10 uat | Removing Aisyah and adding her back put her below Ben, so the leftover sen went to Ben as the rule says | USER | Closed, not a bug |
| 81 | D-01 ruled, owner: "i agree with all. for number 4, its a shared state so technically changing at 1 place will change at the other. If they want to add a different bill, we can have this as future implementation. I think its a good thing to have this as future implementation and put this as a doc only so that we can showcase it. So we dont need to implement this but put this like a future implementation kind of doc." | 2026-10-10 uat | Into 1.1.0: the held Enter (SEC-04), a message when the bill cannot be saved, Safari's engine (WebKit) in the test runs. Kept as known limits: the shared github.io address, the Dismiss note double click, the invisible-only name. Two tabs kept as is, and several bills becomes a future-implementation document in 1.1.0, not code | USER | Ruled |
| 82 | 1.1.0 scope, owner: "3.  Yes." (to the spare-sen choice for the user) | 2026-10-10 uat | UAT-F1 becomes a 1.1.0 scope | USER | Ruled |
| 83 | Name, owner: "for split, change it to SplitIO. Also, if both names cant be used, then add Danials [app name] Or if theres a better way to make it uniquely to me." | 2026-10-10 uat | Name check: "SplitIO" is Split.io, the feature-flag company Harness bought in 2024. Not usable. His fallback applies. The name and the wordmark are chosen with him in the 1.1.0 design round | USER | Into the 1.1.0 design round |
| 84 | Design round, owner: "Yes, doesnt need to be functionable, as long as i can see the design. Including popups and modals or anything that requires a button click or something. If its easier and faster to make it work instead , then do it. The important thing is, the prototype design should be quick and mainly focus on the design. Also, this phase should be with the designer. Before doing this, list out what the designer does. I forgot" | 2026-10-10 uat | 1.1.0 design round with him: 5 directions per app as clickable static prototypes (dialogs and popups reachable), the test-case layout in the same round. The designer's role listed for him before it starts | USER | Ruled |
| 85 | Showcase, owner: "For comments 4, i like all of that." | 2026-10-10 uat | The showcase shows the version story from UAT to 1.1.0, the test sheet with both columns, one bug story, the design exploration and the pixel match | USER | Ruled |
| 86 | Seal, owner: "1. Seal both apps" | 2026-10-10 uat | v1.0.0 sealed: SEAL.md, local tag v1.0.0, next working version 1.1.0 | USER | Sealed |

---

## Needs the human

### H-01 - Review the decisions taken under delegation
- **Why an agent cannot decide it:** requirement and design choices belong to the owner. He delegated
  them for this run, so each one is recorded and reversible.
- **Where they are:** the brainstorm grill log (`docs/brainstorm/brainstorm.md`), the design picks
  (`docs/design-explore/round-1/DECISION.md`), the design rulings (`docs/design/RULINGS.md`), the
  clarify-gate rulings above, and the planner decisions in `docs/modules/ROADMAP.md`.
- **Recommendation:** read the two compare pages and the rulings first. They carry the most taste.
- **Ruling:** 2026-10-10, USER, at UAT: "i am happy with the choices made." Every delegated choice stands.

### H-02 - The by-item table is wider than a 360 px phone on a big bill (added 2026-10-09)
- **What:** the split-app QA finder (O-1) measured the by-item shares table overflowing a 360 px screen
  once the item total passes RM 653.40 (365 px wide), up to 466 px for a 12-person, 50-item bill. The four
  sample states in the spec all fit.
- **Why an agent cannot decide it:** the cause is the approved golden CSS, which is immutable outside the
  design phase. Changing it is a design decision.
- **Options:** accept for v1.0 (the page scrolls sideways on big bills on small phones), or reopen the
  design for the table (for example a smaller amount column or wrapping names).
- **Recommendation:** accept for v1.0 and note it in the README. A restaurant bill that large on a 360 px
  phone is uncommon.
- **Ruling:** 2026-10-09 21:35, USER. Asked what the next version holds, the owner chose "Fix the v1.0
  limits", with H-02 named in the choice. So v1.0.0 ships with the overflow (accepted for v1.0, noted in
  the README), and v1.1.0 fixes it through a small design pass on the table, since the golden CSS can
  only change in the design phase.

---

## Field reference

| field | values | why |
|---|---|---|
| Status | `SHIPPED` · `PARTIAL` · `NOT SHIPPED` | Whether the scope actually landed, as a field, not prose. |
| Tag | `IN SCOPE` · `ORCH` · `USER` · `DEFERRED` | Who owns the decision. `ORCH` items are reversible; the human may overturn any of them. |
| Proof | measurement + where it lives | Without it, "Solved" is a claim. |
| Who | `USER` · `ORCH` · `LANE` (+ which agent) · `IN SCOPE` | Who authored the change. |
| Outcome | `Solved` · `PARTIAL` · `DEFERRED → vX.Y.Z` · `WITHDRAWN` · `NEEDS THE HUMAN` | `WITHDRAWN` keeps a wrong finding visible, so the record never reads cleaner than reality. |
