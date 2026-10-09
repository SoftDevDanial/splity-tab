# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.0.0
- **mode:** greenfield
- **phase:** execute (split-app: finders)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09 | `329679e` |
| split-app | FE + live composition | split-core | built (13/13 tasks, 205 browser + 265 unit tests, fidelity 0 px on 10 pairs, live gate 7/7, c40140e); QA finder next, then code review, security (incl. the double-click check on New bill), fidelity | |

## Blockers
none

## Next action
Run finders two at a time: QA, code review, security, fidelity. Solvers, official live gate re-run, README, module close.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
