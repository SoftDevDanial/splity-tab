# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 plan, step 3 plan check BLOCK (2026-10-13 22:08, 4 BLOCK, 10 FLAG, 8 NOTE), planner fix pass next. All contracts written by three planner runs. Clarify gate parts 1 and 2 ruled (CG-P1 to CG-P8, all USER)
- **next:** planner fix pass on PLAN-CHECK.md, plan re-check, then the ledger scope map, CLAUDE.md stack line, commit. The orchestrator installs WebKit (owner approved 2026-10-13) before app task A0
- **last-regression:** PASS @ 2026-10-10 14:30 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09: code review PASS, security PASS, QA PASS (54 scenarios), 254 tests, credential gate clean | `329679e` |
| split-app | FE + live composition | split-core | CLOSED 2026-10-09: QA PASS, code review solved, security clean (SEC-04 accepted for v1.0), fidelity 10 of 10 at 0 px, live gate 7 of 7, 312 browser + 275 unit, README, credential gate clean | `22ac9af` |

## Blockers
none

## Next action
Design v1.1.0 closed. The owner approved the final set and the replacement of 1.0's goldens on 2026-10-11 23:45 ("Yes, but later"). On 2026-10-13 final/ was copied into docs/design/ (34 files, SHA-256 equal), the v1.1.0 rulings sit beside 1.0's as RULINGS-v1.1.0.md, and check_final.py rerun against docs/design/ gave 747 of 748 with every golden section equal to the final/ run, the one fail being 1.0's RULINGS.md header picked up by the markdown lint (design-explore/v1.1.0/finalize/). Ledger S7 row 14. Next is sdlc:plan. Its inputs are the goldens below, both RULINGS files, design-explore/v1.1.0/final/SELF-CRITIQUE.md (the approved copy list and thirteen interaction rules the rulings point to) and the brainstorm delta. Build swap notes, mark28-src at 28 px only, favicon-src for the tab icon, mark-src (56 grid) from 48 px up, keep the desktop `.brand` 1 px offset.

## Notes
Goldens (immutable, v1.1.0, 1.0's in tag v1.0.0): docs/design/bill-items.html (key), bill-items-open.html, bill-even.html, spare-sen.html, spare-sen-one.html, spare-sen-random.html, splits-sheet.html, new-bill-dialog.html, bill-empty.html, rate-error.html, bill-unassigned.html, bill-unreadable.html, bill-twelve.html, bill-large.html, states.html (specimen sheet), each with its .md, plus system.md, system.css, LINKS.json, MANIFEST.md, RULINGS.md (1.0), RULINGS-v1.1.0.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
