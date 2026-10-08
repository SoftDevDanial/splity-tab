# Design rulings: Split

**Date:** 2026-10-08 · **Ruled by:** orchestrator under the owner's delegation (**ORCH**, reversible)

The composer listed questions the brainstorm leaves open (`final/SELF-CRITIQUE.md`). They are ruled here
so the plan phase does not have to guess. Every ruling reuses a component already in `system.md`.

## Added copy, approved
All copy in the "Copy the brainstorm does not word" table of `final/SELF-CRITIQUE.md` is approved as
written, including "Enter the subtotal to see the shares." and the S5 singular and plural messages.

## Open questions, ruled
| # | Question | Ruling |
|---|---|---|
| 1 | What happens when a field is cleared? | An **empty** field never shows an inline error. It still blocks the result, which shows the matching message from row 3. An inline error shows only for **non-empty** text that is not valid. This applies to the subtotal, item prices and both rates. |
| 2 | What error does an out-of-range or invalid charge rate show? | The inline error under that field: "Enter a rate from 0 to 30" for service charge, "Enter a rate from 0 to 20" for SST. |
| 3 | Which message does the bill panel show when the shares cannot be worked out? | The first that applies, in this order. (a) A rate is empty or invalid: "Check the charges to see the shares." (b) Even mode, the subtotal is empty or invalid: "Enter the subtotal to see the shares." (c) By item, there are no items: "Add an item to see the shares." (d) By item, an item's price is empty or invalid: "Give every item a price to see the shares." (e) By item, items with nobody tapped: the S5 message. For (a) to (d) the bill summary is hidden too (there is no valid total). For (e) the summary stays (every item has a price). |
| 4 | Where do "Person N" and "Item N" show for a blank name? | The input shows them as its placeholder. The fallback name is used everywhere else the name appears: item toggles, the shares table, the copy summary and the remove button's accessible name. |
