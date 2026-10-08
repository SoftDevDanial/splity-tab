# Split design system

**Phase.** design (sdlc:design steps 5, 6 and 8) · **Date.** 2026-10-08 · **Source direction.** round 1, C "Working shown", with the three changes in `round-1/DECISION.md`.
**Files.** `system.css` holds every token and component rule. Every golden inlines it verbatim inside its first `<style>` block, so the build copies one stylesheet, not six.

## The idea in one paragraph
Split is a calculator that shows its working. The bill panel reads like an adding tape. Operators sit in a fixed gutter, figures sit right aligned in one column, a rule sits above the Total and a double rule sits under it. The shares table reads across (Items + Charges = Share) and down (the shares add back to the Total). The one bold element is the proof line "Adds up to", the only place the green accent appears. Everything around it stays quiet, ink on pale green-grey, one radius, no shadows.

**Design read.** A single-purpose utility web app for one person at a restaurant table, in a calculator-tape "working shown" language, built with native CSS and system fonts.
**Dials.** Variance 3 (columns must line up), motion 2 (colour changes only), density 5 (a dense but calm form).

## Skills loaded and what transferred
| Skill | Transferred | Not transferred, and why |
|---|---|---|
| `taste-skill:taste-skill` | Design read and dials. Zero long dashes. One accent locked to one job. One radius. Button and form contrast checks. CTA labels on one line. One label per intent ("New bill", "Copy summary" used once each). Labels above inputs, errors below. No placeholder as label. Every state designed (empty, error, success, disabled). Pressed state as a 1 px shift. Reduced motion respected. Copy self-audit. No decorative dots, eyebrows, middle-dot strings or section numbers. Icons from Phosphor only, never hand drawn. No pure black or white. | React, Next, Tailwind, Motion, GSAP (the brief allows no dependencies). Web fonts (system stack only). Dark mode (one light theme, a theme switcher is a non-goal). Real images and hero rules (a utility, not a landing page). |
| `frontend-design:frontend-design` | Grounded in the subject (a receipt, an adding tape). One memorable element (the proof line), everything else quiet. A clear type scale with deliberate weights. Sentence case, no all-caps labels, no labels that do not earn their place. Copy says what happens ("Start new bill", "Copy summary"). Empty and error states give direction. Screenshot critique at every width. | Choosing a distinctive typeface (the brief limits type to system fonts). |

## Colour roles
All colours live on `:root`. Components use them only through `var()`.

| Role | Token | Hex | Where it is used |
|---|---|---|---|
| Page | `--page` | `#EEF0EE` | Page background, the states sheet frames |
| Surface | `--surface` | `#FBFCFB` | The bill panel, the note banner, the dialog |
| Field | `--field` | `#FDFEFD` | Input fill, outline buttons, toggles when off, mode switch track |
| Ink | `--ink` | `#141917` | All main text, primary button fill, toggles when on, the checked mode, rules, focus ring, panel border |
| Ink hover | `--ink-hover` | `#2A302D` | Primary button fill on hover |
| Ink muted | `--ink-muted` | `#4A524E` | Hints, working lines, operators, table secondary cells, table column heads, RM and % units, placeholder, icons in outline buttons, remove icons, dialog body |
| Ink disabled | `--ink-disabled` | `#9AA19D` | Text and icon of a disabled control |
| On ink | `--on-ink` | `#F3F5F4` | Text on ink fills |
| Line | `--line` | `#C9CECB` | Hairline between items, left edge of the person remove button, disabled button border, panel bottom edge on phone |
| Line strong | `--line-strong` | `#78807C` | Borders of every control, the note border, the states sheet frames |
| Hover | `--hover` | `#E3E7E4` | Hover fill of outline controls |
| Accent | `--accent` | `#0B6B4D` | The "Adds up to" row only (check icon, label, final share) |
| Error | `--error` | `#B42318` | Amount error text and the error border, the copy failure message |
| Scrim | `--scrim` | `rgba(20, 25, 23, 0.48)` | Dialog backdrop (ink at 48%) |

### Tokens C did not have, with the reason
| Token | Reason |
|---|---|
| `--ink-disabled` | S8 needs disabled controls (Add person at 12, remove at 2). C had no disabled state. |
| `--error` | S4 needs an inline amount error and S6 a copy failure message. C had no error state. Red is used for errors only, never for actions. |
| `--scrim` | M1 needs a backdrop. C had no dialog. |
| `--ink-hover` | Not a new colour. C hardcoded `#2A302D` for the primary hover. It is now a token so no component carries a raw hex. |
| Named type, space, size and layout tokens | Not new values. They name C's numbers so the build can reuse them. Where C used an off-scale value it was moved onto the scale (see SELF-CRITIQUE.md). |

