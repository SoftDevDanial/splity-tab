# Self-critique of the Splity Tab v1.1.0 final design set

**Phase.** design, `sdlc:design` step 8 · **Date.** 2026-10-11 · **Skills loaded.** `taste-skill:taste-skill` and `frontend-design:frontend-design` (what transferred is in `system.md`)

## The walk
Every golden was rendered headless at 390 x 844 (a touch phone with overlay scrollbars), 360 x 780 (classic scrollbars, the stricter width) and 1280 x 800, compared with g2 at the same state and width, looked at, and checked by `checks/check_final.py`. Results are in `checks/results.json`, screenshots in `checks/shots/`.

| File | One primary action | Spacing on the scale | AA contrast | States present | Real, consistent copy | Money aligned and adding up | No template tells | 390 / 360 / 1280 |
|---|---|---|---|---|---|---|---|---|
| `bill-items.html` (K1) | Copy summary | Yes, as g2 | Yes | By item, toggles on and off, a shared item, 1 spare sen, sections folded | Yes | Yes, 6926 sen | Yes | Pass / Pass / Pass |
| `bill-items-open.html` (K1 phone) | Copy summary | Yes | Yes | Both sections open | Yes | Yes, 6926 | Yes | Pass / Pass / Pass (K1) |
| `bill-even.html` (K2) | Copy summary | Yes | Yes | Even, 2 spare sen | Yes | Yes, 11660 | Yes | Pass / Pass / Pass |
| `spare-sen.html` (P1) | The choice itself, it applies at once | Yes | Yes | Top of the list chosen | Yes | Yes, 6926 | Yes | Pass / Pass / Pass |
| `spare-sen-one.html` (P1 picker) | The choice | Yes | Yes | One person, picker, Ben | Yes | Yes, 11660 | Yes | Pass / Pass / Pass |
| `spare-sen-random.html` (P1 random) | The choice, Pick again is second | Yes | Yes | At random, Pick again twice | Yes | Yes, 11660 | Yes | Pass / Pass / Pass |
| `splits-sheet.html` (P2) | Copy summary | Yes | Yes | The sheet open over K1 | Yes | Yes, 6926 | Yes | Pass / Pass / Pass (K1) |
| `new-bill-dialog.html` (M1) | Start new bill | Yes | Yes | Open over K1, page inert | Yes, all brainstorm copy | n/a | Yes | Pass / Pass / Pass |
| `bill-empty.html` (S1) | None needed, the Subtotal is the next step | Yes | Yes | New bill, remove disabled at two, Copy summary disabled | Yes | n/a | Yes | Pass / Pass / Pass |
| `rate-error.html` (S2 rate) | None, fix the rate | Yes | Yes | Charges open on load, the error, the receipt blocked, Copy summary disabled | Yes | n/a, blocked (open question 1, ruled) | Yes | Pass / Pass / Pass |
| `bill-unassigned.html` (S3) | None, tap who had it | Yes | Yes | Marker, messages on card and strip, Copy summary disabled | Yes | Bill lines yes, 6926 | Yes | Pass / Pass / Pass |
| `bill-unreadable.html` (S6) | None, Dismiss note or name people | Yes | Yes | The note, then S1 with People open | Yes | n/a | Yes | Pass / Pass / Pass |
| `bill-twelve.html` (S7) | Copy summary | Yes | Yes | Add person disabled, two columns on desktop | Yes | Yes, 11660 | Yes | Pass / Pass / Pass |
| `bill-large.html` (W1) | Copy summary | Yes | Yes | Four figure bill, frame scrolls at 360 | Yes | Yes, 119387 | Yes | Pass / Pass / Pass |
| `states.html` (sheet) | n/a | Yes | Yes | S2 amount twice, S2 on SST, three Check markers, S4 four ways, S5, plural S3, By item empty | Yes | n/a | Yes | Pass / Pass / Pass |

"Spacing on the scale" means every value is g2's own, the 4 px scale plus the derived values listed in `system.md`. Nothing new was added.

