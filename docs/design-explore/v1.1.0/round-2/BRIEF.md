# Round 2 brief: Danial's Splity Tab, v1.1.0

**Phase:** design (sdlc:design step 4, critique and converge) · **Date:** 2026-10-10 · **Ledger:** S7 row 3, H-03
**Round 1 brief still applies** (`../BRIEF.md`: who, the key screen's job, hard constraints, logo, the whole
inventory with its exact figures). This file only adds what the owner's pick changes.

## The owner's pick (his words, 2026-10-10 21:43)
"1. Color i like Night console, remove neon backgrounds. 2. For desktop version, Move charges above Split
3. By items, make it a a scrollable frame or something. I dont want the whole page to scroll, it should be
scrolled within a div instead. 4. For mobile, make the receipt collapsed or maybe display on button press or tab
change. Make it easier to input stuff. Right now, its pushed down. 5. Overall, looks good and i love the sen left
over"

Clarified 21:49: "neon backgrounds" means **bright filled buttons**.

## The one new direction: F "Orbit Console"
**D Share Orbit's layout and interactions, in A Night Console's colours, with no bright filled buttons.**

| Take | From | What |
|---|---|---|
| Layout and interactions | `round-1/d.html`, `d.md` | The ring around the total with name callouts, one segment per person as long as their share, the shares table (Person, Items, Charges, Share), the Bill summary, "Adds up to", "1 sen left over", the spare-sen dropdown, the **"+1 sen"** label beside a share (the owner loves it, keep it), the picker, New bill, every state |
| Colours | `round-1/a.md` tokens, `a.html` | The layered slate surfaces (`--l0` to `--l5`, `--field`), text and muted text, control borders, indigo as the one accent (`--accent` #5059DA as a line or tint, `--accent-ink` #A3AAFF as text), error and danger |
| Person colours | `round-1/d.html` | A muted colour per person stays (it ties the ring, the rows and the callouts). Retune them to sit on slate if needed, 3 to 1 against their background as graphics |

## The five changes
1. **No bright filled buttons.** The selected Even/By item, the chosen spare-sen option, Copy summary and any
   other primary control use an indigo outline, indigo text, or a dark indigo tint, never a solid bright fill.
   Night Console's slate panes and the indigo accent stay. Danger (Start new bill) may keep its red, as an outline
   or tint too.
2. **Desktop: Charges moves to the top of the input column, above the Even/By item switch.** Order: Charges
   (Service charge, SST, the hint), the Even/By item switch, People, Items. (ORCH reading of "above Split": the
   switch is the split mode. Flagged to the owner.)
3. **By item: the item list scrolls inside its own frame. The page does not scroll at 1280 x 800.** Not in K1,
   K2, S7 (12 people), nor in a long bill. The frame shows that it scrolls (a fade or a visible edge, plus a
   normal scrollbar). Decide whether People sit inside the scrolling region or above it so S7 still fits, and say
   which in your notes.
4. **Phone: inputs come first.** The receipt (ring, shares, Bill summary) is not above the inputs any more. A bar
   pinned to the bottom of the screen carries the Total, a **Shares** button that opens the receipt as a bottom
   sheet (Esc, backdrop and Close shut it), and Copy summary. The "+1 sen" label and "1 sen left over" show in the
   sheet. The input order on the phone matches the desktop (Charges, switch, People, Items) unless that reads
   badly at 390 px, in which case say why. (ORCH reading of "collapsed, button press or tab change". Flagged.)
5. **Keep the spare sen.** "+1 sen" beside the share that got it, and "1 sen left over" by the spare-sen choice.

## Inventory for round 2
Everything in the round 1 inventory (K1, K2, P1, M1, S1 to S7, W1), with the exact figures, plus:

| ID | Screen, popup or state | Content |
|---|---|---|
| P2 | **Shares sheet (phone, new)** | The receipt from K1 or K2 in a bottom sheet opened from the pinned bar's Shares button |
| W2 | **Long bill (prototype only)** | Ten items so the item frame visibly scrolls at 1280 x 800 and 390 x 844. Figures computed live in whole cents with the brainstorm rules, shown only behind Prototype states. Not a golden figure |

## Prototype rules (round 1 rules, plus the round 1 flags)
- One self-contained file `round-2/f.html`, inline CSS and JS, colours as custom properties, no network.
- Every popup and sheet opens from the design's own controls. States with no natural trigger sit behind a small
  "Prototype states" tab that **never covers content** at 390, 360 or 1280 px (round 1 flag: B's tab covered a
  name field), sits under any open popup's backdrop, and never overlaps the pinned bar.
- "At random" is a real random pick, not a fixed seed (round 1 flag: A, B and C used a seed).
- The page computes shares live in whole cents so every inventory figure matches.

## Output
`round-2/f.html`, `round-2/f.md` (what you took from where, every reading you made, contrast table, suggestions not
built), render checks in `round-2/checks/f/`.
