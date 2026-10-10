# Manifest, Splity Tab v1.1.0 final design set

**Phase.** design, `sdlc:design` steps 5, 6 and 8 · **Date.** 2026-10-11 · **Source.** `round-2/g2.html`, with the three rulings in `COMPOSE-BRIEF.md`
**Rule for the build.** Every golden inlines `system.css` verbatim as its first `<style>`. A second short `<style>` marked "Golden only" holds what the build works out by script (a fade, a measured height, the popover's place, a fitted summary). The `.md` beside each golden is its spec. W2 (the ten item bill) stays prototype only and has no golden.

## Inventory to golden
| Row | What | Golden | State shown | Width that matters |
|---|---|---|---|---|
| K1 | Bill screen, by item, with splits (key screen) | `bill-items.html` | Four items, three people, sections folded on a phone, 1 sen left over, Top of the list | All three |
| K1, phone | K1 with People and Charges open | `bill-items-open.html` | Both header rows open | 390 and 360 (at 1280 it is K1) |
| K2 | Bill screen, even split | `bill-even.html` | Subtotal RM 100.00, 2 sen left over, Top of the list | All three |
| P1 | Spare sen choice | `spare-sen.html` | K1, Top of the list chosen | All three (popover on desktop, bottom sheet over the Splits sheet below 1024) |
| P1, picker | One person, with the picker of people | `spare-sen-one.html` | K2, One person, Ben chosen, 38.86, 38.88, 38.86 | All three |
| P1, At random | At random, with Pick again | `spare-sen-random.html` | K2, At random, Ben and Chen drawn, 38.86, 38.87, 38.87 | All three |
| P2 | Splits sheet | `splits-sheet.html` | K1 receipt in the sheet | 390 and 360 (at 1280 it is K1, there is no sheet) |
| M1 | New bill dialog | `new-bill-dialog.html` | Over K1 | All three |
| S1 | First open | `bill-empty.html` | Person 1, Person 2, Even, empty Subtotal, People open on a phone | All three |
| S2, amount | Amount error | `states.html` | The Subtotal at `100,00` and an item price at `13,50` | 390 |
| S2, rate | Rate error | `rate-error.html` | K1 with Service charge 35, Charges open on load | All three |
| S2, rate, SST | Rate error on SST | `states.html` | SST at 25 | 390 |
| S3 | An item still needs a person | `bill-unassigned.html` | Mee goreng mamak untapped, amber marker, receipt and strip say why | All three |
| S3, plural | Two or more items | `states.html` | The card message | 1280 |
| S4 | Copy status | `states.html` | Summary copied and Could not copy, on the strip and on the card | 390 (strip) and 1280 (card) |
| S5 | Save warning | `states.html` | The warning note in the top bar | 390 |
| S6 | Saved bill could not be read | `bill-unreadable.html` | The note, then S1 with People open (ruling 1) | All three |
| S7 | 12 people reached | `bill-twelve.html` | Add person disabled, twelve splits, two columns on desktop | All three |
| W1 | Fits 360 px at RM 1,193.87 | `bill-large.html` | K1 with a fifth item of RM 964.50 | 360 |
| Variants | Folded Check markers, By item with nothing to work out | `states.html` | Check service charge, Check SST, Check both rates, and the strip message | 390 |
| W2 | Long bill, ten items | none | Prototype only, in `round-2/g2.html` | |

## Files
| File | What |
|---|---|
| `system.css`, `system.md` | The locked design system (step 5) |
| The fifteen goldens above, each with its `.md` | Step 6 |
| `MANIFEST.md` | This file |
| `LINKS.json` | Every natural trigger and every close between goldens, for step 7 |
| `SELF-CRITIQUE.md` | Step 8, every difference from g2 with its reason, and the questions for the owner |
| `checks/check_final.py`, `checks/g2_measure.py` | The render checks and the g2 measurements behind the golden-only styles |
| `checks/results.json`, `checks/g2-measure.json` | Their results |
| `checks/shots/` | Every golden at 390, 360 and 1280 (`<golden>-<width>.png`, plus `-full` on a phone), g2 at the same state (`g2-<golden>-<width>.png`), and side by side with the diff (`side-<golden>-<width>.png`, golden, g2, then the golden dimmed with every differing area boxed in red) |

## Names kept from 1.0
`bill-items.html` (K1), `bill-even.html` (K2), `bill-empty.html` (S1), `bill-unassigned.html` (S3), `new-bill-dialog.html` (M1) and `states.html` keep their 1.0 jobs. The new screens take new names, `bill-items-open.html`, `spare-sen.html`, `spare-sen-one.html`, `spare-sen-random.html`, `splits-sheet.html`, `rate-error.html`, `bill-unreadable.html`, `bill-twelve.html` and `bill-large.html`.

## How the goldens connect
`LINKS.json` lists them. Copy summary is not in it, because its result is K1 with the S4 status line, which only the specimen sheet draws (compare that line against `states.html`). A blocked clipboard has no natural trigger in a test. Two steps need more than one trigger and are not in it either. The K1 phone golden with both sections open is reached from K1 by tapping the People row, then the Charges row, and folds back the same way. The P1 picker and At random goldens are on the K2 bill, reached from `bill-even.html` by Splits (phone), the chip, then the choice (and Ben for the picker).
