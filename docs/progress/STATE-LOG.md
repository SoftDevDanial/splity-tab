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

## 2026-10-09 14:10 split-core code-review re-check
- Code-review re-check: PASS, 5 low warnings WR-11 to WR-15, all test or doc. Commit bd7282c
- Routed to a sonnet dev solver. Stop rule: QA finder next, then module close

## 2026-10-09 14:27 split-core re-check warnings solved
- Solver (sonnet): WR-11 to WR-15 resolved, 254 of 254 tests, HEAD 6edc1b6
- Per the stop rule: QA finder next, then module close

## 2026-10-09 14:38 split-core closed, version relabelled 1.0.0
- QA finder PASS: 54 scenarios, R1 to R26 covered. Commit 329679e
- Module close: credential gate CLEAN (2,991 files), 254 of 254. Last green 329679e. README deferred to the split-app close
- Version relabelled 0.1.0 to 1.0.0 on the owner's word: docs/v0.1.0 moved to docs/v1.0.0, ledger header carries the dated relabel

## 2026-10-09 15:10 split-app part 1 built
- Builder part 1 (sonnet): Tasks 1-10, 17a95c2..4b11bfb, handoff a3e7d04 at 40% context
- Ruled RD-1 (system.css hash vs RC-5), RD-2 (status is the only live element), RD-3 (lost tap below an invalid price is a defect, fix by rendering the blur error after the pointer release). Fresh builder started on Tasks 11-13

## 2026-10-09 15:47 split-app builder stopped by the owner
- Fresh builder (Tasks 11-13 plus RD-1 to RD-3) stopped by the owner at 15:46 before any commit. Work in progress left uncommitted in the tree, listed under Blockers. HEAD a3e7d04

## 2026-10-09 17:11 split-app resumed on the owner word
- Owner chose: resume as planned (2026-10-09 15:50). Fresh builder started 17:12 after the usage reset; it reviews the uncommitted work in progress before committing

## 2026-10-09 17:29 cross-project note
- Streaks security found a double-click delete through an overlapping dialog button (SEC-01 HIGH). The Split security audit must test the same on New bill and Start new bill, which wipes the bill

## 2026-10-09 17:41 split-app built
- Builder part 2: RD-1 to RD-3 and Tasks 11-13, 4a544c3..c40140e. 205 browser, 265 unit. Fidelity 0 px on all 10 pairs, live gate 7/7
- mouseup instead of pointerup for RD-3 accepted (measured touch behaviour)

## 2026-10-09 18:06 split-app QA PASS
- QA (sonnet): PASS 145/145, R1-R42 covered. F-1 MEDIUM double click on Cancel changes the bill (ruled a defect, batched for the solver). O-1 overflow at 360 px on big bills goes to Needs the human H-02. New bill double click is safe
- Code review (sonnet) started

## 2026-10-09 19:00 split-app code review
- Code review (sonnet): 1 BLOCKER (double click on Cancel, same as QA F-1), 12 warnings incl. double click on Remove. Commit 044800e
- Routed to a sonnet dev solver with rulings. Stop rule set

## 2026-10-09 20:11 split-app review solver collected
- Solver resolved CR-01 and F-1, WR-01 to WR-11 in 15 commits, final `61c3cd3`. Browser 244, unit 275, fidelity 10 of 10 at 0 px.
- Accepted the solver's wider repeat-press guard (mousedown too), reversible.
- Dismiss note double click moves focus to the body, no data effect: accepted residual, listed for the owner's UAT.
- Next: security finder, fidelity re-check, official live gate, README, module close.

## 2026-10-09 20:54 split-app security audit collected
- Audit: SEC-01 MEDIUM (double click on the last Remove adds a blank person), SEC-02 LOW publish scope, SEC-03 LOW nextId ceiling.
- ORCH: SEC-01 and I-1 fixed with swallowRepeatClicks in dom.js, SEC-02 Publish section, SEC-03 accepted residual, spec gaps in the doc pass.