**Removed.** `--on-ink-muted` (C used it for the amount inside an item toggle, and toggles now show the name only).

## Contrast (WCAG AA)
Ratios computed with the WCAG relative luminance formula (`harness/_scratch/design-final/contrast.py`).

### Text
| Text | On | Ratio | AA need | Result |
|---|---|---|---|---|
| Ink | Page | 15.52 | 4.5 | Pass |
| Ink | Field | 17.59 | 4.5 | Pass |
| Ink | Surface | 17.29 | 4.5 | Pass |
| Ink | Hover | 14.24 | 4.5 | Pass |
| Ink muted | Page | 7.03 | 4.5 | Pass |
| Ink muted | Field | 7.96 | 4.5 | Pass |
| Ink muted | Surface | 7.83 | 4.5 | Pass |
| Ink muted | Hover | 6.45 | 4.5 | Pass |
| On ink | Ink | 16.24 | 4.5 | Pass |
| On ink | Ink hover | 12.30 | 4.5 | Pass |
| Accent | Surface | 6.33 | 4.5 | Pass |
| Error | Page | 5.74 | 4.5 | Pass |
| Error | Surface | 6.39 | 4.5 | Pass |
| Ink disabled | Page | 2.30 | none | Exempt (inactive control, WCAG 1.4.3) |
| Ink disabled | Field | 2.61 | none | Exempt (inactive control, WCAG 1.4.3) |

### Controls and graphics (WCAG 1.4.11, 3:1)
| Element | Against | Ratio | Result |
|---|---|---|---|
| Control border (line strong) | Field | 4.01 | Pass |
| Control border (line strong) | Page | 3.54 | Pass |
| Note border (line strong) | Surface | 3.94 | Pass |
| Error border | Field | 6.50 | Pass |
| Focus ring (ink) | Page, Surface, Field | 15.52, 17.29, 17.59 | Pass |
| Toggle on, checked mode, primary button (ink fill) | Page, Field | 15.52, 17.59 | Pass |
| Rules above Total, under Total, above the check row (ink) | Surface | 17.29 | Pass |
| Check icon (accent) | Surface | 6.33 | Pass |
| Dialog surface | Scrimmed page (`#858987`) | 3.45 | Pass |
| Dialog surface | Scrimmed panel (`#8C8F8E`) | 3.17 | Pass |
| Dialog border (ink) | Scrimmed page | 5.02 | Pass |
| Item hairline (line) | Page | 1.39 | Decorative. Each item is already bounded by its own bordered fields, so the hairline carries no meaning on its own. |

## Type
One family, the system UI stack `system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`. Every figure uses `font-variant-numeric: tabular-nums lining-nums` (set on `body`) so money columns line up. Money is always written `RM 38.87`.

| Token | Size / line | Weight | Used for |
|---|---|---|---|
| `--text-total` | 26 / 32 | 700 | The Total amount |
| `--text-brand` | 22 / 28 | 700, tracking -0.01em | Wordmark "Split", states sheet title |
| `--text-heading` | 18 / 24 | 700 | Block headings, panel headings, Total label, each share, dialog title |
| `--text-body` | 16 / 24 | 400 | Body, every input (16 px stops iOS zoom), summary rows, result messages, note text, dialog body, large buttons |
| `--text-control` | 15 / 20 | 600 | Buttons, toggles, mode labels, field labels, names in the shares table, working lines (400) |
| `--text-small` | 14 / 20 | 400 or 600 | Hint (400), error (600), status (600), Items and Charges cells (400) |
| `--text-caption` | 13 / 18 | 600 | Shares table column heads only |

Only three weights exist (400, 600, 700). C used 650, which Segoe UI renders as 700 and other platforms render differently, so it is now 700 everywhere.

## Spacing
4 px base. Tokens `--space-1` to `--space-16`.

