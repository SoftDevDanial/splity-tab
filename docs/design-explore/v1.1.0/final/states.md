# States specimen sheet

**Golden.** `states.html` · **Inventory.** S2 on an amount, S4 copied and blocked, S5, and the variants with no prototype preset (folded Check SST and Check both rates, a rate error on SST, two items still needing a person, By item with nothing to work out) · **Not a screen.** It shows states that live inside a screen, drawn in the system.
**Reference widths.** 390 x 844 for every phone piece, 1280 x 800 for the card pieces (S4 on the card is desktop only). At 1280 the sheet lays out in three columns and fits the screen without scrolling. At 360 and 390 it is one column and scrolls, as a sheet should.

## How to read it
Each state sits in a dashed frame with a short caption above it. The page title, the captions and the frames are sheet chrome, styled by a second `<style>` block marked "Specimen sheet only". They are not app copy. Every frame shows its piece at phone layout whatever the page width (the specimen block restates the phone rules inside `.spec`), except the card pieces, which are the desktop card. Product headings inside frames are `h3` so the sheet's outline stays valid. In the app the section header rows are `h2`. The wordmark inside the S5 frame is a `span`, since the sheet's own title is the page's `h1`.

Each piece was checked against g2's own element in the same state, by computed style and text (`checks/results.json`, `specimen_vs_g2`).

## S2 on an amount (C2, C3)
**Copy.** Enter an amount like 12.50
- **The Subtotal (Even).** Value `100,00`, which is not an amount. The field gets the red edge with a 1 px inset (reads 2 px, nothing moves), `aria-invalid="true"`, and the message 8 px below in 14/20 600 error red with a 16 px warning circle. The field keeps the value as typed. On the screen this is K2 with this field, and the receipt and strip say "Enter the subtotal to see the splits." because there is no valid subtotal.
- **An item price (By item).** Char kuey teow at `13,50`. The message spans the name and price columns and is right aligned, so it ends under the price, then the toggles 8 px below. In g2 an item whose price is not valid is left out of the totals while its error shows (a prototype shortcut, see `SELF-CRITIQUE.md`).

## S2 on a rate, SST (C4)
**Copy.** Enter a rate from 0 to 20
SST at `25`. Same field error as above, the message in two even lines under the half-width field ("Enter a rate" over "from 0 to 20") with the icon on the first. The hint stays under both fields. `rate-error.html` shows the Service charge case on the full screen.

## Charges folded with an error (phone)
**Copy.** Check service charge · Check SST · Check both rates
The header row's summary turns to error red at 600 with a 16 px warning circle 6 px before the words, right aligned beside the caret. The section name stays in body text, so the row still reads as Charges. The accessible name reads, for example, "Charges, Check SST".

## S4 Copy status (C6)
| State | Copy | Look |
|---|---|---|
| Copied | Summary copied | 14/20 600 body text with a 16 px indigo check. On the strip it sits beside the Total, right of it on the same line. On the card it is centred 12 px under Copy summary |
| Blocked | Could not copy. Your browser blocked the clipboard. | The same with a red warning circle. On the strip it does not fit beside the Total, so it takes its own line under it and wraps to two lines, and the strip grows to 153 px. On the card it wraps to two lines, left aligned beside the icon |
- Both use `p.status` with `role="status"`, so the line is read politely. It is empty and hidden until a copy is tried and is cleared by the next change to the bill.
- Copied is body text with an indigo check, not a colour of its own. Red stays for errors.

## S5 Save warning (C10)
**Copy.** This bill is not being saved on this device. It will be lost when you close this tab.
On a phone the note is a second row of the top bar, full width, the warning band (`--warn-bg`) with an amber edge at 45%, a 20 px amber warning triangle, the text in 14/20, 16 px padding at the right (no dismiss). At 390 it wraps to two lines. On desktop it sits centred in the top bar between the brand and New bill, 44 px tall, on one line. It cannot be dismissed and goes away after the next save works. `role="status"`.

## Two items still need a person (card)
**Copy.** 2 items still need a person. Tap who had each one to see the splits.
The plural of S3 (`bill-unassigned.md`). The bill lines stay above it on the screen. The strip says the same with its own amber icon.

## By item, nothing to work out yet (phone)
**Copy.** Add each item and tap who had it to see the splits.
By item with no item that has a valid price. The strip shows the sentence in place of the Total with Copy summary disabled, wrapping to two lines where the strip is narrower than the sentence. The card shows "Total" with the 28 px receipt icon and the same sentence, as S1 does for Even.
