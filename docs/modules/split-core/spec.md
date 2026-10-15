# Module: split-core

> Build contract. Read by the builder. Build ONLY what is here.
> Stack is LOCKED to the project stack (vanilla JavaScript ES modules, zero dependencies, Node 24 for tests).
> Depends on nothing. Nature is pure logic (no DOM, no storage, no network, no clock, no randomness of its own. Since v1.1.0 a caller passes a random number function into the two spare sen draws, R29 and R31).
> Sources are `docs/brainstorm/brainstorm.md` (rules, and its "v1.1.0 delta" section), `docs/design/RULINGS.md` (rulings 1 to 4), `docs/design/RULINGS-v1.1.0.md` (the blocked receipt order a to e), `docs/design-explore/v1.1.0/final/SELF-CRITIQUE.md` (interaction rules 8 and 9), `docs/design/system.md` (money format), and the numbers in `docs/design/bill-items.md`, `bill-even.md`, `spare-sen-one.md`, `spare-sen-random.md` and `bill-large.md`.

## v1.1.0 delta
Written 2026-10-13 by the planner (solutions architect role). The 1.0 text of every changed requirement is in git tag `v1.0.0`. Scopes are the ones in `docs/v1.1.0/CHANGE-LEDGER.md`.

| R# | Status | Scope | What changed |
|---|---|---|---|
| R4 | Changed | S7 | `formatMoney` writes a thousands comma from RM 1,000 (the v1.1.0 design system replaces CG-5) |
| R10 | Changed | S1 | A new bill carries `spare: { rule: "top" }` |
| R11 | Changed | S1 | Adding a person also extends the drawn order when the rule is At random |
| R12 | Changed | S1 | Removing a person also leaves the drawn order, and a removed chosen person resets the rule to Top of the list |
| R18 | Changed | S7 | Row (c) widens from "no items" to "no item has a valid price", reason `"no-prices"` (RULINGS-v1.1.0 row c) |
| R20 | Changed | S1 | Even shares hand their spare sen out by the spare rule, and the result carries `spare` |
| R21 | Changed | S1 | Item and charges spare sen follow the spare rule, and the result carries `spare` |
| R22 | Changed | S1 | The sums hold under every spare rule. The "at most 1 sen apart" rule is stated per rule |
| R24 | Changed | S1, S7 | Same six lines. Shares as chosen. Money as `formatMoney` writes it now (CG-P1, ruled 2026-10-13 by the owner as recommended, ledger S1 row 2) |
| R27 | New | S1 | The spare choice is part of the bill |
| R28 | New | S1 | Who can take the spare sen |
| R29 | New | S1 | Choosing the rule, with the draw for At random |
| R30 | New | S1 | Choosing the one person |
| R31 | New | S1 | Pick again |
| R32 | New | S1 | Where every spare sen goes, and how many there are |
| R33 | New | S1 | The result names the rule in effect |
| R34 | New | S7 | `formatAmount`, a money figure without "RM" |
| R35 | New | S7 (H-10, SEC-S5-1) | `plainName`, a name with every character of R24's class removed. The class is written once in `src/core/` and read by both. Added 2026-10-16 in execute |

No requirement is retired. R1 to R3, R5 to R9, R13 to R17, R19, R23, R25 and R26 are unchanged. R16 and R25 cover the new exports by their own wording, so their tests grow (see `qa.md`).

Changed 2026-10-13 after the plan check (`docs/modules/PLAN-CHECK.md`, F1, F3, F4, F7, F10). The clarify items this module names (CG-P1 to CG-P3) are ruled, the R31 note states the true bound, task C3 carries PD-24, the RED-first method for a new Node case is named, and four prose colons are gone. No requirement changed its meaning.

Changed 2026-10-16 in execute, planner pass for H-10 and the step 5 wording (ledger H-10, S7 rows 40 to 43). The owner ruled H-10 on 2026-10-16 00:07, option (1) (USER), "remove control and bidi characters from names, at the name input and in the draft decoder". The app does the removing (app R62), and this module gives it the one function, new R35 `plainName`, so the class that `summaryText` prints as a space (R24) and the class the app removes are one definition. Task C7 builds it, right before app task A22. R7 says why `allocateEvenly` stays exported with no caller in `src/` (code review CR-S5-4, PD-25 in `docs/modules/ROADMAP.md`). The threat model row "Object integrity" names the one list of Bill fields that the step 5 solver round made (CR-S5-2). Counts are now new 9 (R27 to R35), changed 9, unchanged 17, retired 0, total 35. Each change carries its own dated note.

Changed 2026-10-16 in execute, planner touch after the step 5 re-check (ledger S7 rows 45 and 46, ORCH). One clause of R35 point 2 is reworded, "replaces c with a space" in place of "prints c as a space", with the old text struck in place. No R# is added or changes status, so the counts above stand.

## Module roadmap
- **Build order.** First. Nothing depends on anything else here, and `split-app` imports it.
- **Done when.** Every R# below has a passing `node --test` case (see `qa.md`), the code-review and security finders pass, and the reverse audit finds no exported symbol without an R#.
- **v1.1.0 build order.** After the WebKit switch and baseline (split-app task A0), before any split-app UI task. Core tasks C1 to C6 below. The 1.0 suite must stay green on every commit, because Top of the list keeps every 1.0 number. [Added 2026-10-16 in execute, H-10. C7 builds after the step 5 solver round and right before app task A22, in one build with it, because A22 imports `plainName`.]
- **Shape change from the expected shape, with the reason.** Besides money parsing, bill maths, cent allocation and the summary text, this module also owns the **bill state rules** (the `Bill` shape, the defaults of a new bill, people and item limits, "removing a person removes them from every item", the display-name fallback and the order of the blocking messages). They are DOM-free rules from the brainstorm and `RULINGS.md`, so they get exact, fast unit tests here, and `split-app` stays a thin browser shell that never edits arrays itself.

