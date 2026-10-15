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

## 2026-10-11 00:37 v1.1.0 round 2 revision G2 built, compare page updated
- Designer agent: round-2/g2.html, g2.md, checks/g2 (79 screenshots, check_g2.py, results.json). g.html untouched (byte-equal to HEAD). Designer's check 501 of 501. Self-report: four plain runs of its check script, no rule broken, a near miss on four icon path digits fixed before the first run and now asserted.
- Orchestrator's own spot check at 1280, 390 and 360: desktop block positions equal to G, no page scroll at 1280 x 800 in K1, K2, S7, W2, both sections folded in K1 with the right summaries, 52 px header rows, tap, Enter and Space toggle, summary follows an edit, S1 People open and Charges folded, a rate error opens Charges and a folded Charges reads 'Check service charge', S7 summary on one line, 'Splits' on the bar, the sheet and the heading, no 'share(s)' in visible text or accessible names, '1 sen left over' in the sheet, splits add to RM 69.26, 0 console errors, 0 network, copy to the stand-in only. 58 of 62 at first, the 4 misses were the check comparing the summary with its screen-reader-only ', ' prefix. The visible text is right.
- Designer readings put to him: G2 adds the 1.0 rate error copy (G had none), the summary hides while open, 'and N more' for twelve people, S6 left folded (question for him).
- round-2/compare.html updated: G2 section on top (G beside G2 at 390, the S1 screenshot), his two points added, G2 readings added, G's two questions marked answered with his words, the desktop switch shows G2. Rendered at 1280 and 390, no sideways scroll, no broken images, no long dashes. Console lines are the iframes' autofocus notices only.

## 2026-10-11 01:00 owner accepted G2, compare page fixed, compose brief for steps 5 to 8
- Owner first read G2 as unchanged. Cause: the compare page at the pane's 961 px put G's frame first and the lower section still showed G as the pick. G2 was right. Orchestrator fix: G2 first, G labelled "Before your phone note". Owner: "Nevermind. I saw it. It looks good now." then "Both looks good. We can procceed as usual". G2 accepted. Committed `79bd2ee` with ledger S7 row 8 and the H-03 final ruling (S6 opens People, ORCH).
- sdlc:design steps 5 to 8 next, staged in design-explore/v1.1.0/final/. v1.1.0/COMPOSE-BRIEF.md written.

