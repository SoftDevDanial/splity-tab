# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, steps 5, 6 and 8 composed (final/ committed), step 7 wire and verify next
- **next:** composer builds docs/design-explore/v1.1.0/final/ (system, goldens, manifest, links, self-critique), orchestrator wires and drives the flow (step 7), owner approves the set and the replacement of 1.0's goldens, logo redraw swapped in, finalize, then plan
- **last-regression:** PASS @ 2026-10-10 14:30 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09: code review PASS, security PASS, QA PASS (54 scenarios), 254 tests, credential gate clean | `329679e` |
| split-app | FE + live composition | split-core | CLOSED 2026-10-09: QA PASS, code review solved, security clean (SEC-04 accepted for v1.0), fidelity 10 of 10 at 0 px, live gate 7 of 7, 312 browser + 275 unit, README, credential gate clean | `22ac9af` |

## Blockers
none

## Next action
Composer done: `docs/design-explore/v1.1.0/final/` (system.md, system.css, 15 goldens with .md: bill-items, bill-items-open, bill-even, spare-sen, spare-sen-one, spare-sen-random, splits-sheet, new-bill-dialog, bill-empty, rate-error, bill-unassigned, bill-unreadable, bill-twelve, bill-large, states; MANIFEST.md, LINKS.json with 48 links, SELF-CRITIQUE.md, checks). Next: run `flowcheck_v.py split v1.1.0`, put SELF-CRITIQUE's copy list and 13 interaction rules to the owner, plus four open questions (an invalid rate counts as 0 in the receipt, an invalid price is left out of the totals, the P1 picker and At random goldens sit on K2 to match the inventory figures, the logo swap touches the inline mark and the tab icon). Then logo redraw, then the finalize gate (his approval AND his word to replace 1.0's goldens).

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
