# STATE: split

- **project:** Split, a bill splitter for one shared restaurant bill
- **design-phase:** sdlc:design
- **version:** 1.1.0 (1.0.0 sealed 2026-10-10, tag v1.0.0)
- **mode:** greenfield
- **phase:** v1.1.0 design, step 7 wired and verified (FLOW-CHECK 48 of 48), owner's rulings next
- **next:** owner rules on the composer's copy list, 13 interaction rules and five open questions (v1.1.0/RULINGS.md), logo redraw swapped in, finalize gate (his approval AND his word to replace 1.0's goldens), then plan
- **last-regression:** PASS @ 2026-10-10 14:30 (docs/regression/REGRESSION.md)

## Modules
| module | nature | depends on | status | last green |
|---|---|---|---|---|
| split-core | logic | none | CLOSED 2026-10-09: code review PASS, security PASS, QA PASS (54 scenarios), 254 tests, credential gate clean | `329679e` |
| split-app | FE + live composition | split-core | CLOSED 2026-10-09: QA PASS, code review solved, security clean (SEC-04 accepted for v1.0), fidelity 10 of 10 at 0 px, live gate 7 of 7, 312 browser + 275 unit, README, credential gate clean | `22ac9af` |

## Blockers
none

## Next action
Step 7 done. `docs/design-explore/v1.1.0/FLOW-CHECK.md` 48 of 48 links, zero errors, prototype in `v1.1.0/prototype/`. Orchestrator fix in final/ (ledger S7 row 10). People and Charges are named by their section name and described by their summary (Chromium read "People , Aisyah, Ben, Chen"). check_final.py 778 of 778. Next, put SELF-CRITIQUE's copy list, its 13 interaction rules and five open questions (an invalid rate counts as 0 in the receipt, an invalid price is left out of the totals, the P1 picker and At random goldens sit on K2, dialogs against their scrim 1.01 to 1.21, the logo swap touches the inline mark and the tab icon) to the owner and record his answers in `docs/design-explore/v1.1.0/RULINGS.md`. Then logo redraw ("Splity Tab"), then the finalize gate.

## Notes
Goldens (immutable): docs/design/bill-items.html (key), bill-even.html, bill-empty.html, bill-unassigned.html, new-bill-dialog.html, states.html (specimen sheet), system.md, system.css, RULINGS.md.

For the split-app builder brief (core solver and security audit): the draft decoder rejects an unknown `mode`; rebuilds or rejects people and items with unknown or `__proto__` keys; rejects duplicate person ids, a `who` that is not an array of known ids, and a stale `nextId`; keeps an empty people list out of even mode. `personLabel` shows control and bidi characters as typed while the summary prints a space, so the name input or decoder should reject or strip them to keep screen and summary the same. Name rule D8 rejects only LF and CR today.