## 2026-10-09 21:28 split-app security solver collected
- Solver: SEC-01 and I-1 fixed with swallowRepeatClicks on every Remove and the New bill opener, SEC-02 Publish section, SEC-03 and two-tab last writer wins accepted. Browser 312, unit 275, fidelity 10 of 10 at 0 px.
- Scoped re-check launched (sonnet). Stop rule after it.

## 2026-10-09 21:54 split-app security re-check collected, security clean
- Re-check: SEC-01 and I-1 closed, no over-swallow. New LOW SEC-04 (held Enter on the only item's Remove adds a blank item) accepted for v1.0 and scoped to v1.1.0. Stop rule reached.
- Owner's versioning decision recorded: after the v1.0.0 seal, v1.1.0 fixes H-02 and SEC-04.

## 2026-10-09 21:56 split-app closed, all modules closed
- Official live gate 7 of 7 on the final code (`341d990`).
- README written from BUILD.md, verified by symbol, ROADMAP PD-14 fixed (`22ac9af`).
- Full credential gate CLEAN (3,448 files). split-app CLOSED, last green `22ac9af`. Scopes C1 to C8 SHIPPED pending regression.

## 2026-10-09 21:57 regression started
- ORCH economy ruling recorded: security and fidelity verdicts stand on identical code; code-review delta and QA re-run; cold boot by the orchestrator.

## 2026-10-09 22:26 regression code review collected
- RG-CR-01 BLOCKER: 071577a regressed a double click on the right edge of Add person (adds then removes). Routed to the dev solver with RG-CR-02 and RG-CR-04.

## 2026-10-09 23:04 regression solver collected, README reconciled
- RG-CR-01 fixed (Add buttons arm the guard), RG-CR-02 and RG-CR-04 fixed, 421 browser, 275 unit, fidelity 0 px.
- README reconciled (RG-CR-03, RG-CR-06).

## 2026-10-09 23:50 regression re-check collected, RG-CR-08 blocker
- Re-check: RG-CR-01 to 04 hold. New RG-CR-08 BLOCKER, second regression of 071577a (chip double press removes the item). Fix verified by the re-check in a scratch copy. Queued for next session.

## 2026-10-10 12:48 RG-CR-08 solved, code review closed
- Dev solver round 2: 4a36354 fix (isRepeatClick exported, Remove handlers ignore a repeat press, 6 test rows), 059f560 docs. Red 6 of 6 then green, probe 0 of 96, B1 killed, B2 recorded.
- Suites 427 browser, 275 unit. Fidelity 10 of 10 at 0 px (qa/fidelity/20261010-123651/). Live gate check 7 of 7.
- Solver section and ORCH ruling merged into findings/regression-code-review.md, status pass. Stop rule: code review ends for v1.0.0.
- README reconciled: 427 browser tests, swallowRepeatClicks bullet.

## 2026-10-10 14:26 regression --full closed, PASS
- Fidelity finder (the gap found at 13:16): 1-to-1 clean, 157 of 157 rows, 10 of 10 at 0 px. Commit a1658e6.
- Cold boot 7 of 7 PASS into docs/regression/20261010-142445/.
- REGRESSION.md written (mode, scope, the fidelity gap, the security ruling on the regression's fixes, finder verdicts, two solver rounds, cold boot table).
- CHANGE-LEDGER: re-verified rows C1 to C8, the security ruling, the close row. Process ledger +31 rows. Full credential gate exit 0.
- last-regression = PASS @ 2026-10-10 14:30.

## 2026-10-10 14:49 review, shippable for UAT
- Precondition: regression PASS at 14:30, no code change since dc180ad.
- Stakeholder drive on a cold boot, real gestures, no seed: 80 of 80 checks, H-02 measured again as a known limit. Evidence docs/review/20261010-144746/.
- docs/lifecycle.md (phase table, verdict, deviations with cause) and docs/init/repo-summary.md written.
- Compliance skipped (personal). No out-of-project artifacts logged.
- Staleness check: newest ledger entry 2026-10-10 review, docs/progress/handoff/ is empty, so the ledger is current.

## 2026-10-10 15:02 uat sitting 1 written and pre-run, ready for the owner
- TEST-CASES.md: 8 cases from the ledger scopes, handover (a) OPEN H-01 and D-01, (b) SOLVED seven items.
- App booted by the orchestrator on 127.0.0.1:8732, pid 9084, served output verified. Deliberately running for the owner.
- sdlc-uat-tester (sonnet): 8 of 8 PASS at 1280 x 800 and 390 x 844, 235 checks each, paste step not driven (CG-7). Evidence pre-run/20261010-145359/.
- Script wording repaired from the tester's nine notes, tester column filled, human column empty.

## 2026-10-10 15:58 owner's UAT verdicts recorded
- Owner: 8 of 8 PASS, his words recorded with the date in TEST-CASES.md. H-01 ruled ("i am happy with the choices made."), D-01 in discussion.
- findings.md: UAT-F1 leftover sen chosen by the user (FULL, 1.1.0), UAT-F2 script precision (taken), UAT-F3 his 2.25 and 4.13 not reproduced in Chromium, Chrome or Edge, they appear only with Ben above Aisyah.
- Ledger rows with his exact words, including his comments on the logo, the plain look, the test-case layout and the showcase, and a dated correction of the logo row.

## 2026-10-10 16:35 v1.0.0 sealed
- Owner's words: "1. Seal both apps". All UAT cases PASS in his words, his rulings recorded (D-01, H-01, names, design round, showcase).
- Both UAT servers found already ended at 16:33 (most likely the session restart at about 16:10, after his verdicts at 15:48). Process ledger rows closed.
- SEAL.md written (checks, shipped scopes, UAT both columns, residuals as ruled, what goes into 1.1.0). Ledger marked sealed. Credential gate clean. Local tag v1.0.0 on the seal commit.

## 2026-10-10 16:37 v1.1.0 opened
- docs/v1.1.0/CHANGE-LEDGER.md opened with the scopes the owner approved at UAT and at the seal.
- STATE version 1.1.0.

## 2026-10-10 16:46 to 20:25 v1.1.0 design round 1 and the UAT sheet
- Inputs with the owner: feeling words "Decide for me" (ORCH: sharp, quick, social), "futuristic but minimal, like discord", the spare-sen line with Top of the list, One person and At random, name "Danial's Splity Tab" (the logo and header show "Splity Tab"). Brainstorm delta, docs/future/several-bills.md (S9) and docs/design-explore/v1.1.0/BRIEF.md committed `22641e1`.
- UAT sheet: three layouts `94bda22`, his pick "C revised" after two rounds of notes (`da8a354`, `c4e37f2`), approved 19:27 (`ac5f73f`, ledger off-scope row 5). Shipped as sdlc 2.2.0's test sheet template on his ask.
- Five directions, each by its own designer agent, two at a time, with render checks at 390, 360 and 1280 px: A Night Console `da8a354`, B Glass Receipt `755447a`, C Daylight Instrument `9ce713c`, D Share Orbit `efb824b`, E Command Line `ceaaf87`. All 0 console errors, no sideways scroll at 360, every inventory figure asserted.
- Rule slips by designers, all self-reported, no file left behind: A redirected output once ("> run2.log", deleted) and fetched six public Phosphor icon files. E used "2>&1" to the terminal (no file). Later briefs forbid both by name.
- compare.html written by the orchestrator `d1deb01`: pick D Share Orbit, runner-up A. Waiting for the owner (ledger H-03).

## 2026-10-10 21:43 to 21:55 v1.1.0 round 1 ruled, round 2 briefed
- Owner picked a mix: D Share Orbit's layout in A Night Console's colours, no bright filled buttons (his clarification of "neon backgrounds"), Charges above the Even/By item switch on desktop, the item list in its own scroll frame, inputs first on a phone with the receipt behind a button, keep the spare sen ("i love the sen left over"). Ledger H-03 ruling, S7 row 3.
- ORCH readings, flagged for round 2: "Split" is the Even/By item switch, the phone receipt becomes a pinned bar with Total, Shares (a sheet) and Copy summary.
- round-2/BRIEF.md written. One new direction F Orbit Console next.
## 2026-10-10 22:18 v1.1.0 round 2 direction F Orbit Console built
- Designer agent: round-2/f.html, f.md, checks/f (43 screenshots). Verified on disk: 69 of 69 boolean checks, no fails, 0 console and page errors, 0 network requests, no bright fills, no page scroll at 1280 x 800 in K1, K2, S3, S5, S6, S7, W2 (item frame 1229 px in 269 px in W2), every inventory figure, no browser left running.
- Designer readings to flag on the compare page: People above the item frame in two columns on desktop, the pinned bar in two rows (Total, then Shares and Copy summary), Copy summary also inside the Shares sheet, four person colours changed (periwinkle and lavender read as the indigo accent), S5 and S6 notes in the top bar, Copy summary now really copies on a press (D only showed the status), Add person and Add item in their headings. At 390 px the Prototype states tab sits tight against the People avatars (no overlap measured).
## 2026-10-10 22:50 owner corrected the round 2 base
- Owner: "My mistake. What i meant for splity is color night console but use glass receipt". Clarified: "neon backgrounds" means only the glow behind the receipt, Copy summary keeps a solid indigo fill. Ledger H-03 correction and new readings, S7 row 4.
- The orchestrator had mapped his comments onto D, its own recommendation. F Orbit Console (b1587bf) is WITHDRAWN and kept as a record. round-2/BRIEF-G.md written for direction G Glass Console on B. Designer not yet launched (5-hour usage 72%, context past the handoff point).
## 2026-10-10 23:41 v1.1.0 round 2 direction G Glass Console built, compare page written
- Designer agent: round-2/g.html, g.md, checks/g (65 screenshots, check_g.py, results.json). Verified on disk: designer's check 0 fails, 0 console errors, 0 network, clipboard stand-in only. Orchestrator's own spot check at 1280, 390 and 360: block order People, Charges, Split, Items, no page scroll at 1280 x 800 in K1, K2, S7, W2, the W2 list scrolls in its 291 px frame, strip pinned to the bottom, Shares opens the sheet and Esc closes it, copy to the stand-in only, shares add up to RM 69.26, Copy summary fill #5059DA, no radial glow in the source, the Prototype states tab overlaps nothing. Committed `2d5f222`.
- One catch, flagged on the compare page: on a phone "1 sen left over" is only inside the Shares sheet.
- Designer's self-reported slip: one run of its check script piped through grep with a stderr redirect (2>&1 | grep). Read-only, nothing written, no file left behind. Later briefs keep forbidding it by name.
- round-2/compare.html written (B, A, G at 390 and 1280, his points table with B's measured figures: desktop page 1,262 px tall, phone first field at 775 px, against G's 800 and 130, readings table). Rendered at 1280 and 390, no sideways scroll, no broken images, desktop switch works, no long dashes. The 6 console lines are Chromium's 'Blocked autofocusing' notices for the dialogs' autofocus inside file:// iframes. The prototypes alone log 0.

## 2026-10-11 00:05 owner accepted G, brief for phone revision G2
- Owner: "For Splity, i like it. Small thing is the mobile." People and Charges collapse on the phone, Items is the heavy part. On the sen line: it stays in the sheet, and "Shares" becomes "Splits". His words in ledger H-03 round 2 ruling, S7 row 6.
- ORCH readings, flagged: (f) phone only, desktop unchanged. (g) collapsed by default with a summary line, People open on a new bill, errors open their section. (h) "Splits" everywhere the word "Shares" was read.
- round-2/BRIEF-G2.md written. One designer builds g2.html from g.html next.
