# S5 Bill screen, by item, an item still needs a person

**Golden.** `bill-unassigned.html` · **Inventory.** S5 · **Capabilities.** C3 Split by item, C5 Shares that add up (the block rule)

## Intent
A partial split would not add up to the receipt, so the app does not show one. The bill summary still shows (every item has a price, so the Total is known), but the shares, the check row and Copy summary are replaced by one message that counts the items still waiting for a person.

## What changes from S1
1. "Mee goreng mamak" has **no one tapped** (Aisyah, Ben and Chen all off).
2. The Shares section keeps its heading and holds the message instead of the table, Copy summary and the status line.
Everything else is identical to S1, including the full Bill summary (Subtotal RM 59.40, + Service charge RM 5.94 "10% of RM 59.40", + SST RM 3.92 "6% of RM 65.34", = Total RM 69.26).

## Exact copy
| Where | Copy |
|---|---|
| Panel message, 1 item (new copy, see SELF-CRITIQUE.md) | 1 item still needs a person. Tap who had it to see the shares. |
| Panel message, 2 or more (not drawn) | N items still need a person. Tap who had each one to see the shares. |
| Everything else | As in `bill-items.md` |

## States this screen covers
- By item, every item priced, at least one item with no one tapped.
- The count updates as toggles change. When the last item gets a person, the table, check row and Copy summary appear (S1).
- No error styling on the item or its toggles. The brainstorm asks only for the count in the result area.

## Spacing and alignment that matter
- The Shares section sits 32 px under the Total as in S1, heading 18/24 700, message 8 px below in 16/24 ink, aligned with the heading.
- The message wraps naturally. At 390 and 360 it takes two lines, at 1280 inside the 420 px card it takes two lines.
- The panel is shorter than S1, so on desktop the sticky card ends after the message (24 px bottom padding).
