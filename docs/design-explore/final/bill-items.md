# S1 Bill screen, by item, with shares (key screen)

**Golden.** `bill-items.html` · **Inventory.** S1 · **Capabilities.** C1 People, C3 Split by item, C4 Charges, C5 Shares that add up, C6 Copy summary

## Intent
Turn a receipt into shares everyone trusts. The person types each item, taps who had it, and sees each share without doing any maths. The proof is on the screen. Each charge shows its base ("10% of RM 59.40"), and the shares table adds across (Items + Charges = Share) and down to the receipt Total in the green "Adds up to" row.

## What the screen holds, top to bottom
1. **Header.** Wordmark "Split" (`h1`) and the secondary button "New bill".
2. **People.** Aisyah, Ben, Chen, each a name field with a remove button, then "Add person".
3. **Mode switch.** "Even" and "By item", with "By item" checked.
4. **Items.** Four item rows, each with name, price, remove and a toggle group, then "Add item".
5. **Charges.** "Service charge" 10 and "SST" 6, then the hint.
6. **Bill panel.** Bill summary, then Shares with the check row, then "Copy summary" and the (empty, hidden) status line.

## Exact data
| Item | Price | Tapped |
|---|---|---|
| Nasi lemak ayam | RM 15.90 | Aisyah |
| Char kuey teow | RM 13.50 | Ben |
| Mee goreng mamak | RM 12.00 | Chen |
| Satay, 10 sticks | RM 18.00 | Aisyah, Chen |

| Bill summary row | Working line | Amount |
|---|---|---|
| Subtotal | none | RM 59.40 |
| + Service charge | 10% of RM 59.40 | RM 5.94 |
| + SST | 6% of RM 65.34 | RM 3.92 |
| = Total | none | RM 69.26 (double rule) |

| Shares | Items | + Charges | = Share |
|---|---|---|---|
| Aisyah | RM 24.90 | RM 4.14 | RM 29.04 |
| Ben | RM 13.50 | RM 2.24 | RM 15.74 |
| Chen | RM 21.00 | RM 3.48 | RM 24.48 |
| Adds up to (check row) | RM 59.40 | RM 9.86 | RM 69.26 |

## Exact copy
| Where | Copy |
|---|---|
| Wordmark | Split |
| Header button | New bill |
| Block headings | People · Items · Charges |
| People button | Add person |
| Mode switch | Even · By item (hidden legend "Split mode") |
| Items button | Add item |
| Charge labels | Service charge · SST (each with visually hidden " in percent") |
| Charges hint | Set a charge to 0 if your bill already includes it. |
| Panel headings | Bill summary · Shares |
| Summary labels | Subtotal · Service charge · SST · Total |
| Working lines | 10% of RM 59.40 · 6% of RM 65.34 |
| Table column heads | (Person, visually hidden) · Items · + Charges · = Share |
| Check row | Adds up to |
| Primary button | Copy summary |
| Accessible names | Person 1 name, Person 2 name, Person 3 name · Remove Aisyah (Ben, Chen) · Item 1 name to Item 4 name · Item 1 price in RM to Item 4 price in RM · Remove Nasi lemak ayam (and each item) · Who had Nasi lemak ayam (and each item) |

**What Copy summary puts on the clipboard for this bill** (built from the brainstorm template, not shown on screen):
```
Bill split
Total RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)
Aisyah RM 29.04
Ben RM 15.74
Chen RM 24.48
Adds up to RM 69.26
```

## States this screen covers
- Mode "By item" checked, every item has at least one person, so the summary and shares show.
- Toggle on (ink) and off (field) side by side. Satay shows a shared item (two people on).
- Status line present but empty and hidden. After a copy it shows S6 (see `states.md`).
- Hover, focus and pressed states come from the system (see `system.md`). Tab order follows the page. New bill, people names and removes, Add person, mode, each item's name, price, remove, toggles, Add item, Service charge, SST, Copy summary.

## Behaviour the golden implies (from the brainstorm)
- The shares and Copy summary show only when every item has at least one person tapped. Otherwise the Shares section shows the S5 message (`bill-unassigned.md`).
- Removing a person removes them from every item's toggle group.
- Switching to "Even" keeps the items, and switching back restores them.
- The panel updates as the user types. It is not a live region (it would speak on every keystroke).

## Spacing and alignment that matter for a 1-to-1 build
- **Header.** Phone padding 12 px top, 16 px sides. 600 px and up, 20 px top. 1024 px and up, 32 px top and 32 px gutters.
- **Blocks.** Every block (People, mode switch, Items, Charges) starts 24 px below the previous one. Heading 18/24 700, content 12 px below.
- **People grid.** `auto-fill, minmax(140px, 1fr)`, 8 px gap. Two columns at 360 and 390, three at 1280 (left column 556 px). "Add person" fills the next cell.
- **Item row.** Grid columns `1fr 96px 44px` (120 px price from 600 px), 8 px gap. Toggles 8 px below, 8 px apart. Item padding 16 px, 1 px `--line` hairline above every item except the first. "Add item" sits right after the last item's 16 px bottom padding, left aligned, natural width.
- **Charges.** Uses the same cell grid as People, so "Service charge" lines up under the first person column and "SST" under the second. Label 8 px above its field, hint 8 px below the fields.
- **Panel, phone.** 32 px below the hint, full bleed, 2 px ink rule on top, 1 px line at the bottom, padding 20 / 16 / 24.
- **Panel, 1024 px and up.** Right column 420 px, 64 px from the inputs, sticky at 24 px. Its top edge lines up with the top of the People block. 1 px ink border, 6 px radius, 24 px padding.
- **Operator gutter.** 20 px for `+` and `=`, then 8 px. Labels, working lines, the Total rule, the shares names and the check-row rule all start at 28 px from the panel's content edge. The check icon sits in the gutter at 0.
- **Summary rows.** 4 px top and bottom. Working lines (15/20 ink muted) sit directly under their label. Total row 12 px margin and 12 px padding above, label 18 px 700, amount 26/32 700 on a 3 px double rule.
- **Shares.** Section starts 32 px under the Total. Table 8 px under its heading. Column heads 13/18 600 ink muted, bottom aligned, 4 px above the first row. Cells 8 px top and bottom, 8 px left padding. Names 15 px 600 ink. Items and Charges 14 px ink muted. Share 18 px 700 ink. Check row 12 px above, 1 px ink rule across Items, Charges and Share and from 28 px in the name column, check icon 18 px, label and final share in accent.
- **Copy summary.** 24 px below the table, full width, 48 px tall, copy icon 20 px, 8 px gap.
- **Money format.** Always `RM 0.00`, tabular figures, right aligned in every column.
