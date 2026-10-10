# W1 A large bill on a 360 px phone

**Golden.** `bill-large.html` · **Inventory.** W1 · **Capabilities.** C3 Split by item (fits 360 px at any bill size)
**Reference widths.** 360 x 780 is the one that matters (no sideways scroll at RM 1,193.87). 390 and 1280 are shown too. Pixel for pixel the same as g2's "W1 RM 1,193.87" at all three.

## Intent
Prove the by-item screen and its receipt hold a four-figure bill at the narrowest width with no sideways scroll and no clipped figure.

## What changes from K1
A fifth item with no name (placeholder "Item 5") at RM 964.50, tapped for Aisyah.

## Exact figures
| Line | Figure | Working |
|---|---|---|
| Subtotal | RM 1,023.90 | 59.40 + 964.50 |
| Service 10% | RM 102.39 | 10% of 1,023.90 |
| SST 6% | RM 67.58 | 6% of 1,126.29 = 67.5774 |
| Total | RM 1,193.87 | |

| Split | Items | Charges | Split |
|---|---|---|---|
| Aisyah | 989.40 | 164.25 (16424 sen and the 1 spare) | RM 1,153.65 |
| Ben | 13.50 | 2.24 | RM 15.74 |
| Chen | 21.00 | 3.48 | RM 24.48 |
| Adds up to | 1,023.90 | 169.97 | RM 1,193.87 |

"1 sen left over", Top of the list.

## What to look at
| Width | Detail |
|---|---|
| 360 x 780 | The item frame holds 614 px in 581 (the screen less the 111 px strip and 88 px), so it scrolls inside itself and shows its 36 px bottom fade. The price field (104 px) shows "964.50" in full. The strip reads "Total RM 1,193.87" on one line |
| 390 x 844 | The frame is tall enough for the five items, no fade |
| 1280 x 800 | The Total at 48 px fits the 412 px card body. The frame holds 614 px in 291 with the bottom fade |

## Exact copy
As K1, plus "Item 5" (placeholder and accessible names "Item 5 name", "Item 5 price in RM", "Remove Item 5", "Who had Item 5").
