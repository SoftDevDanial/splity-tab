# S3 Bill screen, first open (empty)

**Golden.** `bill-empty.html` · **Inventory.** S3 · **Capabilities.** C1 People, C2 Even split, C7 Draft kept (this is what a new or reset bill looks like)

## Intent
The screen someone sees the first time, after "Start new bill", or after a draft that could not be read. It must make the next step obvious. Two people are listed, Even is selected, the rates are already set, and the bill panel says exactly what to enter.

## What the screen holds
1. Header with "Split" and "New bill".
2. **People.** "Person 1" and "Person 2" as field values. Both remove buttons are **disabled** (the brainstorm allows no fewer than 2 people). "Add person" is enabled.
3. Mode switch with **"Even"** checked.
4. **Subtotal** field, empty, with its "RM" unit showing.
5. **Charges.** Service charge 10, SST 6, the hint. Editable before any amount is entered.
6. **Bill panel.** Only the Shares section, holding one message. No bill summary, no table, no Copy summary.

## Exact copy
| Where | Copy |
|---|---|
| People values | Person 1 · Person 2 |
| Remove names (disabled) | Remove Person 1 · Remove Person 2 |
| Panel heading | Shares |
| Panel message (new copy, see SELF-CRITIQUE.md) | Enter the subtotal to see the shares. |
| Everything else | As in `bill-even.md` |

## States this screen covers
- First open, Even mode, no valid amount.
- Remove disabled at 2 people (the same state is also shown in `states.html`, S8).
- The empty subtotal shows **no error** on first open. The error (S4) is for a value that is present and not valid.
- The same panel message shows whenever even mode has no valid subtotal (empty or invalid), because there is nothing to sum.
- With the S7 note, this screen gets the note banner under the header (see `states.md`).

## Spacing and alignment that matter
- The bill panel keeps its place and frame (full bleed with the 2 px ink rule on phone, the 420 px sticky card on desktop), so nothing jumps when the shares appear.
- Panel content is the heading (18/24 700) and the message 8 px below it (16/24 ink), aligned with the heading. There is no operator indent, because there are no operators.
- On phone the panel ends with its 24 px bottom padding, then the page background.
- On desktop the card is short (heading and one line). Its top lines up with the People block.
- A disabled remove button keeps its borders (they are part of the field outline) and only the X turns `--ink-disabled`. No hover, `not-allowed` cursor, skipped by Tab.
