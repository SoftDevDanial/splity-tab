# Direction B, Glass Receipt

**File** `round-1/b.html` (one self-contained page, no network). **Checks** `round-1/checks/b/` (`check_b.py` and the screenshots).

## Thesis
The receipt becomes one floating holographic card, the only glass on the page, with the total softly lit.

**Design read.** A one-job utility for the person who paid, in a dark holographic-glass language, built with native CSS and system fonts.
**Dials.** Variance 5, motion 4, density 5.

## The bet and what it costs
| | |
|---|---|
| **The bet** | The answer comes first. On a phone the card opens the page with the total lit at the top and every share under it, so the first screen is the result a visitor remembers. On a desktop the card floats alone in the left column over two soft lights, and the working sits in a quiet rail on the right. One material (glass) and one light (the total) carry all the spice. Everything else is plain navy, so the page still reads as minimal. |
| **What it costs** | On a phone the inputs sit under the card, so while typing an item the person scrolls up to read the shares. Glass needs light behind it, so the lights limit how pale the secondary text on the card can be (it uses a lighter grey than the rest of the page to stay at AA). Holographic foil and glow are easy to overdo, so they are rationed to three places (the top strip, the "Adds up to" seal and the light under the total). |

## What makes it B and not the others
- One glass surface. Popovers, dialogs, notes and inputs are solid navy. The card has a reduced-transparency fallback (a solid `#13233B` card) and a fallback for browsers without backdrop-filter.
- The total is the headline of the receipt, set in monospace at 38 to 48 px with a soft cyan light under it. With nothing to split (S1) the light goes out and the lamps behind the card dim.
- Cyan hairlines are the line language. A dashed hairline splits the bill lines from the shares, a solid one sits above "Adds up to", and every control is drawn in a 1 px line.
- Each share reads like a receipt line, the name and the share on one line and its working (`24.90 + 4.14`) in small monospace under it. A legend "items + charges" heads the column. This layout fits 360 px at any bill size, which answers W1 by design rather than by squeezing a four-column table.
- "Adds up to" carries a foil seal (Phosphor seal-check filled with the foil gradient), the receipt's proof of trust.

## Tokens (all on `:root`)
| Role | Token | Value |
|---|---|---|
| Field | `--navy-1` | `#0A1424` |
| Dialog, note | `--navy-2` | `#101D33` |
| Hover in a dialog | `--navy-3` | `#172A45` |
| Text | `--ink` | `#E8F0F7` |
| Secondary text on the field | `--ink-muted` | `#9DB0C4` |
| Secondary text on the glass | `--ink-soft` | `#C3D1DE` |
| Accent (hairlines, checked states, primary button, the lit total) | `--cyan` | `#62D6E8` |
| Text on cyan | `--on-cyan` | `#04212B` |
| Control border | `--line` | `#4D7189` |
| Focus ring | `--focus` | `#9BEAF5` |
| Error | `--error` | `#FF8F86` |
| Warning (S3 marker, S5 note) | `--warn` | `#F2C879` |

Type is the system UI stack for words and `ui-monospace, "Cascadia Mono", "SF Mono", Menlo, Consolas` for every figure, with tabular numerals. Shape rule is card 22, dialogs and notes 16, fields and buttons 10, choices (people toggles, spare sen chip, picker) full pill. Motion is one load sweep across the card and its foil strip, the lamps fading when the total appears or goes, a slide up for the sheet and a short fade for the dialog. All of it sits inside `prefers-reduced-motion: no-preference`.

## How each inventory row is reached
| ID | How |
|---|---|
| K1 | The default view. Also "K1 By item" in Prototype states |
| K2 | The mode switch "Even" (the even subtotal RM 100.00 is kept, as the rules say). Also "K2 Even split" |
| P1 | The chip "Top of the list" on the receipt's spare sen line. On a phone it opens a bottom sheet, from 600 px a popover beside the card (never over the shares). "One person" opens the people picker, "At random" shows "Pick again" in the sheet and on the receipt line. Esc, the backdrop and the close button close it |
| M1 | "New bill" in the header. "Start new bill" goes to S1, "Cancel", Esc and the backdrop close it |
| S1 | "Start new bill" in M1, or "S1 First open" |
| S2 | Type a bad amount in any price or the subtotal, or "S2 Amount error" (subtotal `100,00`) |
| S3 | Untap everyone on an item, or "S3 Needs a person" (Mee goreng mamak). The item gets an amber marker in the gutter |
| S4 | "Copy summary" shows "Summary copied" (no clipboard call). "S4 Copied" and "S4 Copy failed" in Prototype states |
| S5 | "S5 Save warning" (a note under the header with no dismiss) |
| S6 | "S6 Unreadable bill" (the note over a fresh S1 bill, with a dismiss button) |
| S7 | "Add person" up to 12, or "S7 12 people" (even split, Add person disabled) |
| W1 | "W1 RM 1,193.87". A fifth item with a blank name (shown as "Item 5", the 1.0 blank-name rule) at RM 964.50 for Aisyah makes the subtotal RM 1,023.90 and the total RM 1,193.87, with Aisyah's share RM 1,153.65 |

