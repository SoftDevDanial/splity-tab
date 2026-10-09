# Module: split-core

> Build contract. Read by the builder. Build ONLY what is here.
> Stack is LOCKED to the project stack (vanilla JavaScript ES modules, zero dependencies, Node 24 for tests).
> Depends on nothing. Nature is pure logic (no DOM, no storage, no network, no clock, no randomness).
> Sources are `docs/brainstorm/brainstorm.md` (rules), `docs/design/RULINGS.md` (rulings 1 to 4), the S1 and S2 numbers in `docs/design/bill-items.md` and `docs/design/bill-even.md`.

## Module roadmap
- **Build order.** First. Nothing depends on anything else here, and `split-app` imports it.
- **Done when.** Every R# below has a passing `node --test` case (see `qa.md`), the code-review and security finders pass, and the reverse audit finds no exported symbol without an R#.
- **Shape change from the expected shape, with the reason.** Besides money parsing, bill maths, cent allocation and the summary text, this module also owns the **bill state rules** (the `Bill` shape, the defaults of a new bill, people and item limits, "removing a person removes them from every item", the display-name fallback and the order of the blocking messages). They are DOM-free rules from the brainstorm and `RULINGS.md`, so they get exact, fast unit tests here, and `split-app` stays a thin browser shell that never edits arrays itself.

## Invariants & assumptions
- Every money value is a non-negative integer number of cents (sen). No money value is ever a fraction.
- Every charge rate is a non-negative integer number of basis points (hundredths of a percent). 10% is 1000, 6.25% is 625.
- No money calculation passes through floating point. Division is exact integer division. Any product that can exceed `Number.MAX_SAFE_INTEGER` (9007199254740991) is computed with `BigInt`.
- Bounds that make the arithmetic safe. An amount is at most 9,999,999 cents. A by-item subtotal is at most 50 x 9,999,999 = 499,999,950 cents. Rates are at most 3000 bp (service) and 2000 bp (SST). The largest charges total is 279,999,972 cents, so `charges x weight` can reach ~~about 1.4e16~~ [Changed 2026-10-09, ORCH, code-review WR-02: about 1.4e17, that is 279,999,972 x 499,999,950 when one person holds every item. 1.4e16 was the MAX-I product 279,999,972 x 49,999,995.] and needs `BigInt`. Every other product stays below 2^53. [Added 2026-10-09, WR-02: the largest of them is the service step, 499,999,950 x 3000, about 1.5e12.]
- Text fields of a `Bill` (names and the raw texts of amounts and rates) are held exactly as typed. Parsing happens on read, never on write.
- A name never contains U+000A or U+000D. The browser strips them from `<input type="text">` values, and `split-app`'s draft decoder rejects them. Core relies on this and does not re-check.
- Every id in an item's `who` is the id of a person in the same bill, with no duplicates. `removePerson` keeps this true. `split-app`'s draft decoder rejects bills that break it.
- Functions are pure. The same input always gives the same output, and no input object is mutated.

## Requirements

### Parsing (C2, C3, C4, RULINGS 1 and 2)
- **R1. Amount grammar and range.** `parseAmount(text)` first removes leading and trailing white space (`String.prototype.trim`). The rest must match `^[0-9]+(\.[0-9]{0,2})?$` (ASCII digits only, at most one dot, at most 2 decimals, a trailing dot allowed). Its value is integer part x 100 + the decimal digits right-padded to 2. It is valid when 1 <= cents <= 9,999,999 (above 0 and at most 99,999.99). Leading zeros are allowed. Valid gives `{ ok: true, cents }`. [CG-4 ruled 2026-10-08, ORCH. Accepted as written.]

  | text | result | text | result |
  |---|---|---|---|
  | `12` | 1200 | `0` | invalid (not above 0) |
  | `12.5` | 1250 | `0.00` | invalid |
  | `12.50` | 1250 | `100000` | invalid (above 99,999.99) |
  | `0.01` | 1 | `99999.991` | invalid |
  | `99999.99` | 9999999 | `12.505` | invalid (3 decimals) |
  | `1.15` | 115 (naive `parseFloat` x 100 gives 114) | `13.505` | invalid (the S4 golden value) |
  | `4.35` | 435 (naive gives 434) | `-5`, `+5` | invalid |
  | `0.29` | 29 | `1,000` | invalid (no group separator) |
  | ` 12.50 ` | 1250 (trimmed) | `.5` | invalid (no leading digit) |
  | `007` | 700 | `1e3`, `0x10`, `Infinity`, `NaN`, `abc`, `12 50` | invalid |
  | `12.` | 1200 | full-width `１２` | invalid (ASCII digits only) |
  | `0000000012.50` | 1250 | `1` followed by 400 zeros | invalid, no overflow, no exception |
