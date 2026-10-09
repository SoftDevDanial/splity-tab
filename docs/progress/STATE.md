# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 0.1.0
- **mode:** greenfield
- **phase:** execute (split-core: code-review re-check)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | code-review solver done (212 tests); security PASS with 1 MEDIUM 3 LOW, fix batch running; then QA finder and code-review re-check | |
| split-app | FE + live composition | split-core | not started | |

## Blockers
none

## Next action
Collect the security fix batch. Then QA finder and a scoped code-review re-check (covers both solver rounds). Then README reconcile, ledger, credential gate, record last green. Version relabel to v1.0.0 once no agent is writing.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
