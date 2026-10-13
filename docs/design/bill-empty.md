# S1 First open, a new bill

**Golden.** `bill-empty.html` · **Inventory.** S1 · **Capabilities.** C1 People, C2 Even split, C8 New bill
**Reference widths.** All three. Pixel for pixel the same as g2's "S1 First open" at 390, 360 and 1280.

## Intent
A new bill has nothing to work out yet, so the screen says what to do next. Naming people is the first step, so on a phone People opens and the names are in front of the person.

## What it holds
| Part | Here |
|---|---|
| People (phone) | Open. "Person 1" and "Person 2" as the field values, each remove button disabled (two is the least a bill takes), "Add person" under the list. Folded it would read "Person 1, Person 2" |
| Charges (phone) | Folded, "Service 10%, SST 6%" |
| Split | Even chosen |
| Subtotal | Empty, placeholder "0.00" in muted text. No error, an empty field is not wrong |
| Receipt (card) | "Total" alone, then the 28 px receipt icon (muted) and "Enter the subtotal to see the splits." 12 px under it. No lines, no splits, no Copy summary |
| Strip | "Enter the subtotal to see the splits." (14/20) in place of the Total, Splits, and Copy summary disabled (faint label and icon, `--l5` border, no fill). The strip is 108 px |

## Exact copy
| Where | Copy |
|---|---|
| People values | Person 1 · Person 2 |
| Remove (disabled) | Remove Person 1 · Remove Person 2 |
| Receipt and strip | Enter the subtotal to see the splits. |

## Measured at 390 x 844
People ends at 243, Charges at 296, Split at 355. The page does not scroll. The strip's top is at 736.

## Behaviour this golden implies
- Typing a valid subtotal shows the Total and the splits at once.
- Copy summary is disabled, not hidden, so the strip keeps its shape.
- Reached by Start new bill (`new-bill-dialog.html`) or on a first visit. A saved bill that cannot be read also lands here, with a note (`bill-unreadable.html`).
