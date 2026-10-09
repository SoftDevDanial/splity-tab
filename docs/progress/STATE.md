# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 0.1.0
- **mode:** greenfield
- **phase:** plan (done)
- **next:** execute

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | not started | |
| split-app | FE + live composition | split-core | not started | |

## Blockers
none

## Next action
Execute: split-core builder (sdlc-backend-dev). Then finders wave 1.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.