## Invariants & assumptions
- Every money value is a non-negative integer number of cents (sen). No money value is ever a fraction.
- Every charge rate is a non-negative integer number of basis points (hundredths of a percent). 10% is 1000, 6.25% is 625.
- No money calculation passes through floating point. Division is exact integer division. Any product that can exceed `Number.MAX_SAFE_INTEGER` (9007199254740991) is computed with `BigInt`.
- Bounds that make the arithmetic safe. An amount is at most 9,999,999 cents. A by-item subtotal is at most 50 x 9,999,999 = 499,999,950 cents. Rates are at most 3000 bp (service) and 2000 bp (SST). The largest charges total is 279,999,972 cents, so `charges x weight` can reach ~~about 1.4e16~~ [Changed 2026-10-09, ORCH, code-review WR-02: about 1.4e17, that is 279,999,972 x 499,999,950 when one person holds every item. 1.4e16 was the MAX-I product 279,999,972 x 49,999,995.] and needs `BigInt`. Every other product stays below 2^53. [Added 2026-10-09, WR-02: the largest of them is the service step, 499,999,950 x 3000, about 1.5e12.]
- Text fields of a `Bill` (names and the raw texts of amounts and rates) are held exactly as typed. Parsing happens on read, never on write.
- A name never contains U+000A or U+000D. The browser strips them from `<input type="text">` values, and `split-app`'s draft decoder rejects them. ~~Core relies on this and does not re-check.~~ [Changed 2026-10-09, ORCH, code-review WR-10, security: the input does not strip U+000B, U+000C, U+0085, U+2028 or U+2029, and some chat clients render them as line breaks. `summaryText` no longer relies on this invariant. It prints every line-breaking character in a name as a space (R24).] [Changed 2026-10-09, ORCH, security SEC-01: the set is now ~~every control character and separator~~, see R24.] [Changed 2026-10-09, ORCH, security re-check wording: "every control character and separator" was looser than the code. The set is exactly `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]`: the C0 and C1 controls, the line separator U+2028, the paragraph separator U+2029 and the bidi controls. Space separators such as NBSP (U+00A0) and U+3000 are kept.] [Added 2026-10-16 in execute, H-10. Since app R62 the app removes that same class from every person and item name, at the name inputs and in the draft decoder, with `plainName` (R35), so a name the app hands to core holds none of it. Core's own actions still store a name exactly as given (R15), and `summaryText` still prints the class as a space, so core does not rely on the app for this.]
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
- **R4. Money format.** (v1.1.0 changed) `formatMoney(cents)` returns `"RM "` followed by `formatAmount(cents)` (R34). Examples are 0 to `RM 0.00`, 1 to `RM 0.01`, 10 to `RM 0.10`, 100 to `RM 1.00`, 3887 to `RM 38.87`, 11660 to `RM 116.60`, 99999 to `RM 999.99`, 100000 to `RM 1,000.00`, 119387 to `RM 1,193.87`, 15599999 to `RM 155,999.99`, 779999922 to `RM 7,799,999.22`. [Changed 2026-10-13, v1.1.0, S7. CG-5 (no group separator, ruled 2026-10-08, ORCH) is replaced by the approved v1.1.0 design system, `docs/design/system.md` Type, "Money is always written `RM 38.87`, with a thousands comma from 1,000", and the W1 golden `bill-large.html` (RM 1,193.87).]
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

  [Added 2026-10-16 in execute, code review CR-S5-4, PD-25 in `docs/modules/ROADMAP.md` (ORCH, reversible).] Since C4, `computeResult` splits each division with its own floor step, so no file under `src/` calls `allocateEvenly`. It stays exported and tested as R7 says, because it is the definition of Top of the list. R20 states the even shares under `{ rule: "top" }` as exactly `allocateEvenly(charges.total, people.length)`, and the tests use it as that oracle (`assertEvenRule` in `tests/invariants.test.js`). So the non-goal "Generic helpers nobody calls" does not cover it. Removing it would move R20's definition into a test helper and retire R7, a contract change with no gain for the user.
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
- **R10. New bill.** (v1.1.0 changed) `newBill()` returns exactly `{ mode: "even", people: [{ id: "p1", name: "Person 1" }, { id: "p2", name: "Person 2" }], subtotalText: "", items: [], serviceText: "10", sstText: "6", spare: { rule: "top" }, nextId: 3 }`. [Changed 2026-10-13, v1.1.0, S1. The `spare` field, R27. Top of the list is the default (brainstorm v1.1.0, capability C9).]
- **R11. Add person.** (v1.1.0 changed) `addPerson(bill)` appends `{ id: "p" + nextId, name: "" }` and increments `nextId`. With 12 people it returns the input unchanged (same reference). The new person is on no item. [The empty name is CG-1, ruled 2026-10-08, ORCH. Accepted as written.] [Added 2026-10-13, v1.1.0, S1. When `spare.rule` is `"random"`, the new id is also appended to the end of `spare.order`, so the order keeps every person of the bill (R27) and the people already drawn keep their places.]
- **R12. Remove person.** (v1.1.0 changed) `removePerson(bill, personId)` removes that person from `people` and removes their id from the `who` of every item. With 2 people, or with an unknown id, it returns the input unchanged (same reference). [Added 2026-10-13, v1.1.0, S1. It also removes the id from `spare.order` when the rule is `"random"`, and when the rule is `"one"` with that `personId` the spare choice becomes `{ rule: "top" }`. The source is interaction rule 8 of `SELF-CRITIQUE.md`, approved in `RULINGS-v1.1.0.md`, "If the chosen person is removed, the rule falls back to Top of the list".]
- **R13. Add and remove item.** `addItem(bill)` appends `{ id: "i" + nextId, name: "", priceText: "", who: [] }` and increments `nextId`. With 50 items it returns the input unchanged. `removeItem(bill, itemId)` removes that item, or returns the input unchanged for an unknown id.
- **R14. Tap a person on an item.** `toggleItemPerson(bill, itemId, personId)` adds `personId` to that item's `who` when absent and removes it when present. The order of ids in `who` carries no meaning. An unknown item or person id returns the input unchanged.
- **R15. Field setters.** `setPersonName`, `setItemName`, `setItemPriceText`, `setSubtotalText`, `setServiceText`, `setSstText` and `setMode` replace exactly one field and keep everything else. `setMode` changes only `mode`, so `subtotalText` and `items` both survive any number of switches. Setters store the text exactly as given (no trimming, no parsing). `setMode` with a value other than `"even"` or `"item"` returns the input unchanged.
- **R16. Purity.** No exported function mutates its arguments (a deep-frozen input never throws), and every action that changes something returns a new `Bill` object.
- **R17. Display names.** `personLabel(person, index)` returns `person.name.trim()` when that is not empty, otherwise `"Person " + (index + 1)`. `itemLabel(item, index)` does the same with `"Item " + (index + 1)`. `index` is the 0-based position in the current list, so the fallback follows the position after a removal.

