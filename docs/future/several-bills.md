# Future implementation: several bills

**Status:** not built. A design note for a later version. · **Asked for:** 2026-10-10, by the owner at the v1.0.0 UAT
· **Ledger:** v1.1.0 scope S9 (document only)

## Why this note exists
Splity Tab keeps one bill. Two tabs open on the same device show the same bill, and the last change wins. The owner's
reading at UAT was "its a shared state so technically changing at 1 place will change at the other. If they want to add
a different bill, we can have this as future implementation." He asked for it to be written up, not built.

## What the user would get
A short list of bills on this device, for example "Friday dinner" and "Team lunch". One is open at a time. Each keeps
its own people, items, charges and spare-sen choice. A bill can be renamed, opened, and deleted after a confirmation.

## How it could work
- **Storage.** Today one draft lives under one key. Several bills would each get their own key, plus a small index
  of ids, names and last-changed times. The 1.0 draft becomes the first bill on the first load, so nothing is lost.
- **Two tabs.** Each tab works on the bill it opened. A tab that sees its bill changed in another tab (the browser's
  storage event) reloads that bill instead of overwriting it, which ends "last change wins" for the common case.
- **Limits.** A cap on the number of bills (for example 20) keeps storage small, with the oldest offered for deletion.
- **Screens.** A bill list (the key new screen), the open bill as today, and the delete confirmation.

## What it would change
| Area | Change |
|---|---|
| Brainstorm | A new capability, and "a history of past bills" leaves the non-goals |
| Design | The bill list, the empty list, the rename field, the delete dialog |
| split-core | Nothing. The maths works on one bill at a time |
| split-app | The draft store and a list screen. The decoder already treats stored text as untrusted |
| Security | The index is untrusted input too, and a crafted index must not break the page |

## Not decided
Whether a finished bill should be marked as paid, and whether the list sorts by name or by date. Both are the owner's
calls when this is picked up.