## Verification result
| Check | Result |
|---|---|
| Asserts | 748 passed, 0 failed (778 at step 8. The 30 money asserts on `rate-error.html`'s old Total, ten per width, no longer apply since its receipt is blocked) |
| Console and page errors | 0 (every golden at the three widths, and once more with motion allowed) |
| Network requests | 0 (anything that is not file or data is aborted and logged, none were) |
| Sideways scroll | None at 360, 390 or 1280, and no element past the viewport |
| Page scroll at 1280 x 800 | None in all fifteen goldens. Neither column of a screen overflows |
| Touch targets | Every button, field, switch label, choice, pill and toggle 44 px or more at all three widths |
| Money | In every golden with splits, the splits add to the Total and to Adds up to, each person's items plus charges equal their split, the working under Adds up to equals the Subtotal plus the charges, the items column equals the Subtotal, the bill lines add to the Total, the item prices add to the Subtotal, and the strip's Total equals the receipt's. Totals 6926, 11660 and 119387 sen |
| The strip and the inputs | With the sections folded, People, Charges and Split end above the strip on the first screen. At the page end no control is under it. Tabbing every control in the working (4 to 37 per golden) never left one under the strip, with no script (the build's `scroll-padding-bottom` does it) |
| "Shares" | Absent from the visible text and every accessible name in every golden at every width |
| `system.css` | The first `<style>` of every golden is `system.css` byte for byte |
| Icons | Every `<symbol>` line and the seal gradient are g2's, byte for byte. One mark `<svg>` per page |
| Script, remote URLs, long dashes | None in any golden. No long dash in any file in `final/` |
| Notes | No colon or semicolon in the prose of any `.md` here (tables and code aside) |
| Contrast | Recomputed from `system.css` with the glass composited (`system.md`). Every pair WCAG needs passes |
| Specimen pieces | Eleven pieces of `states.html` match g2's own element in the same state by computed style and text |
| Links | Every link in `LINKS.json` was opened on its source golden at its width. Every named control was found and every point lands on the intended control or backdrop |

## Every difference from g2, and why
Each golden was screenshotted beside g2 at the same state and width (`checks/shots/side-*.png`) and diffed pixel by pixel. With g2's Prototype states tab hidden, every golden matched at every width with 0 differing pixels, except where a ruling changes it.

### Visible
| Golden | Width | Difference | Why |
|---|---|---|---|
| `bill-unreadable.html` (S6) | 390, 360 | People is open, so the two name fields and Add person show, and Charges, Split and the Subtotal sit 126 px lower than in g2's S6 (about 20,900 pixels in four areas, `side-bill-unreadable-vs-g2-unruled-*.png`). Against g2 after a tap on People it is identical | Ruling 1. S6 starts a fresh bill like S1, so naming people is the first step |
| `bill-unreadable.html` (S6) | 1280 | None | Sections are always open on desktop |
| `rate-error.html` (S2 rate) | All | The receipt is blocked, the Total label and "Check the charges to see the splits." under a 28 px receipt icon, where g2 shows Total RM 62.96 with "Service 0%". On a phone the strip shows the message with Copy summary disabled and is 108 px, not 111 (about 11,300 to 45,700 pixels, `side-rate-error-*.png`). The work column is identical, save the scrollbar thumb at 360, since the page is 3 px shorter | Open question 1, ruled 2026-10-11 (ORCH) by the sealed 1.0 spec, core R18 (a) and app R17 `rates` |
| Every golden | All | No Prototype states tab in the left gutter | Not part of the design (g2 says so itself). It was hidden in g2's screenshots for the comparison |

Ruling 2 (the rate error copy) and ruling 3 (the mark recoloured, one inline `<svg>` per page) were already true in g2, so they cause no difference.

### Not visible, in the markup of a static golden
| What | Why |
|---|---|
| No script. What g2 works out by script is written into a short "Golden only" style per file (the item frame's fades, the strip's height when it is not 111, P1's place on desktop, the sheet's room under P1, the twelve person summary) | The brief asks for static goldens. Each value was measured in g2 (`checks/g2-measure.json`) |
| Dialogs open with the `open` attribute, their backdrops are divs, and the page behind is `inert` | A golden cannot call `showModal()`. The rules match only an open, non-modal dialog, so the build never sees them. Because the page is inert, `splits-sheet.html` at 1280 exposes four fewer accessible names than g2's K1 there (the heading, New bill and the two regions). It looks the same |
| `autofocus` left out (Cancel in M1, the sheet in P2) | It would put a focus ring in the static picture. The `.md` says where focus starts |
| Script hooks (`data-*`), ids used only by script, the hidden block of the other Split mode, P1's hidden picker and Pick again, the closed P1 and M1 dialogs | They render nothing. The closed Splits sheet is kept as an empty `<dialog>` so the strip's `aria-controls` points at something |
| The receipt is written twice where the sheet is open (the card for desktop, the sheet for a phone) | g2 moves one receipt between them by script |
| `--strip-h` defaults to 111 px | g2 set it by script (`system.md`) |
| S2 on an amount, S4 and S5 are pieces in `states.html`, not full screens | 1.0's precedent for states that live inside a screen. Each piece was matched to g2's own element by computed style and text |

## What I changed while composing, and why
1. **Removed the Prototype states CSS and `--t-proto`.** Not part of the design.
2. **Wrote the static stand-ins and the layer order into `system.css`.** The goldens need them and the order was only implicit in g2's top layer.
3. **Put P1's picker and At random on K2.** The inventory gives its P1 figures for K2 (Ben gives 38.86, 38.88, 38.86, and random gives two different people one sen each). P1 Top of the list stays on K1, g2's own P1 state.
4. **Fixed the specimen sheet to fit 1280 x 800.** It was 858 px tall. I dropped an empty band above the strips, tightened the column gap from 16 to 12 and the page padding from 16 to 12. It is now 800 or less. I also made the price error frame flush, because its padding narrowed the item row below the app's own width and clipped "Char kuey teow" at 360.
5. **Fixed my own transcription.** The first K1 golden had four numbers in the seal path written with a trailing zero (the same shape, different bytes). The byte check caught it. Two notes had a colon inside an accessible name in prose, now in code.
6. **Fixed two links.** At 360 the Chen toggle on S3 sits partly under the taller strip, so its link point is now on the visible part. On a phone P1 has a second Close behind it (the sheet's, inert), so P1's Close is a measured point rather than a name.

## Template tells checked and absent
No eyebrows, no all-caps labels, no section numbers, no middle-dot strings in the UI, no decorative dots (the only dot is a chosen radio), no glow, no gradient text, no fake screenshots. One accent with one meaning (chosen, the proof, the one Copy summary fill). One shape rule, written down. Glass on one object only, the receipt. Phosphor icons only. No long dash in any file. Monospace is used for money only, for tabular figures. The one flourish is g2's 3 px indigo sheen along the receipt's top edge and its single sweep on load, off with reduced motion.

## Copy the brainstorm does not word (for the owner's ruling)
| Copy | Where | Source |
|---|---|---|
| Splity Tab | Wordmark | Brainstorm v1.1.0 (USER) |
| Splits | The strip button, the sheet's name, the receipt heading | g2, the owner's rename of "Shares" |
| items + charges | Beside the Splits heading in By item | g2 (from round 1 B) |
| Total · Subtotal · Service 10% · SST 6% | Receipt and strip | g2 (brainstorm nouns) |
| Enter the subtotal to see the splits. | Receipt and strip, Even with no valid subtotal | 1.0's line with the rename |
| Add each item and tap who had it to see the splits. | Receipt and strip, By item with no valid price | g2, new in round 2 |
| Check the charges to see the splits. | Receipt and strip, a rate that is not valid (`rate-error.html`) | 1.0's line with the rename (app R17 `rates`), added 2026-10-11 by the ruling on open question 1 |
| 1 item still needs a person. Tap who had it to see the splits. · N items still need a person. Tap who had each one to see the splits. | Receipt and strip, S3 | 1.0's lines with the rename |
| Enter a rate from 0 to 30 · Enter a rate from 0 to 20 | Under a rate field | Ruling 2 (1.0's suggested wording, added in g2) |
| Check service charge · Check SST · Check both rates | A folded Charges row with an error | g2, new |
| Spare sen | P1 title | g2, new |
| Top of the list · One person · At random · Pick again | P1 and the receipt chip | Brainstorm wording, capitalised as labels |
| One person, Ben | The chip after a pick | g2, new |
| Who pays the spare sen | Hidden legend of the picker | g2, new |
| `Spare sen: Top of the list. Change` | The chip's accessible name | g2, new |
| Bill and splits · Edit the bill | Region names of the card and the working | g2, new |
| Close · Dismiss note · Remove <name> · Who had <item> · Person N name · Item N name · <item> price in RM · Subtotal in RM | Accessible names | 1.0 and g2 |

Brainstorm copy used verbatim is "Enter an amount like 12.50", "Set a charge to 0 if your bill already includes it.", "Summary copied", "Could not copy. Your browser blocked the clipboard.", "Your saved bill could not be read, so a new one was started.", "This bill is not being saved on this device. It will be lost when you close this tab.", "Start a new bill?", "This clears the people, items and amounts.", "Start new bill", "Cancel", "New bill", "Copy summary", "Adds up to", "Service charge", "SST", "Person 1", "Person 2" and "2 sen left over".

## Interaction rules I specified, or carried from g2, that the brainstorm does not word
1. People and Charges fold to one header row below 1024 px. A bill opens with both folded, except a new bill (S1, S6) opens People and a rate error opens Charges. A section opens on load only.
2. A header row hides its summary while open and keeps its place. Opening reveals over 200 ms, folding is instant. Open state is not saved with the bill.
3. The People summary shows as many names as fit, then "and N more", and "12 people" only when not even one name fits.
4. Folded with an error, the Charges summary turns red and says what to check.
5. The strip shows the Total, or the reason there is none, with Copy summary disabled rather than hidden.
6. Splits opens the receipt as a bottom sheet below 1024 px. Esc, the scrim and Close shut it, focus returns to Splits, and it closes by itself when the screen reaches 1024 px.
7. P1 is a popover beside the card on desktop, its bottom level with the chip, and a bottom sheet over the Splits sheet on a phone, where the sheet pads its bottom so the splits stay in view. Focus starts on the chosen choice. A choice applies at once.
8. One person picks the first eligible person at once and lists only people with a split above zero. If the chosen person is removed, the rule falls back to Top of the list.
9. At random draws a real random order kept with the bill. Pick again draws until the result changes.
10. The copy status shows on the card and on the strip, and the next change to the bill clears it.
11. M1 starts on Cancel. Start new bill returns focus to New bill.
12. Dismiss note on S6 removes the note and sends focus to New bill.
13. The rate fields name their error in `aria-describedby` only while it shows. A blank rate is not an error.

## Open questions for the owner (nothing invented)
1. **A rate that is not valid counts as 0 in the receipt.** `rate-error.html` showed g2 as it is, Total RM 62.96 with "Service 0%", while the field says the rate is wrong. A Total built on a rate the person did not mean can be copied. g2.md suggested the receipt say so instead (for example "Check the rates to see the splits." with no Total). **Ruled 2026-10-11, ORCH, told to the owner.** The sealed 1.0 spec already settles it. Core R18 (a) blocks the result first on a rate that fails its parser, and app R17 words it "Check the charges to see the shares.", now "splits". `rate-error.html` now shows the blocked receipt at all three widths, no Total, Copy summary disabled on the strip.
2. **A price that is not valid is left out of the totals while its error shows** (g2's prototype shortcut, S2 on a price). The same choice as question 1, for items. **Ruled 2026-10-11, ORCH, with question 1.** Core R18 (d) blocks the result, and app R17 `prices` words it "Give every item a price to see the splits." with the rename. No golden shows it, it is a builder note.
3. **P1's picker and At random are shown on K2,** following the inventory's figures. If the owner wants all of P1 on K1, the figures would be 29.03, 15.75, 24.48 for One person, Ben. **Ruled 2026-10-11, owner, keep them on K2.**
4. **Dialogs against their scrim** measure 1.01 to 1.21 (`system.md`). Not a WCAG requirement, and the owner accepted the look in g2. Recorded so it is a choice, not an accident. **Ruled 2026-10-11, owner, accepted as he saw them.**
5. **The logo swap touches two places per page,** the inline mark `<svg>` and the tab icon's data URI in `<head>`. **Ruled 2026-10-11, owner, the mark is redrawn** (`../RULINGS.md`).

## Known limits, accepted
- On desktop P1's place is written for 1280 and wider (`left: calc(50% - 66px)`). Between 1024 and 1279 the build's script places it.
- The W1 fade rule reads the screen's height, which matches the build's rule at the three sizes here.
- The twelve person summary is written for 390 and 360. Wider phones and tablets fit more names, which the build measures.
- Tablet widths (600 to 1023 px) use the phone layout and have no golden of their own, as in g2.

## After the run, orchestrator (design step 7)
- **Header row names.** A visually hidden ", " between a flex button's flex items gave "People , Aisyah, Ben, Chen" in Chromium's own accessibility tree (a space is added between flex items). The People and Charges buttons are now named by `.sec-name` (`aria-labelledby`) and described by `.sec-sum` (`aria-describedby`), the hidden comma is gone. Measured after the change, name "People", description "Aisyah, Ben, Chen" (at 360 in S7 the narrow summary), and "Charges" with "Check service charge" on a rate error. Nothing visible changed.
