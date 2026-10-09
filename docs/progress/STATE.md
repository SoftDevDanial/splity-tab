# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.0.0
- **mode:** greenfield
- **phase:** execute (split-app: PAUSED, builder stopped by the owner)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09 | `329679e` |
| split-app | FE + live composition | split-core | Tasks 1-10 built (149 browser, 265 unit tests, a3e7d04); fresh builder on Tasks 11-13 plus rulings RD-1 to RD-4 | |

## Blockers
Builder for Tasks 11-13 was stopped by the owner at 15:46 mid RD-3. Uncommitted, untested work in progress is in the tree: src/ui/field-leave.js (new), src/ui/charges.js, items.js, subtotal.js, tests/browser/conftest.py, test_app.py, spec.md and qa.md notes, docs/modules/split-app/qa/. Do not commit or revert it before the owner says how to proceed.

## Next action
Wait for the owner. To resume: a fresh builder reviews the work in progress against RD-3, finishes it with red then green tests, then Tasks 11-13 (see BUILD.md handoff).

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
