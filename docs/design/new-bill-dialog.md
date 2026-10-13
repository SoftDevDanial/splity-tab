# M1 New bill dialog

**Golden.** `new-bill-dialog.html` · **Inventory.** M1 · **Capabilities.** C8 New bill
**Reference widths.** All three. Pixel for pixel the same as g2's "M1 New bill" at 390, 360 and 1280.

## Intent
Starting over clears everything, so it asks once, plainly, with the destructive action named for what it does.

## What it holds
1. K1 behind, under the 72% scrim, inert and not scrolling.
2. The dialog, centred, `min(400px, 100% - 32px)` wide, `--l3`, a 1 px white 10% edge, 16 px radius, `--shadow-pop`, 24 px padding.
3. "Start a new bill?" (18/24 700).
4. "This clears the people, items and amounts." (16/24 muted), 8 px below.
5. The actions, 24 px below. "Start new bill" (danger, `#C4313C` fill, `#FFF5F5` label, 48 px, 20 px sides) and "Cancel" (ghost, 48 px). On a phone they stack full width, Start new bill first, 8 px apart. From 600 px they sit in a row, right aligned.

## Exact copy
| Where | Copy |
|---|---|
| Title | Start a new bill? |
| Body | This clears the people, items and amounts. |
| Buttons | Start new bill · Cancel |
| The button that opened it | New bill (top bar) |

## Behaviour this golden implies
- Opened by "New bill". Focus starts on Cancel, the safe choice.
- Cancel, Esc and a tap on the scrim close it and return focus to New bill.
- Start new bill clears the bill to two people, "Person 1" and "Person 2", Even, an empty Subtotal, 10% and 6%, and opens People on a phone (`bill-empty.html`). Focus returns to New bill.
- The dialog fades in from 98% over 160 ms, instant with reduced motion.

## Golden only
`div.backdrop` stands in for the `::backdrop`, `inert` on the page stands in for the modal, and the open-not-modal rule centres the dialog as `showModal()` would.
