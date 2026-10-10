# P1 Spare sen, Top of the list

**Golden.** `spare-sen.html` · **Inventory.** P1 · **Capabilities.** C9 Spare sen choice
**Reference widths.** All three. On desktop P1 is a popover beside the card. Below 1024 px it is a bottom sheet over the Splits sheet. Pixel for pixel the same as g2's "P1 Spare sen" at 390, 360 and 1280.

## Intent
Let the person decide who pays the sen that do not divide, in one small choice, without hiding the splits it changes.

## What it holds
1. The bill behind, K1, under a 40% scrim (`--scrim-light`), inert. On a phone the Splits sheet stays open under P1 (itself under the 72% scrim), inert while P1 is open.
2. P1 on `--l3`, 16 px radius, 20 px padding, `--shadow-pop`.
3. "Spare sen" (16/24 700) with Close (X, 44 x 44) at the right, the head pulled 10 px up and 12 px right so the X sits in the corner.
4. "1 sen left over" (14/20 muted).
5. Three choices, 48 px rows 2 px apart, a 20 px radio ring (2 px `--line-strong`) and the label (16/24 600). The chosen ring and its 10 px dot are indigo. "Top of the list" is chosen.

## Where it sits
| Width | Place |
|---|---|
| 1280 x 800 | 340 px wide, 16 px right of the card (left 574), its bottom level with the chip's bottom (632.8). It sits over the working column and never over the splits |
| Under 1024 px | A bottom sheet, full width up to 560 px, 16 px top corners, no bottom border, at most 82% of the screen tall, 255 px tall here. The Splits sheet pads its own bottom by 271 px (P1's height and 16), so the splits stay in view above P1. For K1 no scroll is needed |

## Exact copy
| Where | Copy |
|---|---|
| Title | Spare sen |
| Count | 1 sen left over |
| Choices | Top of the list · One person · At random |
| Close | Close (accessible name) |
| The chip that opened it | Top of the list, accessible name "Spare sen: Top of the list. Change" |

## Behaviour this golden implies
- Opened by the chip on the receipt's spare sen line. Esc, a tap on the scrim and Close shut it, and focus returns to the chip.
- Focus starts on the chosen radio. Arrow keys move between the three choices (native radios).
- A choice applies at once. The splits behind update while P1 stays open, and the chip's label follows.
- "One person" opens the picker of people under it (`spare-sen-one.html`). "At random" shows Pick again under it (`spare-sen-random.html`).
- P1 rises 8 px and fades in over 200 ms, instant with reduced motion.

## Golden only
`div.backdrop.light` stands in for P1's `::backdrop`, and on desktop the golden style sets `left` and `bottom`, which the build's script works out from the card and the chip.
