# G Glass Console, round 2 notes

**File** `g.html`, one self-contained page with inline CSS and JS and no network. **Checks** `checks/g/` (`check_g.py`, `results.json` and the screenshots). Run it with `python -B checks/g/check_g.py`.

## The bet
B Glass Receipt's layout and its one glass receipt card, in A Night Console's slate and indigo, with no glow anywhere.

**Design read.** A one-job utility for the person who paid, at a Malaysian restaurant table, in a layered slate console language with one frosted receipt, built with native CSS, system fonts and Phosphor icons.
**Dials.** Variance 5 (money columns must line up), motion 4 (one sweep across the card on load, the sheet lifts, nothing loops), density 5 (a calm form beside a dense receipt).

| | |
|---|---|
| **What it bets on** | The receipt is one object everywhere. On desktop it is the glass card beside the working. On a phone the same card is docked at the bottom as a strip that carries the Total, and Shares lifts it up as a sheet. So the phone opens on the inputs, and the answer is one tap away and never gone. Indigo means one thing (chosen, the proof, and the one solid Copy summary button), so the page stays quiet and the card does the talking. |
| **What it costs** | Without the light pools there is nothing behind the card for the glass to bend on desktop, so the material reads through its edge, its top highlight and its gradient rather than through blur. It is calmer than B and less of a show piece. On a phone the shares are behind a tap, so the person reads the Total at a glance but opens Shares to read each person's figure. At 1280 x 800 the item frame shows about two and a half items of K1 at a time, by design, because the page itself must not scroll. |

## What came from where
| Take | From | What |
|---|---|---|
| Layout and interactions | `round-1/b.html`, `b.md` | The card left and the working right on desktop, the receipt's content and order (the Total, Subtotal, Service, SST, the dashed rule, Shares with "items + charges", Adds up to with the seal, "1 sen left over" with its chip, Copy summary and its status), people as fields with a remove button, the Split switch, items with person toggles, Charges with the hint, the spare sen popover and picker, New bill, every state and its copy, the money maths in whole cents |
| Colours | `round-1/a.html` `:root`, `a.md` | `--l0` to `--l5`, `--field`, text and muted text, `--line-strong`, indigo as fill, ink, line and tint, `--on-accent`, `--error-ink`, `--danger` and `--on-danger`, the warning and note bands, the focus colour |
| Mechanics | `round-2/f.html`, `checks/f/check_f.py` | The item scroll frame with its edge fades, the pinned bar and the Shares sheet (moving one receipt between the card and the sheet), the real Copy summary in the 1.0 text, the left gutter Prototype states tab, the W2 bill, the clipboard stand-in and most of the check script. Nothing of F's look or layout |

## The five changes, as built
| # | Change | How |
|---|---|---|
| 1 | Night Console colours, no glow | Slate layers and one indigo. No light pools, no page gradient, no light under the total, no text glow. The card is slate glass with an indigo hairline edge. Copy summary is a solid indigo fill (`#5059DA`) with `#F7F8FF` text, 5.24 to 1. Chosen states use B's treatment in indigo (a tint with an indigo edge) |
| 2 | Desktop Charges above Split | The working runs People, Charges, Split, Items (or Subtotal in Even). Asserted by position at 1280 and 390 |
| 3 | Items scroll in their own frame | A framed well that takes the rest of the column and scrolls inside itself, with a visible scrollbar and a fade at the edge that has more. The page never scrolls at 1280 x 800 in K1, K2, S7 or W2 (asserted, and in S1 to S6 and W1 too) |
| 4 | Phone inputs first | The card is gone from the top. A strip pinned to the bottom carries the Total, Shares and Copy summary. Shares opens the receipt card as a bottom sheet that Esc, the backdrop and Close shut. The phone order matches desktop |
| 5 | Keep "1 sen left over" | Kept exactly as B had it, on the receipt's spare sen line. No "+1 sen" label beside a share |

