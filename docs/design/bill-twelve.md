# S7 Twelve people

**Golden.** `bill-twelve.html` · **Inventory.** S7 · **Capabilities.** C1 People, C2 Even split
**Reference widths.** All three. Pixel for pixel the same as g2's "S7 12 people" at 390, 360 and 1280.

## Intent
Twelve is the most a bill takes, so Add person turns off, and a long table still fits. On desktop the splits list in two columns so the card needs no inner scroll.

## What changes from K2
| Part | Here |
|---|---|
| People | Aisyah, Ben, Chen, then nine blank names that show "Person 4" to "Person 12" as placeholders. Every remove is enabled. Add person is disabled (faint label and icon, `--l5` border, `not-allowed`, skipped by Tab) |
| People row (phone, folded) | "Aisyah, Ben, Chen, Person 4 and 8 more" at 390, "Aisyah, Ben, Chen and 9 more" at 360. As many names as fit, then "and N more". "12 people" alone only if not even one name fits |
| Receipt (desktop) | Twelve splits in two columns of six (`.r-splits.many`, 24 px column gap, 8 px row gap), filled down then across. The card is 658 px |
| Receipt (sheet, phone) | One column of twelve, as on the card at phone width |
| Spare line | 8 sen left over, Top of the list |

## Exact figures
11660 sen / 12 = 971 each with 8 sen left over, one each to the first eight.

| Split | Figure |
|---|---|
| Aisyah, Ben, Chen, Person 4 to Person 8 | RM 9.72 each (8 x 972 = 7776) |
| Person 9 to Person 12 | RM 9.71 each (4 x 971 = 3884) |
| Adds up to | RM 116.60 |

## Behaviour this golden implies
- Removing anyone turns Add person back on.
- A blank name shows as "Person N" (its place) in the receipt, the summary, the accessible names and the copied summary.

## Golden only
The two summary spans (`.fit-wide`, `.fit-narrow`) stand in for the build's fitting, which measures the row.
