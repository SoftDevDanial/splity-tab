# Design rulings, Split v1.1.0

**Date.** 2026-10-11 · **Ruled by.** the owner (**USER**), who picked the option recommended to him on each of four questions, and the orchestrator under his delegation (**ORCH**, reversible) where a ruling says so

The composer listed copy, interaction rules and questions the brainstorm leaves open (`final/SELF-CRITIQUE.md`). They are ruled here so the plan phase does not have to guess. 1.0's rulings (`../RULINGS.md`) still stand, with "shares" read as "splits" (the owner's rename, ledger H-03), unless a ruling here replaces one.

## Added copy, approved (USER)
All copy in the "Copy the brainstorm does not word" table of `final/SELF-CRITIQUE.md` is approved as written. "Check the charges to see the splits." joined the table after the ruling on the receipt below. It is 1.0's line with the rename.

## Interaction rules, approved (USER)
All thirteen rules in "Interaction rules I specified, or carried from g2" of `final/SELF-CRITIQUE.md` are approved as written.

## Small points, accepted (USER)
| # | Point | Ruling |
|---|---|---|
| 1 | P1's picker and At random are shown on K2, following the inventory's figures (open question 3) | Keep them on K2 |
| 2 | Dialogs against their scrim measure 1.01 to 1.21 (open question 4). Not a WCAG requirement | Accepted as he saw them in g2 |

## The mark (USER)
Redraw the mark with the logo-design skill. Four directions, each checked by a separate QA agent, and the owner picks one on the design board. Splity Tab's mark grows from the glass receipt. No "Danial" and no "D" in the mark. The pick replaces the one inline `<svg class="mark">` and the tab icon's data URI in every golden (open question 5), then `final/checks/check_final.py` runs again.

**Source widened (USER, 2026-10-11 17:40).** Seven receipt directions were drawn and six retired at QA, because at 28 and 16 px a receipt is a plain rectangle and only a check (S3) lands on it (`logo/QA.md`). The owner chose to keep the receipt as the root and let the mark grow from what it does, the split into shares, the people at the table, the sheet that lifts, not only the paper object. Three new directions, the same QA bar (constraint 7 stays). S3 stays in the set.

## The receipt when the bill cannot be worked out (ORCH, told to the owner)
Open questions 1 and 2 asked whether a rate or a price that is not valid may count as 0 or be left out, as g2 did. The sealed 1.0 spec already settles it. Core R18 blocks the result and app R17 words the message, so there is no Total to copy. 1.1.0 keeps 1.0's order and uses the approved copy.

| # | First rule that applies | Receipt (card and sheet) and strip | Proof |
|---|---|---|---|
| a | A rate is empty or not valid | "Check the charges to see the splits." No Total, Copy summary disabled | `final/rate-error.html` |
| b | Even, the subtotal is empty or not valid | "Enter the subtotal to see the splits." No Total, Copy summary disabled | `final/bill-empty.html` |
| c | By item, no item has a valid price (no items, or every price empty or not valid) | "Add each item and tap who had it to see the splits." No Total, Copy summary disabled | `final/states.html` |
| d | By item, some item has a valid price and another's is empty or not valid | "Give every item a price to see the splits." No Total, Copy summary disabled | Builder note, no golden |
| e | By item, an item nobody had | The S3 messages, the bill lines stay | `final/bill-unassigned.html` |

- An empty field never shows an inline error (1.0 ruling 1). It still blocks with its message. A blank rate does not count as 0.
- Folded on a phone, Charges shows its "Check" marker whenever a rate blocks the receipt, blank or not valid, with the approved copy ("Check service charge", "Check SST", "Check both rates"). A Charges summary never reads "Service 0%" for a blank rate. ORCH, it reuses the marker and its copy, nothing new.
- For the plan phase. Row c widens 1.0's core R18 (c) from "no items" to "no item has a valid price", as the approved copy list words it ("By item with no valid price"). Its line replaces 1.0's "Add an item to see the shares." Every app R17 message takes "splits" for "shares".
