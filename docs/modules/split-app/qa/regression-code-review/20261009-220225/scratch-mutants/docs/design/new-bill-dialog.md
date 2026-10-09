# M1 New bill confirmation

**Golden.** `new-bill-dialog.html` · **Inventory.** M1 · **Capabilities.** C8 New bill

## Intent
"New bill" wipes everything with no undo, so it asks first. The question names what will be lost. The action button repeats the action's name ("Start new bill"), so the person knows exactly what the tap does.

## What the golden shows
The S2 screen (`bill-even.html`) behind a scrim, with the dialog centred in the viewport. The page behind is `inert` in the golden. In the app, `dialog.showModal()` makes it inert and the `.app` clip rule in `system.css` stops it scrolling.

## Exact copy
| Where | Copy |
|---|---|
| Title (`h2`, names the dialog) | Start a new bill? |
| Body (describes the dialog) | This clears the people, items and amounts. |
| Primary button | Start new bill |
| Secondary button | Cancel |

## States and behaviour
- **Opens** from the "New bill" header button.
- **Start new bill** clears the bill and closes the dialog. The app returns to S3 (two people "Person 1" and "Person 2", Even, 10% and 6%, empty subtotal).
- **Cancel** and **Esc** close the dialog and change nothing. A click on the backdrop does nothing (native modal behaviour), so a stray tap cannot lose or keep data by accident.
- **Focus.** On open, focus goes to "Cancel", the safe choice. Tab cycles between the two buttons. On close, focus returns to "New bill".
- The view has one primary action, "Start new bill" (ink). Red is not used. In this system red means an error, and the question already says what will be cleared.

## Spacing and alignment that matter
- Width is `min(400px, 100% - 32px)`, so 358 px at 390, 328 px at 360 and 400 px at 1280. Centred both ways.
- Padding 24 px. Surface fill, 1 px ink border, 6 px radius, no shadow.
- Title 18/24 700. Body 16/24 ink muted, 8 px below the title. At 360 the body wraps to two lines.
- Actions 24 px below the body. Under 600 px the two 48 px buttons stack full width, "Start new bill" on top, 8 px apart. From 600 px they sit in a row, right aligned, "Start new bill" then "Cancel", 8 px apart, natural width.
- Scrim `--scrim` (ink at 48%) over the whole viewport. The page behind does not scroll while the dialog is open, so a full-page render equals the viewport (390 x 844, 360 x 780, 1280 x 800).
