# Splity Tab design system, v1.1.0

**Phase.** design, `sdlc:design` step 5 · **Date.** 2026-10-11 · **Source.** `round-2/g2.html` (Glass Console, revised), accepted by the owner ("Both looks good. We can procceed as usual"), with every reading in `round-2/g.md` and `round-2/g2.md` standing.
**Files.** `system.css` holds every token and component rule. Every golden inlines it verbatim as its first `<style>` block (asserted byte for byte), so the build copies one stylesheet. A golden that needs a state-only rule (a fade, a measured height, the popover's place) carries it in a second, short `<style>` marked "Golden only".

## The idea in one paragraph
The receipt is one object everywhere. On desktop it is a frosted glass card beside the working. On a phone the same card is docked at the bottom as a strip that carries the Total, and Splits lifts it up as a sheet, so the phone opens on the inputs and the answer is never more than one tap away. The page is layered slate with one indigo accent, and indigo means one thing, chosen or proven, plus the one solid Copy summary button. Nothing glows. Everything around the receipt stays quiet so the card does the talking.

**Design read.** A one-job utility for the person who paid, at a Malaysian restaurant table, in a layered slate console language with one frosted receipt, built with native CSS, system fonts and Phosphor icons.
**Dials.** Variance 5 (money columns must line up), motion 4 (one sweep across the card on load, the sheet lifts, nothing loops), density 5 (a calm form beside a dense receipt).

## Skills loaded and what transferred
| Skill | Transferred | Not transferred, and why |
|---|---|---|
| `taste-skill:taste-skill` | Design read and dials. One accent locked to one meaning. One shape rule, written down. Button and form contrast checks. Labels above fields, errors below, no placeholder as label. Every state designed (empty, error, blocked, success, failure, disabled). Pressed state as a 1 px shift. Motion only where it answers something, off under reduced motion. Glass with a solid fallback for reduced transparency. Zero long dashes. No decorative dots, eyebrows, all caps labels or section numbers. Phosphor icons only, never hand drawn. No pure black or white. A written z-index order for the layers. | React, Next, Tailwind, Motion, GSAP and web fonts (the stack allows none). Real images and the landing page hero rules (this is a utility, not a landing page). A light mode (one dark theme by the owner's choice, a theme switcher is a non-goal). |
| `frontend-design:frontend-design` | Grounded in the subject (a receipt that proves itself). One memorable element, the glass receipt, everything else quiet. Plain copy that says what happens ("Copy summary", "Start new bill", "Check service charge"). Empty and blocked states that say what to do next. Screenshot critique at every width. | A distinctive typeface (system fonts only). |

## Colour roles
All colours live on `:root`. Components use them only through `var()`.

| Role | Token | Value | Where it is used |
|---|---|---|---|
| Deepest layer | `--l0` | `#0B0E13` | The tab icon background only |
| Top bar, item frame well | `--l1` | `#10141B` | The top bar, the item frame |
| Page | `--l2` | `#151A23` | The page field behind everything |
| Dialog | `--l3` | `#1B212B` | M1, P1 |
| Spare layer | `--l4` | `#232A36` | Kept from g2, not used by any golden |
| Raised | `--l5` | `#2D3545` | A P1 choice on hover, the sheet's grab, a disabled button's border |
| Inset field | `--field` | `#0E1219` | Every input, the Split switch track |
| Divider | `--line` | white at 8% | Hairlines between blocks and between items, the top bar's bottom edge |
| Frame edge | `--line-frame` | white at 14% | The item frame's edge |
| Control border | `--line-strong` | `#6E7891` | Every control's border on the page and in dialogs, the unchosen radio ring |
| Control border on glass | `--line-glass` | `#7A84A0` | The spare sen chip, Pick again, the strip's Splits button |
| Hover fill | `--hover` | `#E8EBF2` at 7% | Hover on ghost buttons, icon buttons and chips |
| Text | `--text` | `#E8EBF2` | All main text |
| Muted text | `--text-muted` | `#A7AFBF` | Labels, hints, section summaries, bill lines, working lines, units, placeholders, untapped people, quiet icons |
| Disabled text | `--text-faint` | `#5F6878` | Disabled controls only (exempt from contrast, WCAG 1.4.3) |
| Accent fill | `--accent` | `#5059DA` | Copy summary only |
| Accent fill hover | `--accent-hover` | `#434BC6` | Copy summary on hover |
| Accent ink | `--accent-ink` | `#A3AAFF` | The mark, the Adds up to figure, a check on a chosen person or pill, the chosen radio dot, the status tick, the S6 icon |
| Accent line | `--accent-line` | `#7C85F7` | The edge of a chosen person, the chosen mode, a chosen pill |
| Accent tint | `--accent-tint` | indigo at 16% | The fill of a chosen person, mode or pill |
| Text on accent | `--on-accent` | `#F7F8FF` | Copy summary's label and icon |
| Danger fill | `--danger` | `#C4313C` | Start new bill only |
| Danger fill hover | `--danger-hover` | `#AA2731` | Start new bill on hover |
| Text on danger | `--on-danger` | `#FFF5F5` | Start new bill's label |
| Error | `--error-ink` | `#FF8A8F` | Field errors, the error edge, the folded Check marker, the copy failure icon |
| Warning | `--warn-ink` | `#F2C063` | The S3 marker and icons, the S5 icon |
| Warning band | `--warn-bg` | `#2A2414` | The S5 note |
| Note band | `--info-bg` | `#1E2140` | The S6 note |
| Focus | `--focus` | `#A3AAFF` | The one focus ring |
| Scrim | `--scrim` | `rgba(4, 6, 10, 0.72)` | Behind M1 and the Splits sheet |
| Light scrim | `--scrim-light` | `rgba(4, 6, 10, 0.4)` | Behind P1 |
| Glass layers | `--glass-hi`, `--glass-mid`, `--glass-lo` | `rgba(200, 206, 255, 0.10)`, `rgba(150, 158, 235, 0.04)`, `rgba(8, 10, 14, 0.34)` | The glass gradient, top left to bottom right |
| Glass base | `--glass-base` | `rgba(27, 33, 43, 0.50)` | The card on desktop, over the still page |
| Dense glass | `--glass-dense` | `rgba(27, 33, 43, 0.92)` | The strip and the sheet, over content that moves |
| Solid glass | `--glass-solid` | `#1D2330` | The fallback with reduced transparency or without backdrop-filter |
| Glass edge | `--glass-edge` | indigo `#A3AAFF` at 30% | The receipt's hairline edge |
| Glass shine | `--glass-shine` | `rgba(232, 235, 255, 0.18)` | The receipt's top highlight |
| Receipt rule | `--hair` | indigo `#A3AAFF` at 42% | The dashed rule and the proof rule |
| Sheen | `--sheen-a`, `--sheen-b`, `--sheen-c` | `#5059DA`, `#7C85F7`, `#C9CDFF` | The 3 px top edge of the receipt and the seal gradient |
| Lit total | `--total-ink` | `#F4F5FF` | The Total figure on the card, strip and sheet |

### Tokens and rules not in g2, with the reason
| Change | Reason |
|---|---|
| `--strip-h` defaults to `111px` below 1024 px and `0px` from 1024 px (g2 had `0px`, then set the real height by script) | A golden has no script. 111 px is the strip's height with its usual content (the Total and two buttons), measured in g2 at 390 and 360. A golden whose strip is taller sets its own value in its golden style (108 with a one-line message, 128 for S3, 153 for the copy failure). The build keeps g2's way, it measures the strip and sets the variable |
| The "static stand-ins" section at the end of `system.css` (`.backdrop`, `.backdrop.light`, `.backdrop.under-sheet`, and the `[open]:not(:modal)` rules) | A golden cannot call `showModal()`. It opens a dialog with the `open` attribute, puts `inert` on what sits behind, and draws each backdrop as a div. The rules match only a dialog that is open but not modal, so the build's own dialogs never see them. They also write down the layer order (below) |
| `--t-proto` removed | It styled the Prototype states tab, which is not part of the design |
| The Prototype states tab and panel rules removed | Not part of the design |

No colour, size or space value was added or changed. Every golden renders pixel for pixel as g2 at the same state and width, apart from the ruling on S6 (see `SELF-CRITIQUE.md`).

## Contrast (WCAG AA)
Recomputed by `checks/check_final.py` from the tokens in `system.css`, with WCAG relative luminance. Glass is composited over what sits behind it at its lightest corner (the top left highlight), so every ratio is the worst case for that surface.

### Text
| Text | On | Ratio | Need |
|---|---|---|---|
| Body text | The page | 14.62 | 4.5 |
| Body text | A field | 15.72 | 4.5 |
| Body text | The top bar and the item frame | 15.46 | 4.5 |
| Body text | A dialog | 13.55 | 4.5 |
| Body text | A P1 choice on hover | 10.31 | 4.5 |
| Muted text (labels, hint, summary) | The page | 7.91 | 4.5 |
| Muted text (placeholder, RM, %) | A field | 8.51 | 4.5 |
| Muted text (untapped person) | The item frame | 8.37 | 4.5 |
| Muted text | A dialog | 7.33 | 4.5 |
| Body text | The indigo tint, a tapped person in the frame | 12.72 | 4.5 |
| Body text | The indigo tint, the chosen mode | 12.99 | 4.5 |
| Body text | The indigo tint, a chosen pill in P1 | 10.97 | 4.5 |
| Copy summary label | Its indigo fill, its hover | 5.24, 6.48 | 4.5 |
| Start new bill label | Its red fill, its hover | 5.10, 6.45 | 4.5 |
| Error text (rate error, Check marker) | The page | 7.71 | 4.5 |
| Error text (price error) | The item frame | 8.16 | 4.5 |
| S5 text | Its warning band | 12.93 | 4.5 |
| S6 text | Its note band | 13.07 | 4.5 |
| Card, the Total figure | Card glass | 12.31 | 4.5 |
| Card, body text (names, Total label, Adds up to) | Card glass | 11.19 | 4.5 |
| Card, muted text (bill lines, working, sen left over) | Card glass | 6.06 | 4.5 |
| Card, indigo Adds up to figure | Card glass | 6.20 | 4.5 |
| Card, chip label | The chip's fill on card glass | 13.34 | 4.5 |
| Strip, the Total figure | Strip glass | 11.85 | 4.5 |
| Strip, body text (Total label, status, messages) | Strip glass, over the page, over a field | 10.78, 10.87 | 4.5 |
| Strip, Splits label | The button's fill on strip glass | 13.37 | 4.5 |
| Strip, worst case, body text | Strip glass over an unblurred white line | 8.58 | 4.5 |
| Sheet, the Total figure | Sheet glass over the scrim | 12.03 | 4.5 |
| Sheet, body text, muted text, indigo figure | Sheet glass over the scrim | 10.94, 5.92, 6.06 | 4.5 |
| Sheet, worst case, muted text | Sheet glass over an unblurred white line | 5.57 | 4.5 |
| Solid fallback card, muted text, indigo figure | `--glass-solid` | 7.13, 7.30 | 4.5 |
| Disabled text | Any | not computed | Exempt (inactive control, WCAG 1.4.3) |

### Controls and graphics (WCAG 1.4.11, 3 to 1)
| Element | Against | Ratio | Need |
|---|---|---|---|
| Control border | The page, a field, the top bar and frame, a dialog | 3.95, 4.25, 4.18, 3.66 | 3 |
| Unchosen radio ring in P1 | A dialog | 3.66 | 3 |
| Indigo edge, tapped person, chosen mode, chosen pill | The frame, a field, a dialog | 5.76, 5.86, 5.05 | 3 |
| Indigo check on a tapped person | The tint in the frame | 7.05 | 3 |
| Indigo radio dot and pill check | A dialog | 7.51 | 3 |
| Focus ring | The page, the top bar and frame, a dialog | 8.10, 8.57, 7.51 | 3 |
| Focus ring | Card glass, strip glass | 6.20, 5.97 | 3 |
| Error edge on a field | A field | 8.29 | 3 |
| S3 amber marker | The item frame | 10.98 | 3 |
| S3 icon | Card glass, strip glass | 7.95, 7.65 | 3 |
| S4 failure icon | Card glass | 5.90 | 3 |
| S5 icon, S6 icon, S6 dismiss X | Their bands | 9.18, 7.24, 7.07 | 3 |
| Chip border (spare sen, Pick again) | Card glass, sheet glass, solid fallback | 3.58, 3.50, 4.22 | 3 |
| Splits button border | Strip glass over the page, over a field | 3.45, 3.48 | 3 |
| Sheet Close X | Sheet glass | 5.92 | 3 |

### Surfaces against their backdrop (recorded, not a WCAG requirement)
| Surface | Against | Ratio |
|---|---|---|
| A dialog (M1) | The scrimmed page | 1.21 |
| A dialog's 1 px edge (white at 10% over `--l3`) | The scrimmed page | 1.64 |
| P1 on desktop | The light scrim over the page | 1.16 |
| P1 on a phone | The light scrim over the Splits sheet | 1.01 |
| The sheet's grab | Sheet glass | 1.06 |

A dialog's edge is not information a person needs to use it, so WCAG 1.4.11 does not ask for 3 to 1 here. Every control inside meets its own ratio above. The dialogs separate from what is behind them by the scrim, a 1 px light edge (white at 10%) and their shadow, as in g2. On a phone P1 sits over the sheet almost at the same lightness, so its top edge and its rounded corners carry the separation. Flagged in `SELF-CRITIQUE.md` as a look the owner accepted in g2, not a fault.

## Type
Two system stacks. Words use `ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` (`--font-ui`). Every money figure, unit and working line uses `ui-monospace, "Cascadia Mono", "SF Mono", Menlo, Consolas, "Roboto Mono", monospace` (`--font-num`). The body sets `font-variant-numeric: tabular-nums lining-nums`, so money columns line up. Money is always written `RM 38.87`, with a thousands comma from 1,000.

| Token | Size / line | Weight | Used for |
|---|---|---|---|
| `--t-total` | 38 to 48 (11vw) / 1.1 | 600, tracking -0.03em | The Total on the card and in the sheet ("RM" at 0.42 of it, no tracking, in body text) |
| `--t-strip` | 24 / 30 | 600, tracking -0.02em | The Total on the strip ("RM" at 14) |
| `--t-brand` | 19 / 24 | 700, tracking -0.01em | The wordmark "Splity Tab" |
| `--t-title` | 18 / 24 | 700 | The M1 title |
| `--t-share` | 18 / 24 | 600 | Each person's split, the Adds up to figure |
| `--t-body` | 16 / 24 | 400 | Body, every input (16 px stops iOS zoom), the empty and blocked messages, large buttons, the P1 title (700) and choices (600) |
| `--t-control` | 15 / 20 | 600 | Buttons, block headings, section names, the Split switch, bill lines (400, 22 px line) |
| `--t-small` | 14 / 20 | 400 or 600 | Labels (600), hints (400), section summaries (400, the Check marker 600), person toggles and chips (600), errors and status (600), notes (400), the Splits heading and Total label (600) |
| `--t-micro` | 13 / 18 | 400 | The working under a split and under Adds up to, "items + charges" |

Three weights exist, 400, 600 and 700.

## Spacing
4 px base, `--s1` 4 to `--s16` 64. Touch targets are `--tap` 44 px.

| Token | px | Main uses |
|---|---|---|
| `--s1` | 4 | Note padding, the Total's gap to its label, the working's top on a phone, a section's top padding |
| `--s2` | 8 | Gaps in the top bar, between people, between toggles, label to field, field to error, button icon gap, the strip's row gap |
| `--s3` | 12 | Field text padding, item padding, the gap under the Splits heading, between splits, the Split row's top on a phone, status margin |
| `--s4` | 16 | Page gutters on a phone, button side padding, the Total's bottom padding, the proof rule's spacing, the spare line's margin |
| `--s5` | 20 | Gap between blocks on a phone, the dashed rule's top margin, Copy summary's top margin, dialog padding, sheet side padding |
| `--s6` | 24 | M1 padding and its actions' margin, the card's padding on desktop, the working's bottom padding |
| `--s7` | 28 | The desktop charge hint's drop (a label's height plus its gap), the stage's bottom padding |
| `--s8` | 32 | The least desktop column gap |
| `--s12` | 48 | Desktop side padding |
| `--s16` | 64 | The widest desktop column gap |

Derived values that sit off the scale, each tied to a size rather than to rhythm, all as g2 renders them. 2 px (gap between the choices in P1, the strip top's row gap, the gap between a rate and its %). 6 px (the bill lines' gap, an error's icon gap, a toggle's icon gap, the money input's left padding, the phone item row's gap). 10 px (the mark to wordmark gap, a solo heading's bottom margin, the money unit's left padding and the input's right padding, the proof row's column gap, the strip's top padding, the stage's side padding). 14 px (the chip's side padding, the frame's left padding on desktop). 46 px (a field's height, 44 for the input plus its border). 52 px (`--sec-h`, a folded header row). 104 and 128 px (the price field on a phone and from 600 px).

## Shape
| Radius | Token | Where |
|---|---|---|
| 22 | `--r-card` | The receipt card, the strip and the Splits sheet (top corners only on the strip and sheet) |
| 16 | `--r-surface` | Dialogs, P1 (top corners only on a phone), the notes, the item frame |
| 10 | `--r-ctl` | Fields, buttons, icon buttons, the Split switch's frame, a header row's focus ring, a P1 choice |
| Full pill | `--r-pill` | Choices, person toggles, the spare sen chip, Pick again, the picker's pills |

Borders are 1 px everywhere. An error field adds a 1 px inset shadow in the error colour, so the edge reads 2 px and nothing moves.

## Elevation
| Token | Value | Where |
|---|---|---|
| `--shadow-card` | `0 40px 80px -32px` and `0 14px 28px -14px`, near black | The card |
| `--shadow-pop` | `0 30px 70px -24px`, near black | Dialogs and P1 |
| `--shadow-up` | `0 -14px 32px -10px`, near black | The strip, lifting it off the page |

Shadows are tinted to the page (`rgba(4, 6, 10, ...)`), never pure black. Nothing glows.

## The glass, and its solid fallback
The receipt's one material. A 155 degree gradient (`--glass-hi` to `--glass-mid` at 40% to `--glass-lo`) over a base, `backdrop-filter: blur(24px) saturate(140%)`, a 1 px indigo edge (`--glass-edge`), a 1 px top highlight (`--glass-shine`), a 1 px inner indigo ring at 6%, and the card shadow. The card uses `--glass-base` (50%) over the still page. The strip and the sheet use `--glass-dense` (92%) because content moves under them. A 3 px indigo sheen (`.foil`) runs along the top edge. It is the only glass, and it is never used for dialogs, notes or controls.

**Fallback.** With `prefers-reduced-transparency: reduce`, or where `backdrop-filter` is not supported, every glass surface is a solid `--glass-solid` `#1D2330` with no blur, and the card's sheen is removed. The ratios on the fallback are in the table above.

## Motion
Only where it answers something, and only inside `@media (prefers-reduced-motion: no-preference)`. With reduced motion every change is instant and nothing moves by itself.

| What | How |
|---|---|
| Hover and press | Background, border and text colour over 120 ms ease. Pressed is an instant 1 px shift down |
| The receipt's arrival | On load the sheen sweeps the 3 px top edge (1.8 s) and a faint light crosses the card once (1.4 s). Never loops |
| A folded section opening (phone) | A 200 ms height reveal, the caret turns 180 degrees in 200 ms. Folding is instant |
| The item frame's fades | Opacity over 160 ms |
| The Splits sheet | Lifts 48 px into place in 240 ms |
| P1 | Rises 8 px and fades in, 200 ms |
| M1 | Fades in from 98% scale, 160 ms |

## Layout and breakpoints
| Width | Layout |
|---|---|
| Under 600 px | Phone. The working is one column with 16 px gutters, in the order People, Charges, Split, then Items or Subtotal. People and Charges are folded header rows. The strip is fixed at the bottom. The item frame is at most the screen less the strip and 88 px, and scrolls inside itself |
| 600 to 1023 px | The phone layout in a centred column of at most 640 px. The price field grows to 128 px. P1 and the sheet are bottom sheets of at most 560 px. M1's buttons sit in a row, right aligned |
| 1024 px and up | The card beside the working. Top bar 64 px. The layout is at most 1280 px with 48 px sides. Columns are `minmax(320px, 1fr)` for the card and `minmax(440px, 560px)` for the working, with a gap of 5vw between 32 and 64 px. The card is at most 460 px, centred in its column. People and Charges are always open with their own headings. Items fill the rest of the column in their frame. **The page never scrolls.** Each column scrolls inside itself if it must, and in every golden neither does |

### Layer order
| Layer | z-index |
|---|---|
| The item frame's fades | 1, inside the frame |
| The strip | 20 |
| The scrim (M1, under the Splits sheet) | 40, the build's top layer |
| The Splits sheet | 41, the build's top layer |
| The light scrim over the sheet (P1 on a phone) | 42, the build's top layer |
| P1 and M1 | 43, the build's top layer |

## Focus
One ring, 2 px `--focus` with a 2 px offset, on every control (`:focus-visible`). Fields draw it on their wrapper. A remove button inside a field draws it inset (-3 px). The Split switch draws it inset on the focused half (-5 px). A folded header row draws it 8 px wider than the row on each side, so it clears the text that sits on the column edge. An error field keeps its red edge and gains the ring.

## Icons
Phosphor Icons (MIT), regular weight except check (bold), inlined once per page as `<symbol>`s and used with `<use>`. X, plus, copy, check, caret, shuffle, warning, warning circle, receipt and seal check. Every symbol line is g2's line, byte for byte (asserted). Never hand drawn. Every icon is `aria-hidden` and its control carries the name. Sizes are 18 px in buttons and fields, 16 px in chips, status and the Check marker, 14 px in toggles and pills, 20 px in notes, 22 px for the S3 message, 24 px for the seal, 28 px for the empty receipt.

**The mark.** `docs/brand/mark.svg`'s geometry, recoloured `--accent-ink`, 28 px, in one inline `<svg class="mark">` per page beside the live wordmark "Splity Tab" (ruling 3). The tab icon is the same mark as a data URI in each page's `<head>`. The redrawn logo swaps both, the inline svg and the data URI.

## Component inventory
Class names are the ones in `system.css`.

### Buttons
| Kind | Default | Hover | Pressed | Focus | Disabled |
|---|---|---|---|---|---|
| Primary `.btn.btn-primary` (Copy summary only) | Indigo fill, `--on-accent` label and icon, 15/20 600, 44 px tall | `--accent-hover` | 1 px down | Ring | Faint label and icon, `--l5` border, no fill (the strip's Copy summary while there is nothing to copy) |
| Danger `.btn.btn-danger` (Start new bill only) | Red fill, `--on-danger` label | `--danger-hover` | 1 px down | Ring | Not used |
| Ghost `.btn.btn-ghost` | Clear, `--line-strong` border, text label, muted icon | `--hover` fill | 1 px down | Ring | Faint label and icon, `--l5` border, `not-allowed` (Add person at 12) |
| Block `.btn-block` | Full width, 48 px, 16 px label (Copy summary on the card) | as its kind | | | |
| Large `.btn-lg` | 48 px, 20 px sides, 16 px label (M1's two buttons) | as its kind | | | |
| On the strip `.strip-acts .btn` | 12 px sides. The ghost gets a dark fill at 50% and the glass border | as its kind | | | |

### Icon button `.icon-btn`
44 x 44, muted 18 px icon, 10 px radius. Hover turns the icon to text colour on the hover fill. Disabled is faint, no hover (Remove at two people). Used for Remove (inside a person field, the right corners only), Remove item, Close (sheet, P1) and Dismiss note.

### Chip `.chip-btn`
On the glass only. 44 px tall, full pill, 14 px sides, `--line-glass` border, a dark fill at 45%, 14/20 600 label, 16 px muted icon. The spare sen chip shows the rule ("Top of the list", "One person, Ben", "At random") with a caret. Pick again shows the shuffle icon first.

### Field `.field` with `input`
46 px tall (a 44 px input inside a 1 px border), `--field` fill, `--line-strong` border, 10 px radius, 16/24 text, 12 px side padding, muted placeholder. Focus draws the ring on the wrapper. Error adds `.is-bad` (red edge plus inset), `aria-invalid="true"`, and the message 8 px below in 14/20 600 error red with a 16 px warning circle.

### Money field `.field.money`
"RM" first (14 px monospace, muted, 10 px from the left, `aria-hidden`), then the figure, monospace, right aligned, 6 px left and 10 px right padding. The accessible name ends "in RM". Item prices are 104 px wide on a phone and 128 px from 600 px. The Subtotal field is at most 240 px.

### Percent field `.field.pct`
The figure right aligned, then "%" 2 px after it and 12 px from the right edge. Label above in 14/20 600 muted. Both point to the hint with `aria-describedby`, and gain their error's id only while it shows.

### Person row `li.field.person`
A name input (Person N name, at most 20 characters, placeholder "Person N") joined to a remove icon button ("Remove <name>"). The grid is `auto-fill, minmax(148px, 1fr)`, 8 px gaps, two across on a phone and three on desktop. Remove is disabled at two people, Add person at twelve.

### Person toggle `.tap` (the person chip on an item)
A `button` with `aria-pressed`, full pill, 44 px tall, 16 px sides, 14/20 600. Off is clear with a `--line-strong` border and a muted name. On is the indigo tint with an indigo edge, the name in text colour and a 14 px indigo check (12 px left padding). The toggles for one item sit in a `role="group"` named "Who had <item>", 8 px apart, wrapping.

### Split switch `.mode-sw`
Two radios "Even" and "By item" in a `role="group"` named by the "Split" heading. Equal halves, 44 px, `--field` track, `--line-strong` frame and divider, 10 px radius. The chosen half is the indigo tint with an inset indigo edge and text colour, the other half muted. It sits right of the heading in one row, at most 280 px wide.

### Section header row `.sec-btn` (below 1024 px)
An `h2` holding one `button` across the whole row, 52 px tall, `aria-expanded` and `aria-controls`. The button is named by its section name (`aria-labelledby` on `.sec-name`) and described by its summary (`aria-describedby` on `.sec-sum`), so the name stays People or Charges while the summary changes. The name on the left (15/20 600), the summary right aligned beside the caret (14/20 400 muted, one line, ellipsis as a last resort), the 18 px caret, which turns when open. The summary hides while open and keeps its place. With an error inside and folded, the summary turns to the error colour at 600 with a 16 px warning circle and reads "Check service charge", "Check SST" or "Check both rates". The section's own `h2` is hidden on a phone, and the header row is the heading.

### Item row `li.item` and the item frame `.frame-wrap`
The frame is an `--l1` well, 16 px radius, `--line-frame` edge, that scrolls inside itself with a thin scrollbar. A 36 px fade at the top or bottom shows there is more that way (`data-up`, `data-down`, set by the build). Each item is a grid of name, price and remove (8 px gaps, 6 on a phone), then its toggles 8 px below, 12 px top and bottom padding, a hairline above every item but the first. An item nobody had gets a 3 px amber bar on its left edge (`.needs`). A price error spans the name and price columns, right aligned.

### Receipt `.rbody` (in the card or the sheet)
Top to bottom. "Total" (14/20 600) and the figure. The bill lines (Subtotal, Service N%, SST N%) as a `dl`, muted label and monospace figure. A dashed indigo rule. "Splits" (14/20 600 muted) with "items + charges" on the right in By item. One row per person, the name (600) and the split (18/24 monospace 600), with the working "items + charges" under it in By item. The proof row, a solid indigo hairline above it, the seal, "Adds up to" and the Total again in indigo, with the working total under it in By item. The spare sen line, when there are spare sen, "N sen left over" with the chip (and Pick again for At random). Copy summary, full width. The status line under it.

When there is nothing to work out, the Total label stays and a 28 px receipt icon with one message replaces the rest. When an item still needs a person, the bill lines stay and a 22 px amber warning with one message replaces the splits and Copy summary.

### Receipt card `.glass.card` (1024 px and up)
At most 460 px wide, 24 px padding, 22 px radius, the foil along its top, centred in its column 20 px below the top bar.

### Strip `.strip.glass.dense` (below 1024 px)
Fixed to the bottom, full width, 22 px top corners, dense glass, the foil on top, `--shadow-up`. Inside, at most 608 px, 10 px top and 12 px bottom padding. The first row is "Total" with the figure (24/30), or the message when there are no splits, with the status to its right when there is room and on its own line when not. The second row is "Splits" with an upward caret (ghost) and Copy summary (primary), 1 to 1.3. Copy summary is disabled, not hidden, when there is nothing to copy, so the strip keeps its shape.

### Splits sheet `.sheet-dlg` with `.glass.dense.sheet` (P2, below 1024 px)
The receipt card lifted from the strip. A bottom sheet at most 560 px wide and 92% of the screen tall, 22 px top corners, the foil, a 48 px top row with the grab and Close, then the receipt with 20 px sides, scrolling inside itself. Named "Splits". Esc, the backdrop and Close shut it and focus returns to Splits.

### Popover `.pop` (P1)
`--l3`, 16 px radius, 20 px padding, `--shadow-pop`. On desktop 340 px wide, beside the card, its bottom level with the chip's bottom. Below 1024 px a bottom sheet at most 560 px wide over the Splits sheet, which pads its own bottom by P1's height and 16 px so the splits stay in view. Inside, "Spare sen" (16/24 700) with Close, the count ("1 sen left over"), and three choices (48 px rows, a 20 px radio ring, the chosen dot indigo). One person shows the picker of people with a split above zero, as pills. At random shows Pick again.

### Dialog `.modal` (M1)
`min(400px, 100% - 32px)` wide, 24 px padding, `--l3`, 16 px radius. Title 18/24 700, body 16/24 muted 8 px below, actions 24 px below. On a phone the two 48 px buttons stack full width, Start new bill first. From 600 px they sit in a row, right aligned.

### Banner `.note` (S5, S6)
Under the top bar's first row on a phone (a second row of the bar), centred in the top bar on desktop. 48 px tall on a phone and 44 on desktop, 16 px radius, 16 px left padding, a 20 px icon, 14/20 text, `role="status"`. S5 is the warning band with an amber edge and no dismiss. S6 is the note band with an indigo edge and a 44 x 44 Dismiss note button.

### Status `p.status[role="status"]`
14/20 600 with a 16 px icon, centred 12 px under Copy summary on the card, beside the Total on the strip (on its own line when it does not fit). "Summary copied" with an indigo tick, or "Could not copy. Your browser blocked the clipboard." with a red warning circle. Empty and hidden until a copy is tried, cleared by the next change.
