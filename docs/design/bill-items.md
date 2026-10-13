# K1 Bill screen, by item, with splits (the key screen)

**Golden.** `bill-items.html` · **Inventory.** K1 · **Capabilities.** C1 People, C3 Split by item, C4 Charges, C5 Splits that add up, C6 Copy summary, C9 Spare sen choice, C0 Look
**Reference widths.** All three. 390 x 844 and 360 x 780 show the phone layout (sections folded, the strip), 1280 x 800 the desktop layout (the card beside the working). Pixel for pixel the same as g2's K1 at all three (`checks/shots/side-bill-items-*.png`).

## Intent
Turn a receipt into splits everyone trusts, at a glance, and show that they add back up to the Total. The person lists the items and taps who had each one. The receipt shows the bill, each person's split with its working, and the proof line "Adds up to" in indigo. On a phone the inputs come first and the strip at the bottom carries the Total, Splits and Copy summary, so the answer is never more than one tap away.

## What the screen holds
**Phone (under 1024 px), top to bottom.**
1. Top bar. The mark and "Splity Tab" (`h1`), "New bill" (ghost, plus icon) on the right.
2. People, folded. The header row reads "People" with "Aisyah, Ben, Chen" and a caret.
3. Charges, folded. "Charges" with "Service 10%, SST 6%" and a caret.
4. Split. The heading "Split" and the switch, "By item" chosen.
5. Items. The heading "Items" with "Add item" (ghost, plus icon), then the item frame with four items.
6. The strip, fixed at the bottom. "Total RM 69.26", then "Splits" (ghost, caret up) and "Copy summary" (primary, copy icon).

**Desktop (1024 px and up).** The top bar, then two columns. Left, the glass card (the receipt). Right, the working with every section open, People (heading, "Add person", three name fields), Charges (Service charge 10, SST 6, the hint beside them), Split, Items in their frame. The strip is not shown. The page does not scroll.

## Exact data
| Item | Price | Tapped |
|---|---|---|
| Nasi lemak ayam | RM 15.90 | Aisyah |
| Char kuey teow | RM 13.50 | Ben |
| Mee goreng mamak | RM 12.00 | Chen |
| Satay, 10 sticks | RM 18.00 | Aisyah, Chen |

| Bill line | Figure | Working |
|---|---|---|
| Subtotal | RM 59.40 | 15.90 + 13.50 + 12.00 + 18.00 |
| Service 10% | RM 5.94 | 10% of 59.40, rounded half up |
| SST 6% | RM 3.92 | 6% of 65.34 = 3.9204, rounded half up |
| Total | RM 69.26 | 59.40 + 5.94 + 3.92 |

| Split | Items | Charges | Split |
|---|---|---|---|
| Aisyah | 24.90 (15.90 + 9.00, half the satay) | 4.14 (413 sen + the 1 spare sen) | RM 29.04 |
| Ben | 13.50 | 2.24 | RM 15.74 |
| Chen | 21.00 (12.00 + 9.00) | 3.48 | RM 24.48 |
| Adds up to | 59.40 | 9.86 (5.94 + 3.92) | RM 69.26 |

Charges are shared in proportion to items, rounded down (Aisyah 986 x 2490 / 5940 = 413.3, Ben 224.1, Chen 348.6, so 413 + 224 + 348 = 985). The 1 sen left over goes to the top of the list, Aisyah. The receipt shows "1 sen left over" with "Top of the list" chosen.

## Exact copy
| Where | Copy |
|---|---|
| Wordmark | Splity Tab |
| Page title | Danial's Splity Tab |
| Top bar button | New bill |
| Header rows (phone) | People, with "Aisyah, Ben, Chen" · Charges, with "Service 10%, SST 6%" |
| Block headings | People · Charges · Split · Items |
| Buttons | Add person · Add item |
| Charge labels | Service charge · SST |
| Charges hint | Set a charge to 0 if your bill already includes it. |
| Split switch | Even · By item |
| Receipt | Total · Subtotal · Service 10% · SST 6% · Splits · items + charges · Adds up to · 1 sen left over · Top of the list · Copy summary |
| Strip | Total · Splits · Copy summary |
| Accessible names | Bill and splits (card region) · Edit the bill (working region) · People and Charges (header rows, each described by its summary, here Aisyah, Ben, Chen and Service 10%, SST 6%) · Person 1 name to Person 3 name · Remove Aisyah, Remove Ben, Remove Chen · Item 1 name to Item 4 name · Nasi lemak ayam price in RM (and each item) · Remove Nasi lemak ayam (and each item) · Who had Nasi lemak ayam (and each item) · Spare sen: Top of the list. Change (the chip) · Splits (the strip button, which controls the sheet) |
| Hidden working | Each split's working reads "Items 24.90 + charges 4.14" to a screen reader, "24.90 + 4.14" on screen |

