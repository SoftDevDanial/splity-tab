# P1 Spare sen, At random with Pick again

**Golden.** `spare-sen-random.html` · **Inventory.** P1, At random · **Capabilities.** C9 Spare sen choice
**Reference widths.** All three, placed as P1 (`spare-sen.md`). Pixel for pixel the same as g2 at the same state (K2, At random with the draw fixed to Ben and Chen, Splits sheet open on a phone, the chip).

## Intent
At random gives each spare sen to a different person, drawn once and kept, so the splits never jump while typing. Pick again draws again and always changes who.

## What changes from P1 Top of the list
| Part | Here |
|---|---|
| The bill behind | K2, Total RM 116.60 |
| Count | 2 sen left over |
| Chosen | At random |
| Under it | Pick again, a ghost button (44 px, shuffle icon), 40 px left inset |
| The receipt's spare line | "2 sen left over", then two chips, "Pick again" (shuffle icon first) and "At random" (caret), 8 px apart. At 360 in the sheet the two chips wrap to a second line under the count |
| P1 height | 309 px on a phone, 310 on desktop. The Splits sheet pads its bottom by 325 px |
| Desktop place | Left 574, bottom level with the chip's bottom (560.8) |

## Exact figures
The draw shown gave Ben and Chen one sen each. A static golden needs one draw, the build draws for real.

| Split | Figure |
|---|---|
| Aisyah | RM 38.86 |
| Ben | RM 38.87 |
| Chen | RM 38.87 |
| Adds up to | RM 116.60 |

## Exact copy
At random · Pick again (twice, in P1 and on the receipt line) · the chip's accessible name `Spare sen: At random. Change`.

## Behaviour this golden implies
- The draw is a real random order of the people, kept with the bill until Pick again. Each spare sen goes to the next person in that order, so two spare sen always go to two different people.
- Pick again draws until the result differs from the one shown.
- Copy summary copies the splits as drawn.
