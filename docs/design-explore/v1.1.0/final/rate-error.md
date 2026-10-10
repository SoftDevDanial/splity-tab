# S2 on a rate, Service charge 35

**Golden.** `rate-error.html` · **Inventory.** S2, on a rate · **Capabilities.** C4 Charges
**Reference widths.** All three. Pixel for pixel the same as g2's "S2 Rate error (opens Charges)" at 390, 360 and 1280.

## Intent
A rate outside its range is an error the person must see, even on a phone where Charges is folded. A section with an error inside opens on load, and folded it says "Check" in the error colour.

## What changes from K1
| Part | Here |
|---|---|
| Charges (phone) | Open on load. The row carries the error marker (hidden while open) |
| Service charge field | Value `35`, red edge with a 1 px inset (reads 2 px), `aria-invalid="true"`, `aria-describedby="chargeHint svcErr"` |
| Error | "Enter a rate from 0 to 30" in 14/20 600 error red with a 16 px warning circle, 8 px under the field. In a half-width cell it breaks into two even lines, "Enter a rate" over "from 0 to 30", the icon on the first |
| Desktop | The error grows its own cell downward. The SST field and the hint stay where they were. The item frame shrinks to 243 px and shows its bottom fade |
| Folded (after a tap on the row) | The summary turns to error red at 600 with a 16 px warning circle and reads "Check service charge". The specimen sheet shows it, and "Check SST" and "Check both rates" (`states.html`) |

## Exact copy
| Where | Copy |
|---|---|
| Error under Service charge | Enter a rate from 0 to 30 |
| Error under SST (specimen) | Enter a rate from 0 to 20 |
| Folded marker | Check service charge · Check SST · Check both rates |

## The receipt in this state, a flagged prototype shortcut
g2 counts a rate that is not valid as 0, and this golden shows exactly what g2 shows. Total RM 62.96 from Subtotal RM 59.40, "Service 0%" RM 0.00, SST 6% RM 3.56 (6% of 59.40 = 3.564). Splits Aisyah RM 26.40 (24.90 + 1.50), Ben RM 14.31 (13.50 + 0.81), Chen RM 22.25 (21.00 + 1.25), Adds up to RM 62.96 (59.40 + 3.56), "2 sen left over". The figures add up in whole sen, but a Total built on a rate the person did not mean is a question for the owner (`SELF-CRITIQUE.md`, open questions). The build must not copy this behaviour without that ruling.

## Measured at 390 x 844
People ends at 117, Charges at 348, Split at 407. The page is 1128 px and scrolls.

## Behaviour this golden implies
- A blank rate is not an error, it counts as 0, as in 1.0.
- The error shows while the value is wrong and goes as soon as it is valid. The rate fields name their error in `aria-describedby` only while it shows.
- A section opens on load only. Typing a bad rate with Charges open does not reopen anything later, and folding shows "Check".
