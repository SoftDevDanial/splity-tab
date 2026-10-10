# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, round 2 (sdlc:design step 4): direction G Glass Console next (F withdrawn, built on a misread base)
- **next:** designer builds round-2/f.html, orchestrator writes round-2/compare.html, owner reviews, then lock, compose, wire, goldens
- **last-regression:** PASS @ 2026-10-10 14:30 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09: code review PASS, security PASS, QA PASS (54 scenarios), 254 tests, credential gate clean | `329679e` |
| split-app | FE + live composition | split-core | CLOSED 2026-10-09: QA PASS, code review solved, security clean (SEC-04 accepted for v1.0), fidelity 10 of 10 at 0 px, live gate 7 of 7, 312 browser + 275 unit, README, credential gate clean | `22ac9af` |

## Blockers
none

## Next action
Launch one designer for direction G "Glass Console" from `docs/design-explore/v1.1.0/round-2/BRIEF-G.md`: B Glass Receipt's layout and glass card in A Night Console's colours, no glow, Copy summary a solid indigo fill, Charges above the Split switch, item list in its own frame, phone inputs first with a pinned bar and a Shares sheet, keep "1 sen left over" (ledger H-03 correction, S7 row 4). F `round-2/f.html` was built on D by the orchestrator's misread and is kept only as a record. Then `round-2/compare.html` (round 1 B and A beside G, readings flagged), his review, sdlc:design steps 5 to 9, the logo with "Splity Tab", then plan on sdlc 2.4.0. S9 several-bills doc is written (docs/future/several-bills.md).

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