| Token | px | Main uses |
|---|---|---|
| `--space-1` | 4 | Summary row padding, money input left padding, table head bottom padding, gap after a table-head operator |
| `--space-2` | 8 | Grid and toggle gaps, label to field, field to hint or error, money unit padding, table cell padding, status margin, dialog text margin |
| `--space-3` | 12 | Header top padding (phone), heading to content, input text padding, toggle side padding, Total rule spacing, table footer padding |
| `--space-4` | 16 | Item padding, note margin and left padding, button side padding |
| `--space-5` | 20 | Panel top padding (phone), header top padding (600 to 1023) |
| `--space-6` | 24 | Gap between blocks, panel bottom padding, Copy summary margin, dialog padding, desktop panel offset |
| `--space-8` | 32 | Panel margin above (phone), gap between Bill summary and Shares, desktop header top padding |
| `--space-10` | 40 | Page bottom padding (phone) |
| `--space-16` | 64 | Desktop column gap, desktop bottom padding |

A few derived values sit off the scale, each tied to a size rather than to rhythm. They are the 2 px gap between a percent figure and its `%`, the -1 px overlap that puts the person remove button over the field border, the -3 px and 3 px / 5 px focus insets, and the 14 px top offset that centres the 18 px check on its label.

## Shape, borders and rules
- **Radius.** 6 px on every control, the panel (600 px and up), the note and the dialog. Nothing else is rounded.
- **Borders.** 1 px. Controls use `--line-strong`. The panel on wider screens and the dialog use `--ink`.
- **Rules.** The panel top on phone is a 2 px ink rule (`--rule-panel`). A 1 px ink rule sits above the Total and above the check row, starting at the label column so the operator gutter stays open. The Total amount sits on a 3 px double rule (`--rule-total`), which belongs to the Total alone.
- **Elevation.** None. No shadows anywhere. The dialog separates from the page by the scrim and its ink border.

## Focus ring
One ring everywhere, 2 px solid ink with a 2 px offset (`:focus-visible`).
- Text, money and percent fields draw the ring on the field wrapper, not the bare input.
- The person remove button draws it inset (-3 px offset) so it stays inside the field.
- The mode switch draws the outer ring on the whole switch and an inset double ring on the focused half (3 px field band, then 2 px ink band), so it shows on both the ink half and the light half.
- An error field keeps its red border and gains the ink ring.

## Motion
- Only background and text colour change, over 120 ms ease, on buttons, toggles, icon buttons and mode labels.
- The pressed state is an instant 1 px downward shift (not animated).
- **Reduced motion.** Transitions exist only inside the `prefers-reduced-motion` `no-preference` media query. With reduced motion on, every change is instant. Nothing on the page moves by itself.

## Layout
| Width | Layout |
|---|---|
| Under 600 px | One column. 16 px gutters. The bill panel runs full bleed after the Charges block, with a 2 px ink rule on top. |
| 600 to 1023 px | One centred column, 560 px max. The bill panel becomes a bordered card (1 px ink, 6 px radius, 24 px padding). Item price field grows to 120 px. |
| 1024 px and up | Two columns inside 1104 px max with 32 px gutters. Inputs on the left (fluid, 556 px at 1280), the bill panel on the right (420 px), 64 px apart. The panel is sticky at 24 px from the top and its top lines up with the People block. |

The **cell grid** (`.cells`, `repeat(auto-fill, minmax(140px, 1fr))`, 8 px gap) is shared by People, Subtotal and Charges so their columns line up. It gives two columns at 360 and 390 and three at 1280.

The **app root** (`.app`) wraps the header and main. While a dialog is open it is clipped to the viewport height, so the page behind the dialog does not scroll and a full-page render of the dialog equals the viewport.

## Icons
Phosphor Icons (MIT), regular weight, inlined as SVG paths. X (remove, dismiss), Plus (add), Copy (Copy summary) and Check bold (check row). Never hand drawn. Every icon is `aria-hidden` and its button carries the accessible name.

## Component inventory
Class names are the ones in `system.css`.

### Button
| Variant | Default | Hover | Pressed | Focus | Disabled |
|---|---|---|---|---|---|
| Primary `.btn.btn-primary` | Ink fill, on-ink text, 15/20 600, 44 px min height | Ink hover fill | 1 px down | Ring | Not used in any screen (Copy summary is replaced, never disabled) |
| Primary large `.btn-large` (+ `.btn-block`) | 48 px, 16/24 text. Copy summary is full width. Dialog buttons are large. | same | same | same | n/a |
| Secondary (outline) `.btn.btn-outline` | Field fill, 1 px line strong, ink text, 18 px icon in ink muted | Hover fill | 1 px down | Ring | Transparent fill, line border, ink disabled text and icon, no hover, no shift, `not-allowed` cursor, `disabled` attribute (S8 Add person) |
| Icon button `.icon-btn` | 44 x 44, ink muted 20 px icon | Hover fill, icon turns ink | 1 px down | Ring | Ink disabled icon, no hover (S8 remove at 2 people) |

