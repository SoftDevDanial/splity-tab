# STATE-LOG: split

Append-only history. STATE.md holds the situation, this file holds what happened.

## 2026-10-08 10:45 init
- Ran the `sdlc:init` steps. Greenfield project, track `sdlc`, working version 0.1.0.
- Installed `docs/constitution.md`, `docs/phase-skills.md`, the Windows context hooks in
  `.claude/settings.json`, and the day-one `.gitignore`.
- This project is one of two showcase examples. The owner delegated the run to the orchestrator
  ("Auto create with lifecycles for 2 projects", 2026-10-08). Decisions taken under that delegation are
  tagged ORCH. The human UAT column and the seal stay with the owner.

## 2026-10-08 10:50 brainstorm
- Wrote docs/brainstorm/brainstorm.md. Personal direction, so no market panel.
- 13 grill questions answered by the orchestrator under the owner delegation, all tagged ORCH.
- Gate approved under delegation (ORCH). Owner may reopen any row.

## 2026-10-08 10:50 design started
- Wrote docs/design-explore/BRIEF.md with the inventory (steps 1 and 2). Inventory confirmed under delegation (ORCH).
- Phase skills loaded by the orchestrator: taste-skill, frontend-design. Each direction agent is told to load them too.
- Round 1: three direction agents, run two at a time across both examples (the owner caps parallel agents at two).

## 2026-10-08 11:10 plugin upgraded mid-run
- The owner split the plugin on 2026-10-08. sdlc 2.0.0 records design-phase: in place of track:. STATE.md and docs/.sdlc-init now say design-phase: sdlc:design.
- Re-copied docs/constitution.md from sdlc 2.0.0 (two lines changed, both about naming the design phase). No rule this run relies on changed.

## 2026-10-08 11:21 design round 1
- Three direction agents wrote round-1/a.html (Receipt tape), b.html (Colour per person), c.html (Working shown). Each verified at 390, 360 and 1280 px, PROCESSES none.
- Wrote round-1/compare.html with the recommendation. Picked C under delegation (ORCH), see round-1/DECISION.md. Two changes folded into the system lock, so no round 2.
- Spawned the composer agent for steps 5, 6 and 8.

## 2026-10-08 15:52 design finalized
- Composer agent wrote design-explore/final/ (system, 5 screens, states sheet, 6 docs, self-critique). Cut off once by the usage limit at 11:31, resumed at 15:35 with its context.
- Flow check: 12 of 12 links pass, zero console errors (design-explore/FLOW-CHECK.md).
- Ruled four open questions and approved the added copy under delegation (ORCH), design-explore/RULINGS.md.
- Promoted final/ to docs/design/ under delegation (ORCH). Phase skills loaded throughout: taste-skill, frontend-design.

## 2026-10-08 15:53 plan started
- Step 1 research: no unknown blocks a confident plan (Playwright 1.61 with page.clock and Node v24.11.1 confirmed installed). 0 researchers spawned.
- Step 1b compliance: personal direction, skipped by rule.
- Step 2: spawned sdlc-planner (Opus, effort high).

## 2026-10-08 23:01 plan, architect and gates
- sdlc-planner wrote split-core (25 R#) and split-app (41 R#), ROADMAP. Cut off once by the usage limit, resumed.
- Clarify gate CG-1 to CG-8 ruled under delegation (ORCH). CG-7: tests never touch the OS clipboard, after a planning probe overwrote the owner clipboard. CG-8 supersedes one line of new-bill-dialog.md.
- Found three plugin harness gaps while planning, fixed in sdlc 2.1.0, 2.1.1, 2.1.2 (state setup flags, freeze that never ran, CSP bypass). Strict CSP restored in R38.
- Opened docs/v0.1.0/CHANGE-LEDGER.md (8 scopes).
- sdlc-plan-checker: BLOCK, 3 block, 9 flag. Fixes ruled (ORCH) and routed to a fresh planner.

## 2026-10-09 11:41 plan gate cleared
- Fresh planner fixed 3 BLOCK and 9 FLAG. Re-check PASS (0 block, 1 flag). Flag ruled RC-5 (hidden attribute) and written into split-app spec as a dated correction.
- Ledger: CG-9 to CG-11, RC-5, plan gate rows, C1 now names core R26 and app R42.
- Plan phase done. Next: execute, split-core then split-app.

## 2026-10-09 11:48 split-core built
- sdlc-backend-dev (sonnet) built split-core: commits bb3fba9, 3399736, 5d98d13, 8228969, e40c171, 50b6a8b, 27458ba, 025e232, BUILD.md 67e4b6e. 185 node tests pass.
- Five judgment calls accepted under delegation (ORCH, ledger). Spawned code-review finder (Opus).

## 2026-10-09 12:33 split-core solver round closed, owner sets v1.0.0 target
- Dev solver: WR-01 to WR-10 resolved in 12 commits, 212 of 212 tests pass at `46f5670`, 28 of 28 mutants killed. Findings Solver section and evidence `qa/solver/20261009-121000/` committed by the orchestrator
- Behaviour change: `summaryText` prints the seven Unicode mandatory line breaks in names as a space (R24 amended, dated)
- Owner's words 2026-10-09: "Make sure both app reach a stable 1.0 version. Then i will test it out." The run's version label moves from 0.1.0 to 1.0.0
- Next: security auditor (WR-10 plus threat model), then QA and code-review re-check

## 2026-10-09 13:01 split-core security audit
- Security auditor: PASS, 1 MEDIUM (control characters other than the 7 breaks), 3 LOW (bidi controls, spec residual wording, purity list). Commit e034951
- Ruled ORCH: widen the guard to Cc, Zl, Zp and Bidi_Control; accept two residuals for v1.0; extend the purity list incl. queueMicrotask. Resumed the split-core dev solver for the fixes (economy)

## 2026-10-09 13:12 split-core security fix batch
- Solver: SEC-01 b3b43fe, SEC-02 a09ce03, SEC-03 b5b448d, SEC-04 e56b396. 230 of 230 tests pass, each commit green on its own
- Next: security re-check (resume the auditor), then QA finder and code-review re-check

## 2026-10-09 13:31 split-core security re-check
- Re-check: SEC-01 to SEC-04 closed. New LOW SEC-05 (codeOnly lexer false negatives) and SEC-06 (R24 tests pin 13 of 79 code points). Commit a47bcb7
- Ruled ORCH: runtime trap test as primary R25 guard, property test for R24, exact wording in spec and JSDoc. No third security round; the code-review re-check verifies

## 2026-10-09 13:42 split-core security round 2 fixes
- Solver: SEC-05 fedaa7a (runtime trap test is the primary R25 guard), SEC-06 5d5d02a (property tests over every code point), wording 4e2740b. 246 of 246 tests pass
- Next: scoped code-review re-check of every change since 67e4b6e, then QA finder
