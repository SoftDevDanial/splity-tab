# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.0.0
- **mode:** greenfield
- **phase:** execute (split-app: security finder)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09 | `329679e` |
| split-app | FE + live composition | split-core | built, QA PASS, code review solved (244 browser + 275 unit tests, fidelity 0 px on 10 pairs, `61c3cd3`); security finder next, then fidelity re-check, official live gate, README, module close | |

## Blockers
none

## Next action
Security finder (sonnet, includes the ghost-click class on every control). Then fidelity re-check, official live gate into docs/modules/split-app/qa/live-e2e/<ts>/, README (WR-08) and qa.md scenarios for the double click, backdrop press and right click, ROADMAP PD-14 fix, module close.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
