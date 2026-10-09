# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 0.1.0
- **mode:** greenfield
- **phase:** execute (split-core: re-check finders)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | code-review solver done (10/10 WR, 212 tests pass at `46f5670`); security audit running, then QA and code-review re-check | |
| split-app | FE + live composition | split-core | not started | |

## Blockers
none

## Next action
Collect the split-core security audit (threat model plus WR-10). Then QA finder and a scoped code-review re-check. Then README reconcile, ledger, credential gate, record last green. Target version relabelled to v1.0.0 per the owner (2026-10-09), applied once no agent is writing.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (from the core solver, ledger off-scope 15): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; `personLabel` shows VT, FF, U+0085, U+2028, U+2029 as typed while the summary prints a space (reject them in input or decoder to keep the two the same).