## 2026-10-11 02:37 v1.1.0 steps 5, 6 and 8 composed
- Composer agent: final/ with 15 goldens and notes, system.md + system.css (no colour, size or space value changed, --strip-h default 111 px for scriptless goldens, a static stand-ins section for open dialogs, the Prototype states rules removed), MANIFEST, LINKS (48), SELF-CRITIQUE. Its check 778 of 778: 0 console, 0 page errors, 0 network, no sideways scroll, no page scroll at 1280 in all 15, targets 44 px, contrast with glass composited, sums 6926, 11660, 6296, 119387 in whole sen, the strip never over an input, no 'Shares', system.css byte-equal in every golden. Only difference from g2: S6 on a phone opens People (ORCH ruling).
- Orchestrator check: nothing changed outside final/ (docs/design, 1.0's final/ and round-2 clean in git), all 15 goldens render at 390 and 1280 with 0 console errors, 0 requests, no sideways scroll, no page scroll at 1280, bill-items.html at 390 matches g2.
- Composer's self-reported bends: two scripts (measure and check), scripts wrote their own results and screenshots inside checks/.

## 2026-10-11 11:58 v1.1.0 step 7 wired and verified
- flowcheck_v.py split v1.1.0 first run 24 of 32, all eight helper limits (hidden mode radios, the composer's chip taps as points). Helper fixed, 48 of 48 with width-less links at all three widths.
- One golden defect found while testing names. Chromium's own tree read the phone header rows as "People , Aisyah, Ben, Chen". People and Charges now named by .sec-name and described by .sec-sum, hidden comma gone, nothing visible changed. check_final.py 778 of 778 (specimen compare ignores g2's hidden comma).
- FLOW-CHECK.md and prototype/ written. Ledger S7 rows 9 and 10.

## 2026-10-11 13:01 owner's rulings on the composed set, rate error follows 1.0
- Owner chose the recommended option on all four questions. Copy list and interaction rules approved, small points accepted, logo marks to be redrawn.
- ORCH, told to him. An invalid rate or price blocks the receipt as in 1.0 core R18 and app R17, so rate-error.html will show the blocked receipt. Not done yet.

## 2026-10-11 13:25 rate-error golden blocked as in 1.0
- rate-error.html, the card's receipt and the strip now show the blocked state of 1.0 core R18 and app R17, "Check the charges to see the splits." under the receipt icon, no Total, Copy summary disabled. Golden strip height 108 px as bill-empty.html.
- rate-error.md, SELF-CRITIQUE (ruled difference from g2, copy list, open questions 1 and 2 ruled) and the prototype copy updated. check_final.py 748 of 748, 0 console, 0 network (the 30 money asserts on the old Total no longer apply). Flow check 48 of 48. Ledger S7 row 11.
- sdlc 2.5.0 install confirmed (installed_plugins.json, cache 2.5.0, commit 087dc18).

## 2026-10-11 13:33 v1.1.0 RULINGS.md written
- docs/design-explore/v1.1.0/RULINGS.md. USER, copy list and thirteen rules approved, P1 on K2, dialog edges accepted, the mark redrawn. ORCH, the blocked receipt order a to e, a blank rate blocks (1.0 core R18 (a)) and never counts as 0, folded Charges shows Check for a blank rate, row c widens R18 (c) to no valid price, a plan delta.
- rate-error.md had said a blank rate counts as 0 "as in 1.0". 1.0 blocks on it. Fixed, with states.md's price note. check_final.py 748 of 748. Ledger S7 row 12.

## 2026-10-11 15:08 logo round 1 started
- Brief written (glass receipt, one flat fill, 28 px header and 16 px favicon slots, no D). S1 the fan retired after two reviews (a W or crest, or a three-card fan). S2 the receipt S retired (a plain bold S at the real sizes). S3 the tear is the tick passed 26 of 28. Lesson added as hard constraint 7, the idea must read at 28 and 16 px. Committed 3d847dc.

## 2026-10-11 23:36 Logo S12 approved and swapped
- Round 1 closed, S3 and S8 declined, round 2 stopped, the owner kept the 1.0 mark with a receipt outline
- S12 passed QA 26 of 28 after a mirrored tear and a chat tail were fixed, owner approved, empty state shows S12 muted
- S12 swapped into final/ (15 goldens), check_final 748 of 748, FLOW-CHECK 48 of 48, ledger S7

## 2026-10-13 design v1.1.0 finalized
- Finalize gate approved by the owner 2026-10-11 23:45 ("Yes, but later"), run in the showcase session after the unify move
- final/ copied into docs/design/, 34 files (20 new, 14 replacing 1.0's, 1.0's in tag v1.0.0), SHA-256 equal. v1.1.0 rulings beside 1.0's as RULINGS-v1.1.0.md. checks/ and SELF-CRITIQUE.md stay in design-explore
- check_final.py rerun with goldens read from docs/design/, 747 of 748, every golden section equal to the final/ run. The fail is 1.0's RULINGS.md header in the markdown lint's glob, left as sealed (design-explore/v1.1.0/finalize/)
- Phase skills loaded throughout the round, taste-skill and frontend-design (docs/design/system.md, Skills loaded). Ledger S7 row 14. Next sdlc:plan

## 2026-10-13 plan v1.1.0 done
- Research, clarify gate parts 1 and 2 (CG-P1 to CG-P8, all USER as recommended), delta contracts for split-core (34 R#) and split-app (61 R#), ROADMAP v1.1.0
- First plan check BLOCK (`9c5a673`), fix pass, re-check PASS, touch-up of F11, F12, N9, N10. Done at `853afe1` (23:05). Ledger scopes S1 to S9 name their module R#s

## 2026-10-14 execute v1.1.0 started
- Resumed by sdlc:continue at 11:54. Ledger current (newest entry 2026-10-13 23:05, newest handoff 19:38). Process sweep by name, age, port and command line found nothing of the project's after the 11:46 reboot
- Owner said start the build waves now, both apps, and confirmed the WebKit download again
- Step 0 done 12:34. WebKit 26.5 (webkit-2311) installed and launched headless once. Playwright's install also removed two unreferenced Chromium 1187 folders from its cache. Process ledger row 41, ledger S5 row 3. Next A0
- 12:34 to 15:07, A0, C1 to C6 and A1 built and committed. The record is the ledger (S1 rows 4 to 8, S5 rows 4 and 5, Needs the human H-04, H-05) and the handoff `handoff-2026-10-14-execute-orchestrator.md`

## 2026-10-14 15:20 resumed by sdlc:continue
- Ledger current (ledger written 15:07:53, newest handoff 15:07:30). Process sweep by name (node, python, bash, sh, cmd, browsers, Playwright), command line (sdlc-showcase, http.server, pytest, live_e2e) and listening ports 3000 and up found nothing of either app. Ports held only by the owner's apps (Steam, Discord, display pad service)
- Orchestrator action 2 done, WebKit commands in `CLAUDE.md` (ledger S5 row 6)
- 15:27 frontend dev (Opus, high) launched for A2 to A4, stop before a new task past 30 percent context. Streaks builder runs beside it
- 15:45 A2 built, NOT committed, builder stopped at 39 percent context (ledger S7 row 17, handoff `handoff-2026-10-14-execute-split-A2.md`). Q-A2-1 and Q-A2-3 and the R29 test ruled ORCH. Process ledger row 47
- 15:55 owner rulings. The seven untracked run folders stay untracked (his test, no value to a reader, no loss). Q-A2-2 "Follow the rule i said previously", read as the house rule, six fixtures archived to `{archive}\2026-10-14-split-fixtures\`, SHA-256 equal 6 of 6 (ledger S7 row 18)
- 15:57 frontend dev launched to finish and commit A2, then A3 and A4 if context allows
- 16:17 A2 DONE `d62c270` (ledger S7 row 19). WebKit 35 failures against the A0 48, the shift ruled ORCH (S5 row 7). Builder stopped at 35 percent context before A3. Process ledger row 48
- 16:20 planner launched for the owed pass (H-04 rule draft for the owner, H-05 capture, five class (b) lines, Q-A2-1 wording, test context defaults, task ticks). A3 after it
- 16:45 planner pass DONE `42f47e8` (ledger S5 row 8). 19:56 resumed (the owner's break). Fresh 5-hour window, weekly 86 percent. Orchestrator sweep clean
- 20:00 H-04 ruled USER "Time + place" (ledger H-04). A17 moves up after A3 (ORCH). 20:02 planner resumed for the follow-up commit
- 20:07 follow-up DONE `4c9d2c8` (ledger S5 row 9). 20:10 frontend dev for A3 then A17
- 20:36 A3 DONE `695bff5` (ledger S4 row 4). Builder stopped at 37 percent context before A17, handoff `handoff-2026-10-14-execute-split-A17.md`. F-A3-1 and Q-A3-1 ruled ORCH. Process ledger row 49
- 20:40 orchestrator stopped at 34 percent context and weekly usage 88 percent, no new agent. Handoff `handoff-2026-10-14-execute-orchestrator-2.md`
- 20:43 orchestrator resumed after compaction. Owner ruling USER "Keep going ... stop at 98% only this time", so this run's stop line for either usage window is 98 percent (in place of the 90 percent write-now line and the 75 percent launch line). Ledger staleness check, ledger 20:41 newer than handoff 20:40, current. Sweep by name, age, port and command line found nothing of either app. Run folder `functional/20261014-153212-chromium/` (A2 intermediate run, process row 47) stays untracked with the seven, same class (ORCH)
- 20:45 frontend dev launched for A17 from `handoff-2026-10-14-execute-split-A17.md`
- 21:16 A17 DONE `22cc845` (ledger S5 row 10, H-04 built), verified on disk (junit counts and failing ids, `system.css` blob, `docs/design/` unchanged, no attribution line). Builder stopped at 31 percent context, handoff `handoff-2026-10-14-execute-split-A4.md`. Process ledger row 50
- 21:20 frontend dev launched for A4
- 22:12 A4 DONE `7dac4de` (ledger S7 row 20), verified on disk (junit counts and failing ids, `system.css` blob, `docs/design/` unchanged, no attribution line). Builder stopped at 46 percent context, handoff `handoff-2026-10-14-execute-split-A5.md`. Process ledger row 51. Orchestrator sweep 22:13 clean. Usage 5 hour 41 percent, weekly 91 percent
- 22:15 frontend dev launched for A5
- 22:44 A5 DONE `8b882a6` (ledger S7 row 21), verified on disk (junit counts and failing ids, `system.css` blob, `docs/design/` unchanged, no tar in the repo, no attribution line). F-A5-1 ruled ORCH to A16. Builder stopped at 41 percent context, handoff `handoff-2026-10-14-execute-split-A6.md`. Process ledger row 52. Usage 5 hour 51 percent, weekly 93 percent
- 22:46 frontend dev launched for A6
- 23:22 A6 DONE `4b806ff` (ledger S7 row 22), verified on disk (junit counts and failing ids, `system.css` blob, `docs/design/` unchanged, no attribution line). Builder stopped at 39 percent context, handoff `handoff-2026-10-14-execute-split-A7.md`. Process ledger row 53
- 23:25 usage 5 hour 71 percent (resets 00:50), weekly 95 percent (resets 01:00), orchestrator context 20 percent. At the present rate both reach 98 percent near 00:35, before the resets. ORCH plan, both builders time-boxed to have their files written by 00:10, then a pause until the resets and a resume at 01:01 by a background timer. Frontend dev launched for A7 with the 00:10 deadline
- 23:43 A7 DONE `0180d36` (ledger S7 row 23), verified on disk (junit counts and failing ids, `system.css` blob, `docs/design/` unchanged, no attribution line). Builder stopped at 19 percent context, handoff `handoff-2026-10-14-execute-split-A8.md`. Process ledger row 54, the orchestrator's timer row 55
- 23:45 usage 5 hour 77 percent, weekly 96 percent, orchestrator context 23 percent. Split lane held until the 01:00 reset (ORCH), A8 would not finish by 00:10 and a second agent would bring the weekly window near 98 percent. Streaks task 26 runs to its 00:10 deadline
- 23:48 both lanes held, resume timer set for 01:02 (process row 56)
- 2026-10-15 00:25 owner "Wrap up. Timer doesnt need to wake you. Going to put my pc to sleep". 00:26 timer stopped, handoff `handoff-2026-10-15-execute-orchestrator-3.md`, ledger off-scope row 17. Nothing running. Resume with `/sdlc:continue`, NEXT A8

## 2026-10-15 07:38 execute v1.1.0 resumed, fourth orchestrator session (Split and Streaks)
- `/sdlc:continue` read the constitution, phase-skills, STATE, handoff 3 and the A8 handoff. Ledger staleness check: newest ledger entry 2026-10-15 00:27, newest handoff 00:26, ledger CURRENT in both apps
- Sweep 07:39 by name, age, command line and listening ports, shells included. The PC rebooted 07:25. Timer PIDs 19428, 10700, 7408, 20692 not present. No python, node, browser or bash process of either app. Port 8000 is the owner's Base Camp app (PID 21376), not ours
- Usage 5 hour 0 percent (resets 12:30), weekly 0 percent (resets 2026-10-22 01:00). House rule applies again (no new agent at 75 percent of the 5 hour window)
- 07:42 frontend dev (Opus, high) launched for A8 from `handoff-2026-10-14-execute-split-A8.md`. Streaks task 27 builder beside it
- 08:16 A8 DONE `e1969da` (ledger S7 row 24), verified on disk (junit counts and failing ids, `src/system.css` and `docs/design/` unchanged, `tests/fixtures/` gone, no STUB in `src/`, no attribution line). Chromium 544 tests 0 failures 94 xfail, WebKit 4 failures, all A16's. Builder stopped at 44 percent context, handoff `handoff-2026-10-15-execute-split-A9.md`. Process ledger row 57. README reconciled (`placeModeBlocks`, `markFrame`). Q-A8-1 to the owner as H-06, the build follows R18 as written until he rules. F-A8-1 qa wording joins the planner's list
- 08:21 frontend dev (Opus, high) launched for A9. Streaks QA finder beside it
- 08:20 to 11:50 the H-06 question waited on the owner (the orchestrator blocked on it, both agents had returned by 08:46). 11:50 USER "Keep as written (Recommended)"
- 11:55 A9 DONE `386fce1` (ledger S7 row 25), verified on disk (junit counts and failing ids, `src/system.css` and `docs/design/` unchanged, no STUB, no attribution line). Chromium 555 tests 0 failures 93 xfail, WebKit 3 failures, all A16's. Builder stopped at 44 percent context, handoff `handoff-2026-10-15-execute-split-A10.md`. Process ledger row 58. README reconciled (`createReceipt`). Q-A9-1 ruled ORCH by Q-A2-2, three deleted files (A8's `states.html` and `.gitattributes`, A9's `panel.js`) archived to `{archive}\2026-10-15-split-deletions\`, blob ids equal 3 of 3 (off-scope row 18, process row 59). Orchestrator slip, one read-only `cat` with `2>/dev/null` while checking `.gitattributes`, no file written
- 11:58 frontend dev (Opus, high) launched for A10. Streaks code reviewer beside it. Usage 5 hour 25 percent (resets 12:30), weekly 4 percent. Orchestrator context 25 percent
- 12:22 A10 DONE `fb8dbc3` (ledger S7 row 26), verified on disk (junit counts and failing ids, `src/system.css` and `docs/design/` unchanged, no deletion, no STUB, no attribution line). Chromium 562 tests 0 failures 87 xfail, WebKit 3 failures, all A16's. Builder stopped at 37 percent context, handoff `handoff-2026-10-15-execute-split-A11.md`. Process ledger row 60. README reconciled (`setStatus` line replaced). Q-A10-1 to the owner in chat as H-07, the build follows the recommendation. F-A10-1 joins the planner's list
- 12:26 frontend dev (Opus, high) launched for A11
- 12:57 A11 DONE `7a8dd78` (ledger S7 row 27), verified on disk (junit counts and failing ids, `src/system.css` and `docs/design/` unchanged, no deletion, no STUB, no attribution line). Chromium 570 tests 0 failures 56 xfail, WebKit 4 failures, A16's three and the new F-A11-1 (WebKit leaves a Tab-focused control under the strip, WCAG 2.4.11). To the owner in chat as H-08 with the recommendation of a `focusin` spec row through the planner. Builder stopped at 41 percent context, handoff `handoff-2026-10-15-execute-split-A12.md`. Process ledger row 61. README reconciled (`createStrip`)
- 13:00 frontend dev (Opus, high) launched for A12, F-A11-1 on its allowed WebKit list. Usage 5 hour 10 percent, weekly 7 percent. Orchestrator context 30 percent
- 13:41 A12 DONE `0ebcf10` (ledger S7 row 28), verified on disk (junit counts and failing ids, `src/system.css` and `docs/design/` unchanged, no deletion, no STUB, no attribution line). Chromium 582 tests 0 failures 43 xfail, WebKit 3 failures (F-A11-1, A16's R29 and R30 `[escape]`). Builder stopped at 43 percent context, handoff `handoff-2026-10-15-execute-split-A13.md`. Process ledger row 62. README reconciled (`createSheet`, `closeOnBackdropClick`). F-A12-1 joins the planner's list
- 13:44 frontend dev (Opus, high) launched for A13. Usage 5 hour 25 percent, weekly 9 percent. Orchestrator context 31 percent
- 14:29 A13 DONE `7618c89` (ledger S7 row 29), verified on disk (junit counts and failing ids, no `src/` file newer than the WebKit run's start, `src/system.css` and `docs/design/` unchanged, no deletion, no STUB, no attribution line). Chromium 617 tests 0 failures 32 xfail, WebKit 3 failures (F-A11-1, A16's R29 and R30 `[escape]`). Builder stopped at 45 percent context, handoff `handoff-2026-10-15-execute-split-A14.md`. Process ledger row 63. README reconciled (`createSpareLine`, `createSpareChoice`, `makeRoom`). F-A13-1 joins the planner's list. Orchestrator slip, one `touch ... 2>/dev/null` while checking file times, which may have left an empty `/tmp/ref_a13` in the system temp folder (unused)
- 14:31 frontend dev (Opus, high) launched for A14. Usage 5 hour 42 percent, weekly 11 percent. Orchestrator context 34 percent, handoff after A14 and the Streaks solver return
- 14:59 A14 DONE `e310216` (ledger S7 row 30), verified on disk (junit counts and failing ids, no `src/` file newer than the proof runs, `src/system.css` and `docs/design/` unchanged, no deletion, no STUB, no attribution line). Chromium 621 tests 0 failures 26 xfail, WebKit 3 failures (F-A11-1, A16's two). Builder stopped at 34 percent context, handoff `handoff-2026-10-15-execute-split-A15.md`. Process ledger row 64. README reconciled (`createPicker`, `drawPills`, `setChecked`). Q-A14-1 joins the planner's list
- 15:02 session handoff `handoff-2026-10-15-execute-orchestrator-4.md` (orchestrator context about 37 percent, usage 5 hour 49 percent, weekly 12 percent). A15 not launched. Ledger off-scope row 19

## 2026-10-15 15:27 execute v1.1.0 resumed, fifth orchestrator session
- `/sdlc:continue`. Law read (constitution, phase-skills, plugin README 2.6.0). Ledger staleness check, newest ledger entry 15:16 in both apps, newest handoff 15:02 (Split, `handoff-2026-10-15-execute-orchestrator-4.md`) and 14:41 (Streaks pointer), ledgers CURRENT. Sweep 15:30 by name (python, node, bash, sh, cmd, powershell, browsers), age, command line (`sdlc-showcase`, `http.server`, `playwright`, `pytest`, `scratchpad`, `live_e2e`) and listening ports found nothing of either app. Three `powershell.exe` (11932, 22096, 18192) belong to the desktop app (parent `claude.exe` 17836), not ours. The handoff named no PID. Usage 5 hour 56 percent, weekly 13 percent. Another session in this workspace ("SDLC version and upgrade plans") was active at 15:28, idle at resume
- STATE's "Next action" still read "A2 to A4 in flight (15:27)" from 2026-10-14, corrected
- 15:36 frontend dev (sdlc-frontend-dev, Opus) launched for A15 from `handoff-2026-10-15-execute-split-A15.md`, scratch in this session's scratchpad `split-a15/`, design row from `frontend-design/c2bdb427efe8` (the current install). Streaks QA re-check beside it
- 16:05 A15 DONE `afea90a` and `dce28e9` (ledger S7 row 31), verified on disk (junit counts and failing ids, no `src/` file newer than the proof runs, `src/system.css` blob `bf30dda` and `docs/design/` unchanged, no deletion, no STUB, no attribution line, Node 379). Chromium 624 tests 0 failures 22 xfail, WebKit 3 failures (F-A11-1, A16's R29 and R30 `[escape]`). Builder stopped at 36 percent context, handoff `handoff-2026-10-15-execute-split-A16.md`. Process ledger row 65. README reconciled (`createRandWrap`, `choicesFor`, `onPickAgain`). F-A15-1 joins the planner's list. An `http.server` on 4610 (PID 20140, 15:51) is this workspace's `.claude/launch.json` preview, started by the desktop app, not by this session, left running and named to the owner
- 16:08 frontend dev (Opus) launched for A16 from `handoff-2026-10-15-execute-split-A16.md`. Usage 5 hour 72 percent, weekly 15 percent, the last launch before the 75 percent line. Streaks planner beside it
- 16:14 usage 5 hour 75 percent, no new agent until the 17:30 reset (house rule)
- 16:20 owner rulings. H-08 USER "ok" (the `focusin` row joins the planner touch before A18). H-07 USER "1" keep as built, after real headless captures of the app showed the late answer case (scratchpad `h07/shots/`, the owner's memory `explain-with-drawings`)
- 16:45 A16 DONE `3c3d9b0` and `9bdb9ee` (ledger S7 row 32), verified on disk (no `src/` change, junit counts and failing ids, no `src/` file newer than the proof runs, `src/system.css` and `docs/design/` unchanged, no deletion, no STUB, no attribution line, Node 379). Chromium 623 tests 0 failures 21 xfail, WebKit 1 failure, F-A11-1 only. Builder stopped at 39 percent context, handoff `handoff-2026-10-15-execute-split-A18.md`. Process ledger row 66. README unchanged (tests only). F-A16-1 joins the planner's list. Long tracked paths to publish prep (off-scope row 20). Usage 5 hour 80 percent, no launch until the 17:30 reset
- 16:52 session handoff `handoff-2026-10-15-execute-orchestrator-5.md` (orchestrator context near 35 percent, usage 5 hour 80 percent, weekly 16 percent). Closing sweep 16:46 clean. Ledger off-scope row 21. Both lanes idle
