# Compose brief: Danial's Splity Tab v1.1.0 (sdlc:design steps 5, 6 and 8)

**Date:** 2026-10-11 · **Ledger:** S7 row 8, H-03 final ruling · **Owner's words:** "Both looks good. We can procceed as usual"

## The accepted direction
`round-2/g2.html` (G2 "Glass Console, revised") with `round-2/g2.md`, `round-2/g.md`, `round-2/BRIEF-G2.md` and
`round-2/BRIEF-G.md`. Every reading in g.md and g2.md stands (ledger H-03). The prototype is the truth for look,
copy, figures and behaviour. Your job is to turn it into a locked system and one golden per screen. Not a redesign.
Nothing new. `round-2/f.html` and `round-2/BRIEF.md` are withdrawn, ignore them.

## Rulings for this step (ORCH, reversible, from the open items)
1. **S6 opens People**, like S1. A saved bill that could not be read starts a fresh bill with "Person 1" and
   "Person 2", so naming people is the first step (g2.md reading 8, the orchestrator's recommendation, no separate
   answer from the owner).
2. **The rate error copy G2 added stays** ("Enter a rate from 0 to 30" for Service charge, "Enter a rate from 0 to
   20" for SST, the 1.0 wording).
3. **The header mark** stays the current `docs/brand/mark.svg` recoloured, as in g2. The logo is redrawn with the
   name "Splity Tab" after this step and swapped in before finalize. Keep the mark in one inline `<svg>` per page so
   the swap is mechanical.

## Output, all in `docs/design-explore/v1.1.0/final/` (nothing anywhere else)
| File | What |
|---|---|
| `system.md` + `system.css` | Step 5. Colour roles (not only hex), type scale (words and figures), spacing scale, the shape rule, elevation, the glass material and its solid fallback (reduced transparency, no backdrop-filter), motion (with reduced motion), breakpoints, the component inventory (button kinds, icon button, field, money field, person chip, switch, section header row, receipt card, strip, sheet, popover, dialog, banner). **Every text and non-text pair with its WCAG ratio**, glass composited over what sits behind it, as g.md did. A token not in g2 needs a written reason |
| One golden `<screen>.html` + `<screen>.md` per screen below | Step 6. Self-contained, `system.css` values inlined in a `<style>`, real content, no network, no Prototype states tab, static (no script needed to show the state). Each renders correctly at 360 x 780, 390 x 844 and 1280 x 800, the phone and the desktop layout from one file as g2 does. The `.md` gives intent, states, the exact copy, icons, sizes, spacing and every figure, and which inventory row and capability it serves |
| `MANIFEST.md` | Every inventory row (K1, K2, P1 with its picker and At random, P2 Splits sheet, M1, S1 to S7, W1, and the phone K1 with People and Charges open) mapped to its golden file and the state shown. W2 stays prototype only, no golden. Keep the 1.0 file name where the screen's job is the same (`bill-items.html` K1, `bill-even.html` K2, `bill-empty.html` S1, `bill-unassigned.html` S3, `new-bill-dialog.html` M1, `states.html` as the specimen sheet for states without their own screen). New names for new screens (for example `spare-sen.html`, `splits-sheet.html`, `bill-items-open.html`). Say which golden shows which width matters |
| `LINKS.json` | For step 7 (the orchestrator wires and drives it). Format `{"links": [{"from": "a.html", "role": "button", "name": "Splits", "to": "splits-sheet.html", "exact": true}, {"from": "x.html", "key": "Escape", "to": "a.html"}, {"from": "x.html", "click": [10, 10], "to": "a.html", "why": "backdrop"}]}`. Every natural trigger and every close between goldens, at the width where it applies (add `"width": 390` or `1280` to a link when it only exists there) |
| `SELF-CRITIQUE.md` | Step 8. Walk every golden against the list (one primary action per view, alignment and spacing on the scale, AA contrast, every state present, real and consistent copy, money columns aligned, no AI-template tells per the loaded skills, works at 360, 390 and 1280). What failed and what you changed. Then "copy the brainstorm does not word" and "interaction rules I specified", as 1.0's `final/SELF-CRITIQUE.md` did, for the owner's rulings |
| `checks/` | Your render checks (script, results.json, screenshots) |

Every figure must add up in whole sen in every golden (K1 RM 69.26, K2 RM 116.60, W1 RM 1,193.87 and the rest as g2
computes them). Read 1.0's `docs/design-explore/final/` (bill-items.md, states.md, SELF-CRITIQUE.md) for the shape
of the notes. Never write to `docs/design/` (1.0's immutable goldens) or to `docs/design-explore/final/` (1.0's
staging).
