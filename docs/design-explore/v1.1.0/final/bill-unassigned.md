# S3 An item still needs a person

**Golden.** `bill-unassigned.html` · **Inventory.** S3 · **Capabilities.** C3 Split by item, C5 Splits that add up
**Reference widths.** All three. Pixel for pixel the same as g2's "S3 Item needs a person" at 390, 360 and 1280.

## Intent
A split that leaves out an item would not add up to the receipt, so the splits wait and the screen says exactly what is missing and where.

## What changes from K1
| Part | Here |
|---|---|
| Mee goreng mamak | Nobody tapped (Aisyah, Ben and Chen all off). A 3 px amber bar (`--warn-ink`) on the item's left edge, 12 px in from its top and bottom, 7 px left of the content on a phone and 10 px on wider screens |
| Receipt (card) | Total RM 69.26 and the three bill lines stay. Under the dashed rule a 22 px amber warning circle and "1 item still needs a person. Tap who had it to see the splits." No splits, no proof, no spare line, no Copy summary |
| Strip | The amber warning circle (18 px) and the same sentence in place of the Total, on two lines, Copy summary disabled. The strip is 128 px |

## Exact copy
| Where | Copy |
|---|---|
| One item | 1 item still needs a person. Tap who had it to see the splits. |
| Two or more (specimen) | 2 items still need a person. Tap who had each one to see the splits. |

## Figures
The bill lines are K1's (59.40, 5.94, 3.92, Total 69.26), because the bill is whole. Only the splits wait.

## Behaviour this golden implies
- Tapping anyone on the marked item gives the splits back. Tapping Chen gives K1 (`bill-items.html`).
- On a phone the strip says the same thing as the card, so the person does not need to open Splits to learn why there is no figure.
- The marker is not announced on its own. The item's toggle group already reads "Who had Mee goreng mamak" with every toggle off.
