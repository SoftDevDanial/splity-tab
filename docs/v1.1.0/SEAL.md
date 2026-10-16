# SEAL: Split v1.1.0

**Sealed:** 2026-10-16, on the owner's word at 19:38: "seal both".
**Tag:** `v1.1.0` (local, on the commit that adds this file). This folder is read-only from here on.
**Next working version:** 1.2.0, not opened yet.

## Checks at the seal
- Staleness. The newest ledger entry is S7 row 60 (19:38), newer than the newest handoff (06:19), so the ledger is current.
- Credential gate. Clean over the whole tree (11,390 files), exit 0, the planted control caught and 0 false hits on prose.
- Last green code. `src/` and `index.html` last changed at `b0992b4` (2026-10-16 03:01). `sdlc:regression --full`
  passed on it at `22e388b` (2026-10-16 04:22), QA both modules, the pixel gate 40 of 40, the cold boot in Chromium and
  WebKit, security and code review with the consistency sweep. The review, the UAT pre-run, the owner's sitting and the
  Android layout run all ran on the same code.

## What shipped (from the ledger)

| scope | title | status |
|---|---|---|
| S1 | The user decides who takes the spare sen | SHIPPED |
| S2 | The by-item table fits a 360 px phone (H-02) | SHIPPED, with H-12 below |
| S3 | Holding Enter on Remove adds no blank item (SEC-04) | SHIPPED |
| S4 | A bill that cannot be saved says so | SHIPPED |
| S5 | Tested in Safari's engine too | SHIPPED, the phone cases not run on a real phone |
| S6 | The logo in the app | SHIPPED |
| S7 | A livelier look, chosen from five directions | SHIPPED |
| S8 | A name that is free to use | SHIPPED |
| S9 | Several bills, written up as a future implementation (document only) | SHIPPED as a document |

## UAT (2026-10-16, sitting 1 at the owner's desk, sitting 2 not run on a phone)

| case | scope | tester (pre-run) | owner | Android layout run |
|---|---|---|---|---|
| UAT-01 | S1 Spare sen, even bill | PASS | PASS, with a note (a future upgrade) | |
| UAT-02 | S7 A livelier look | BLOCKED (script, repaired) | PASS | |
| UAT-03 | S1 Spare sen, by item | PASS | PASS | |
| UAT-04 | S2 A 360 px phone | PASS | PASS, one line crossed (step 9, script wording) | |
| UAT-05 | S3 Holding Enter | PASS | PASS | |
| UAT-06 | S4 Cannot be saved | PASS | PASS | |
| UAT-07 | S6 and S8, logo and name | BLOCKED (seat) | PASS | |
| UAT-08 | S9 Several bills | PASS | PASS | |
| UAT-09 | S5 with S7 | FAIL (script, repaired) | BLOCKED, not run on an iPhone | BLOCKED (one script line, struck) |
| UAT-10 | S5 with the double tap rule | PASS | BLOCKED, not run on an iPhone | PASS |
| UAT-11 | S5 with S7 and H-08 | PASS | BLOCKED, not run on an iPhone | PASS |
| UAT-12 | S5 with S2 | PASS | BLOCKED, not run on an iPhone | PASS |
| UAT-13 | S5 with S7 and H-09 | BLOCKED (seat) | BLOCKED, not run on an iPhone | BLOCKED (seat) |
| UAT-14 | S5 with S4 | BLOCKED (seat) | BLOCKED, not run on an iPhone | PASS |
| UAT-15 | S5 with S6 | BLOCKED (seat) | BLOCKED, not run on an iPhone | BLOCKED (seat) |

The owner's ruling on the phone cases, "Iphone test cases and even phones just remain as blocked or fail or as not
run. Yes its not what the apps themselves do but data integrity saying its passed when its not tested is bad. So not
run is better with note on why. But the release is still good to be released as it doesnt depend on iphone." The
Android layout run is evidence only. Script, verdicts in his words, and findings: `user-test-2026-10-16/`.

## Known residuals, as ruled
| residual | ruling |
|---|---|
| H-12 at 360 px a price of 99999.99 shows as "99999.9" until focused | Kept (owner, "H-12 is ok to keep."), README known limit |
| H-11 in Safari's engine a tap that opens a popup draws the keyboard focus ring | Kept as built, not checked on a real iPhone |
| A selected price can look unselected in Android-style phone browsers | A design note for the next version (`docs/future/bugs-found.md`) |
| CS-1 and SEC-R1, names that bring only control characters, an IME holding a bidi mark | Accepted to the next version (ORCH, ledger S7 rows 51 and 52) |
| No real iPhone or Android phone used | Phone layouts checked in emulation only (owner's ruling) |
| The earlier limits in the README's Known limits | As listed there |

## Going into the next version
The spare sen given to people the user chooses (`docs/future/spare-sen-chosen-people.md`, a brainstorm first),
several bills (`docs/future/several-bills.md`), the selection colour, the ledger's DEFERRED rows and the v1.2.0 doc and
test pass, the stray file outside the project (handover A4, his to delete) and the publish prep choice on paths (A5).
