# States specimen sheet

**Golden.** `states.html` · **Inventory.** S4, S6, S7, S8 · **Not a screen.** It shows states that live inside the screens, drawn in the system.

## How to read it
Each state sits in a frame drawn at phone layout, whatever the page width (one column at 360 and 390, three columns at 1280). The frame, its grey caption above it and the sheet title are labels for this sheet only. They are not part of the app and are styled by a second `<style>` block marked "Specimen sheet only". Product headings inside frames are `h3` here so the sheet outline stays valid. In the app they are `h2`, as in the screen goldens.

## S4 Amount error (C2, C3)
**Copy.** Enter an amount like 12.50
- Shown under the Subtotal field (value `0`, which is not above 0) and under an item price (value `13.505`, three decimals).
- The input gets `aria-invalid="true"` and `aria-describedby` pointing at the message.
- Field. Border turns `--error` and thickens to 2 px through an inset shadow, so the layout does not move. The value stays as typed.
- Message. 14/20 600 `--error`. Under the Subtotal it sits 8 px below the field, left aligned. In an item row it spans the name and price columns and is right aligned, so it ends under the price field, directly above the toggles (which keep their 8 px gap).
- When the field is focused it keeps the red border and gains the normal ink focus ring.

## S6 Copy status (C6)
| State | Copy | Look |
|---|---|---|
| Success | Summary copied | 14/20 600 ink, centred, 8 px under Copy summary |
| Failure | Could not copy. Your browser blocked the clipboard. | Same, in `--error`. Wraps to two centred lines at 360. |
- Both use the same `p.status` with `role="status"`, so the message is announced politely. It is empty and hidden until a copy is tried, and it is replaced by the next attempt.
- Success is ink, not green. Green stays reserved for the "Adds up to" proof line.

## S7 Saved bill could not be read (C7)
**Copy.** Your saved bill could not be read, so a new one was started.
**Dismiss control.** X icon button, accessible name "Dismiss note".
- The note sits under the header and above the People block, inside `.note-wrap`, so it has the header's width and gutters (full width of the content area on desktop, 1040 px at 1280).
- Surface fill, 1 px `--line-strong` border, 6 px radius, 16 px left padding, 16 px below the header. Text 16/24 ink, vertically centred against the 44 x 44 dismiss button. At phone width the text wraps to two lines and the button stays at the top right.
- `role="status"`. Dismissing removes the note and the content below moves up. Focus then goes to the next control in order.
- The screen under the note is S3 (a new bill), so the frame shows "Person 1" and "Person 2" with remove disabled.

## S8 People limits (C1)
| State | What is disabled | Look |
|---|---|---|
| 12 people (Aisyah, Ben, Chen, Devi, Farid, Grace, Hafiz, Indra, Jia Hui, Kumar, Lina, Mei Ling) | Add person | Transparent fill, `--line` border, `--ink-disabled` text and plus icon, `disabled` attribute, skipped by Tab, no hover |
| 2 people (Aisyah, Ben) | Both remove buttons | Borders stay (they outline the field), the X turns `--ink-disabled`, `disabled` attribute, skipped by Tab |
- At 12 people the grid holds six rows of two at phone width, and "Add person" sits in the next cell.
- Disabled colours are exempt from contrast rules (WCAG 1.4.3) and were chosen to read clearly as unavailable next to the enabled controls.
