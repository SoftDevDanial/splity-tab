# S6 The saved bill could not be read

**Golden.** `bill-unreadable.html` · **Inventory.** S6 · **Capabilities.** C7 Draft kept
**Reference widths.** All three. At 1280 x 800 it is pixel for pixel g2's "S6 Saved bill unreadable". On a phone it is g2's S6 with People opened (ruling 1), pixel for pixel the same as g2 after a tap on the People row.

## Intent
Say plainly that the saved bill was lost and a new one started, then put the first step, naming people, in front of the person, as on S1.

## Ruling 1, applied
The brief's ruling makes S6 open People, like S1. g2 left People folded here (g2.md reading 8, flagged as a question). The difference is on a phone only. People is open with "Person 1" and "Person 2", Charges stays folded.

## What it holds
| Part | Here |
|---|---|
| Note (phone) | A second row of the top bar, full width, 16 px radius, the note band (`--info-bg`) with an indigo edge at 38%, a 20 px indigo warning circle, the text in 14/20, and Dismiss note (X, 44 x 44) at the right. 4 px padding top, right and bottom, 16 px left |
| Note (desktop) | Centred in the top bar between the brand and New bill, 44 px tall, no padding top or bottom |
| Below | S1 exactly (`bill-empty.md`), People open on a phone |

## Exact copy
| Where | Copy |
|---|---|
| Note | Your saved bill could not be read, so a new one was started. |
| Dismiss | Dismiss note (accessible name) |

## Measured at 390 x 844
The note wraps to two lines and adds 78 px to the top bar (the note, the 8 px row gap and 4 px under it). People ends at 321, Charges at 374, Split at 433. The page does not scroll.

## Behaviour this golden implies
- The note is a polite status (`role="status"`), read once.
- Dismiss note removes it, the page moves up, and focus goes to New bill. The screen is then S1 (`bill-empty.html`).
- The note does not come back for this bill.
