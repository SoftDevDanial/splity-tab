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

S1 was retired after two QA reviews (`QA.md`). Its fan of strips reached a structural limit, a W or crest when the back feet hide, a stock three-card fan when they show, with no way to carry the receipt. S5 replaces it.

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