## Readings I made
1. **The strip is the receipt, collapsed.** It uses the same slate glass and the same indigo top edge as the card, and Shares lifts it into the full card as a sheet. Only one glass surface is ever on screen, the card on desktop and the strip or the sheet on a phone. Flagged, because the brief names the card as the one glass.
2. **No glow went further than the pools.** B also had a soft light under the total and a glow on the total figure, both inside the card. They read as glow, so both are gone and the total is lit by colour and size alone. Flagged.
3. **The foil became one indigo sheen.** B's rainbow strip and rainbow seal are retinted from `#5059DA` through `#C9CDFF`, because A has one accent.
4. **Add person and Add item sit in their block's heading row.** B had Add person as the last cell of the people grid and Add item under the list. In the heading row Add item stays in reach while the frame scrolls, and twelve people still fit 1280 x 800.
5. **Split is one row**, the heading on the left and the switch on the right, which saves a line of height on desktop.
6. **On desktop the charge hint sits beside the two fields** for the same reason. On a phone it sits under them as in B.
7. **The working column is wider than B's** (up to 560 px against 440), so People sit three across and the card keeps its 460 px.
8. **Twelve people in an even split list their shares in two columns on desktop**, so S7's card fits without an inner scroll.
9. **The S5 and S6 notes sit in the top bar on desktop**, centred, so the page still fits with a note showing. On a phone they are a second row of the bar.
10. **P1 is a popover beside the card on desktop, as in B, and a bottom sheet below 1024 px.** There the receipt makes room under itself and scrolls so the shares sit just above P1. Asserted at 390, 360, 768 and 1280.
11. **When the shares cannot be worked out the strip says why** (S1, S3), in the receipt's own words, and Copy summary is disabled rather than hidden so the strip keeps its shape.
12. **The S4 status shows in two places**, beside the Total on the strip and under Copy summary on the card.
13. **Start new bill uses A's danger fill** (`#C4313C`, text `#FFF5F5`, 5.10 to 1). B used its primary fill.
14. **The phone item frame is as tall as the screen less the strip and 88 px**, so it is never taller than the space above the strip. K1's four items fit with no inner scroll and W2's ten scroll inside the frame.
15. **Icons on quiet buttons are muted, not indigo**, so indigo keeps its one meaning.
16. **Controls on the glass use a border one step lighter** (`--line-glass` `#7A84A0`), because A's `#6E7891` measured 2.91 to 1 on the strip glass.
17. **The page field is A's `--l2` and the top bar A's `--l1`**, with A's inset `--field` for every input.
18. **Copy summary really copies** the 1.0 plain text with the shares as chosen (F's mechanic). B only showed the status.
19. **At random is a real random order** (Math.random), kept until Pick again so the shares never jump while typing. Pick again draws until the pick changes, so the button always visibly does something.
20. **W2 is F's ten-item bill**, so both round 2 pages show the same long bill. Total RM 109.84, 6 sen left over, worked out live and not golden.
21. **"The strip never covers inputs" was read as three tests.** On a three-person bill People, Charges and Split sit above the strip on the first screen, the last control clears the strip at the end of the page, and any control that takes keyboard focus is scrolled above the strip.
22. **On desktop there is no sheet**, since the card is on the page. The P2 shortcut there loads K1.
23. **Prototype states is a thin dashed tab in the left gutter**, F's position, with its panel stopping above the strip.
24. **Tablet widths (600 to 1023 px) use the phone layout**, with the sheet centred and at most 560 px wide.

## Tokens (all on `:root`)
| Role | Token | Value |
|---|---|---|
| Top bar, item frame well | `--l1` | `#10141B` |
| Page | `--l2` | `#151A23` |
| Dialogs, popovers | `--l3` | `#1B212B` |
| Inset fields | `--field` | `#0E1219` |
| Control borders | `--line-strong` | `#6E7891` |
| Control borders on the glass | `--line-glass` | `#7A84A0` |
| Text, muted text | `--text`, `--text-muted` | `#E8EBF2`, `#A7AFBF` |
| Indigo fill (Copy summary only), its text | `--accent`, `--on-accent` | `#5059DA`, `#F7F8FF` |
| Indigo as text and icon, as a line, as a tint | `--accent-ink`, `--accent-line`, `--accent-tint` | `#A3AAFF`, `#7C85F7`, `rgba(110,120,255,.16)` |
| Danger fill, its text | `--danger`, `--on-danger` | `#C4313C`, `#FFF5F5` |
| Error, warning | `--error-ink`, `--warn-ink` | `#FF8A8F`, `#F2C063` |
| Glass layers | `--glass-hi`, `--glass-mid`, `--glass-lo` | `rgba(200,206,255,.10)`, `rgba(150,158,235,.04)`, `rgba(8,10,14,.34)` |
| Glass base (card), dense base (strip, sheet), solid fallback | `--glass-base`, `--glass-dense`, `--glass-solid` | `rgba(27,33,43,.5)`, `rgba(27,33,43,.92)`, `#1D2330` |
| Glass edge, receipt rules | `--glass-edge`, `--hair` | `rgba(163,170,255,.30)`, `rgba(163,170,255,.42)` |
| The lit total | `--total-ink` | `#F4F5FF` |

Type is the system UI stack for words and `ui-monospace, "Cascadia Mono", "SF Mono", Menlo, Consolas` for every figure, with tabular numerals. The total is 38 to 48 px, the strip total 24, shares 18, inputs 16. Shape rule is the receipt (card, strip, sheet) 22, dialogs, popovers, notes and the item frame 16, fields and buttons 10, choices full pill. Motion is one sweep of the indigo edge and a sheen across the card on load, the sheet lifting, a short rise for P1 and a fade for M1, all inside `prefers-reduced-motion: no-preference`. With reduced transparency, or without backdrop-filter, the glass becomes a solid `#1D2330`.

## How each inventory row is reached
| ID | How |
|---|---|
| K1 | The default view. Also "K1 By item (key screen)" in Prototype states |
| K2 | The Split switch, "Even" (the K1 bill keeps RM 100.00 as its even subtotal). Also "K2 Even split" |
| P1 | The chip "Top of the list" on the receipt's spare sen line. Desktop, on the card. Phone, "Shares" on the strip, then the chip in the sheet. "One person" opens the people picker, "At random" shows "Pick again" in P1 and on the receipt line. Esc, the backdrop and Close shut it |
| P2 | "Shares" on the strip (phone and tablet). Esc, the backdrop and Close shut it |
| M1 | "New bill" in the top bar. "Start new bill" gives S1. "Cancel", Esc and the backdrop close it |
| S1 | "Start new bill", or "S1 First open" |
| S2 | Type an amount that is not valid (for example `100,00`) into a price or the Subtotal, or "S2 Amount error" |
| S3 | Untap everyone on an item, or "S3 Item needs a person" (Mee goreng mamak gets an amber marker in the frame) |
| S4 | "Copy summary" on the strip or the card shows "Summary copied". A blocked clipboard shows the failure line. Also "S4 Summary copied" and "S4 Copy blocked" |
| S5 | "S5 Save warning" |
| S6 | "S6 Saved bill unreadable", with its dismiss X |
| S7 | "Add person" until twelve, or "S7 12 people" (Add person disabled) |
| W1 | "W1 RM 1,193.87". A blank-named fifth item at RM 964.50 for Aisyah, so the total is RM 1,193.87 and her share RM 1,153.65 |
| W2 | "W2 Long bill, ten items" (prototype only) |

## Check results
| Check | Result |
|---|---|
| Console and page errors | 0 at 390, 360, 1280, 1024, 768 and with reduced motion |
| Network requests | 0 |
| Clipboard | A stand-in replaced `navigator.clipboard` before load on every page and `document.execCommand("copy")` was wrapped. The stand-in recorded 2 writes (the K1 summary in the 1.0 text, and the strip's Copy summary). Real clipboard writes 0 |
| Page scroll at 1280 x 800 | Document height 800 in K1, K2, S7, W2 and W2 after its frame scrolled, and in S1 to S6 and W1. Neither column overflows |
| Item frame | W2 at 1280 holds 1229 px in a 291 px frame, a mouse wheel scrolls the frame and the page stays at 0. K1 holds 491 px in 291. Fades show on the edge that has more |
| Sideways scroll at 360 | None in K1, K2, S1 to S7, W1, W2, with P1, the P1 picker, P2, M1 and the prototype panel open. No element past the viewport (the 360 run keeps a classic scrollbar, so content had 345 px) |
| The strip and the inputs | On the first screen People, Charges and Split end above the strip (K1 and W2 at 390 and 360). At the end of the page no control is under it. Tabbing through every control in the working (35 in K1, 71 in W2, 28 in S7) never left one under the strip |
| Shares add up in whole cents | K1 6926, K2 11660, S7 11660, W1 119387, W2 10984, after One person Ben, and on all 48 random draws |
| Figures | K1 29.04, 15.74, 24.48 from 24.90 + 4.14, 13.50 + 2.24, 21.00 + 3.48, adds up to 59.40 + 9.86 = RM 69.26, bill 59.40, 5.94, 3.92, "1 sen left over", Top of the list. One person Ben gives 29.03, 15.75, 24.48. K2 38.87, 38.87, 38.86, "2 sen left over", bill 100.00, 10.00, 6.60, 116.60. One person Ben gives 38.86, 38.88, 38.86. At random gave two different people one sen each on every draw and Pick again always changed the pair |
| P1 and the shares | P1 never covers the shares at 390, 360, 768 or 1280, with the picker open or closed |
| Prototype states tab | Covers no content at 390, 360 and 1280 in every state, sits under every popup's backdrop, and its panel stops above the strip |
| Touch targets | Every control 44 px or more at 390, 360 and 1280, and inside P2 and M1 |
| Icons | All ten Phosphor paths match round 1 byte for byte. The mark is `mark.svg`'s geometry, recoloured |
| Long dashes | 0 in `g.html` and in these notes |
| Reduced motion, reduced transparency | No sweep, sheen or lift with reduced motion. With reduced transparency emulated, the card is solid `#1D2330` with no blur |

### Contrast (from the page's own tokens, glass composited over what sits behind it)
| Pair | Ratio | Need |
|---|---|---|
| Body text on the page, on a field, in the frame, on a dialog | 14.62, 15.72, 15.46, 13.55 | 4.5 |
| Muted text on the page, on a field (placeholder), in the frame, on a dialog | 7.91, 8.51, 8.37, 7.33 | 4.5 |
| Copy summary text on its indigo fill, on its hover | 5.24, 6.48 | 4.5 |
| Start new bill text on its red fill, on its hover | 5.10, 6.45 | 4.5 |
| Text on the indigo tint (tapped person, chosen mode, chosen pill) | 12.72, 12.99, 10.97 | 4.5 |
| Indigo line on the frame, a field, a dialog | 5.76, 5.86, 5.05 | 3 |
| Control border on the page, a field, the frame, a dialog | 3.95, 4.25, 4.18, 3.66 | 3 |
| Focus ring on the page, the frame, a dialog | 8.10, 8.57, 7.51 | 3 |
| Error text on the page, in the frame | 7.71, 8.16 | 4.5 |
| Card glass, the Total figure, body text, muted text, indigo Adds up to | 12.31, 11.19, 6.06, 6.20 | 4.5 |
| Card glass, chip border, focus ring | 3.58, 6.20 | 3 |
| Strip glass, the Total figure, body text, over a field | 11.85, 10.78, 10.87 | 4.5 |
| Strip glass, Shares border, focus ring | 3.45, 5.97 | 3 |
| Strip glass worst case (body text over an unblurred white line) | 8.58 | 4.5 |
| Sheet glass, the Total, body, muted, indigo | 12.03, 10.94, 5.92, 6.06 | 4.5 |
| Sheet glass, chip border | 3.50 | 3 |
| Sheet glass worst case (muted text over an unblurred white line) | 5.57 | 4.5 |
| Solid fallback card, muted text, indigo, chip border | 7.13, 7.30, 4.22 | 4.5, 4.5, 3 |
| S5 text on its band, S6 text on its band | 12.93, 13.07 | 4.5 |

The full table, with every pair, is in `checks/g/results.json`.

## Prototype shortcuts (not design decisions)
- A price that is not a valid amount is left out of the totals while its error shows, and a rate that is not valid counts as 0, as in B. The build decides both.
- The receipt is re-rendered on every keystroke, which is fine for a prototype and not how a build should do it.

## Suggestions (not built)
1. Show "1 sen left over" on the strip as well, so the owner's favourite line is on the first phone screen.
2. Let the strip be dragged up to open the sheet, and the sheet swiped down to close.
3. Show the item count in the Items heading, so a long bill says how much is in the frame.
4. Count the total up from the old figure when a price changes, 200 ms, off under reduced motion (B's suggestion).
5. If the owner misses the lit total, a faint glow on the figure alone (never behind the card) could come back as a single token.
6. On a phone, fold Charges into one line once set, with a tap to edit, to lift Items higher.
7. Show each person's share inside the One person picker.

## Skills applied
`taste-skill` gave the design read and dials, one accent locked to one meaning, one radius rule, the button and form contrast checks, labels above fields with errors below, every state designed, no long dashes, no decorative dots, Phosphor icons only, and a solid fallback for the glass. `frontend-design` gave the one memorable element (the receipt, wherever it lives) with everything around it quiet, plain copy that says what happens, and a screenshot critique at every width. Not taken, because the brief forbids them, are React, Tailwind, Motion, web fonts and remote images.