Prototype states is a grey dashed bar at the bottom left, labelled "Not part of the design". The dialogs use the top layer, so it always sits under their backdrop.

## Figures
Shares are computed live in whole cents with the brainstorm's rules, and the check script asserts every inventory figure.
- K1 total RM 69.26, lines RM 59.40, RM 5.94, RM 3.92, shares RM 29.04, RM 15.74, RM 24.48 from `24.90 + 4.14`, `13.50 + 2.24`, `21.00 + 3.48`, adds up to `59.40 + 9.86` = RM 69.26, "1 sen left over", Top of the list.
- K1 with One person Ben gives RM 29.03, RM 15.75, RM 24.48.
- K2 total RM 116.60 (RM 100.00, RM 10.00, RM 6.60), shares RM 38.87, RM 38.87, RM 38.86, "2 sen left over". One person Ben gives 38.86, 38.88, 38.86. At random gives two different people one sen each.

## Check results (`python -B checks/b/check_b.py`)
- Console errors 0. Network requests 0.
- Sideways scroll at 360 px none in K1, K2, S1 to S7, W1 and with P1 open. The script also checks that no element pokes past the viewport, because the app clips overflow and scrollWidth alone would hide it (this caught a real Charges grid overflow, now fixed).
- Esc, backdrop and Cancel close M1. Esc and backdrop close P1. The Prototype states bar sits under the backdrop. Pick again draws a different result.
- Every icon path is a byte-exact Phosphor copy from `src/ui/icons.js` or round-1 `a.html`. The header mark uses the `mark.svg` geometry unchanged, recoloured cyan. No em or en dashes in the page.
- Reduced transparency gives a solid card (backdrop-filter none). Reduced motion stops the load sweep.

### Contrast
| Pair | Ratio | Need |
|---|---|---|
| Body text (ink) on the navy field | 16.02 | 4.5 |
| Secondary text (ink-muted) on the field | 8.29 | 4.5 |
| Accent cyan on the field | 10.81 | 4.5 |
| Text on the cyan button | 9.78 | 4.5 |
| Error on the field, on a dialog | 8.37, 7.65 | 4.5 |
| Control border on the field | 3.55 | 3 |
| Focus ring on the field | 13.6 | 3 |
| Glass, worst case per text element (the brightest pixel inside each text box, text hidden, at 360, 390 and 1280) | lowest is 5.11 (bill line labels, W1 at 360). Total figure 5.99, "Total" label 5.63, share figures and the cyan "Adds up to" figure 9.01 or more | 4.5 |
| Secondary text and cyan on the solid fallback card | 10.14, 9.24 | 4.5 |

### Screenshots (in `checks/b/`)
K1 at 390, 360, 768 and 1280 (`k1-*.png`, plus full-page versions). P1 sheets and popovers (`p1-k1-open-390`, `p1-k1-one-person-picker-390`, `p1-k1-one-ben-390`, `p1-k1-random-390`, `p1-k1-pick-again-390`, `p1-k2-one-ben-390`, `p1-k2-random-390`, `p1-w1-360`, `p1-k1-768`, `p1-k1-one-person-1280`, `p1-k1-random-1280`). M1 (`m1-390`, `m1-360`, `m1-1280`). States (`state-*-390`, `state-*-1280`, `state-w1-360`, `s1-after-start-new-bill-390`, `s4-copied-via-button-390`). Also `proto-panel-390`, `focus-ring-1280` and `k1-1280-reduced-transparency-and-motion`.

## Prototype shortcuts (not design decisions)
- Copy summary never touches the clipboard. It only shows the status.
- A price that is not a valid amount is left out of the totals while its error shows. A rate that is not valid counts as 0. The real build decides both.
- In the two-column layout the card is sticky. A bill taller than the window (12 people in by item mode with many items) would keep the card's foot out of reach until the rail ends. The build should switch sticky off when the card is taller than the viewport.

## Suggestions (not built)
- Let the receipt card's total count up from the old figure to the new one when a price changes, 200 ms, so the person sees what their edit did. Off under reduced motion.
- On a phone, a slim sticky strip with just the lit total while the person scrolls the inputs, so the answer is never off screen.
- Tapping a share could highlight that person's items in the list (the working of one line).
- The foil seal could also be the favicon's accent at large sizes. The brand rules would need to allow a second colour first.

## Skills applied
`taste-skill` gave the design read and dials, one accent locked to one job, one radius rule, the button and form contrast checks, labels above fields with errors below, every state designed, no em dashes, no decorative dots or section numbers, Phosphor icons only, and the reduced-transparency fallback for glass. `frontend-design` gave the grounding in the subject (a receipt that proves itself), one memorable element with everything around it quiet, plain copy that says what happens, and screenshot critique at every width. Not taken, because the brief forbids them, are React, Tailwind, Motion, web fonts, a dark and light switch, and stock images.
