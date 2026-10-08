# Flow check

**Run:** 2026-10-08 15:51 · **Method:** headless Chromium (Python Playwright) at 390 x 844, one fresh page per link.
The prototype is `prototype/`, a copy of `final/` with one wiring script per page. The wiring script is
not part of any golden.

| from | trigger | expected | landed on | console | result |
|---|---|---|---|---|---|
| bill-empty.html | click label[for=mode-item] | bill-items.html | bill-items.html | clean | PASS |
| bill-even.html | click label[for=mode-item] | bill-items.html | bill-items.html | clean | PASS |
| bill-even.html | button "New bill" | new-bill-dialog.html | new-bill-dialog.html | clean | PASS |
| bill-items.html | click label[for=mode-even] | bill-even.html | bill-even.html | clean | PASS |
| bill-items.html | button "New bill" | new-bill-dialog.html | new-bill-dialog.html | clean | PASS |
| bill-items.html | click [aria-label='Who had Mee goreng mamak'] button:nth-child(3) | bill-unassigned.html | bill-unassigned.html | clean | PASS |
| bill-unassigned.html | click [aria-label='Who had Mee goreng mamak'] button:nth-child(3) | bill-items.html | bill-items.html | clean | PASS |
| bill-unassigned.html | button "New bill" | new-bill-dialog.html | new-bill-dialog.html | clean | PASS |
| new-bill-dialog.html | button "Cancel" | bill-even.html | bill-even.html | clean | PASS |
| new-bill-dialog.html | key Escape | bill-even.html | bill-even.html | clean | PASS |
| new-bill-dialog.html | click at [10, 10] (backdrop) | bill-even.html | bill-even.html | clean | PASS |
| new-bill-dialog.html | button "Start new bill" | bill-empty.html | bill-empty.html | clean | PASS |

**Result:** 12 of 12 links pass. Zero errors.
