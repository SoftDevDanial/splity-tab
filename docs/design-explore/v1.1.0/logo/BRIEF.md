# Logo brief, Splity Tab v1.1.0

**Date.** 2026-10-11 · **Ruling.** The owner, 2026-10-11, "redraw both marks", Splity Tab's mark grows from the glass receipt, four directions, each QA-checked, he picks on the design board. No "Danial" and no "D" in the mark (`../RULINGS.md`).

## The product
Splity Tab splits one shared restaurant bill among friends in Malaysia (ringgit, SST, service charge). One screen, phone first, offline, no account. People, Charges, Split (Even or By item), Items. The answer is the receipt.

## The source motif, the glass receipt
The receipt is the one expressive object in the app (locked direction G2 "Glass Console", `../final/system.md`). On desktop it is a frosted glass card beside the working, 22 px radius. A 3 px indigo foil sheen runs along its top edge. Inside, top to bottom, Total, the bill lines, a dashed indigo rule, one row per person with their split, then the proof row, a seal check with "Adds up to" and the Total again. On a phone the same card docks at the bottom as a strip that carries the Total, and Splits lifts it up as a sheet. Everything else on the page is quiet layered slate.

Read `../final/bill-items.html` (1280 wide shows the card, 390 shows the strip) and `../final/splits-sheet.html` before drawing.

## Tone
Calm, exact, a little bit of light. A calculator that shows its working. Friendly to a table of friends, never cute. Not a fintech bank, not a payments brand.

## The category to stand apart from
Bill-splitting and expense-sharing apps. Their marks lean on receipt icons with a zigzag foot, pie and wedge charts, divided circles, coins and currency signs, equals and percent signs, and two-colour S lettermarks. A plain receipt-with-zigzag is the category cliché, so a receipt direction must carry one idea the stock icon does not.

## Hard constraints (every direction)
1. **One colour, fill only.** The production mark is one or a few `<path>` elements, no `stroke` attributes (outline any stroke into a filled path), `fill-rule` allowed. The app colours it with CSS `.mark { fill: var(--accent-ink) }`, so it must be complete in one flat fill. No gradient, no opacity, no glow, no glass effect inside the mark. The glass is the source of the idea, not a render effect.
2. **Its real slots.** The app header shows it at 28 x 28 px beside the live wordmark "Splity Tab" (system font stack, 700, -0.01em) on the top bar `#10141B`, in `#A3AAFF`. The favicon is a 16 x 16 tile `#0B0E13` with the mark in `#A3AAFF`, every edge on a whole pixel at 16 and 32 px. It must hold at both sizes.
3. **No "D", no "Danial".** No letter D, nothing that reads as a D at 16 px (a rounded slab with one straight side and one round side is a D risk, check it). The only letter allowed is an S, and only in the lettermark direction.
4. **No myths, no rationalisation.** One idea you can say in one sentence. No golden ratio claims.
5. **The wordmark is live text,** never traced into paths (licensed outlines). "Splity Tab" on one line.
6. **No em or en dashes** anywhere in the file. Phosphor-style icons are not the mark, draw it.
7. **The idea must read at the real slots.** At 28 px and in the 16 px favicon, every feature that carries the idea is at least 2 px. A feature that only reads at hero size is texture, not the idea (round 1 retired two directions for this, `QA.md`).

## The four directions (one designer each, one idea each)
| Id | Type | The one idea |
|---|---|---|
| S1 | Abstract geometric | **The fan.** Three equal slips fanned from one pivot, like a receipt dealt out into shares. The slips stay separate by knockout gaps of one width, so it reads in one colour. Pressure test against a hand of cards, a paint swatch fan, a peacock and a loading icon |
| S2 | Lettermark | **The receipt S.** One paper strip curls into an S, its loose end torn with a short serrated edge. The receipt itself writes the S. Pressure test against a dollar sign, a snake, a scroll and the 1.0 equals mark |
| S3 | Negative space, dual meaning | **The tear is the tick.** A receipt slip whose torn foot is one deep notch shaped as a tick, the app's "Adds up to" check, cut out of the paper. Receipt and proof in one silhouette. Pressure test against a stock receipt icon, a shield, a bookmark ribbon and a V |
| S4 | Bold geometric, app-icon first | **The tab, cut two to one.** The rounded glass card cut once by one straight line, two to one, the smaller piece slid out by one gap. It carries the 1.0 mark's cut (`../../../brand/BRAND.md`) onto the receipt. Pressure test against a battery icon, a toggle, a folder tab and a D |
| S5 | Pictorial reduction | **The curl.** One receipt slip, straight sides and a square top, whose foot rolls forward into a curl, the way a fresh receipt leaves the printer and the app's strip lifts into a sheet. No zigzag, the curl is the receipt cue. Pressure test against a scroll, a page-curl document icon, a ski, a hockey stick and the letters J and L |
| S6 | Lettermark, negative space | **The slip S.** One receipt slip, a plain upright rectangle, cut twice from alternate sides (once from the right in the upper part, once from the left in the lower part), so the paper left between the cuts writes an S. The bill is split into three shares that still join up as one piece. The outline stays a slip, only the two cuts make the letter. Pressure test against the digits 5 and 2, a dollar sign, a Greek key, a radiator, a hamburger menu, a server rack and the 1.0 equals mark |
| S7 | Negative space, brand carry-over | **The slip adds up.** One receipt slip with the 1.0 mark knocked out of it, an equals sign whose top bar is cut once, two to one (`../../../brand/BRAND.md`). The shares add back to the total, now printed on the bill. The cut is what makes it Splity Tab's. Pressure test against a stock document or notes icon, a credit card with two stripes, a hamburger menu, a battery, a wallet and the I Ching broken line |

