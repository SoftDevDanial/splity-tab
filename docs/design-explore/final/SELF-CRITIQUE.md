# Self-critique of the Split final design set

**Phase.** design, step 8 · **Date.** 2026-10-08 · **Skills loaded.** `taste-skill:taste-skill` and `frontend-design:frontend-design` (what transferred is in `system.md`).

## The walk
Every file was rendered headless at 390 x 844, 360 x 780 and 1280 x 800, looked at, and checked by script (`harness/_scratch/design-final/verify.py`).

| File | One primary action | Spacing on scale | AA contrast | States present | Real, consistent copy | No template tells | 390 / 360 / 1280 |
|---|---|---|---|---|---|---|---|
| `bill-items.html` (S1) | Copy summary | Yes | Yes | By item, toggles on and off, shared item, status hidden | Yes | Yes | Pass / Pass / Pass |
| `bill-even.html` (S2) | Copy summary | Yes | Yes | Even, valid subtotal, status hidden | Yes | Yes | Pass / Pass / Pass |
| `bill-empty.html` (S3) | None needed, the field is the next step | Yes | Yes | First open, remove disabled at 2, empty subtotal, result message | Yes, one new message | Yes | Pass / Pass / Pass |
| `bill-unassigned.html` (S5) | None, Copy summary is replaced | Yes | Yes | One item with no one tapped, summary kept, count message | Yes, one new message | Yes | Pass / Pass / Pass |
| `new-bill-dialog.html` (M1) | Start new bill | Yes | Yes (scrim 3.45) | Open over S2, page behind inert and not scrolling | Yes, all brainstorm copy | Yes | Pass / Pass / Pass |
| `states.html` (S4, S6, S7, S8) | n/a (sheet) | Yes | Yes (disabled exempt) | Two amount errors, copy success and failure, note, both people limits | Yes, all brainstorm copy | Yes | Pass / Pass / Pass |

**Template tells checked and absent.** No eyebrow labels, no all-caps labels, no middle-dot strings in the UI, no decorative dots, no section numbers, no shadows, no gradients, no glass, no cream and terracotta, no purple, no hand-drawn icons, no em or en dashes in any file. One accent with one job. One radius.

**Verification result (all 18 renders).** No horizontal overflow, zero console messages, zero network requests besides the page itself, no touch target under 44 px, no wrapped button, no clipped input value, zero long dashes in any file, and the first `<style>` of every golden is byte-identical to `system.css`.

## What I changed, and why
### Changes the decision asked for
1. **Item toggles show the name only.** C's per-person amounts inside toggles are gone (and with them the `--on-ink-muted` token).
2. **Charges block.** Service charge and SST moved out of the bill summary into their own block after Items (or Subtotal) and before the panel, with the hint under them. They use the same cell grid as People, so they line up under the person columns.
3. **Bill summary keeps C's working as read-only text.** "10% of RM 59.40", "6% of RM 65.34" sit directly under their labels.
4. **Desktop keeps C's two columns.** Inputs left, the bill panel sticky on the right.

### Changes made while composing and critiquing
5. **Spacing moved onto a 4 px scale.** C used 6, 7, 14, 28 and 10 px in places. Toggle gaps 6 to 8, table cell padding 7 to 8, item padding 14 to 16, Total margin 14 to 12, Copy summary margin 28 to 24, table-head operator gap 3 to 4, block gaps 20 to 24, summary rows 6 to 4, money paddings 10 to 8.
6. **Type and weight made deterministic.** C's 650 weight rendered as 700 on Windows and differently elsewhere, so headings and shares are 700. The 17 px heading merged into 18 px. Seven sizes, three weights.
7. **Result messages align with their heading.** I first indented them by the operator gutter like the summary labels. In S3 there are no operators, so the indent looked like a mistake. Removed.
8. **Disabled ink lightened** from `#7E8682` to `#9AA19D`. At the first value a disabled remove X looked almost the same as an enabled one. Now it reads clearly as unavailable. Disabled colours are exempt from contrast rules.
9. **Money field paddings** tightened (8 / 4 / 8) so a 96 px price field still shows "999.99" in full at 360 px, and "Mee goreng mamak" still fits its name field at 360.
10. **Dialog page clip.** A fixed scrim over a long page only covers the viewport, so a full-page render showed half the page dimmed. While a dialog is open the app root (`.app`) is now clipped to the viewport. The golden and the app render the same at every width, and the page behind does not scroll.
11. **Status success in ink, not green.** C's colour rule gives green to the proof line only. "Summary copied" is ink. "Could not copy" is error red.
12. **Destructive confirm in ink, not red.** Red means an error in this system. The question already says what is cleared.
13. **States sheet frames always show the phone layout,** including at 1280 (the desktop rules otherwise removed the frame gutters).

