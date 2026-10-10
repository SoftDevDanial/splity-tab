# F Orbit Console, round 2 notes

**File** `f.html`, one self-contained page with inline CSS and JS and no network. Checks, results and screenshots are in `checks/f/` (run `python -B checks/f/check_f.py`).

## The bet
D Share Orbit's layout and interactions in A Night Console's colours. The ring around the total stays the one memorable thing. Everything around it is quiet layered slate. Indigo is the only accent and it never fills a button. It shows as an outline, a dark tint or text.

**Design read.** A single purpose phone utility for one person at a restaurant table, in a layered slate console language with the share ring at its centre, built with native CSS, system fonts and a drawn SVG ring.
**Dials.** Variance 5 (columns of money must line up), motion 4 (the ring draws itself, the sheet slides up, nothing loops), density 5 (a calm form beside a dense receipt).

## What came from where
| Take | From | What |
|---|---|---|
| Layout and interactions | `round-1/d.html` | The ring with name callouts and tags, one segment per person true to its share, the mini orbit on each share row, hover that lights a segment, the shares table (Person, Items, Charges, Share), Adds up to, the Bill summary, the spare sen line and dropdown, the One person picker, Pick again, the "+1 sen" label, the spare sen dots on the ring, New bill, every state and the Prototype states tab |
| Colours | `round-1/a.html` `:root` | `--l0` to `--l5`, `--field`, text and muted text, `--line-strong` control borders, indigo as `--accent-line` and `--accent-tint` and `--accent-ink`, `--error-ink`, the warning and info bands, the focus colour |
| Person colours | `round-1/d.html` | Eight of D's twelve kept, four retuned (see Readings) |
| The proof row look | `round-1/a.html` | Adds up to sits on the dark indigo tint with indigo text, like A's proof row, inside D's table |

## The five changes, as built
| # | Change | How |
|---|---|---|
| 1 | No bright filled buttons | The chosen mode is an indigo outline on a dark indigo tint. A tapped person is the same. The chosen spare sen option is an indigo tint row with an indigo radio. Copy summary is an indigo outline with indigo text on the tint. Start new bill is a red outline with red text on a faint red tint. The check reads every button's computed background and found no bright fill |
| 2 | Desktop Charges first | The input pane reads Charges (Service charge, SST, the hint), the Even and By item switch, People, then Items. The check asserts the order by position at 1280 and at 390 |
| 3 | Items scroll in their own frame | At 1280 x 800 the item list sits in a framed well that takes the rest of the pane and scrolls inside itself. A fade appears at the top or bottom edge when there is more, and the normal scrollbar shows. The page itself never scrolls in K1, K2, S7 or W2 (asserted, and also in S3, S5 and S6) |
| 4 | Phone inputs first | The receipt is gone from the top. A bar pinned to the bottom shows the Total, a Shares button with a live mini ring, and Copy summary. Shares opens the whole receipt as a bottom sheet. Esc, the backdrop and Close shut it. The ring draws itself as the sheet opens |
| 5 | Keep the spare sen | "+1 sen" sits beside the share that got it in the table, the callouts and the sheet. "1 sen left over" sits beside the spare sen choice. The ring still marks each spare sen with an indigo dot |

