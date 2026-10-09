# CHANGE LEDGER - v0.1.0

> The version's ONE attribution record and the human's only complete view of what happened.
> `STATE.md` is *situation*, handoffs are *resume points*, `findings/` are *evidence*. **None of them is
> the record.** `sdlc:uat` derives its cases from the **scope sections** below and its handover from
> **Needs the human**, so an item that is not here never reaches the human.
>
> **Rules (constitution, The CHANGE LEDGER):** updated at **every close** (round, fix batch, module, live
> gate, finder loop, decision, deferral) · corrections are **additive and dated**, never a silent
> rewrite · **staleness check** at every phase boundary: newest dated entry here vs newest file in
> `./docs/progress/handoff/`. Handoff newer means this file is stale.

**Version:** v0.1.0 · **Opened:** 2026-10-08 by `sdlc:plan` · **Sealed:** not yet (see `SEAL.md` once sealed)

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

---

## Field reference

| field | values | why |
|---|---|---|
| Status | `SHIPPED` · `PARTIAL` · `NOT SHIPPED` | Whether the scope actually landed, as a field, not prose. |
| Tag | `IN SCOPE` · `ORCH` · `USER` · `DEFERRED` | Who owns the decision. `ORCH` items are reversible; the human may overturn any of them. |
| Proof | measurement + where it lives | Without it, "Solved" is a claim. |
| Who | `USER` · `ORCH` · `LANE` (+ which agent) · `IN SCOPE` | Who authored the change. |
| Outcome | `Solved` · `PARTIAL` · `DEFERRED → vX.Y.Z` · `WITHDRAWN` · `NEEDS THE HUMAN` | `WITHDRAWN` keeps a wrong finding visible, so the record never reads cleaner than reality. |