- **R2. Empty versus invalid.** When the trimmed text is empty (`""`, `"   "`), `parseAmount` and `parseRate` return `{ ok: false, empty: true }`. Every other failure returns `{ ok: false, empty: false }`. Neither function ever throws for any string.
- **R3. Rate grammar and range.** `parseRate(text, maxPercent)` uses the R1 grammar. Its value in basis points is integer part x 100 + the decimal digits right-padded to 2. It is valid when 0 <= bp <= maxPercent x 100. 0 is valid (it turns the charge off).

  | text | max | result | text | max | result |
  |---|---|---|---|---|---|
  | `0` | 30 | 0 | `30.01` | 30 | invalid |
  | `10` | 30 | 1000 | `20.01` | 20 | invalid |
  | `6` | 20 | 600 | `25` | 20 | invalid |
  | `6.5` | 20 | 650 | `-1` | 30 | invalid |
  | `6.25` | 20 | 625 | `6.255` | 20 | invalid |
  | `30`, `30.00` | 30 | 3000 | `10%` | 30 | invalid |
  | `20` | 20 | 2000 | `` (empty) | 30 | empty |
  | `0.01` | 30 | 1 | `6.` | 20 | 600 |
  | `06` | 20 | 600 | | | |

### Formatting (brief: money is written `RM 38.87`)
- **R4. Money format.** `formatMoney(cents)` returns `"RM "`, the whole ringgit in plain decimal digits with no group separator, `"."`, then the sen as exactly 2 digits. Examples are 0 to `RM 0.00`, 1 to `RM 0.01`, 10 to `RM 0.10`, 100 to `RM 1.00`, 3887 to `RM 38.87`, 11660 to `RM 116.60`, 15599999 to `RM 155999.99`, 779999922 to `RM 7799999.22`. [CG-5 ruled 2026-10-08, ORCH. Accepted as written.]
- **R5. Rate format.** `formatRate(bp)` returns the whole percent, then (only when the fraction is not zero) `"."` and the fraction digits with trailing zeros removed, then `"%"`. Examples are 0 to `0%`, 600 to `6%`, 1000 to `10%`, 650 to `6.5%`, 625 to `6.25%`, 605 to `6.05%`, 3000 to `30%`. A rate typed as `10.00` therefore shows as `10%`.

