# S2 Bill screen, even split, with shares

**Golden.** `bill-even.html` · **Inventory.** S2 · **Capabilities.** C1 People, C2 Even split, C4 Charges, C5 Shares that add up, C6 Copy summary

## Intent
The common case. One subtotal, everyone pays the same share to the cent, and the screen proves it adds up. It is the by-item screen with the Items block swapped for one Subtotal field and the shares table narrowed to the share alone.

## What changes from S1
1. The mode switch has **"Even"** checked.
2. The Items block is replaced by a **Subtotal** block. Its heading is the field's label (`h2` holding a `label`), and the money field takes one grid cell so it lines up under the first person column.
3. The shares table has **no Items or Charges columns**. Its column heads (Person, Share) are visually hidden, because a lone "Share" head under the "Shares" heading says nothing new. Screen readers still get them.
Everything else (header, People, Charges, Bill summary layout, check row, Copy summary) is identical to S1.

## Exact data
- People are Aisyah, Ben and Chen. The subtotal field holds `100.00`.
- Bill summary rows are Subtotal RM 100.00, + Service charge RM 10.00 with the working "10% of RM 100.00", + SST RM 6.60 with the working "6% of RM 110.00", and = Total RM 116.60 on the double rule.
- Shares are Aisyah RM 38.87, Ben RM 38.87 and Chen RM 38.86, then the check row "Adds up to" RM 116.60.
- The two leftover sen go to the first two people in the list, so the shares differ by at most 1 sen (brainstorm rule).

## Exact copy
| Where | Copy |
|---|---|
| Header | Split · New bill |
| Blocks | People · Subtotal · Charges |
| Buttons | Add person · Copy summary |
| Mode switch | Even · By item (hidden legend "Split mode") |
| Subtotal label | Subtotal (visually hidden " in RM") |
| Charges | Service charge · SST · Set a charge to 0 if your bill already includes it. |
| Panel | Bill summary · Subtotal · Service charge · SST · Total · 10% of RM 100.00 · 6% of RM 110.00 · Shares · Adds up to |
| Hidden table heads | Person · Share |

**Clipboard text** (verbatim from the brainstorm):
```
Bill split
Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)
Aisyah RM 38.87
Ben RM 38.87
Chen RM 38.86
Adds up to RM 116.60
```

## States this screen covers
- Mode "Even" checked with a valid subtotal, so the summary and shares show.
- Status line present but empty and hidden (S6 in `states.md`).
- With an invalid subtotal the field shows the S4 error and the panel shows the S3 message (there is no valid amount to sum).
- Switching to "By item" keeps this subtotal, and switching back restores it.

## Spacing and alignment that matter
- Subtotal block follows the mode switch by 24 px, heading 12 px above the field, field one grid cell wide (175 px at 390, 160 px at 360, 180 px at 1280).
- In even mode the share rows put names at 28 px (operator gutter plus 8 px), shares right aligned 18 px 700. The check row keeps the 1 px ink rule from 28 px to the right edge and the check icon in the gutter.
- Every other measurement as in `bill-items.md`.
