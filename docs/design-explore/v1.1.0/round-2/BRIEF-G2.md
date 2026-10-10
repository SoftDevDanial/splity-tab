# Round 2 brief, G2 "Glass Console, revised": Danial's Splity Tab, v1.1.0

**Phase:** design (sdlc:design step 4, critique and converge) · **Date:** 2026-10-11 · **Ledger:** S7 row 6, H-03
round 2 ruling
**Base:** `round-2/g.html` and `g.md`. Everything in G stays unless this file changes it. `BRIEF-G.md` and `../BRIEF.md`
(round 1) still apply. Where they differ, this file wins.

## The owner's words (2026-10-11 00:01, after seeing G)
"For Splity, i like it. Small thing is the mobile. For people and charges, it should be collapsed from a section.
These will not change often. The one that is heavily changed or added is the items"

Asked whether "1 sen left over" should also sit on the phone's bottom bar, he answered: "I dont understand. 1 sen
left over is in shares ( oh yea, i dont like this, change this to Splits) which is at the bottom above copy summary
on the left split selection. That looks good already"

## The two changes
### 1. Phone: People and Charges collapse
Below 1024 px (the widths where G uses the phone layout), People and Charges each become a section that collapses to
one header row. Items is the part people work in, so it gets the room.

| Part | What |
|---|---|
| Header row | The whole row is one button (`aria-expanded`, `aria-controls`), at least 44 px tall, with the section name, a one-line summary and a caret that turns when open |
| People summary | The names in order, for example "Aisyah, Ben, Chen". When they do not fit on one line, as many names as fit then "and 2 more". With twelve people, "12 people" before the names if that reads better (say which you chose) |
| Charges summary | "Service 10%, SST 6%" with the current rates. A rate of 0 reads "Service 0%" |
| Default | Both collapsed when the page opens with a bill (K1, K2, S3 to S7, W1, W2). (ORCH reading, flagged) |
| A new bill | On S1 (first open, or after Start new bill) People starts open, because its names are still "Person 1" and "Person 2" and naming people is the first step. Charges stays collapsed. (ORCH reading, flagged) |
| Errors | A section with an error inside it opens and shows the error (for example S2 on a rate). While collapsed with an error, its header shows the error colour and the word "Check" or similar, so an error is never hidden. Say what you chose |
| Add person | Lives inside People, so it shows when People is open |
| Split switch | Stays as it is, always visible, one row (Even or By item). Not collapsible |
| Items and Subtotal | Never collapse. Items (By item) or the Subtotal (Even) follow the Split switch |
| Motion | The section opens with a short height reveal, off under reduced motion |
| Desktop, 1024 px and up | **Unchanged.** He named the phone only, and the desktop page already fits 1280 x 800 with nothing to scroll. (ORCH reading, flagged) |

Measure and report the first field of Items (By item) and the Subtotal field (Even) from the top at 390 x 844, against
G's figures, and how many items show above the strip in K1 and W2.

### 2. "Shares" becomes "Splits"
Every place the person reads the word "Shares" or "shares" now says "Splits" or "splits", on every width.

| Where | G | G2 |
|---|---|---|
| The phone bar's button | Shares | Splits |
| The sheet's accessible name, P2 | Shares | Splits |
| The receipt's section heading, card and sheet | Shares | Splits |
| Any sentence copy (for example S1's "Enter the subtotal to see the shares.") | shares | splits |

The "Split" section heading above the Even and By item switch stays "Split". List every string you changed in g2.md,
before and after. (ORCH reading: "change this to Splits" covers the word everywhere, so the button and what it opens
say the same thing. Flagged.) The copied summary text keeps the 1.0 format.

## Must not change
- "1 sen left over" stays where G has it, in the receipt above Copy summary, inside the sheet on a phone. His words,
  "That looks good already".
- Every figure, the money maths, Copy summary's solid indigo, the colours, the glass, the desktop layout, the item
  frame, the pinned bar (Total, Splits, Copy summary), every state and its copy except the rename.
- The page does not scroll at 1280 x 800 in K1, K2, S7 or W2. No sideways scroll at 360. The bar never covers an
  input. The Prototype states tab rules.

## Inventory, G2
Everything in G (K1, K2, P1, P2 now "Splits sheet", M1, S1 to S7, W1, W2). Prototype states keeps a shortcut per row
and adds "K1 People and Charges open (phone)" so both open sections can be seen at once.

## Output
`round-2/g2.html` (start from `g.html`, keep `g.html` untouched), `round-2/g2.md` (what changed from G, every new
reading, the measured positions, every renamed string, updated contrast table if anything new, suggestions not
built), render checks in `round-2/checks/g2/` (start from `checks/g/check_g.py`, keep every G assert that still
applies, add asserts for the collapse and the rename).
