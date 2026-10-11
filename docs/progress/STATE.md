# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, logo done (S12 approved and swapped into final/), finalize gate next
- **next:** finalize gate (step 9), ask him explicitly to approve the final set AND to replace 1.0's goldens in docs/design/ (1.0's stay in tag v1.0.0), then STATE design done, skills-loaded declaration, sdlc:plan with the R18 (c) delta
- **last-regression:** PASS @ 2026-10-10 14:30 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09: code review PASS, security PASS, QA PASS (54 scenarios), 254 tests, credential gate clean | `329679e` |
| split-app | FE + live composition | split-core | CLOSED 2026-10-09: QA PASS, code review solved, security clean (SEC-04 accepted for v1.0), fidelity 10 of 10 at 0 px, live gate 7 of 7, 312 browser + 275 unit, README, credential gate clean | `22ac9af` |

## Blockers
none

## Next action
Logo closed for Splity Tab. The owner kept the 1.0 cut equals and tweaked it, S12, a thin receipt outline with a hand torn foot behind the cut equals, transparent. QA PASS 26 of 28 after two craft revisions. Approved with the favicon's 1 px frame exception, the empty state shows S12 muted. Swapped into the 15 final goldens (mark, tab icon, i-mark empty state, desktop brand offset 1 px). check_final.py 748 of 748 (it now expects i-mark), FLOW-CHECK 48 of 48. Ledger S7. Next is the finalize gate for both apps, his explicit word before anything is copied into docs/design/.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