### Text input `.field` + `input`
| State | Look |
|---|---|
| Default | 44 px tall, field fill, 1 px line strong, 6 px radius, 16/24 ink text, 12 px side padding |
| Focus | Ink ring on the wrapper, 2 px offset |
| Error | `aria-invalid="true"` on the input. Border turns error red and thickens to 2 px through an inset shadow, so nothing moves. The message sits 8 px below in 14/20 600 error red and is linked with `aria-describedby`. |

### Money input `.field.money`
"RM" unit first (ink muted, 8 px from the left edge, `aria-hidden`), then the figure, right aligned, 8 px from the right edge. The accessible name ends "in RM". Item price fields are 96 px wide on phone (fits up to 999.99) and 120 px from 600 px. The subtotal field takes one grid cell. Default, focus and error as the text input.

### Percent input `.field.percent`
Figure right aligned, then "%" (ink muted, `aria-hidden`) 2 px after it and 12 px from the right edge. Label above in 15/20 600, 8 px gap. The accessible name ends "in percent". Both charge inputs point to the hint with `aria-describedby`. Each takes one grid cell. Default, focus and error as the text input.

### Person toggle `.tap` (`button` with `aria-pressed`)
| State | Look |
|---|---|
| Off (`aria-pressed="false"`) | Field fill, 1 px line strong, ink name, 44 px tall, 12 px side padding, 15/20 600 |
| On (`aria-pressed="true"`) | Ink fill and border, on-ink name |
| Hover (off) | Hover fill |
| Focus | Ink ring, 2 px offset (visible against the page on both states) |
| Pressed | 1 px down |
The toggles for one item sit in a `role="group"` named "Who had <item name>", 8 px apart, wrapping as needed. They show the name only.

### Mode switch `fieldset.mode`
Two radio inputs with labels "Even" and "By item" in a `fieldset` with a visually hidden `legend` "Split mode". Equal halves, 44 px tall, 1 px line strong outline and divider. Checked half is ink with on-ink text. Unchecked half is field fill, hover fill on hover. Focus draws the outer ring plus the inset double ring on the focused half. Arrow keys move between the two (native radio behaviour).

### Person row `li.field.person`
A text input (accessible name "Person N name", max 20 characters) joined to a 44 x 44 remove button ("Remove <name>") that overlaps the field's right border, with a lighter `--line` divider on its left. At 2 people both remove buttons are disabled. "Add person" is an outline button that fills the next grid cell. At 12 people it is disabled.

### Item row `li.item`
Grid of name field (fluid, accessible name "Item N name", max 40 characters), price field (money input) and remove button ("Remove <item name>"), 8 px gaps. The toggle group sits 8 px below. Items are separated by 16 px padding and a 1 px `--line` hairline (none above the first). An amount error under a price spans the name and price columns and is right aligned, so it ends under the price field.

### Bill panel `.tape`
Bill summary (a `dl`) then Shares (a `table`), each a `section` with an `h2`. When there is nothing to split, the Shares section holds one result message (`.result-msg`, 16/24 ink) instead of the table and Copy summary. See the screen docs.

### Status message `p.status[role="status"]`
Sits 8 px under Copy summary, centred, 14/20 600. Empty and hidden until a copy is tried.
| State | Copy | Colour |
|---|---|---|
| Success | Summary copied | Ink (green stays reserved for the proof line) |
| Failure (`.status-failure`) | Could not copy. Your browser blocked the clipboard. | Error red |

### Note banner `.note` (dismissible)
Under the header, before the People block, inside `.note-wrap` (same max width and gutters as the header). Surface fill, 1 px line strong border, 6 px radius, 16 px left padding. Text 16/24 ink, vertically centred against a 44 x 44 dismiss button ("Dismiss note", X icon) at the right. `role="status"`.

### Dialog `dialog.dialog`
Opened with `showModal()`. Centred, `min(400px, 100% - 32px)` wide, 24 px padding, surface fill, 1 px ink border, 6 px radius. Title `h2` 18/24 700, body 16/24 ink muted 8 px below, actions 24 px below. Phone, the two large buttons stack full width with the primary first. From 600 px they sit in a row, right aligned, primary first. Backdrop is `--scrim`. Named by its title (`aria-labelledby`) and described by its body (`aria-describedby`).
