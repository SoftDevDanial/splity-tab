# Flow check, v1.1.0

**Run:** 2026-10-11 23:35 · **Method:** headless Chromium (Python Playwright), one fresh page per link, at the width the link
exists at (360 x 780, 390 x 844 or 1280 x 800). The prototype is `v1.1.0/prototype/`, a copy of `v1.1.0/final/` with
one wiring script per page. The wiring script is not part of any golden.

| width | from | trigger | expected | landed on | console | result |
|---|---|---|---|---|---|---|
| 360 | bill-items.html | button "New bill" | new-bill-dialog.html | new-bill-dialog.html | clean | PASS |
| 390 | bill-items.html | button "New bill" | new-bill-dialog.html | new-bill-dialog.html | clean | PASS |
| 1280 | bill-items.html | button "New bill" | new-bill-dialog.html | new-bill-dialog.html | clean | PASS |
| 360 | bill-items.html | radio "Even" | bill-even.html | bill-even.html | clean | PASS |
| 390 | bill-items.html | radio "Even" | bill-even.html | bill-even.html | clean | PASS |
| 1280 | bill-items.html | radio "Even" | bill-even.html | bill-even.html | clean | PASS |
| 360 | bill-even.html | radio "By item" | bill-items.html | bill-items.html | clean | PASS |
| 390 | bill-even.html | radio "By item" | bill-items.html | bill-items.html | clean | PASS |
| 1280 | bill-even.html | radio "By item" | bill-items.html | bill-items.html | clean | PASS |
| 390 | bill-items.html | button "Splits" | splits-sheet.html | splits-sheet.html | clean | PASS |
| 360 | bill-items.html | button "Splits" | splits-sheet.html | splits-sheet.html | clean | PASS |
| 1280 | bill-items.html | button "Spare sen: Top of the list. Change" | spare-sen.html | spare-sen.html | clean | PASS |
| 390 | bill-items.html | click at [218, 657] (untap Chen on Mee goreng mamak) | bill-unassigned.html | bill-unassigned.html | clean | PASS |
| 360 | bill-items.html | click at [218, 657] (untap Chen on Mee goreng mamak) | bill-unassigned.html | bill-unassigned.html | clean | PASS |
| 390 | bill-unassigned.html | click at [210, 657] (tap Chen on Mee goreng mamak) | bill-items.html | bill-items.html | clean | PASS |
| 360 | bill-unassigned.html | click at [210, 642] (tap Chen on Mee goreng mamak, above the taller S3 strip (its top is 652 at 360)) | bill-items.html | bill-items.html | clean | PASS |
| 390 | splits-sheet.html | button "Spare sen: Top of the list. Change" | spare-sen.html | spare-sen.html | clean | PASS |
| 360 | splits-sheet.html | button "Spare sen: Top of the list. Change" | spare-sen.html | spare-sen.html | clean | PASS |
| 390 | splits-sheet.html | button "Close" | bill-items.html | bill-items.html | clean | PASS |
| 390 | splits-sheet.html | key Escape | bill-items.html | bill-items.html | clean | PASS |
| 390 | splits-sheet.html | click at [195, 80] (backdrop above the sheet (sheet top 185 at 390)) | bill-items.html | bill-items.html | clean | PASS |
| 360 | splits-sheet.html | button "Close" | bill-items.html | bill-items.html | clean | PASS |
| 360 | splits-sheet.html | key Escape | bill-items.html | bill-items.html | clean | PASS |
| 360 | splits-sheet.html | click at [180, 80] (backdrop above the sheet (sheet top 124 at 360)) | bill-items.html | bill-items.html | clean | PASS |
| 1280 | spare-sen.html | button "Close" | bill-items.html | bill-items.html | clean | PASS |
| 1280 | spare-sen.html | key Escape | bill-items.html | bill-items.html | clean | PASS |
| 1280 | spare-sen.html | click at [200, 60] (backdrop, away from P1 (574 to 914, 377 to 633)) | bill-items.html | bill-items.html | clean | PASS |
| 390 | spare-sen.html | click at [359, 622] (P1's Close (a second Close, the sheet's, is inert behind P1). P1 closes, the Splits sheet stays) | splits-sheet.html | splits-sheet.html | clean | PASS |
| 390 | spare-sen.html | key Escape | splits-sheet.html | splits-sheet.html | clean | PASS |
| 390 | spare-sen.html | click at [195, 30] (P1's backdrop, closes P1 only) | splits-sheet.html | splits-sheet.html | clean | PASS |
| 360 | spare-sen.html | click at [329, 558] (P1's Close (the sheet's Close is inert behind P1). P1 closes, the Splits sheet stays) | splits-sheet.html | splits-sheet.html | clean | PASS |
| 360 | spare-sen.html | key Escape | splits-sheet.html | splits-sheet.html | clean | PASS |
| 360 | spare-sen.html | click at [180, 30] (P1's backdrop, closes P1 only) | splits-sheet.html | splits-sheet.html | clean | PASS |
| 360 | new-bill-dialog.html | button "Start new bill" | bill-empty.html | bill-empty.html | clean | PASS |
| 390 | new-bill-dialog.html | button "Start new bill" | bill-empty.html | bill-empty.html | clean | PASS |
| 1280 | new-bill-dialog.html | button "Start new bill" | bill-empty.html | bill-empty.html | clean | PASS |
| 360 | new-bill-dialog.html | button "Cancel" | bill-items.html | bill-items.html | clean | PASS |
| 390 | new-bill-dialog.html | button "Cancel" | bill-items.html | bill-items.html | clean | PASS |
| 1280 | new-bill-dialog.html | button "Cancel" | bill-items.html | bill-items.html | clean | PASS |
| 360 | new-bill-dialog.html | key Escape | bill-items.html | bill-items.html | clean | PASS |
| 390 | new-bill-dialog.html | key Escape | bill-items.html | bill-items.html | clean | PASS |
| 1280 | new-bill-dialog.html | key Escape | bill-items.html | bill-items.html | clean | PASS |
| 360 | new-bill-dialog.html | click at [20, 20] (backdrop (the dialog's top is 305 at 390, 261 at 360, 311 at 1280)) | bill-items.html | bill-items.html | clean | PASS |
| 390 | new-bill-dialog.html | click at [20, 20] (backdrop (the dialog's top is 305 at 390, 261 at 360, 311 at 1280)) | bill-items.html | bill-items.html | clean | PASS |
| 1280 | new-bill-dialog.html | click at [20, 20] (backdrop (the dialog's top is 305 at 390, 261 at 360, 311 at 1280)) | bill-items.html | bill-items.html | clean | PASS |
| 360 | bill-unreadable.html | button "Dismiss note" | bill-empty.html | bill-empty.html | clean | PASS |
| 390 | bill-unreadable.html | button "Dismiss note" | bill-empty.html | bill-empty.html | clean | PASS |
| 1280 | bill-unreadable.html | button "Dismiss note" | bill-empty.html | bill-empty.html | clean | PASS |

**Result:** 48 of 48 links pass. Zero errors.