S1 was retired after two QA reviews (`QA.md`). Its fan of strips reached a structural limit, a W or crest when the back feet hide, a stock three-card fan when they show, with no way to carry the receipt. S5 replaces it.

S2 was retired for distinctiveness 0 (a plain bold S at the real sizes) and S4 for concept legibility 0 (a square over a bar at 28 and 16 px, the receipt never shows). S6 replaces S4 and takes the lettermark lane S2 left, with the slip's outline doing the work S2's tear could not.

S5 was retired for concept legibility 0 and a letter reading (an L, a b or a sock at 28 and 16 px). S7 replaces it.

## The source, widened (owner, 2026-10-11 17:40)
S6 and S7 were retired too (a squared S or digital 5, and a face). Six of seven receipt directions failed for one reason, at 28 and 16 px a receipt is a plain rectangle and only a check lands on it (S3). The owner kept the receipt as the root and widened the source to **what the receipt does**: the split into shares, the people at the table, the sheet that lifts. Constraint 7 stays. S3 stays in the set.

Each new direction is a lane, not a fixed drawing. The designer first sketches three candidate ideas for the lane on the 16 px grid (on the sheet, small, with one line each on what a stranger would call it), keeps the one with the strongest 16 px read, then draws it. The sheet shows the two rejected candidates in a small "Also tried" row.

| Id | Lane | Source |
|---|---|---|
| S8 | Abstract geometric | **The split into shares.** One whole divided into unequal shares that still make the whole, a bill rarely splits evenly. The 1.0 cut (two to one) may carry over, not required |
| S9 | Pictorial or symbolic | **The people at the table.** A few friends around one bill, the table that shares it. Never cute, no mascot, no faces |
| S10 | Motion or emblem, app icon first | **The sheet that lifts.** On a phone the receipt docks as a strip at the bottom and lifts into a sheet. The mark carries the lift |

**Every new direction must avoid** what this round has already learned. No letter but S, nothing that reads as a D. No face (two marks over one inside a block). No stock document, notes or ID icon, no squared S or digital 5, no blocks over a bar (computer, toilet), no sock or boot. No stock UI glyph that means something else in an app header (notification badge, status dot, spinner, hamburger menu, copy, printer, trash, battery, upload tray, layout grid). No category cliché (zigzag receipt, pie wedges, divided circle, coins, currency signs, equals or percent signs, two-colour S). No bar chart (finance and analytics).

## Output contract
A self-contained HTML brand sheet, exactly 1440 x 900, background `#0c0d10`, inline CSS and SVG only, no network, system fonts only (`'Segoe UI', system-ui, sans-serif`). Four sections.
1. **Hero.** The mark about 240 px, centred, in `#A3AAFF`, with the direction's id and one-sentence idea beneath in muted text (sentence case, no all caps).
2. **In the app.** The real header row, top bar `#10141B`, mark 28 px in `#A3AAFF`, the word "Splity Tab" 19 px 700 in `#E8EBF2`, a 10 px gap. Beside it the same lockup at 2x for detail.
3. **Legibility.** The mark at 96, 48, 28 and 18 px, then the favicon tile at 32 and 16 px at their actual pixel size, each with a small px label.
4. **Swatches.** The lockup on a dark card `#15171c` and on a light card `#f7f6f3` (mark and word in `#1E2140`), and the mark alone in pure black on white and pure white on black.

Put the production sources in the sheet so they can be lifted without guessing.
- `<svg id="mark-src" viewBox="..." aria-hidden="true">` holding only the mark's path(s) with `fill="currentColor"` and nothing else.
- `<svg id="favicon-src" viewBox="0 0 16 16">` holding the tile rect and the pixel-snapped mark.
Both sit at the end of the body hidden with `style="display:none"` (the `hidden` attribute does not hide an svg in Chromium, so the sheet must stay exactly 900 px tall).

Write the complete file (it must end with `</html>`) to the path you are given. Then reply with one line, the idea, the path and an honest self-critique naming the rubric criterion a reviewer is most likely to dock.
