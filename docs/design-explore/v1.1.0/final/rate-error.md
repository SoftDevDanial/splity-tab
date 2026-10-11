# S2 on a rate, Service charge 35

**Golden.** `rate-error.html` · **Inventory.** S2, on a rate · **Capabilities.** C4 Charges
**Reference widths.** All three. The work column is pixel for pixel g2's "S2 Rate error (opens Charges)" at 390, 360 and 1280. The receipt and the strip differ from g2 by ruling (below).

## Intent
A rate outside its range is an error the person must see, even on a phone where Charges is folded. A section with an error inside opens on load, and folded it says "Check" in the error colour.

## What changes from K1
| Part | Here |
|---|---|
| Charges (phone) | Open on load. The row carries the error marker (hidden while open) |
| Service charge field | Value `35`, red edge with a 1 px inset (reads 2 px), `aria-invalid="true"`, `aria-describedby="chargeHint svcErr"` |
| Error | "Enter a rate from 0 to 30" in 14/20 600 error red with a 16 px warning circle, 8 px under the field. In a half-width cell it breaks into two even lines, "Enter a rate" over "from 0 to 30", the icon on the first |
| Desktop | The error grows its own cell downward. The SST field and the hint stay where they were. The item frame shrinks to 243 px and shows its bottom fade |
| Receipt (card and sheet) | Blocked. The Total label stays, a 28 px receipt icon and "Check the charges to see the splits." replace the rest (`.r-empty`, as `bill-empty.html`). No figure, no bill lines, no Splits, no spare sen, no Copy summary |
| Strip (phone) | The message in place of Total and the figure. Splits stays, Copy summary is disabled, not hidden, so the strip keeps its shape (108 px, as `bill-empty.html`) |
| Folded (after a tap on the row) | The summary turns to error red at 600 with a 16 px warning circle and reads "Check service charge". The specimen sheet shows it, and "Check SST" and "Check both rates" (`states.html`) |

## Exact copy
| Where | Copy |
|---|---|
| Error under Service charge | Enter a rate from 0 to 30 |
| Error under SST (specimen) | Enter a rate from 0 to 20 |
| Folded marker | Check service charge · Check SST · Check both rates |
| Receipt and strip | Check the charges to see the splits. |

## The receipt in this state, ruled
g2 counts a rate that is not valid as 0 and still shows a Total. That was a prototype shortcut, flagged at step 8 (`SELF-CRITIQUE.md`, open question 1). The sealed 1.0 spec settles it. Core R18 (a) blocks the result first when a rate fails its parser, and app R17 gives the blocked message for `rates`, "Check the charges to see the shares.", now "splits" after the 1.1.0 rename. So the receipt shows nothing to work out, the same treatment as `bill-empty.html`, and there is no Total to copy. ORCH, 2026-10-11, told to the owner.

A price that is not valid blocks the same way with "Give every item a price to see the splits." (app R17 `prices` with the rename). No golden shows it, it is a builder note.

## Measured at 390 x 844
People ends at 117, Charges at 348, Split at 407. The strip starts at 736 (672 at 360). The page is 1125 px and scrolls (the golden sets the strip height to 108 px, as `bill-empty.html`). At 1280 the card is 161 px tall.

## Behaviour this golden implies
- A blank rate is not an error, it counts as 0, as in 1.0.
- A rate that is not valid blocks the receipt (core R18). The receipt comes back as soon as both rates are valid, whatever the field's error timing (app R10).
- The error shows while the value is wrong and goes as soon as it is valid. The rate fields name their error in `aria-describedby` only while it shows.
- A section opens on load only. Typing a bad rate with Charges open does not reopen anything later, and folding shows "Check".
