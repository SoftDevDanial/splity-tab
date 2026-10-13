# K1 on a phone, People and Charges open

**Golden.** `bill-items-open.html` · **Inventory.** K1, the phone K1 with People and Charges open · **Capabilities.** C1 People, C4 Charges, with everything in K1
**Reference widths.** 390 x 844 and 360 x 780. At 1280 x 800 the sections are always open and this golden is K1 exactly (`bill-items.md`). Pixel for pixel the same as g2's "K1 People and Charges open (phone)" at all three widths.

## Intent
Show both folded sections opened on a phone, so the build can match the open state of a header row and the section body under it. People and Charges change rarely, so they fold by default (the owner's words, "These will not change often"). This is what a person sees after tapping both rows.

## What changes from K1
| Part | K1 | Here |
|---|---|---|
| People row | Folded, "Aisyah, Ben, Chen" beside the caret | Open, `aria-expanded="true"`, the caret turned up 180 degrees, the summary hidden but keeping its place |
| People body | Hidden | The three name fields in two columns (148 px minimum, 8 px gaps), then "Add person" under the list, left aligned, 12 px below |
| Charges row | Folded, "Service 10%, SST 6%" | Open, the caret turned up, the summary hidden |
| Charges body | Hidden | "Service charge" 10 and "SST" 6 side by side (labels 14/20 600 muted, 8 px above the fields), the hint under them 12 px below |
| Section padding | | 4 px above the body and 20 px below it, then the hairline to the next row |

Everything else, the receipt, the strip, the items and every figure, is K1's (`bill-items.md`).

## Measured at 390 x 844
People ends at 297, Charges at 480 and Split at 539. The strip's top is at 733. The page is 1260 px tall and scrolls, and the strip never covers a control at the page end or while one has focus (37 controls in the working, asserted).

## Behaviour this golden implies
- A tap, Enter or Space on a header row toggles it. Opening reveals the body over 200 ms and turns the caret, folding is instant. Both are instant with reduced motion.
- The summary is hidden while open (the fields say the same thing right under the row) and returns when folded.
- Which sections are open is not saved with the bill. A bill opens folded unless it is new (People opens) or a rate has an error (Charges opens).
