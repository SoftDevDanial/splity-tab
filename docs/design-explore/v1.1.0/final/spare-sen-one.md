# P1 Spare sen, One person with its picker

**Golden.** `spare-sen-one.html` · **Inventory.** P1, its picker · **Capabilities.** C9 Spare sen choice
**Reference widths.** All three, placed as P1 (`spare-sen.md`). Pixel for pixel the same as g2 at the same state (K2, Splits sheet open on a phone, the chip, "One person", then "Ben").

## Intent
The inventory's own example. On K2, giving both spare sen to Ben gives 38.86, 38.88, 38.86. The picker lists only people with a split above zero.

## What changes from P1 Top of the list
| Part | Here |
|---|---|
| The bill behind | K2 (`bill-even.md`), Subtotal RM 100.00, Total RM 116.60 |
| Count | 2 sen left over |
| Chosen | One person |
| Picker | A `fieldset` under "One person" (40 px left inset, 8 px bottom), its legend "Who pays the spare sen" for screen readers only. Three pills, Aisyah, Ben, Chen, 44 px tall, full pill, 16 px sides, 8 px apart. Ben is chosen (indigo tint, indigo edge, a 14 px indigo check, 12 px left padding) |
| P1 height | 309 px on a phone, 310 on desktop. The Splits sheet pads its bottom by 325 px |
| Desktop place | Left 574, bottom level with the chip's bottom (560.8) |

## Exact figures
| Split | Figure |
|---|---|
| Aisyah | RM 38.86 |
| Ben | RM 38.88 |
| Chen | RM 38.86 |
| Adds up to | RM 116.60 |

3886 each, and both spare sen to Ben (3888). The chip reads "One person, Ben", accessible name `Spare sen: One person, Ben. Change`.

## Behaviour this golden implies
- Choosing "One person" picks the first eligible person (the top of the list) at once, so the splits never wait on a second tap. Here Ben was then tapped.
- If the chosen person is removed from the bill, the rule falls back to Top of the list.
- Pills are radios. Arrow keys move between them.
