# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.0.0
- **mode:** greenfield
- **phase:** execute (split-app: official live gate, README, module close)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09 | `329679e` |
| split-app | FE + live composition | split-core | built, QA PASS, code review solved, security clean (SEC-04 accepted for v1.0, to v1.1.0), 312 browser + 275 unit, fidelity 0 px (`b02386b`); official live gate, README, module close next | |

## Blockers
none

## Next action
Official live gate into docs/modules/split-app/qa/live-e2e/<ts>/ on the final code. README (WR-08) from BUILD.md, noting the v1.0 limits (H-02, SEC-04, Dismiss note focus). ROADMAP PD-14 fix. Module close. Then regression --full, review, UAT pre-run.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