### Bill maths (C4, C5)
- **R6. Charges.** `billCharges(subtotal, serviceBp, sstBp)` returns `{ subtotal, serviceBp, service, sstBp, sstBase, sst, total }` where service = subtotal x serviceBp / 10000 rounded half up to the cent, sstBase = subtotal + service, sst = sstBase x sstBp / 10000 rounded half up, total = subtotal + service + sst. Round half up for a non-negative n / 10000 is floor((n + 5000) / 10000) done with exact integer operations.

  | subtotal | service bp | SST bp | service | sstBase | sst | total | what it proves |
  |---|---|---|---|---|---|---|---|
  | 10000 | 1000 | 600 | 1000 | 11000 | 660 | 11660 | S2 golden |
  | 5940 | 1000 | 600 | 594 | 6534 | 392 | 6926 | S1 golden (SST 392.04 rounds down) |
  | 8765 | 1000 | 600 | 877 | 9642 | 579 | 10221 | service 876.5 rounds up |
  | 5 | 1000 | 0 | 1 | 6 | 0 | 6 | half a sen rounds up |
  | 25 | 1000 | 0 | 3 | 28 | 0 | 28 | 2.5 rounds up (banker's rounding would give 2) |
  | 4 | 1000 | 0 | 0 | 4 | 0 | 4 | 0.4 rounds down |
  | 1000 | 0 | 0 | 0 | 1000 | 0 | 1000 | both charges off |
  | 5000 | 1250 | 625 | 625 | 5625 | 352 | 5977 | decimal rates (SST 351.5625 rounds up) |
  | 9999999 | 3000 | 2000 | 3000000 | 12999999 | 2600000 | 15599999 | largest even-mode bill |
  | 499999950 | 3000 | 2000 | 149999985 | 649999935 | 129999987 | 779999922 | largest by-item bill |
- **R7. Even allocation.** `allocateEvenly(amount, count)` returns `count` integers. Each is floor(amount / count), and the first (amount mod count) entries get one more cent. They sum to `amount` exactly and differ by at most 1, with the larger ones first.

  | amount | count | result |
  |---|---|---|
  | 11660 | 3 | [3887, 3887, 3886] (S2) |
  | 1800 | 2 | [900, 900] (the S1 satay) |
  | 1001 | 3 | [334, 334, 333] |
  | 1 | 3 | [1, 0, 0] |
  | 0 | 2 | [0, 0] |
  | 10221 | 4 | [2556, 2555, 2555, 2555] |
  | 15599999 | 12 | eleven times 1300000, then 1299999 |
- **R8. Proportional allocation.** `allocateByWeight(amount, weights)` returns one integer per weight. Entry i is floor(amount x weight_i / sum of weights), computed exactly with `BigInt`. The leftover cents (amount minus the sum of those floors) go one each to the entries with the lowest index whose weight is above 0. An entry with weight 0 always gets 0. The result sums to `amount` exactly.

  | amount | weights | result | what it proves |
  |---|---|---|---|
  | 986 | [2490, 1350, 2100] | [414, 224, 348] | S1 golden charges |
  | 10 | [0, 1, 1, 1] | [0, 4, 3, 3] | the leftover skips a zero weight |
  | 0 | [5, 7] | [0, 0] | no charges |
  | 249 | [0, 1251, 250] | [0, 208, 41] | example I2 in `qa.md` |
  | 236419679 | [314963010, 157876348] | [157481505, 78938174] | ~~naive `Math.floor(a * w / W)` gives [157481506, 78938173]~~ [Changed 2026-10-09, ORCH, code-review WR-01: BigInt trap. A float allocator (Math.floor of a x w / W, then the leftover rule) gives [157481506, 78938173]. The floors alone are [157481505, 78938173].] |
  | 61846725 | [49676084, 322894546] | [8246230, 53600495] | [Added 2026-10-09, ORCH, WR-01] BigInt trap. A float allocator gives [8246231, 53600494]. The amount is the charges total of a 372570630 subtotal at 10% and 6%. |
  | 178450942 | [111531837, 207130558] | [62457829, 115993113] | [Added 2026-10-09, ORCH, WR-01] BigInt trap. A float allocator gives [62457830, 115993112]. The amount is the charges total of a 318662395 subtotal at 30% and 20%. |

  [Added 2026-10-09, ORCH, code-review WR-01] A float allocator agrees with the exact one on almost every input, MAX-I included. It differs only on specific inputs where amount x weight passes 2^53, so the float product is rounded and a floor moves by one sen. The rows marked BigInt trap are such inputs, and each test checks that a float allocator misses its row.
- **R9. Allocation preconditions.** `allocateEvenly` throws `RangeError` when `count` is not an integer of at least 1 or `amount` is not a non-negative safe integer. `allocateByWeight` throws `RangeError` when `weights` is empty, a weight is not a non-negative safe integer, the weights sum to 0, or `amount` is not a non-negative safe integer.

### Bill state rules (C1, C3, C7, C8)
- **R10. New bill.** `newBill()` returns exactly `{ mode: "even", people: [{ id: "p1", name: "Person 1" }, { id: "p2", name: "Person 2" }], subtotalText: "", items: [], serviceText: "10", sstText: "6", nextId: 3 }`.
- **R11. Add person.** `addPerson(bill)` appends `{ id: "p" + nextId, name: "" }` and increments `nextId`. With 12 people it returns the input unchanged (same reference). The new person is on no item. [The empty name is CG-1, ruled 2026-10-08, ORCH. Accepted as written.]
- **R12. Remove person.** `removePerson(bill, personId)` removes that person from `people` and removes their id from the `who` of every item. With 2 people, or with an unknown id, it returns the input unchanged (same reference).
- **R13. Add and remove item.** `addItem(bill)` appends `{ id: "i" + nextId, name: "", priceText: "", who: [] }` and increments `nextId`. With 50 items it returns the input unchanged. `removeItem(bill, itemId)` removes that item, or returns the input unchanged for an unknown id.
- **R14. Tap a person on an item.** `toggleItemPerson(bill, itemId, personId)` adds `personId` to that item's `who` when absent and removes it when present. The order of ids in `who` carries no meaning. An unknown item or person id returns the input unchanged.
- **R15. Field setters.** `setPersonName`, `setItemName`, `setItemPriceText`, `setSubtotalText`, `setServiceText`, `setSstText` and `setMode` replace exactly one field and keep everything else. `setMode` changes only `mode`, so `subtotalText` and `items` both survive any number of switches. Setters store the text exactly as given (no trimming, no parsing). `setMode` with a value other than `"even"` or `"item"` returns the input unchanged.
- **R16. Purity.** No exported function mutates its arguments (a deep-frozen input never throws), and every action that changes something returns a new `Bill` object.
- **R17. Display names.** `personLabel(person, index)` returns `person.name.trim()` when that is not empty, otherwise `"Person " + (index + 1)`. `itemLabel(item, index)` does the same with `"Item " + (index + 1)`. `index` is the 0-based position in the current list, so the fallback follows the position after a removal.

### The result (C2, C3, C5, RULINGS 3)
- **R18. Blocking order.** `computeResult(bill)` returns `{ kind: "blocked", reason }` for the first rule that applies, in this order. (a) `"rates"` when `serviceText` fails `parseRate(_, 30)` or `sstText` fails `parseRate(_, 20)` (empty or invalid). (b) `"subtotal"` in even mode when `subtotalText` fails `parseAmount`. (c) `"no-items"` in by-item mode when there are no items. (d) `"prices"` in by-item mode when any item's `priceText` fails `parseAmount`. Even mode ignores `items`, and by-item mode ignores `subtotalText`.
- **R19. Unassigned items.** In by-item mode, when every price is valid but one or more items have an empty `who`, `computeResult` returns `{ kind: "unassigned", count, charges }`, where `count` is the number of such items and `charges` is `billCharges` of the sum of all item prices (the bill summary stays visible, ruling 3e).
- **R20. Even result.** In even mode with valid rates and subtotal, `computeResult` returns `{ kind: "even", charges, rows, check }`. `charges` is `billCharges(subtotal, serviceBp, sstBp)`. `rows` has one `{ name, share }` per person in list order, `name` is `personLabel`, and the shares are `allocateEvenly(charges.total, people.length)`. `check.share` is the sum of the row shares.
- **R21. By-item result.** In by-item mode with valid rates, at least one item, every price valid and every item tapped, `computeResult` returns `{ kind: "item", charges, rows, check }`. (1) Each item's price is split with `allocateEvenly` over the people on it, taken in **people-list order** (not tap order), so leftover sen go to whoever is highest in the list. (2) A person's `items` is the sum of their parts. (3) `charges` is `billCharges` of the sum of all prices. (4) The charges total (service + sst) is split with `allocateByWeight` using each person's `items` as the weight. (5) `share` = `items` + that person's charges part. `rows` has one `{ name, items, charges, share }` per person in list order, including people with nothing (all three values 0). `check` is `{ items, charges, share }`, each the sum of that column.
- **R22. The shares always add up.** For every `even` and `item` result, `check.share === charges.total`. For `item` results also `check.items === charges.subtotal` and `check.charges === charges.service + charges.sst`. Even-mode shares differ by at most 1 sen with the larger ones at the top. Every value is a non-negative safe integer.
- **R23. Bounds.** The largest bills compute exactly (see the MAX rows in `qa.md`). Twelve people, a 99,999.99 subtotal, 30% and 20% give a total of 15599999 and shares of eleven times 1300000 then 1299999. Fifty items at 99,999.99, item k tapped by person (k mod 12), 30% and 20% give items [49999995, 49999995, then ten times 39999996], charges [27999998, 27999998, six times 22399998, four times 22399997], shares [77999993, 77999993, six times 62399994, four times 62399993] and a total of 779999922. ~~A floating-point implementation gets these charges wrong.~~ [Changed 2026-10-09, ORCH, code-review WR-01: that sentence was false. A float allocator still gets MAX-I right. The BigInt guard is the R8 rows marked BigInt trap.]

### Summary text (C6)
- **R24. Summary text.** `summaryText(result)` takes an `even` or `item` result and returns these lines joined with `"\n"` and no trailing newline. Line 1 is `Bill split`. Line 2 is `Total <total> (subtotal <subtotal>, service <service rate> <service>, SST <SST rate> <sst>)` with money from `formatMoney` and rates from `formatRate`. Then one line per row in list order, `<name> <share>`. The last line is `Adds up to <check.share>`. Rates of 0 still print (`service 0% RM 0.00`). Any other `result.kind` throws `TypeError`. For the S2 bill the text is exactly

  ```
  Bill split
  Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)
  Aisyah RM 38.87
  Ben RM 38.87
  Chen RM 38.86
  Adds up to RM 116.60
  ```

  and for the S1 bill exactly

  ```
  Bill split
  Total RM 69.26 (subtotal RM 59.40, service 10% RM 5.94, SST 6% RM 3.92)
  Aisyah RM 29.04
  Ben RM 15.74
  Chen RM 24.48
  Adds up to RM 69.26
  ```

### Hygiene
- **R25. Pure module.** Files under `src/core/` import only from `src/core/`. They do not reference `window`, `document`, `globalThis`, `localStorage`, `sessionStorage`, `navigator`, `fetch`, `XMLHttpRequest`, `Date`, `Math.random`, `parseFloat`, `Number.parseFloat` or `toFixed`. They load and pass under `node --test` with no DOM shim.

### Names (C1, added 2026-10-08 after the plan check)
- **R26. Duplicate names are allowed.** The brainstorm rule "Duplicate names are allowed" had no requirement. A name is a label and never an identity, and people are addressed by `id` only. `setPersonName` stores a name that equals another person's name, whether it matches exactly, after trimming or only in letter case, and no function rejects, merges, renames or reorders people because of it. `computeResult` gives one row per person, so two people called "Ben" give two rows with the same `name`, each with its own share. `toggleItemPerson` and `removePerson` act on the person with the given id, so tapping or removing one of two people called "Ben" never touches the other. `summaryText` prints one line per row, so both "Ben" lines appear. Examples D1 (even) and D2 (by item) are in `qa.md`.

## Contracts

### Files
| File | Exports |
|---|---|
| `src/core/money.js` | `parseAmount`, `parseRate`, `formatMoney`, `formatRate`, `AMOUNT_MIN_CENTS` (1), `AMOUNT_MAX_CENTS` (9999999) |
| `src/core/allocate.js` | `allocateEvenly`, `allocateByWeight` |
| `src/core/bill.js` | `LIMITS`, `newBill`, `addPerson`, `removePerson`, `setPersonName`, `setMode`, `setSubtotalText`, `setServiceText`, `setSstText`, `addItem`, `removeItem`, `setItemName`, `setItemPriceText`, `toggleItemPerson`, `personLabel`, `itemLabel` |
| `src/core/result.js` | `billCharges`, `computeResult` |
| `src/core/summary.js` | `summaryText` |

No other exports. Helpers stay module-private.

### Types (JSDoc in the source, shown here as the contract)
```js
/** @typedef {"even" | "item"} Mode */
/** @typedef {{ id: string, name: string }} Person */              // id is "p" + a positive integer
/** @typedef {{ id: string, name: string, priceText: string, who: string[] }} Item */  // id is "i" + a positive integer
/**
 * @typedef {{
 *   mode: Mode, people: Person[], subtotalText: string, items: Item[],
 *   serviceText: string, sstText: string, nextId: number
 * }} Bill
 */
/** @typedef {{ ok: true, cents: number } | { ok: false, empty: boolean }} AmountResult */
/** @typedef {{ ok: true, bp: number } | { ok: false, empty: boolean }} RateResult */
/**
 * @typedef {{ subtotal: number, serviceBp: number, service: number,
 *             sstBp: number, sstBase: number, sst: number, total: number }} Charges
 */
/** @typedef {{ name: string, share: number }} EvenRow */
/** @typedef {{ name: string, items: number, charges: number, share: number }} ItemRow */
/**
 * @typedef {
 *   | { kind: "blocked", reason: "rates" | "subtotal" | "no-items" | "prices" }
 *   | { kind: "unassigned", count: number, charges: Charges }
 *   | { kind: "even", charges: Charges, rows: EvenRow[], check: { share: number } }
 *   | { kind: "item", charges: Charges, rows: ItemRow[],
 *       check: { items: number, charges: number, share: number } }
 * } Result
 */
```

### Constants
```js
export const LIMITS = Object.freeze({
  minPeople: 2, maxPeople: 12, maxItems: 50,
  personNameMax: 20, itemNameMax: 40,          // used by split-app for maxlength and the draft decoder
  serviceMaxPercent: 30, sstMaxPercent: 20,
});
```

### Functions
| Signature | Behaviour |
|---|---|
| `parseAmount(text: string): AmountResult` | R1, R2 |
| `parseRate(text: string, maxPercent: number): RateResult` | R2, R3 |
| `formatMoney(cents: number): string` | R4 |
| `formatRate(bp: number): string` | R5 |
| `allocateEvenly(amount: number, count: number): number[]` | R7, R9 |
| `allocateByWeight(amount: number, weights: number[]): number[]` | R8, R9 |
| `newBill(): Bill` | R10 |
| `addPerson(bill: Bill): Bill` | R11 |
| `removePerson(bill: Bill, personId: string): Bill` | R12 |
| `addItem(bill: Bill): Bill` · `removeItem(bill: Bill, itemId: string): Bill` | R13 |
| `toggleItemPerson(bill: Bill, itemId: string, personId: string): Bill` | R14 |
| `setPersonName(bill, personId, name)` · `setItemName(bill, itemId, name)` · `setItemPriceText(bill, itemId, text)` · `setSubtotalText(bill, text)` · `setServiceText(bill, text)` · `setSstText(bill, text)` · `setMode(bill, mode)`, each returning `Bill` | R15 |
| `personLabel(person: Person, index: number): string` · `itemLabel(item: Item, index: number): string` | R17 |
| `billCharges(subtotal: number, serviceBp: number, sstBp: number): Charges` | R6 |
| `computeResult(bill: Bill): Result` | R18 to R22 |
| `summaryText(result: Result): string` | R24 |

### Persistence and state
None. This module holds no state. `split-app` stores a `Bill` in its draft envelope (see `split-app/spec.md`).

## Tasks
Each task is one commit, adds its `node --test` cases (named `@R<n> ...`) and leaves `node --test "tests/**/*.test.js"` green.
1. [ ] `src/core/money.js` parsing (`parseAmount`, `parseRate`, the two constants) with `tests/money.test.js` parsing cases. -> R1, R2, R3
2. [ ] `src/core/money.js` formatting (`formatMoney`, `formatRate`) with their cases. -> R4, R5
3. [ ] `src/core/allocate.js` with `tests/allocate.test.js`, including the BigInt trap case and the precondition throws. -> R7, R8, R9
4. [ ] `src/core/bill.js` (`LIMITS`, `newBill`, every action, the labels) with `tests/bill.test.js`, including the deep-freeze purity test and the duplicate-name cases (equal names stored, tap and remove by id). -> R10, R11, R12, R13, R14, R15, R16, R17, R26
5. [ ] `src/core/result.js` (`billCharges`, `computeResult`) with `tests/result.test.js`: the charges table, the blocking-order table, S1, S2, S5, I2, I3, I4, E1, E3, D1, D2 and the two MAX bills. -> R6, R18, R19, R20, R21, R23, R26
6. [ ] `tests/invariants.test.js`, a seeded sweep over generated bills checking R22 (no new source). -> R22
7. [ ] `src/core/summary.js` with `tests/summary.test.js` (S1, S2, E2 zero rates, E3 decimal rates, I2 zero share, D1 and D2 equal names, blank-name fallback, the TypeError). -> R24, R26
8. [ ] `tests/hygiene.test.js`, a static scan of `src/core/` for the banned names and foreign imports. -> R25

## Threat model
| Asset | Trust boundary | Threat | Required mitigation |
|---|---|---|---|
| Correct shares (people pay what the screen says) | Text typed by the user or read from storage enters `parseAmount` and `parseRate` | Floating-point drift (`1.15` read as 114 sen) or a precision loss above 2^53 gives a wrong share that still looks plausible | R1, R3 integer-only parsing. R6, R7 exact integer division. R8 `BigInt` products. ~~R23 bound tests.~~ [Changed 2026-10-09, ORCH, WR-01: R8 BigInt trap rows. The R23 bound tests prove the MAX bills are exact, and a float allocator passes them too.] R25 bans `parseFloat` and `toFixed`. |
| Correct shares | Same | A rounding rule that differs from the brainstorm (banker's rounding, rounding each share instead of allocating leftovers) | R6 half-up table rows (5, 25, 8765). R7, R8 leftover order. R22 sum invariant over a generated sweep. |
| Availability of the page | Arbitrary strings, including very long ones from storage | Catastrophic regex backtracking or an exception on odd input freezes or breaks rendering | The grammar is a single linear pattern with no nested quantifier. Parsing checks the digit count before any numeric conversion ~~(400-digit case in R1)~~ [Changed 2026-10-09, ORCH, code-review WR-06: the cap is the digit count of the caller's ceiling, derived once in `readHundredths`. Its proof is the R1/R3 test that spies on numeric conversion. The 400-digit R1 row proves only "invalid, no exception", which holds with or without the cap.]. R2 says the parsers never throw for a string. |
| Clipboard text integrity | Names flow into `summaryText` | A name with a line break forges an extra line such as a fake "Adds up to" in the group chat | Invariant that names never hold CR or LF (the input strips them, the `split-app` decoder rejects them). `summaryText` writes one line per row and nothing else. |
| Object integrity | `Bill` objects may come from parsed JSON | Prototype pollution through `__proto__` keys when copying objects | Actions build new objects from known fields only. No `Object.assign` or spread of a whole parsed object onto a target. |

Residual risk accepted. None in this module beyond what `split-app` documents.

## Non-goals
Do NOT build any of the following. Building one is a defect.
- Payments, transfer links or DuitNow QR.
- Currencies other than ringgit, currency conversion, other languages or locale-aware number formats (no `Intl.NumberFormat`, no group separators, CG-5 ruled 2026-10-08, ORCH).
- 5-sen cash rounding.
- Tips, discounts, vouchers, per-item tax exemptions, or any charge besides service charge and SST.
- A history of past bills or more than one bill.
- Any DOM, storage, clipboard, network or timer code (that is `split-app`, or nothing at all).
- Generic helpers nobody calls (a money class, a rounding-mode option, configurable currency, an undo stack).