## Readings I made
1. **People sit above the item frame, not inside it.** On desktop People take two columns, so twelve people fit and the frame keeps its own scroll. S7 (twelve people, even split, as in round 1) fits 1280 x 800 with no scroll of any kind. With twelve people in By item the frame would fall under its 150 px floor, so the input pane scrolls inside itself as a fallback. The page still never scrolls.
2. **Phone input order matches desktop** (Charges, switch, People, Items). It reads well at 390 because Charges is one short row, and People still start on the first screen (top at 313 px of 844).
3. **The bar has two rows.** The Total sits on top, Shares and Copy summary share the row below. Three controls with full labels do not fit one row at 360 px once the total reaches RM 1,193.87.
4. **Copy summary also sits inside the Shares sheet**, under the spare sen line, because the sheet covers the bar.
5. **When shares cannot be worked out, the bar says why.** It shows the same message as the receipt (S1, S3) and Copy summary is disabled rather than hidden, so the bar keeps its shape.
6. **Four person colours retuned.** D's periwinkle (p2) and lavender (p8) read as the indigo accent on slate, so they became apricot and gold. D's sand (p6) sat too close to the new apricot and became rose. D's olive (p10) sat too close to gold and became caramel. The other eight are D's. All twelve pass 3 to 1 as ring segments and 4.5 to 1 as letters.
7. **The mark** takes the first two person colours (teal and apricot) for the two shares and the text colour for the total, as D did.
8. **The notes (S5, S6) sit in the top bar.** Beside the brand on desktop and as a second row of the bar on phone, so the 1280 page still fits with a note showing.
9. **Many people read in two columns.** On desktop an even split with more than six people lists its shares in two columns, so S7's receipt fits without an inner scroll.
10. **The ring is shorter without callouts.** Callouts show only on a wide ring with six or fewer people (D's rule), and without them the ring drops its extra height.
11. **The phone item frame** is as tall as the screen less the top bar, the pinned bar and 72 px. K1's four items show with no inner scroll and W2's ten scroll inside the frame.
12. **Shape rule.** 8 px for controls and fields, 12 px for panels and frames, 16 px for sheets, pills for the switch, the person chips and the spare sen chip, circles for avatars. A's corners with D's pills.
13. **Add person and Add item moved into their block's heading row**, so they stay in reach while the frame scrolls.
14. **Start new bill uses A's error red (#FF8A8F) for its outline and text.** A's darker danger red (#C4313C) as an outline is 2.96 to 1 on the dialog, under the 3 to 1 a control edge needs.
15. **Copy summary really copies** the 1.0 plain text with the shares as chosen. D only showed the status. The blocked case shows the 1.0 failure line.
16. **Tablet (640 to 1023 px) uses the phone layout** with the pinned bar and a centred sheet up to 600 px wide.
17. **W2's ten items** are K1's four plus Roti canai 2 pieces RM 5.00 (Ben), Teh tarik 2 glasses RM 7.00 (Aisyah, Ben), Kopi O ais RM 3.20 (Chen), Sirap bandung RM 4.20 (Chen), Ais kacang RM 8.90 (all three) and Keropok lekor RM 6.50 (all three). Total RM 109.84 with 6 sen left over. Worked out live, not golden.
18. **A loaded prototype state starts at the top** of the page and of the item list.

## Tokens
| Role | Token | Value |
|---|---|---|
| Top bar | `--l0` | #0B0E13 |
| Desktop receipt side, item frame well | `--l1` | #10141B |
| Input pane (and the phone page) | `--l2` | #151A23 |
| Receipt panel, pinned bar, sheets, dialogs | `--l3` | #1B212B |
| Lit share row | `--l4` | #232A36 |
| Hover, ring track | `--l5` | #2D3545 |
| Inset fields | `--field` | #0E1219 |
| Control borders | `--line-strong` | #6E7891 |
| Text | `--text` | #E8EBF2 |
| Muted text | `--text-muted` | #A7AFBF |
| Indigo as text | `--accent-ink` | #A3AAFF |
| Indigo as a line | `--accent-line` | #7C85F7 |
| Indigo as a tint | `--accent-tint` | rgba(110, 120, 255, 0.16) |
| Error and Start new bill | `--error-ink` | #FF8A8F |
| People 1 to 12 | `--p1` to `--p12` | #79B8A7, #E0A97E, #C99FCF, #7DB4D8, #A9C17F, #D8939A, #8FC9C3, #D9C27A, #A7B2C2, #C4A27F, #9FC6A1, #C9AFC0 |

Type is the system UI stack with tabular figures. Inputs are 16 px, body 15, controls 14, the ring total 32 on phone and 44 on desktop.

## How every inventory row is reached
| ID | How |
|---|---|
| K1 | The default view |
| K2 | The Even half of the switch (the K1 bill keeps RM 100.00 as its even subtotal) |
| P1 | Desktop, the spare sen chip ("Top of the list") under the shares. Phone, Shares in the bar, then the same chip in the sheet. One person opens the people picker, At random closes it and shows Pick again. Esc, Close and the backdrop shut it |
| P2 | Shares in the pinned bar (phone and tablet). Esc, Close and the backdrop shut it |
| M1 | New bill in the top bar. Cancel, Esc and the backdrop close it. Start new bill gives S1 |
| S1 | Start new bill, or Prototype states |
| S2 | Type a bad amount and leave the field, or Prototype states |
| S3 | Untap everyone on an item, or Prototype states |
| S4 | Copy summary (in the bar or the sheet) shows "Summary copied". The blocked line is in Prototype states |
| S5, S6 | Prototype states. S6's X dismisses it |
| S7 | Add person until twelve, or Prototype states |
| W1, W2 | Prototype states |

The Prototype states tab is a 14 px dashed strip in the left gutter, between the top bar and the pinned bar. It covers no content at 390, 360 or 1280 (asserted at several scroll positions), sits under every popup's backdrop, and its panel stops above the pinned bar.

## Check results
| Check | Result |
|---|---|
| Console and page errors | 0 at 390, 360, 1280, 1024, 768 and with reduced motion |
| Network requests | 0 |
| Clipboard | A stand-in replaced `navigator.clipboard` before load. It recorded the K1 summary in the 1.0 format |
| Sideways scroll at 360 | None in K1, K2, S1 to S7, W1, W2, with P1, P2 and M1 open, and no element past the viewport. The 360 run keeps a classic scrollbar, so the content had only 345 px |
| Page scroll at 1280 x 800 | Document height 800 in K1, K2, S7, W2 and W2 after scrolling the frame, and in S3, S5 and S6. Neither column overflows |
| Item frame | W2 at 1280 holds 1229 px in a 269 px frame, a mouse wheel scrolls the frame and the page stays at 0. W2 at 390 holds 1229 px in 609 px. Fades show above and below |
| Figures | K1 29.04, 15.74, 24.48 (items 24.90, 13.50, 21.00, charges 4.14, 2.24, 3.48), adds up to 59.40, 9.86, 69.26, bill 59.40, 5.94, 3.92, 69.26, "1 sen left over". One person Ben gives 29.03 and 15.75. K2 38.87, 38.87, 38.86, "2 sen left over", bill 100.00, 10.00, 6.60, 116.60. One person Ben gives 38.86, 38.88, 38.86. At random gave two different people one sen each on every draw and the pair changed between draws. W1 totals RM 1,193.87 and fits 360 with no collisions |
| Ring arcs against shares | Worst gap 0.00001 of the ring |
| Touch targets | Every control 44 px or more at 390, 360 and 1280 |
| Bright filled buttons | None |
| Icons | All nine Phosphor paths match the round 1 and 1.0 sources byte for byte |
| Long dashes and middle dots in the page | 0 |
| Reduced motion | The ring is drawn at once on load and when the sheet opens |

### Contrast
| Pair | Ratio |
|---|---|
| Body text on the input pane | 14.62 |
| Body text on the receipt panel | 13.55 |
| Body text on the indigo tint | 11.90 |
| Muted text, lowest (on the lit row) | 6.54 |
| Muted text on the indigo tint | 5.94 |
| Indigo text on the receipt panel | 7.51 |
| Indigo text on the indigo tint (Copy summary, Adds up to) | 6.08 |
| Indigo outline, lowest (Copy summary edge) | 5.05 |
| Control borders, lowest (on the receipt panel) | 3.66 |
| Focus ring, lowest | 7.51 |
| Error text, lowest | 7.71 |
| Start new bill text on its tint | 6.03 |
| Person colours as ring segments, lowest (rose p6) | 6.59 |
| Person colours as letters, lowest (rose p6) | 7.52 |
| Tag text on a person colour, lowest (rose p6) | 7.52 |

The full table is in `checks/f/results.json`.

## Known limits
- Between 1024 and 1199 px the receipt stacks under the ring and scrolls inside its own column. The page still does not scroll.
- Twelve people in By item at 1280 x 800 make the input pane scroll inside itself (Reading 1).

## Suggestions (not built)
1. On phone, let Charges fold into one line ("10% service, 6% SST") once set, with a tap to edit, to lift People by about 90 px.
2. Swipe the Shares sheet down to close it.
3. Show the item count in the Items heading, so a long bill says how much is in the frame.
4. A short highlight on a share row when the spare sen moves to it, so the change is seen without comparing numbers.
5. Show each person's share inside the One person picker.
