# Build record: split-core

Built by the backend developer role from `spec.md` and `qa.md`. Pure ES modules under `src/core/`, no
dependencies, no DOM, no I/O. Money is integer cents, rates are integer basis points.

## Tasks to commits
| Task | Requirements | Commit | Files |
|---|---|---|---|
| 1. Parsing | R1, R2, R3 | `bb3fba9` | `src/core/money.js`, `tests/money.test.js`, `tests/support/rng.js` |
| 2. Formatting | R4, R5 | `3399736` | `src/core/money.js`, `tests/money.test.js` |
| 3. Allocation | R7, R8, R9 | `5d98d13` | `src/core/allocate.js`, `tests/allocate.test.js` |
| 4. Bill state rules | R10 to R17, R26 | `8228969` | `src/core/bill.js`, `tests/bill.test.js`, `tests/support/bills.js` |
| 5. Charges and result | R6, R18 to R21, R23, R26 | `e40c171` | `src/core/result.js`, `tests/result.test.js` |
| 6. Invariant sweep | R22 | `50b6a8b` | `tests/invariants.test.js` |
| 7. Summary text | R24, R26 | `27458ba` | `src/core/summary.js`, `tests/summary.test.js` |
| 8. Hygiene scan | R25 | `025e232` | `tests/hygiene.test.js` |

8 of 8 tasks done. Last run of `node --test "tests/**/*.test.js"`: tests 185, pass 185, fail 0.

## How to run the tests
From the project root (Node 24): `node --test "tests/**/*.test.js"`. The quotes matter, and a bare
`node --test tests/` fails on Node 24 (CG-6). No install step, no `package.json`: Node 24 detects ES
module syntax in `.js` files by itself.

Test titles start with their tag (`@R8 ...`), so `grep -r "@R8" tests` maps a requirement to its cases.

## Deviations
None architectural. No new dependency, table, service or contract change. Three judgment calls where the
spec is silent, listed so the orchestrator can confirm or overturn them:

1. **Setters with an unknown id.** `setPersonName`, `setItemName` and `setItemPriceText` return the input
   unchanged (same reference) when the id is not in the bill. R15 does not say; this follows R12 to R14.
2. **How `computeResult` finds unassigned items.** It counts an item as unassigned when no person in the
   bill is on it (`holderIndexes` is empty), not when `who` is empty. The two are identical while the
   invariant "every id in `who` is a person of the bill" holds. The difference is that a bill breaking the
   invariant yields `unassigned` instead of a `RangeError` from `allocateEvenly(price, 0)`.
3. **Test helpers.** `tests/support/rng.js` (mulberry32, `randomInt`) and `tests/support/bills.js`
   (`buildBill`, `deepFreeze` and the named example bills of `qa.md`) are shared by several test files, so
   they exist once (DRY). They are not under `src/core/`, and the test glob only picks `*.test.js`.

QA evidence file `docs/modules/split-core/qa/unit/<timestamp>/node-test.txt` was not written. It belongs to
the QA run, and the filesystem rules forbid writing it through a shell redirect.

## Non-goals honoured
No payments or QR, no other currency or locale formatting (no `Intl`, no group separator), no 5-sen
rounding, no tips or discounts or other charges, no history or second bill, no DOM, storage, clipboard,
network or timer code, and no generic helpers beyond what the requirements call. `tests/hygiene.test.js`
enforces the purity part mechanically.

## Exports (the contract, nothing more)
| File | Exports |
|---|---|
| `src/core/money.js` | `parseAmount`, `parseRate`, `formatMoney`, `formatRate`, `AMOUNT_MIN_CENTS`, `AMOUNT_MAX_CENTS` |
| `src/core/allocate.js` | `allocateEvenly`, `allocateByWeight` |
| `src/core/bill.js` | `LIMITS`, `newBill`, `addPerson`, `removePerson`, `setPersonName`, `setMode`, `setSubtotalText`, `setServiceText`, `setSstText`, `addItem`, `removeItem`, `setItemName`, `setItemPriceText`, `toggleItemPerson`, `personLabel`, `itemLabel` |
| `src/core/result.js` | `billCharges`, `computeResult` |
| `src/core/summary.js` | `summaryText` |

## Internal helpers (module-private, by symbol)
| File | Symbols | Why they exist |
|---|---|---|
| `money.js` | `readHundredths`, `DECIMAL_TEXT`, ~~`MAX_WHOLE_DIGITS`~~ [removed 2026-10-09, solver, WR-06], `EMPTY`, `INVALID`. [Added 2026-10-09, solver, WR-08: `wholePart`.] | One reader for the amount and rate grammar. ~~The digit-count cap runs before any numeric conversion, so a 400-digit string is never converted.~~ [Changed 2026-10-09, WR-06: `readHundredths` takes the caller's ceiling and derives the digit cap from it. The reasoning is its comment.] [Added 2026-10-09, WR-08: `wholePart` is the exact integer division shared by `formatMoney`, `formatRate` and the digit cap.] |
| `allocate.js` | `assertAmount` | The shared amount precondition of both allocators (R9). |
| `bill.js` | `billWith`, `personWith`, `itemWith`, `changeItem`, `labelOf` | Rebuild a bill, person or item from known fields only (no spread of a parsed object), the shared item setter, and the shared label fallback. |
| `result.js` | `applyRate`, `BASIS_POINTS`, `sum`, `blocked`, `evenResult`, `itemResult`, `holderIndexes`, `itemTotals` | Half-up rate application with remainder arithmetic, and the two result builders split by mode. |

## Notes for the README reconcile
- ~~Rounding: `applyRate` stays in `Number` because its products are at most 649,999,935 x 2000 (below 2^53),
  and it uses remainder arithmetic so the division is exact. `allocateByWeight` is the only `BigInt` site,
  as the spec requires (charges x weight reaches about 1.4e16).~~
  [Changed 2026-10-09, solver, code-review WR-02: both numbers were wrong, and the derivation was a copy of
  source comments. Rounding and exact division are explained once, in the comments on `applyRate` and
  `allocateByWeight` (the only `BigInt` site), with the bounds in spec Invariants.]
- ~~`allocateEvenly` subtracts the remainder before dividing, so the division is exact for any safe integer.~~
  [Changed 2026-10-09, solver, WR-02: see the comment in `allocateEvenly`.]
- ~~Parsing caps the whole part at 9 digits after dropping leading zeros. This is an internal safety cap, not
  a rule: the range checks (99,999.99 for amounts, 30 and 20 percent for rates) decide validity.~~
  [Changed 2026-10-09, solver, code-review WR-06: the 9 was a magic number. The cap is now derived from
  the caller's ceiling, and the derivation is stated once, in the comment in `readHundredths`.]
- ~~Actions rebuild every object from known fields, so a `Bill` parsed from JSON loses stray keys and a
  `__proto__` key on its first action (threat model, object integrity). `tests/bill.test.js` covers it.~~
  [Changed 2026-10-09, solver, code-review WR-03: false. Untouched people and items keep their stray keys.
  What is rebuilt and what is shared is stated once, in the `bill.js` module header. The tests titled
  `@R16 <action> on a parsed bill builds only known fields` check each action on a parsed bill directly.]

## Boot
Nothing to boot. This module has no server or UI. `split-app` imports it with relative ES module paths such
as `./core/money.js`.
