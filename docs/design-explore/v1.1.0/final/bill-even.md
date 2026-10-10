# K2 Bill screen, even split

**Golden.** `bill-even.html` · **Inventory.** K2 · **Capabilities.** C2 Even split, C4 Charges, C5 Splits that add up, C6 Copy summary, C9 Spare sen choice
**Reference widths.** All three. Pixel for pixel the same as g2's K2 at 390, 360 and 1280.

## Intent
The common case. One subtotal, everyone pays the same, and the spare sen are visible and owned.

## What changes from K1
| Part | Here |
|---|---|
| Split switch | "Even" chosen |
| Under the switch | "Subtotal" (15/20 600, 10 px above) and the money field, at most 240 px wide, value `100.00`. The item frame is not shown, the items are kept |
| Receipt | No "items + charges" legend, no working under the splits or under Adds up to |
| Strip | "Total RM 116.60" |
| Phone page | Fits 390 x 844 without scrolling |

## Exact figures
| Line | Figure | Working |
|---|---|---|
| Subtotal | RM 100.00 | |
| Service 10% | RM 10.00 | 10% of 100.00 |
| SST 6% | RM 6.60 | 6% of 110.00 |
| Total | RM 116.60 | |

| Split | Figure |
|---|---|
| Aisyah | RM 38.87 |
| Ben | RM 38.87 |
| Chen | RM 38.86 |
| Adds up to | RM 116.60 |

11660 sen / 3 = 3886 each with 2 sen left over, one each to the top of the list (Aisyah, Ben). The spare line reads "2 sen left over" with "Top of the list".

## Exact copy
As K1, plus "Subtotal" (label), "Subtotal in RM" (the field's accessible name), and the placeholder "0.00".

## Behaviour this golden implies
- "By item" on the switch gives K1 again, with the four items as they were.
- The chip opens P1 for this bill (`spare-sen-one.html` and `spare-sen-random.html` show two of its choices on this bill).
- On desktop the card is 570 px tall and its chip sits at 392, 517.
