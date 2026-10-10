# P2 Splits sheet

**Golden.** `splits-sheet.html` · **Inventory.** P2 Splits sheet · **Capabilities.** C5 Splits that add up, C6 Copy summary, C9 Spare sen choice
**Reference widths.** 390 x 844 and 360 x 780. The sheet exists below 1024 px only. At 1280 x 800 this golden is K1 (the card is on the page), as g2 shows it. Pixel for pixel the same as g2's "P2 Splits sheet (phone)" at all three widths.

## Intent
On a phone the receipt card is docked as the strip. "Splits" lifts the same card up as a bottom sheet, so the person reads each split, the proof and the spare sen, and can copy, without leaving the bill.

## What it holds
1. The page behind (K1) under the 72% scrim, inert.
2. The sheet, the same dense glass as the strip, 22 px top corners, the 3 px indigo foil along its top edge, at most 560 px wide and 92% of the screen tall.
3. A 48 px top row with the 36 x 4 grab (`--l5`) centred 10 px from the top and Close (X, 44 x 44) at the right.
4. The receipt with 20 px sides, exactly as on the card. Total RM 69.26, the bill lines, the dashed rule, Splits with "items + charges", the three splits with their working, Adds up to RM 69.26 with "59.40 + 9.86", "1 sen left over" with "Top of the list", Copy summary.

Every figure is K1's (`bill-items.md`).

## Sizes
At 390 x 844 the receipt is 607 px and fits without scrolling, so the sheet is about 660 px tall. At 360 x 780 the receipt is 604 px and fits. The strip's Splits button reads `aria-expanded="true"` while the sheet is open.

## Exact copy
| Where | Copy |
|---|---|
| The sheet's accessible name | Splits |
| Close | Close (accessible name) |
| Receipt | As K1 |

## Behaviour this golden implies
- Opened by "Splits" on the strip. Esc, a tap on the scrim and Close shut it, and focus returns to Splits.
- Focus starts on the sheet itself (`tabindex="-1"`, no ring), so a screen reader starts at the receipt.
- The chip opens P1 over the sheet (`spare-sen.html`). Copy summary copies and shows the status under the button in the sheet and beside the Total on the strip.
- The sheet lifts 48 px into place over 240 ms, instant with reduced motion.
- When the screen grows to 1024 px or more the sheet closes and the receipt is the card again.

## Golden only
The golden opens the dialog with the `open` attribute, draws the scrim as `div.backdrop.under-sheet`, and puts `inert` on the page behind (`system.md`, static stand-ins). Because the page is inert, the 1280 render exposes fewer accessible names than g2's K1 there. It looks the same.
