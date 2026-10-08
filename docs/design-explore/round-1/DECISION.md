# Round 1 decision: Split

**Date:** 2026-10-08 · **Decided by:** orchestrator under the owner's delegation (**ORCH**, reversible)
**Compare page:** `compare.html` in this folder.

## Picked
**C, Working shown.** It is the only direction that puts the proof on the screen. Each charge shows its
base and the shares table sums across and down to the receipt total.

## Changes to C before locking the system (no round 2)
The changes below are small and taste-neutral, so they go straight into the system lock instead of a
second round.
1. **Remove the amounts inside the item toggles** ("Aisyah RM 9.00"). The brainstorm does not ask for a
   per-item share. Moved to the suggestions note below.
2. **Move the charge rates out of the bill summary into their own "Charges" block** above it. C's own
   cost note said the inputs mixed into the output, and it breaks the empty state: the rates must stay
   editable before any amount is entered, when the summary has nothing to show. The summary keeps the
   read-only working text ("10% of RM 59.40").
3. **Keep** the working lines and the column sums in the check row. They present two brainstorm rules
   (C4 how charges are calculated, C5 shares that add up) and invent nothing.

## Rejected
- **A, Receipt tape.** Charming, but the monospace receipt makes a long page longer and its proof is two
  matching frames rather than a sum.
- **B, Colour per person.** Friendly, but six colours repeat past six people, two of them look alike to
  colour-blind users, and the bar shows proportions rather than cents.

## Suggestions (not in the brainstorm, not designed)
- Show each person's share of a shared item inside its toggle (from direction C).
- A stacked bar of the total by person (from direction B).
