# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.0.0
- **mode:** greenfield
- **phase:** execute (split-app: security re-check)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09 | `329679e` |
| split-app | FE + live composition | split-core | built, QA PASS, code review solved, security solved (312 browser + 275 unit, fidelity 0 px, `b02386b`); scoped security re-check running (stop rule after it), then official live gate, README, module close | |

## Blockers
none

## Next action
Scoped security re-check of 071577a and 68ab318 (stop rule). Then official live gate into docs/modules/split-app/qa/live-e2e/<ts>/, README (WR-08) from BUILD.md, ROADMAP PD-14, module close. The fidelity re-check is covered by the solver's 10 of 10 at 0 px on the final code.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
