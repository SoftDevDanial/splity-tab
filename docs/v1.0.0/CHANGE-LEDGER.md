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
documents written before that date still say v0.1.0. · **Sealed:** not yet (see `SEAL.md` once sealed)

> **This run was delegated.** The owner asked for the whole lifecycle to be created ("Auto create with
> lifecycles for 2 projects", 2026-10-08). Every decision an agent or the orchestrator took in his place is
> tagged **ORCH** and is reversible. The human UAT verdicts and the seal are his alone.

## At a glance

| scope | title | status | tag | open items |
|---|---|---|---|---|
| C1 | People | NOT SHIPPED | IN SCOPE | 0 |
| C2 | Even split | NOT SHIPPED | IN SCOPE | 0 |
| C3 | Split by item | NOT SHIPPED | IN SCOPE | 0 |
| C4 | Charges | NOT SHIPPED | IN SCOPE | 0 |
| C5 | Shares that add up | NOT SHIPPED | IN SCOPE | 0 |
| C6 | Copy summary | NOT SHIPPED | IN SCOPE | 0 |
| C7 | Draft kept | NOT SHIPPED | IN SCOPE | 0 |
| C8 | New bill | NOT SHIPPED | IN SCOPE | 0 |

---

## Scope sections

### C1 - People
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** core R10, R11, R12, R17 · app R4, R5, R6, R7, R34, core R26, app R42 (duplicate names allowed, added 2026-10-09 after the plan check)
**Proof:** not yet (set at the module's live gate and at regression)

A list of 2 to 12 people they can add, remove and rename.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C2 - Even split
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** core R1, R7, R18, R20 · app R8, R9, R20
**Proof:** not yet (set at the module's live gate and at regression)

Type the subtotal once and everyone pays the same share, to the cent.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C3 - Split by item
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** core R13, R14, R19, R21 · app R11, R12, R13, R14, R18, R21
**Proof:** not yet (set at the module's live gate and at regression)

List each item, tap who had it, and shared items are split between those people.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C4 - Charges
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** core R3, R5, R6 · app R15, R19
**Proof:** not yet (set at the module's live gate and at regression)

10% service and 6% SST by default, both editable, with SST on subtotal plus service.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C5 - Shares that add up
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** core R7, R8, R9, R22, R23 · app R20, R21
**Proof:** not yet (set at the module's live gate and at regression)

Every share is in whole cents and the shares always add up to the total, with the sum shown.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C6 - Copy summary
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** core R24 · app R22, R23, R24
**Proof:** not yet (set at the module's live gate and at regression)

One tap copies a plain-text summary for the group chat.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |
| 2 | Line-break characters in a name could fake an extra line in the copied summary (WR-10) | 2026-10-09 execute | R24 amended, dated: the seven Unicode mandatory line breaks print as one space. Commits `db3bd35`, `46f5670` | LANE (sdlc-dev-solver), ruled ORCH | Solved, security re-check pending |

### C7 - Draft kept
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** app R2, R25, R26, R27, R28
**Proof:** not yet (set at the module's live gate and at regression)

The bill survives a reload or a closed tab on the same device.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C8 - New bill
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** core R10 · app R29, R30, R31
**Proof:** not yet (set at the module's live gate and at regression)

Clears everything after a confirmation.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

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

---

## Needs the human

### H-01 - Review the decisions taken under delegation
- **Why an agent cannot decide it:** requirement and design choices belong to the owner. He delegated
  them for this run, so each one is recorded and reversible.
- **Where they are:** the brainstorm grill log (`docs/brainstorm/brainstorm.md`), the design picks
  (`docs/design-explore/round-1/DECISION.md`), the design rulings (`docs/design/RULINGS.md`), the
  clarify-gate rulings above, and the planner decisions in `docs/modules/ROADMAP.md`.
- **Recommendation:** read the two compare pages and the rulings first. They carry the most taste.
- **Ruling:** (pending)

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
- **Ruling:** (pending)

---

## Field reference

| field | values | why |
|---|---|---|
| Status | `SHIPPED` · `PARTIAL` · `NOT SHIPPED` | Whether the scope actually landed, as a field, not prose. |
| Tag | `IN SCOPE` · `ORCH` · `USER` · `DEFERRED` | Who owns the decision. `ORCH` items are reversible; the human may overturn any of them. |
| Proof | measurement + where it lives | Without it, "Solved" is a claim. |
| Who | `USER` · `ORCH` · `LANE` (+ which agent) · `IN SCOPE` | Who authored the change. |
| Outcome | `Solved` · `PARTIAL` · `DEFERRED → vX.Y.Z` · `WITHDRAWN` · `NEEDS THE HUMAN` | `WITHDRAWN` keeps a wrong finding visible, so the record never reads cleaner than reality. |