### The result (C2, C3, C5, RULINGS 3)
- **R18. Blocking order.** (v1.1.0 changed) `computeResult(bill)` returns `{ kind: "blocked", reason }` for the first rule that applies, in this order. (a) `"rates"` when `serviceText` fails `parseRate(_, 30)` or `sstText` fails `parseRate(_, 20)` (empty or invalid). (b) `"subtotal"` in even mode when `subtotalText` fails `parseAmount`. (c) `"no-prices"` in by-item mode when no item has a valid price, that is when there are no items or every item's `priceText` fails `parseAmount`. (d) `"prices"` in by-item mode when at least one item's `priceText` passes `parseAmount` and at least one other fails it. Even mode ignores `items`, and by-item mode ignores `subtotalText`. [Changed 2026-10-13, v1.1.0, S7. `RULINGS-v1.1.0.md`, "The receipt when the bill cannot be worked out", row c widens 1.0's (c) from "no items" to "no item has a valid price" ("Add each item and tap who had it to see the splits."), and row d keeps "Give every item a price to see the splits." for the rest. The reason `"no-items"` is renamed `"no-prices"` so its name says what it tests. A blank rate never counts as 0 (row a).]
- **R19. Unassigned items.** In by-item mode, when every price is valid but one or more items have an empty `who`, `computeResult` returns `{ kind: "unassigned", count, charges }`, where `count` is the number of such items and `charges` is `billCharges` of the sum of all item prices (the bill summary stays visible, ruling 3e).
- **R20. Even result.** (v1.1.0 changed) In even mode with valid rates and subtotal, `computeResult` returns `{ kind: "even", charges, rows, check, spare }`. `charges` is `billCharges(subtotal, serviceBp, sstBp)`. `rows` has one `{ name, share }` per person in list order, `name` is `personLabel`. The shares are `charges.total` split in equal floor parts over the people, with the spare sen handed out by the spare rule (R32). With `spare` `{ rule: "top" }` they are exactly `allocateEvenly(charges.total, people.length)`, as in 1.0. `check.share` is the sum of the row shares. `spare` is R33. [Changed 2026-10-13, v1.1.0, S1.]
- **R21. By-item result.** (v1.1.0 changed) In by-item mode with valid rates, every price valid and every item tapped, `computeResult` returns `{ kind: "item", charges, rows, check, spare }`. (1) Each item's price is split in equal floor parts over the people on it, taken in **people-list order** (not tap order), and the item's spare sen go by the spare rule (R32). With Top of the list that is `allocateEvenly` over the people on it in list order, so leftover sen go to whoever is highest in the list, as in 1.0. (2) A person's `items` is the sum of their parts. (3) `charges` is `billCharges` of the sum of all prices. (4) The charges total (service + sst) is split in floor parts weighted by each person's `items`, computed exactly as in R8, and its spare sen go by the spare rule. With Top of the list that is exactly `allocateByWeight(service + sst, items)`. (5) `share` = `items` + that person's charges part. `rows` has one `{ name, items, charges, share }` per person in list order, including people with nothing (all three values 0). `check` is `{ items, charges, share }`, each the sum of that column. `spare` is R33. [Changed 2026-10-13, v1.1.0, S1. "Every leftover sen follows it: the even split's remainder, a shared item's remainder, and the charges' remainder in by-item mode" (brainstorm v1.1.0 rules). "At least one item" is now part of R18 (c).]
- **R22. The shares always add up.** (v1.1.0 changed) For every `even` and `item` result, under every spare rule, `check.share === charges.total`. For `item` results also `check.items === charges.subtotal`, `check.charges === charges.service + charges.sst`, and a person whose `items` is 0 has `charges` 0. In even mode, under Top of the list the shares differ by at most 1 sen with the larger ones at the top (1.0), under At random they differ by at most 1 sen, and under One person every share is floor(total / people) except the chosen person's, which is that plus `spare.count`. Every value is a non-negative safe integer. [Changed 2026-10-13, v1.1.0, S1. "The shares always add up to the total, whichever choice is set" (brainstorm v1.1.0 rules).]
- **R23. Bounds.** The largest bills compute exactly (see the MAX rows in `qa.md`). Twelve people, a 99,999.99 subtotal, 30% and 20% give a total of 15599999 and shares of eleven times 1300000 then 1299999. Fifty items at 99,999.99, item k tapped by person (k mod 12), 30% and 20% give items [49999995, 49999995, then ten times 39999996], charges [27999998, 27999998, six times 22399998, four times 22399997], shares [77999993, 77999993, six times 62399994, four times 62399993] and a total of 779999922. ~~A floating-point implementation gets these charges wrong.~~ [Changed 2026-10-09, ORCH, code-review WR-01: that sentence was false. A float allocator still gets MAX-I right. The BigInt guard is the R8 rows marked BigInt trap.]

### Summary text (C6)
- **R24. Summary text.** (v1.1.0 changed) [Changed 2026-10-13, v1.1.0, S1 and S7. The lines stay the six-line 1.0 format and each row prints the share as the spare rule left it (the result's own rows), so the copied text matches the splits on screen. No line about spare sen is added. Money is `formatMoney`, so a bill from RM 1,000 prints its thousands comma (`Total RM 1,193.87 (subtotal RM 1,023.90, ...)`). ~~That last point waits on clarify item CG-P1 in `docs/modules/ROADMAP.md`.~~ Changed 2026-10-13 after the plan check (F1). The owner ruled CG-P1 as recommended on 2026-10-13, "Yes, same as the screen" (USER, ledger S1 row 2). Below RM 1,000 every line is byte for byte the 1.0 text.] `summaryText(result)` takes an `even` or `item` result and returns these lines joined with `"\n"` and no trailing newline. Line 1 is `Bill split`. Line 2 is `Total <total> (subtotal <subtotal>, service <service rate> <service>, SST <SST rate> <sst>)` with money from `formatMoney` and rates from `formatRate`. Then one line per row in list order, `<name> <share>`. The last line is `Adds up to <check.share>`. Rates of 0 still print (`service 0% RM 0.00`). Any other `result.kind` throws `TypeError`. [Added 2026-10-09, ORCH, code-review WR-10, security: in each row's `<name>`, every line-breaking character (U+000A LF, U+000D CR, U+000B VT, U+000C FF, U+0085 NEL, U+2028 LS, U+2029 PS) is replaced by one space, so a name can never start a new line in the copied text. Rows carry person labels only, since item labels do not appear in the summary.] [Changed 2026-10-09, ORCH, security SEC-01: the replaced set is widened from those seven to every character in `[\p{Cc}\p{Zl}\p{Zp}]` (all C0 and C1 controls, which include the seven, plus LS and PS), each replaced by one space. Other readers end a line or the whole text at controls outside the seven: NUL (U+0000) ends a C-string clipboard and would leave a forged last line, and FS, GS and RS (U+001C to U+001E) end a line for Python's `splitlines`. ESC (U+001B) starts a terminal sequence.] [Changed 2026-10-09, ORCH, security SEC-02: the set also takes `\p{Bidi_Control}` (U+061C, U+200E, U+200F, U+202A to U+202E, U+2066 to U+2069), so the class is `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]`. A name ending in RLO (U+202E) made a bidi-aware renderer draw the rest of its row right to left, so "RM 38.87" read "78.83 MR".] [Added 2026-10-16 in execute, H-10. The class is written once in `src/core/`, and `summaryText` reads that one definition, which `plainName` (R35) also reads. The text `summaryText` returns does not change.] For the S2 bill the text is exactly

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
- **R25. Pure module.** Files under `src/core/` import only from `src/core/`. They do not reference `window`, `document`, `globalThis`, `localStorage`, `sessionStorage`, `navigator`, `fetch`, `XMLHttpRequest`, `Date`, `Math.random`, `parseFloat`, `Number.parseFloat` or `toFixed`. They load and pass under `node --test` with no DOM shim. [Added 2026-10-09, ORCH, code-review WR-07: nor `Intl`, `toLocaleString`, `toLocaleDateString`, `setTimeout`, `setInterval` or `requestAnimationFrame`, so the non-goals "no locale-aware number formats" and "no timer code" are enforced by the same scan.] [Added 2026-10-09, ORCH, security SEC-04: nor, in code, `eval`, `Function(` or `new Function`, a dynamic `import(`, `queueMicrotask` (this supersedes its omission under WR-07), `setImmediate`, `performance`, `crypto`, `WebSocket`, `process` or `require`. These are everyday words, and JSDoc types use `import("./x.js")`, so they are matched as whole words in code only, with comments, string text, template text and regex bodies left out. Code inside a template's `${...}` is scanned.] [Added 2026-10-09, ORCH, security SEC-05: the primary R25 guard is now a runtime trap test, `@R25 runtime trap: ...` in `tests/hygiene.test.js`. It replaces every banned global (`eval`, `Function`, the timers, `queueMicrotask`, `setImmediate`, `performance`, `crypto`, `WebSocket`, `process`, `require`, `fetch`, storage, `Date`, `Intl` and the rest of the list above), `Date.now`, `Math.random`, `Number.parseFloat`, `toFixed`, the locale methods and the function-constructor route with a recorder. It loads a fresh copy of the whole core, runs every export, and requires zero accesses from core code. A negative control shows every trap fires, and the security re-check's plants F1 to F10 go red in every core file. The source scan stays as a secondary, best-effort guard with known limits. It misreads a slash after a postfix `++` or `--` or after a member named like a keyword, a regex literal right after `if (...)`, and a division inside a template `${...}`. It cannot see a bare `Function` reference, an identifier written with a unicode escape, or the constructor route. ~~The trap catches all of these.~~] [Changed 2026-10-09, ORCH, code-review WR-13: that sentence went further than the code. The trap catches all of these on any path the workload runs, whatever the syntax. The workload is `runEveryExport` in `tests/hygiene.test.js`: it calls every export on representative input, so the test proves each export runs, not each branch. A branch the workload never takes is covered only by the name scan, which is best-effort. A banned access in such a branch that the scan misreads (the limits above) passes both guards.] [Added 2026-10-09, ORCH, code-review WR-12: `globalThis` was on the ban list and was not trapped, so "every banned global" above was false for that name. It is trapped now. Tests in `tests/hygiene.test.js` keep it so. One pins the three trap lists name for name, so deleting a trap is red. One checks that every name the scan bans has a trap (`import(` is syntax, so no recorder can watch it). Two more check that the traps are put back after a run, also after a body that throws, and that each run loads its own copy of the core.]

### Names (C1, added 2026-10-08 after the plan check)
- **R26. Duplicate names are allowed.** The brainstorm rule "Duplicate names are allowed" had no requirement. A name is a label and never an identity, and people are addressed by `id` only. `setPersonName` stores a name that equals another person's name, whether it matches exactly, after trimming or only in letter case, and no function rejects, merges, renames or reorders people because of it. `computeResult` gives one row per person, so two people called "Ben" give two rows with the same `name`, each with its own share. `toggleItemPerson` and `removePerson` act on the person with the given id, so tapping or removing one of two people called "Ben" never touches the other. `summaryText` prints one line per row, so both "Ben" lines appear. Examples D1 (even) and D2 (by item) are in `qa.md`.

### Spare sen (C9, added in v1.1.0)
Sources. Brainstorm v1.1.0, capability C9 and its rules (USER and ORCH). `SELF-CRITIQUE.md` interaction rules 8 and 9, approved in `RULINGS-v1.1.0.md`. The goldens `bill-even.md`, `spare-sen-one.md` and `spare-sen-random.md` for the numbers. Every point the inputs leave open is marked with its clarify item in `docs/modules/ROADMAP.md` (CG-P2, CG-P3). Changed 2026-10-13 after the plan check (F1). This sentence said each point "is written here as the recommended answer, so a ruling that differs changes one requirement". The owner ruled both items as recommended on 2026-10-13 (USER, ledger S1 row 2), so the text below is the ruling.

- **R27. The spare choice is part of the bill.** (v1.1.0 new) `bill.spare` is exactly one of `{ rule: "top" }` (Top of the list), `{ rule: "one", personId }` (One person) or `{ rule: "random", order }` (At random). For `"one"`, `personId` is the id of a person in the bill. For `"random"`, `order` holds every person id of the bill exactly once. A new bill has `{ rule: "top" }` (R10). `addPerson` and `removePerson` keep the invariant (R11, R12). `setMode`, the text setters and the item actions never change `spare` (R15), so a mode switch keeps the choice. It is one choice for the whole bill.
- **R28. Who can take the spare sen.** (v1.1.0 new) `sparePeople(bill)` returns the ids of the people who can be chosen, in list order. In even mode that is every person. In by-item mode it is every person whose id is in the `who` of at least one item. [The brainstorm says "only people with a share above zero can be chosen". In by-item mode a person on no item has a split of 0 under every rule, and in even mode every person pays a share. This reading is clarify item CG-P2, ruled as recommended on 2026-10-13, "Yes, every spare sen" (USER, ledger S1 row 2).]
- **R29. Choosing the rule.** (v1.1.0 new) `chooseSpareRule(bill, rule, random)` returns the bill with a new `spare`. `"top"` gives `{ rule: "top" }`. `"one"` gives `{ rule: "one", personId }` with the first id of `sparePeople(bill)` (interaction rule 8, "One person picks the first eligible person at once"), and when `sparePeople(bill)` is empty it returns the input unchanged. `"random"` gives `{ rule: "random", order }` with a newly drawn order (interaction rule 9). The draw is a Fisher and Yates shuffle of the people's ids in list order. For i from n - 1 down to 1, j = `Math.floor(random() * (i + 1))`, then entries i and j swap. With people p1, p2, p3 and `random` returning 0.9 then 0.1, the order is [p2, p1, p3]. Choosing the rule that is already set, or a value that is not one of the three, returns the input unchanged (same reference). `random` is a function the caller passes, returning a number from 0 up to but not including 1. Core never reads a random source of its own (R25).
- **R30. Choosing the one person.** (v1.1.0 new) `chooseSparePerson(bill, personId)` returns the bill with `spare` `{ rule: "one", personId }` when `personId` is in `sparePeople(bill)`. For any other id, or when that person is already the chosen one, it returns the input unchanged (same reference).
- **R31. Pick again.** (v1.1.0 new) `pickAgain(bill, random)` works only when `spare.rule` is `"random"` and `computeResult(bill)` is an `even` or `item` result. It draws new orders as R29 does, one after another, at most 64 times, and returns the bill with the first order whose result rows differ from the current rows (any `share`, `items` or `charges` of any row). In every other case, including 64 draws that all leave the rows as they are, it returns the input unchanged (same reference). [Interaction rule 9, "Pick again draws until the result changes". When no order can change the rows (only one person can take spare sen, or the spare sen divide evenly among them) an unbounded loop would never end. ~~With a change possible, 64 failed draws have a chance of at most 2 to the power -64.~~ Changed 2026-10-13 after the plan check (F4), that sentence holds in even mode only. In even mode with n people and k spare sen (1 to n - 1), a draw keeps the rows with a chance of 1 in C(n, k), at most 1/2, so 64 failed draws have a chance of at most 2 to the power -64. In by-item mode a draw can keep the rows more often. On the four-person bill with items 0.11 (p1, p2), 0.03 (p2, p3, p4), 0.23 (p1, p3) and 0.09 (p2, p3), rates 0 and 0, and the current order [p1, p2, p3, p4], 20 of the 24 orders keep the rows, so 64 failed draws have a chance of (5/6) to the 64th, about 8.6e-6 (recomputed by the planner with a read-only script). So on a rare bill Pick again changes nothing although a change was possible. This is the behaviour the owner ruled, clarify item CG-P3, "Nothing changes" (USER, 2026-10-13, ledger S1 row 2).]
- **R32. Where the spare sen go.** (v1.1.0 new) `computeResult` splits money in **divisions**, in this order. Even mode has one, `charges.total` over every person. By-item mode has one per item in list order (its price over the people on it), then the charges (service + sst over the people whose `items` is above 0, weighted by `items`). Each division gives each of its members a floor part (equal parts in even mode and for an item, the exact R8 floor for the charges), and its **spare sen** are its amount less the sum of those parts. A spare sen given in an item division adds to the receiver's `items`, in the charges division to their `charges`, and in even mode to their `share`. The rule decides who gets each spare sen.
  1. **Top of the list.** Each division gives its spare sen one each to its own members in people-list order, from the first. This is the 1.0 rule, so every 1.0 result is unchanged.
  2. **One person.** Every spare sen of every division goes to the chosen person, also the spare sen of an item they did not have (the owner's words, "have 1 person pay the extras"). When the chosen person is not in `sparePeople(bill)` for the current mode, the bill is worked out as Top of the list and the choice stays stored (a switch to By item and back loses nothing, brainstorm decision 13).
  3. **At random.** One cursor walks the drawn `order` across the whole bill, starting at its first entry. Each spare sen, division by division in the order above, goes to the next person in `order`, from the cursor on and wrapping round at the end, who is a member of that division. The cursor then moves to the entry after that person. In even mode this is "the first spare sen to the first person drawn, the next to the second", so two spare sen always go to two different people (`spare-sen-random.md`).
  The number of spare sen is the sum of every division's spare sen under the rule applied. Worked examples (named bills in `qa.md`):

  | Bill | Spare choice | Shares (and items, charges) | Spare sen |
  |---|---|---|---|
  | S2 | top | 3887, 3887, 3886 (1.0) | 2 |
  | S2 | one, p2 | 3886, 3888, 3886 (`spare-sen-one.html`) | 2 |
  | S2 | random, order [p2, p3, p1] | 3886, 3887, 3887 (`spare-sen-random.html`) | 2 |
  | S1 | top | Aisyah 2490 / 414 / 2904, Ben 1350 / 224 / 1574, Chen 2100 / 348 / 2448 (1.0) | 1 |
  | S1 | one, p2 | Aisyah 2490 / 413 / 2903, Ben 1350 / 225 / 1575, Chen 2100 / 348 / 2448 | 1 |
  | S1 | random, order [p3, p1, p2] | Aisyah 2490 / 413 / 2903, Ben 1350 / 224 / 1574, Chen 2100 / 349 / 2449 | 1 |
  | I3 | top | Aisyah 501 / 84 / 585, Ben 0 / 0 / 0, Chen 500 / 82 / 582 (1.0) | 2 |
  | I3 | one, p3 | Aisyah 500 / 82 / 582, Ben 0 / 0 / 0, Chen 501 / 84 / 585 | 2 |
  | I3 | random, order [p2, p3, p1] | Aisyah 500 / 83 / 583, Ben 0 / 0 / 0, Chen 501 / 83 / 584 | 2 |
  | I2 | one, p1 (Aisyah is on no item) | as I2 under top (1.0), `spare.rule` is `"top"`, `spare.personId` is `null` | 2 (Y's 1 and the charges' 1) |

  [The brainstorm rules "Every leftover sen follows it" and "Top of the list keeps the 1.0 rule" fix rules 1 and 2 for even mode. How One person and At random treat an item's spare sen and the charges' spare sen in by-item mode is not worded anywhere, so points 2 and 3 for by-item mode are clarify item CG-P2 with this recommended answer. Changed 2026-10-13 after the plan check (F1), the owner ruled CG-P2 as recommended on 2026-10-13 (USER, ledger S1 row 2).]
- **R33. The result names the rule in effect.** (v1.1.0 new) Every `even` and `item` result carries `spare: { count, rule, personId }`. `count` is the number of spare sen (R32). `rule` is the rule that was applied, so it reads `"top"` when One person falls back (R32 point 2). `personId` is the chosen id when `rule` is `"one"`, otherwise `null`. `blocked` and `unassigned` results carry no `spare`.

### Formatting (added in v1.1.0)
- **R34. A money figure without the currency.** (v1.1.0 new) `formatAmount(cents)` returns the whole ringgit in plain decimal digits, with a comma between groups of three digits counted from the right when there are four or more, then `"."` and the sen as exactly 2 digits. No currency, no space, and no locale API (R25 already bans `Intl` and `toLocaleString`). Examples are 0 to `0.00`, 2490 to `24.90`, 98940 to `989.40`, 99999 to `999.99`, 100000 to `1,000.00`, 102390 to `1,023.90`, 119387 to `1,193.87`, 100000000 to `1,000,000.00`, 779999922 to `7,799,999.22`. [The goldens write the Total figure as `<span class="cur">RM </span>69.26` and the working under a split as "24.90 + 4.14" and "1,023.90 + 169.97", so the app needs the figure without "RM", and money is formatted only here (split-app invariant).]

### Names (added 2026-10-16 in execute, H-10)
- **R35. A plain name.** (v1.1.0 new) [Added 2026-10-16 in execute, ledger H-10, security SEC-S5-1 and SEC-S5-3. Ruled USER 2026-10-16 00:07, option (1).] `plainName(text)` returns `text` with every character of the class `[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]` deleted (not replaced), and every other character kept, in order. The class is the one R24 prints as a space, 79 code points. That is `\p{Cc}` (65, the C0 controls U+0000 to U+001F, DEL U+007F and the C1 controls U+0080 to U+009F, which hold TAB, LF, CR, ESC and NEL), `\p{Zl}` (U+2028 LINE SEPARATOR), `\p{Zp}` (U+2029 PARAGRAPH SEPARATOR) and `\p{Bidi_Control}` (12, U+061C, U+200E, U+200F, U+202A to U+202E, U+2066 to U+2069).
  1. **Kept.** Every character outside the class, for example U+200B ZERO WIDTH SPACE, U+200C and U+200D (the joiners inside an emoji sequence such as U+1F468 U+200D U+1F469), U+FEFF, U+00A0, U+00AD, U+3000, combining marks and the letters of every script. `plainName("")` is `""`, a text with none of the class comes back equal, and `plainName(plainName(t))` equals `plainName(t)`. It never throws for a string and reads no global (R25).
  2. **One class.** The class is written once under `src/core/`, in `bill.js` as the exported `RegExp` `NAME_CONTROLS` (flags `gu`), and `summaryText` (R24) and `plainName` both read it. Each uses it only through `String.prototype.replace`, which starts every search at 0, so the shared `g` flag carries no state between calls. `\p{Bidi_Control}` appears on one line under `src/`. So for every code point c, `plainName` deletes c exactly when `summaryText` ~~prints c in a row name as a space~~ replaces c in a row name with a space. [Changed 2026-10-16 in execute, ledger S7 row 46, ORCH, planner touch. A typed U+0020 also comes out of `summaryText` as a space, but it is kept as it is and not replaced, so the old wording was false by its letter at U+0020. `qa.md` compares the whole row, ledger S7 row 45.] Why one definition. App R62 removes the class so that the names on screen and the names in the copied summary are the same text, and that holds only while the two classes are equal.
  3. **Who calls it.** `split-app` calls it on every name at its name inputs and in its draft decoder (app R62). No core action calls it. `setPersonName` and `setItemName` still store the text exactly as given (R15), and `personLabel` and `itemLabel` are unchanged (R17).

## Contracts

### Files
| File | Exports |
|---|---|
| `src/core/money.js` | `parseAmount`, `parseRate`, `formatMoney`, `formatRate`, `formatAmount` (v1.1.0), `AMOUNT_MIN_CENTS` (1), `AMOUNT_MAX_CENTS` (9999999) |
| `src/core/allocate.js` | `allocateEvenly`, `allocateByWeight` |
| `src/core/bill.js` | `LIMITS`, `newBill`, `addPerson`, `removePerson`, `setPersonName`, `setMode`, `setSubtotalText`, `setServiceText`, `setSstText`, `addItem`, `removeItem`, `setItemName`, `setItemPriceText`, `toggleItemPerson`, `personLabel`, `itemLabel`, `sparePeople` (v1.1.0), `plainName` and `NAME_CONTROLS` (added 2026-10-16 in execute, H-10, R35) |
| `src/core/result.js` | `billCharges`, `computeResult` |
| `src/core/spare.js` (v1.1.0, new) | `chooseSpareRule`, `chooseSparePerson`, `pickAgain` |
| `src/core/summary.js` | `summaryText` |

No other exports. Helpers stay module-private. [Added 2026-10-13, v1.1.0. A new file, because `pickAgain` needs `computeResult`, and `result.js` already imports `bill.js`, so the choice actions in `bill.js` would make an import cycle. `sparePeople` sits in `bill.js` because `result.js` (the One person fallback) and `spare.js` both need it, written once. The floor and spare sen step of R32 is written once in `result.js` and serves all three rules. `allocateEvenly` and `allocateByWeight` keep their R7 and R8 results, which are the Top of the list rule. The Fisher and Yates draw is one private helper in `spare.js`, used by `chooseSpareRule` and `pickAgain`.]

### Types (JSDoc in the source, shown here as the contract)
```js
/** @typedef {"even" | "item"} Mode */
/** @typedef {{ id: string, name: string }} Person */              // id is "p" + a positive integer
/** @typedef {{ id: string, name: string, priceText: string, who: string[] }} Item */  // id is "i" + a positive integer
/** @typedef {{ rule: "top" } | { rule: "one", personId: string } | { rule: "random", order: string[] }} Spare */  // v1.1.0, R27
/**
 * @typedef {{
 *   mode: Mode, people: Person[], subtotalText: string, items: Item[],
 *   serviceText: string, sstText: string, spare: Spare, nextId: number
 * }} Bill
 */
/** @typedef {{ count: number, rule: "top" | "one" | "random", personId: string | null }} SpareResult */  // v1.1.0, R33
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
 *   | { kind: "blocked", reason: "rates" | "subtotal" | "no-prices" | "prices" }   // v1.1.0: "no-items" became "no-prices" (R18)
 *   | { kind: "unassigned", count: number, charges: Charges }
 *   | { kind: "even", charges: Charges, rows: EvenRow[], check: { share: number }, spare: SpareResult }
 *   | { kind: "item", charges: Charges, rows: ItemRow[],
 *       check: { items: number, charges: number, share: number }, spare: SpareResult }
 * } Result
 */
/** @typedef {() => number} RandomSource */  // v1.1.0, a number from 0 up to but not including 1 (R29, R31)
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
| `computeResult(bill: Bill): Result` | R18 to R22, R32, R33 |
| `summaryText(result: Result): string` | R24 |
| `formatAmount(cents: number): string` (v1.1.0) | R34 |
| `sparePeople(bill: Bill): string[]` (v1.1.0) | R28 |
| `chooseSpareRule(bill: Bill, rule: string, random: RandomSource): Bill` (v1.1.0) | R27, R29 |
| `chooseSparePerson(bill: Bill, personId: string): Bill` (v1.1.0) | R30 |
| `pickAgain(bill: Bill, random: RandomSource): Bill` (v1.1.0) | R31 |
| `plainName(text: string): string` (added 2026-10-16, H-10) | R35 |
| `NAME_CONTROLS: RegExp`, `/[\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}]/gu` (added 2026-10-16, H-10), read by `summaryText` and `plainName` only, through `replace` | R35, R24 |

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

### v1.1.0 tasks (one commit each, `node --test "tests/**/*.test.js"` green on every commit, 1.0 cases unchanged unless `qa.md` marks them)
Every new or changed case is seen failing on its own assertion before the code it tests lands, by the method `qa.md` states once (How to run, "RED first for a new or changed case"). Added 2026-10-13 after the plan check (F3).

- C1. [x] `formatAmount` and the thousands comma in `formatMoney` (`money.js`), with the R4 and R34 tables and the summary of a four figure bill. -> R4, R34, R24 [Ticked 2026-10-14 in execute, commit `d9be159`, ledger S7 row 16.]
- C2. [x] The `spare` field in `bill.js` (`newBill`, `addPerson`, `removePerson`) and `sparePeople`, with `tests/bill.test.js` cases. -> R10, R11, R12, R27, R28 [Ticked 2026-10-14 in execute, commit `ad0436b`, ledger S1 rows 4 and 5.]
- C3. [x] Blocking row (c) as "no item has a valid price" (`result.js`), with the R18 table. The same commit keeps the Chromium browser suite green (PD-24 in `docs/modules/ROADMAP.md`). It renames the key `"no-items"` to `"no-prices"` in `BLOCKED_MESSAGE` of the 1.0 receipt (`src/ui/panel.js`), keeping its 1.0 text "Add an item to see the shares." until app task A9 replaces that receipt. It also updates the two 1.0 browser expectations the widened row (c) changes, both a by-item bill whose one item has an empty price, which now reads "Add an item to see the shares.". They are the `item-unpriced` case of `test_R17_when_the_shares_cannot_be_worked_out` and the first message check of `test_R12_add_an_item_remove_one_and_reach_the_limit` in `tests/browser/test_app.py`. -> R18 [Changed 2026-10-13 after the plan check (F7). PD-24 was written only in the ROADMAP.] [Ticked 2026-10-14 in execute, commit `bf62046`, ledger S1 row 8.]
- C4. [x] The spare sen divisions and `result.spare` in `computeResult` (`result.js`), the R32 table, and the R22 sweep run under all three rules (`tests/invariants.test.js`). -> R20, R21, R22, R32, R33 [Ticked 2026-10-14 in execute, commit `13d74e3`, ledger S1 row 8.]
- C5. [x] `src/core/spare.js` (`chooseSpareRule`, `chooseSparePerson`, `pickAgain`) with `tests/spare.test.js`, driven by a scripted random source. -> R29, R30, R31 [Ticked 2026-10-14 in execute, commit `08f7faa`, ledger S1 row 8.]
- C6. [x] `tests/hygiene.test.js` and the R16 deep-freeze test cover `spare.js` and every new export (the runtime trap workload calls each one, a negative control plants `Math.random` in `spare.js`). -> R16, R25 [Changed 2026-10-09, ORCH, code-review WR-14: since security SEC-05 the file also holds the runtime trap, and the trap is the primary guard. "A static scan" is now the runtime trap plus the scan, see R25.] [Ticked 2026-10-14 in execute, commit `67c1c15`, ledger S1 row 8.]
- C7. [x] (after the step 5 solver round, right before app task A22, one build with it) `plainName` and the one class. [Added 2026-10-16 in execute, planner pass for H-10 (ledger H-10, ruled USER 2026-10-16 00:07, option (1)). A new id, no task renumbered.] `bill.js` gains `NAME_CONTROLS` and `plainName` (R35). `summary.js` drops its own `CONTROLS` and imports `NAME_CONTROLS`, with no other change. `tests/hygiene.test.js` gains the calls its runtime trap workload needs for the new export (as C1 and C5 did), and its static scan finds `\p{Bidi_Control}` on one line under `src/`.
  1. **RED.** The new `@R35` cases of `qa.md` run first against a throwaway stub `plainName` that returns its input, then against a second stub that also deletes `\p{Cf}` (it removes U+200B and the emoji joiner, so the "kept" cases fail), by the method of `qa.md` (How to run, "RED first for a new or changed case"). Every new case is seen failing on its own assertion in one of the two runs, the output and both stubs in `docs/modules/split-core/qa/unit/<stamp>-red/`. The `summary.js` change is a DRY merge, so the R24 cases run green before it and green after it with the same names (constitution, DRY safety), and a planted second class literal in `summary.js` makes the one-line scan red.
  2. **Proof.** `node --test "tests/**/*.test.js"` green on the commit, every 1.0 and v1.1.0 case unchanged. Node only, the browser proofs are A22's. -> R35, R24, R25
  [Ticked 2026-10-16 in execute, commit `abfbe3e`, security solver, ledger H-10. A third RED stub was added for two rows the named stubs cannot fail, see `BUILD.md`, task C7.]

## Threat model
| Asset | Trust boundary | Threat | Required mitigation |
|---|---|---|---|
| Correct shares (people pay what the screen says) | Text typed by the user or read from storage enters `parseAmount` and `parseRate` | Floating-point drift (`1.15` read as 114 sen) or a precision loss above 2^53 gives a wrong share that still looks plausible | R1, R3 integer-only parsing. R6, R7 exact integer division. R8 `BigInt` products. ~~R23 bound tests.~~ [Changed 2026-10-09, ORCH, WR-01: R8 BigInt trap rows. The R23 bound tests prove the MAX bills are exact, and a float allocator passes them too.] R25 bans `parseFloat` and `toFixed`. |
| Correct shares | Same | A rounding rule that differs from the brainstorm (banker's rounding, rounding each share instead of allocating leftovers) | R6 half-up table rows (5, 25, 8765). R7, R8 leftover order. R22 sum invariant over a generated sweep. |
| Availability of the page | Arbitrary strings, including very long ones from storage | Catastrophic regex backtracking or an exception on odd input freezes or breaks rendering | The grammar is a single linear pattern with no nested quantifier. Parsing checks the digit count before any numeric conversion ~~(400-digit case in R1)~~ [Changed 2026-10-09, ORCH, code-review WR-06: the cap is the digit count of the caller's ceiling, derived once in `readHundredths`. Its proof is the R1/R3 test that spies on numeric conversion. The 400-digit R1 row proves only "invalid, no exception", which holds with or without the cap.]. R2 says the parsers never throw for a string. |
| Clipboard text integrity | Names flow into `summaryText` | A name with a line break forges an extra line such as a fake "Adds up to" in the group chat | Invariant that names never hold CR or LF (the input strips them, the `split-app` decoder rejects them). `summaryText` writes one line per row and nothing else. [Added 2026-10-09, ORCH, code-review WR-10: the invariant alone left U+000B, U+000C, U+0085, U+2028 and U+2029 open. `summaryText` now prints each of the seven line-breaking characters as a space (R24), with one test per character.] [Changed 2026-10-09, ORCH, security SEC-01: a NUL truncates the text for a C-string reader, and FS to RS split it for Python, so `summaryText` now replaces every `[\p{Cc}\p{Zl}\p{Zp}]` character (R24). There are tests for NUL, FS, GS, RS and ESC besides the seven.] [Added 2026-10-09, ORCH, security SEC-02: a new threat under the same asset. A bidi control in a name (RLO, RLE, RLI) reorders how that row's share reads in any bidi-aware renderer. `summaryText` also replaces `\p{Bidi_Control}` (R24), with a test for RLO.] [Added 2026-10-16 in execute, H-10, security SEC-S5-1. The same bidi control also reorders the app's People summary on screen, where the copied text is clean, so the screen and the summary disagreed. App R62 now removes the class from every name with `plainName` (R35), which reads the one class `summaryText` reads. Contracted 2026-10-16, not built (tasks C7 and A22).] [Added 2026-10-16 in execute, security solver. Built, C7 `abfbe3e` and A22 `4a19b4d`, see `split-app/findings/security.md`, SEC-S5-1.] |
| Object integrity | `Bill` objects may come from parsed JSON | Prototype pollution through `__proto__` keys when copying objects | Actions build new objects from known fields only. No `Object.assign` or spread of a whole parsed object onto a target. [Added 2026-10-13, v1.1.0: this holds for `spare` too. The choice actions build a new `spare` object from known fields only.] [Added 2026-10-16 in execute, code review CR-S5-2, solved in `9277412`. The known Bill fields are listed once, by `newBill` (R10). The private `BILL_FIELDS = Object.keys(newBill())` in `bill.js` serves `billWith`, and `withSpare` in `spare.js` builds from the same keys. Both copy field by field and never spread. No export was added, and the Contracts name no field list, so nothing else here changes.] |
| Correct shares under every spare rule (v1.1.0) | The spare choice and the drawn order, typed by the user or read from storage | A rule that loses or doubles a sen, gives a sen to a person who had nothing, or changes 1.0's numbers under Top of the list | R32 one written step for all three rules. R22 sum invariants over a generated sweep under all three rules. The R32 table. Every 1.0 case stays green, so Top of the list is unchanged. `split-app`'s decoder checks the stored choice against R27 before core sees it. |
| Availability of the page (v1.1.0) | The caller's random source | Pick again loops for ever on a bill where no new order can change the splits | R31 bounds the draws at 64 and returns the bill unchanged after that. A test drives a source that always returns the same number. |
| Purity (v1.1.0) | The draw needs randomness | Core reads `Math.random` or `crypto`, so its results stop being repeatable in tests | R29 and R31 take the random source as an argument. R25 still bans `Math.random` and `crypto` in core, and the runtime trap covers `spare.js`. |

~~Residual risk accepted. None in this module beyond what `split-app` documents.~~

[Changed 2026-10-09, ORCH, security SEC-03: "None" was false. Two residual risks are accepted for v1.0 by ruling, and the rest is what `split-app` documents.
1. **A name can read like summary text.** The guard stops a name from starting a new line. It cannot stop plain characters from looking like a summary line. The name `Adds up to RM 0.00` gives the row `Adds up to RM 0.00 RM 38.86`, and a narrow chat bubble may wrap that row so its first visual line looks like a total. Accepted because R24 fixes the row format, and the real share and the real `Adds up to` line are still printed.
2. **A name can print as nothing.** A name made only of characters that `String.prototype.trim` keeps but that draw nothing (NEL alone, U+200B, U+2800, U+3164) is not blank under R17, so it skips the `Person N` fallback, and its row and its label on screen show no visible name. The share is still printed. R17 is not changed. Closing this would mean a change to R17, for the human to decide.]

[Added 2026-10-16 in execute, H-10.] In the app, residual 2 narrows. NEL (U+0085) is in R35's class, so app R62 removes it and a name of NEL alone becomes `""`, which takes the `Person N` fallback. U+200B, U+2800 and U+3164 are outside the class and the residual stands for them. Residual 1 is unchanged.

## Non-goals
Do NOT build any of the following. Building one is a defect.
- Payments, transfer links or DuitNow QR.
- Currencies other than ringgit, currency conversion, other languages or locale-aware number formats (no `Intl.NumberFormat`). [Changed 2026-10-13 after CG-P1. The line said "no group separators, CG-5 ruled 2026-10-08, ORCH", which contradicted R4 and R34. v1.1.0 replaces CG-5. `formatMoney` and `formatAmount` write a thousands comma from 1,000 without a locale API (R4, R34, R25), and the owner ruled the comma into the copied summary too (CG-P1, USER, 2026-10-13).]
- 5-sen cash rounding.
- Tips, discounts, vouchers, per-item tax exemptions, or any charge besides service charge and SST.
- A history of past bills or more than one bill.
- Any DOM, storage, clipboard, network or timer code (that is `split-app`, or nothing at all).
- Generic helpers nobody calls (a money class, a rounding-mode option, configurable currency, an undo stack). [Added 2026-10-16 in execute, CR-S5-4, PD-25. `allocateEvenly` is not one of them. It defines Top of the list for R20 and the tests call it, see the R7 note.]
- [Added 2026-10-16 in execute, H-10] A name rule inside a core action (no setter calls `plainName`, R15), any change to `personLabel` or `itemLabel`, any normalisation of names (NFC, case folding, collapsing spaces), and any removal outside R35's class.
- [Added 2026-10-13, v1.1.0] Any spare sen rule besides the three of R27, a split of spare sen typed by hand, or a weight per person.
- [Added 2026-10-13, v1.1.0] A line about spare sen in the copied summary (R24 keeps the 1.0 lines).
- [Added 2026-10-13, v1.1.0] A random source inside core, a seeded generator in shipped code, or a record of past draws.
- [Added 2026-10-13, v1.1.0] Several bills at once. It is written up as a future implementation only (`docs/future/several-bills.md`, ledger S9).