**What Copy summary puts on the clipboard** (the 1.0 format, unchanged, never shown on screen).
```
Bill split
Total RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)
Aisyah RM 29.04
Ben RM 15.74
Chen RM 24.48
Adds up to RM 69.26
```

## States this screen covers
- By item chosen, every item has a person, so the splits, the proof and Copy summary show.
- Toggles on and off side by side, and a shared item (the satay, two people on).
- One spare sen, Top of the list (the default).
- Both sections folded on a phone (a bill that opens with names and rates already set). Both always open on desktop.
- The status line is present but empty and hidden. After a copy it shows S4 (`summary-copied.html`, `copy-blocked.html`).
- The Splits sheet is closed (`splits-sheet.html` shows it open).
- Hover, focus and pressed come from the system (`system.md`). Tab order on a phone is New bill, the People row, the Charges row, the Split radios, Add item, then each item's name, price, remove and toggles, then Splits and Copy summary on the strip (28 controls in the working). On desktop the card comes first (the chip, Copy summary), then the working.

## Icons
Plus (New bill, Add item, Add person), caret (header rows, the chip, Splits turned up), X (remove person, remove item), check bold (a tapped person), copy (Copy summary), seal check with the indigo gradient (Adds up to). All Phosphor, 18 px in buttons, 16 px on the chip, 14 px in toggles, 24 px for the seal.

## Sizes and spacing that matter for a 1 to 1 build
**Phone, at 390 x 844.**
- Top bar 60 px, 16 px sides, `--l1`, a hairline under it. The mark 28 px, 10 px to the wordmark (19/24 700).
- The working starts 4 px under the top bar. People row 52 px, Charges row 52 px, each with a hairline above the next. Split starts 12 px under the Charges hairline. People ends at 117, Charges at 170, Split at 229.
- Items starts 20 px under a hairline. Its heading row is 44 px with Add item on the right, then 8 px to the frame.
- The first Items field sits at 335 from the top (G had 599). Three whole items and the start of a fourth show above the strip. At 360 x 780, two whole items and the start of a third.
- Item frame. 16 px radius, `--l1`, `--line-frame` edge, 10 px left and 8 px right padding on a phone. Each item 12 px top and bottom, the row `minmax(0, 1fr) 104px 44px` with 6 px gaps, toggles 8 px below and 8 px apart. A hairline above every item but the first. The four items are 491 px and fit without scrolling on a phone.
- The strip is 111 px (a 1 px edge, the 3 px foil, 10 px top padding, the 30 px Total row, 8 px, the 44 px buttons, 12 px bottom). Its top is at 733 (669 at 360). Total label 14/20 600, figure 24/30 600 with "RM" at 14. Splits and Copy summary split the row 1 to 1.3 with an 8 px gap.
- The working's bottom padding is the strip's height plus 24 px, so at the end of the page the last toggle clears the strip (asserted, page end and every control while focused).

**Desktop, at 1280 x 800.**
- Top bar 64 px with 48 px sides. Layout 48 px sides, columns 560 and 560, 64 px apart.
- Card at 98, 84, 460 x 642, 24 px padding, the foil along its top. Total label at the top, the figure 48 px (11vw capped). Bill lines 15/22 with a 6 px gap. Dashed rule 20 px below them and 16 px above "Splits". Splits 12 px apart. The proof row 16 px under a solid indigo hairline. The spare line 16 px below, the chip at 392, 589 (141 x 44). Copy summary 20 px below, 48 px tall, full width.
- Working column from 672, 20 px top padding. People heading row 44 px, three name fields across (148 px minimum). Charges fields 150 px each, the hint in a third cell 28 px down so it lines up with the fields. Split row. Items fills the rest, its frame 291 px tall holding 491 px of items, so it scrolls inside itself and the bottom fade shows (the golden's own rule, the build sets `data-down`).

**Money format.** Always `RM 0.00`, monospace, tabular, right aligned. Figures from 1,000 take a thousands comma.

## Behaviour this golden implies
- The receipt and the strip update as the person types. Neither is a live region, so typing is not read out. The status line is a live region.
- Untapping everyone on an item turns this screen into S3 (`bill-unassigned.html`).
- "Even" on the switch gives K2 (`bill-even.html`). Switching keeps both the items and the even subtotal.
- On a phone, a tap on a header row opens that section with a short reveal (`bill-items-open.html` shows both open).
- "Splits" opens P2 (`splits-sheet.html`). The chip opens P1 (`spare-sen.html`, on the card on desktop, in the sheet on a phone). "New bill" opens M1 (`new-bill-dialog.html`).
