# SEAL: Split v1.0.0

**Sealed:** 2026-10-10 16:40, on the owner's word: "1. Seal both apps".
**Tag:** `v1.0.0` (local, on the commit that adds this file). This folder is read-only from here on.
**Next working version:** 1.1.0 (`docs/v1.1.0/CHANGE-LEDGER.md`).

## Checks at the seal
- Staleness: the newest ledger entry is the seal row, `docs/progress/handoff/` is empty, so the ledger is current.
- Credential gate: clean over the whole tree, exit 0.
- Last green code: `src/` and `index.html` last changed at `059f560` (2026-10-10 12:41). `sdlc:regression --full`
  passed on it at `dc180ad` (2026-10-10 14:30): cold boot 7 of 7, 275 unit and 427 browser tests, fidelity 10 of 10
  at 0 px and 157 of 157 element checks. The review drive (80 of 80) and UAT ran on the same code.

## What shipped (from the ledger)

| scope | title | status |
|---|---|---|
| C1 | People | SHIPPED |
| C2 | Even split | SHIPPED |
| C3 | Split by item | SHIPPED, with H-02 below |
| C4 | Charges | SHIPPED |
| C5 | Shares that add up | SHIPPED |
| C6 | Copy summary | SHIPPED |
| C7 | Draft kept | SHIPPED |
| C8 | New bill | SHIPPED |

## UAT (2026-10-10, sitting 1 of 1)

| case | scope | tester | owner |
|---|---|---|---|
| UAT-01 | C1 People | PASS | PASS |
| UAT-02 | C2 Even split | PASS | PASS |
| UAT-03 | C5 Shares that add up | PASS | PASS, with a request (spare sen chosen by the user) |
| UAT-04 | C4 Charges | PASS | PASS |
| UAT-05 | C6 Copy summary | PASS (paste not driven) | PASS |
| UAT-06 | C3 Split by item | PASS | PASS, with a script note and a question (closed, not a bug) |
| UAT-07 | C7 Draft kept | PASS | PASS |
| UAT-08 | C8 New bill | PASS | PASS |

Script, verdicts in his words, and findings: `user-test-2026-10-10/`.

## Known residuals, as ruled
| residual | ruling |
|---|---|
| H-02 the by-item table scrolls sideways on a 360 px phone past about RM 650 of items | Fixed in 1.1.0 (owner, 2026-10-09) |
| SEC-04 holding Enter on the only item's Remove adds a blank item | Fixed in 1.1.0 |
| A bill that cannot be saved (storage blocked or full) gives no message | Fixed in 1.1.0 (owner, D-01) |
| Only Chromium was tested | Safari's engine joins the test runs in 1.1.0 (owner, D-01) |
| Another page on the same github.io address can read the saved bill | Kept (owner, D-01) |
| Two tabs, the last save wins | Kept. Several bills becomes a future-implementation document in 1.1.0 (owner, D-01) |
| A double click on Dismiss note moves the keyboard cursor to the page | Kept (owner, D-01) |
| A name made only of invisible characters copies as blank | Kept (owner, D-01) |
| A hand-edited draft with a huge next id is refused on the next load | Kept (accepted at the security audit) |

## Going into 1.1.0
The owner's UAT requests: the spare sen chosen by the user, the logo in the app, a livelier look from a design round
with him (five directions), the test-case layout, and a new name (SplitIO is taken, chosen in the design round).
