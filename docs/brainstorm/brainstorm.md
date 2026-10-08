# Brainstorm: Split

**Phase:** brainstorm · **Date:** 2026-10-08 · **Direction:** personal · **Track:** sdlc

> **How this brainstorm was run.** The owner delegated this whole run ("Auto create with lifecycles for 2
> projects. Split bill and a todo app", 2026-10-08). The grill below was walked by the orchestrator. Each
> question carries the recommended answer and the decision taken. Every decision is tagged **ORCH**, which
> means it is reversible and the owner may overturn it. The approval gate at the end is recorded the same
> way.

## The problem
A group eats at a restaurant in Malaysia and one person pays. The receipt adds a 10% service charge and
6% SST on top of the food. Working out who owes what by hand is slow, and the shares rarely add back up
to the receipt total because of the cents. When people ordered different things, it gets worse.

## Who uses it
One person at the table, on their phone, with the receipt in hand. They type the numbers in and read
each share out or paste a summary into the group chat. Nobody else needs the app.

## Direction
Personal. A small, free, private tool. No market panel, no pricing, no accounts.

## Resolved scope

### Core capabilities
| ID | Capability | What the user gets |
|---|---|---|
| C1 | People | A list of 2 to 12 people. Add, remove and rename. |
| C2 | Even split | Enter the bill subtotal once and everyone pays the same share, to the cent. |
| C3 | Split by item | Enter each item and its price, tap who had it. A shared item is split between the people tapped on it. |
| C4 | Charges | Service charge (default 10%) and SST (default 6%), both editable. SST is charged on the subtotal plus the service charge, the way Malaysian receipts do it. |
| C5 | Shares that add up | Every share is rounded to the cent and the shares always add up to the bill total exactly. The app shows that check. |
| C6 | Copy summary | One tap copies a plain-text summary for the group chat. |
| C7 | Draft kept | The current bill survives a reload or a closed tab on the same device. |
| C8 | New bill | Clears everything after a confirmation. |

### Key flows
1. **Even split.** Open the app. Two people are listed. Rename them, add a third. Type the subtotal.
   Each share appears, with the bill summary above it and "Adds up to RM X" under it. Tap "Copy summary".
2. **Split by item.** Switch to "By item". Add each item with its price. Tap the names of the people who
   had it. Shares appear once every item has at least one person. Each person shows their items total
   and their share of the charges.
3. **Come back later.** Close the tab mid-bill. Reopen it. The bill is as it was.
4. **Start over.** Tap "New bill", confirm, and the app returns to two people, even split, 10% and 6%.

### Rules the build must follow
- **Money is held in whole cents** (integers). No floating point in any money calculation.
- **Amounts accepted:** a number with up to 2 decimals, above 0, at most 99,999.99. "12", "12.5" and
  "12.50" are all fine. Anything else shows an inline error under the field: "Enter an amount like 12.50".
- **Charge rates:** whole or decimal percent from 0 to 30 for service, 0 to 20 for SST, up to 2 decimals.
  0 turns a charge off. A hint says "Set a charge to 0 if your bill already includes it."
- **Bill maths:** service = subtotal × service rate, rounded half up to the cent. SST = (subtotal +
  service) × SST rate, rounded half up to the cent. Total = subtotal + service + SST.
- **Even split rounding:** total ÷ number of people, rounded down to the cent. The leftover cents go one
  each to the people at the top of the list. Shares differ by at most 1 sen.
- **By item rounding:** a shared item's price is split the same way between the people tapped on it
  (leftover cents to whoever is highest in the people list). That gives each person an items subtotal
  in whole cents. The charges (service + SST together) are then shared in proportion to each items
  subtotal, rounded down, with leftover cents one each to the people highest in the list who have an
  items subtotal above zero. Everyone's share is items subtotal + charges share.
- **Unassigned items block the result.** If any item has nobody tapped, the shares are not shown. The
  result area says how many items still need a person.
- **People:** start with two, named "Person 1" and "Person 2". Names are up to 20 characters. A blank
  name shows as "Person N" (its position). Duplicate names are allowed. Remove is disabled at 2 people,
  add is disabled at 12. Removing a person also removes them from every item.
- **Items (by item):** name optional, up to 40 characters, a blank name shows as "Item N". Price required.
  Remove an item at any time. No limit beyond 50 items.
- **Copy summary text** (plain text, one person per line):
  ```
  Bill split
  Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)
  Aisyah RM 38.87
  Ben RM 38.87
  Chen RM 38.86
  Adds up to RM 116.60
  ```
  On success the app says "Summary copied". If the browser blocks the clipboard it says "Could not copy.
  Your browser blocked the clipboard."
- **Draft:** saved to this browser's storage after every change. If the saved draft cannot be read, the
  app starts a new bill and says "Your saved bill could not be read, so a new one was started." The note
  can be dismissed.
- **Switching modes keeps both sets of input.** The even subtotal and the item list are both kept, so
  switching back and forth loses nothing. The draft keeps both.
- **New bill** asks "Start a new bill? This clears the people, items and amounts." with "Start new bill"
  and "Cancel".
- **Platform:** a static web page. Works on a phone (360 px wide and up) and on desktop. Keyboard usable,
  visible focus, reduced motion respected. English only, Malaysian ringgit only.

### Non-goals (do NOT build)
- Payments, transfer links or DuitNow QR.
- Accounts, login, sync between devices, sharing links.
- Other currencies, currency conversion, other languages.
- Reading the receipt from a photo (OCR).
- A history of past bills. One draft only.
- 5-sen cash rounding.
- Tips, discounts, vouchers, per-item tax exemptions.
- A theme switcher.

## Grill log
| # | Question | Recommended answer | Decision | Tag |
|---|---|---|---|---|
| 1 | Who is the user? | The one person paying, on a phone at the table. | As recommended. | ORCH |
| 2 | Direction? | Personal. It is a showcase example with no business model. | Personal, so no market panel. | ORCH |
| 3 | Even split only, or by item too? | Both. Even split is the common case, by item is where mental maths fails. | Both modes. | ORCH |
| 4 | How are the charges calculated? | Match Malaysian receipts. Service on the subtotal, SST on subtotal plus service. | As recommended, both rates editable. | ORCH |
| 5 | What if the receipt total already includes charges? | Let the user set a charge to 0, with a hint. | As recommended. | ORCH |
| 6 | How are cents rounded? | Integer cents. Leftover cents one each to the top of the list, so shares always sum to the total. | As recommended. | ORCH |
| 7 | How are charges shared in by-item mode? | In proportion to each person's items subtotal. | As recommended. | ORCH |
| 8 | What happens with an item nobody had? | Block the result until every item has a person. A partial split would not add up to the receipt. | Block, with a count of items left. | ORCH |
| 9 | How many people? | 2 to 12. One person is not a split, 12 covers a long table. | As recommended. | ORCH |
| 10 | How does the summary leave the app? | Copy as plain text. Share sheets vary by browser and need no extra build. | Copy only. | ORCH |
| 11 | Is the bill kept? | Keep one draft in this browser. History is a different product. | One draft, no history. | ORCH |
| 12 | Cash rounding to 5 sen? | No. Most splits are paid by transfer. | Non-goal. | ORCH |
| 13 | Does switching modes lose input? | No. Keep both sets so a switch is safe to try. | Keep both. | ORCH |

## Gate
**Resummarized idea.** Split is a one-page web app for the person who paid a restaurant bill in
Malaysia. They list 2 to 12 people, then either type the subtotal for an even split or list the items
and tap who had each one. The app adds 10% service and 6% SST (editable), splits the total in whole
cents so the shares always add back up to the receipt, shows that check, copies a plain-text summary,
keeps one draft in the browser, and can start a new bill after a confirmation. No payments, accounts,
history, OCR or other currencies.

**Approval:** given by the orchestrator under the owner's delegation on 2026-10-08, tagged ORCH. The
owner may reopen any row above.
