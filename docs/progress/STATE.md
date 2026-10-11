# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, logo round 1 in progress (S3 passed, S1 and S2 retired, S4 and S5 next)
- **next:** logo round (redraw the mark from the glass receipt, four directions, QA-checked, he picks on the design board), swap the mark and favicon into every golden, rerun check_final.py, finalize gate (his approval AND his word to replace 1.0's goldens), then plan (sdlc 2.5.0 is installed)
- **last-regression:** PASS @ 2026-10-10 14:30 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09: code review PASS, security PASS, QA PASS (54 scenarios), 254 tests, credential gate clean | `329679e` |
| split-app | FE + live composition | split-core | CLOSED 2026-10-09: QA PASS, code review solved, security clean (SEC-04 accepted for v1.0), fidelity 10 of 10 at 0 px, live gate 7 of 7, 312 browser + 275 unit, README, credential gate clean | `22ac9af` |

## Blockers
none

## Next action
Logo round 1 in docs/design-explore/v1.1.0/logo/ (BRIEF.md, QA.md, round-1/). S3 passed QA 26 of 28. S1 and S2 retired at their structural limits. Next S4, S5 (and S6 if needed), each rendered by the orchestrator and QA-checked, then the board on port 4555. Details in `HANDOFF-2026-10-11c.md` at the showcase root.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