## Copy the brainstorm does not word (for approval)
| Copy | Where | Source |
|---|---|---|
| Enter the subtotal to see the shares. | S3 bill panel message, also shown when the subtotal is invalid | **New in this pass** |
| 1 item still needs a person. Tap who had it to see the shares. | S5 bill panel message | **New in this pass** |
| N items still need a person. Tap who had each one to see the shares. | S5 plural form (not drawn) | **New in this pass** |
| Dismiss note | Accessible name of the S7 dismiss button (icon only) | **New in this pass** |
| Charges | Heading of the new Charges block | **New in this pass** (the brainstorm says "charges" in C4) |
| in percent · in RM | Visually hidden endings of the charge and subtotal labels, and of item price names | New wording of C's "in RM" pattern |
| Even · By item · Split mode (hidden legend) | Mode switch | C, round 1 ("By item" is brainstorm wording) |
| People · Items · Subtotal · Bill summary · Shares · Total | Headings and summary labels | C, round 1 (all brainstorm nouns) |
| Add person · Add item | Buttons | C, round 1 |
| Items · + Charges · = Share · Person (hidden) | Shares table column heads | C, round 1 |
| Person N name · Item N name · Item N price in RM · Remove <name> · Who had <item> | Accessible names | C, round 1 |
| Split states · the intro line · S4 Amount error and the other captions | `states.html` sheet chrome only, not app copy | Documentation |

Brainstorm copy used verbatim is "Enter an amount like 12.50", "Set a charge to 0 if your bill already includes it.", "Summary copied", "Could not copy. Your browser blocked the clipboard.", "Your saved bill could not be read, so a new one was started.", "Start a new bill?", "This clears the people, items and amounts.", "Start new bill", "Cancel", "New bill", "Copy summary", "Adds up to", "Service charge", "SST", "Person 1", "Person 2".

## Open questions for the orchestrator (not designed, nothing invented)
1. **Charge rate error.** The brainstorm sets the ranges (service 0 to 30, SST 0 to 20, up to 2 decimals) but words no error. The system's error pattern fits a percent field as is. The message needs wording and approval (for example "Enter a rate from 0 to 30").
2. **By item with no items, or an item with no valid price.** Neither is in the inventory. With no valid amount there is nothing to sum, so the S3 pattern (panel heading plus one message) fits, but the message is unworded (for example "Add an item to see the shares." or "Enter a price for every item to see the shares.").
3. **Where "Person N" and "Item N" show for blank names.** The brainstorm says a blank name "shows as" Person N or Item N. I suggest the input placeholder (ink muted, 7.96:1 on field) plus the shares table, accessible names and clipboard text. Plan should confirm.
4. **Empty subtotal on blur.** The golden shows no error for an empty field on first open. Whether clearing a filled field shows the S4 error is a plan decision.

## Suggestions (not in the brainstorm, not designed)
- Say why "Add person" is disabled at 12 (a short hint under the grid).
- Mark the item that still needs a person in S5 (the count alone can be hard to act on with many items).
- From round 1, each person's part of a shared item inside its toggle (direction C), and a stacked bar of the total by person (direction B).

## Known limits, accepted
- At phone width a price above 999.99 scrolls inside its 96 px field. From 600 px the 120 px field shows the maximum (99999.99) in full.
- With many people on desktop the sticky panel can be taller than the viewport. Its bottom (Copy summary) comes into view at the end of the left column. No content is ever unreachable.
