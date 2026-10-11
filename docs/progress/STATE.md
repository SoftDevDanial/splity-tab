# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, step 7 done, owner's rulings given 2026-10-11, rate-error golden blocked as in 1.0, RULINGS.md and logo round next
- **next:** write v1.1.0/RULINGS.md, logo round (redraw the mark, four directions, he picks), swap the mark in, finalize gate (his approval AND his word to replace 1.0's goldens), then plan (sdlc 2.5.0 is installed)
- **last-regression:** PASS @ 2026-10-10 14:30 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09: code review PASS, security PASS, QA PASS (54 scenarios), 254 tests, credential gate clean | `329679e` |
| split-app | FE + live composition | split-core | CLOSED 2026-10-09: QA PASS, code review solved, security clean (SEC-04 accepted for v1.0), fidelity 10 of 10 at 0 px, live gate 7 of 7, 312 browser + 275 unit, README, credential gate clean | `22ac9af` |

## Blockers
none

## Next action
rate-error.html shows 1.0's blocked receipt (core R18, app R17), "Check the charges to see the splits.", no Total, Copy summary disabled on the strip, at 390, 360 and 1280. check_final.py 748 of 748, flow check 48 of 48. Next write docs/design-explore/v1.1.0/RULINGS.md (his four answers of 2026-10-11 and the ORCH ruling on open questions 1 and 2), then the logo round, then the finalize gate. Details in `HANDOFF-2026-10-11b.md` at the showcase root.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
