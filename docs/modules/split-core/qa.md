# QA: split-core

> Test contract. This module has no UI, so there is no FE element checklist and no fidelity gate.
> Every scenario below is executed by Node's built-in test runner. Test files live under `tests/` and
> import from `../src/core/`. Each `test()` title starts with its tag (for example `@R8 S1 charges`) so a
> grep maps every test to an R#, and every R# in `spec.md` has at least one scenario here.

## How to run
- Command: `node --test "tests/**/*.test.js"` from the project root (Node 24). This is the unit test
  command in `CLAUDE.md` (CG-6 ruled 2026-10-08, ORCH). The earlier `node --test tests/` exits 1 with
  `MODULE_NOT_FOUND` on Node 24.11.1 (measured during planning), so do not use it.
- Evidence: the full runner output goes to `docs/modules/split-core/qa/unit/<YYYYMMDD-HHMMSS>/node-test.txt`.
  The run is green only when the output shows `fail 0` and the test count is not 0.
- RED first for a new or changed case (added 2026-10-13 after the plan check, F3). A case that imports an export
  that does not exist yet fails when the module links, which is a label earned by exiting non-zero and not a RED
  (constitution, Gates and evidence). So before the code a case tests lands, the case runs against a throwaway
  stub of that export in the working tree. The stub has the export's signature and returns a value of the right
  type that the case must reject (for a changed R#, the 1.0 function as it stands is the stub). Where one stub
  passes some cases of an export (a stub that returns its input passes "returns the same bill object"), a second
  stub that returns a fresh copy covers them, so every new or changed case is seen failing on its own assertion
  in at least one run. That run's output and the stub's source go to
  `docs/modules/<module>/qa/unit/<YYYYMMDD-HHMMSS>-red/` (`node-test.txt`, `stub.txt`), never over an earlier
  run. The build then replaces the stub, the same cases go green, and no commit ever holds a stub. The app's
  Node cases in `tests/draft.test.js` (D13, D14 and the `loadDraft` and `saveDraft` states, R61) use the same
  method. The 1.0 `src/draft.js` is the stub for the cases that expect a version 2 draft read and for the
  `loadDraft` and `saveDraft` states, and a stub decoder that skips the version and `spare` checks covers the
  cases that expect `{ ok: false }`, which the 1.0 decoder already refuses. Their RED output goes to
  `docs/modules/split-app/qa/unit/<YYYYMMDD-HHMMSS>-red/`.

| Test file | Covers |
|---|---|
| `tests/money.test.js` | R1, R2, R3, R4, R5, R34 |
| `tests/allocate.test.js` | R7, R8, R9 |
| `tests/bill.test.js` | R10 to R17, R26, R27, R28, and R35 (added 2026-10-16, H-10) |
| `tests/result.test.js` | R6, R18 to R21, R23, R26, R32, R33 |
| `tests/invariants.test.js` | R22 |
| `tests/summary.test.js` | R24, R26 |
| `tests/hygiene.test.js` | R25 |
| `tests/spare.test.js` (v1.1.0, new) | R29, R30, R31 |

**v1.1.0 delta (2026-10-13, planner, solutions architect role).** New scenarios for R27 to R34 sit at the end of the Gherkin block under "Spare sen" and "Formatting". Scenarios whose expected result changed carry a `# [Changed 2026-10-13, v1.1.0, <scope>]` line saying what changed, and keep their tag. The R27, R28 and R32 cases live in `tests/bill.test.js` and `tests/result.test.js` beside the 1.0 cases of the same functions, R34 in `tests/money.test.js`. Every 1.0 case not marked here keeps its expected result, which is the proof that Top of the list is the 1.0 rule. The random source in every test is scripted (a list of numbers returned in turn), never `Math.random`.

Changed 2026-10-16 in execute, planner pass for H-10 and the step 5 wording. Three `@R35` scenarios for `plainName` sit at the end of the Gherkin block under "Names" (H-10, ruled USER 2026-10-16 00:07, option (1), task C7). The `@R21 @R8` scenario for the trap bill of code review CR-S5-1 (test `042c359`) sits after the R8 trap rows.

## Named example bills
Used by the scenarios. Rates are `serviceText` / `sstText`. People are listed in order with their ids.

| Name | Mode | People | Input | Expected |
|---|---|---|---|---|
| **S2** | even | p1 Aisyah, p2 Ben, p3 Chen | subtotal `100.00`, rates `10` / `6` | charges 10000, 1000, 11000, 660, total 11660. Shares 3887, 3887, 3886 |
| **S1** | item | p1 Aisyah, p2 Ben, p3 Chen | i4 `Nasi lemak ayam` `15.90` who [p1]. i5 `Char kuey teow` `13.50` who [p2]. i6 `Mee goreng mamak` `12.00` who [p3]. i7 `Satay, 10 sticks` `18.00` who [p1, p3]. Rates `10` / `6` | charges 5940, 594, 6534, 392, total 6926. Rows Aisyah 2490 / 414 / 2904, Ben 1350 / 224 / 1574, Chen 2100 / 348 / 2448. Check 5940 / 986 / 6926 |
| **S5** | item | as S1 | S1 with i6 who [] | unassigned, count 1, charges as S1 |
| **E1** | even | four people A, B, C, D | subtotal `87.65`, rates `10` / `6` | charges 8765, 877, 9642, 579, total 10221. Shares 2556, 2555, 2555, 2555 |
| **E2** | even | as S2 | subtotal `10.00`, rates `0` / `0` | total 1000. Shares 334, 333, 333 |
| **E3** | even | `newBill()` people (Person 1, Person 2) | subtotal `50.00`, rates `12.5` / `6.25` | charges 5000, 625, 5625, 352, total 5977. Shares 2989, 2988 |
| **I2** | item | as S2 | X `10.00` who [p2]. Y `5.01` who [p2, p3]. Rates `10` / `6` | charges 1501, 150, 1651, 99, total 1750. Rows Aisyah 0 / 0 / 0, Ben 1251 / 208 / 1459, Chen 250 / 41 / 291. Check 1501 / 249 / 1750 |
| **I3** | item | as S2 | one item `10.01` who [p3, p1] (tapped Chen first) | items 501 / 0 / 500, charges 84 / 0 / 82, shares 585 / 0 / 582, total 1167 |
| **I4** | item | as S2 | one item `0.10` who [p1, p2, p3], rates `0` / `0` | shares 4, 3, 3 |
| **MAX-E** | even | twelve people | subtotal `99999.99`, rates `30` / `20` | charges 9999999, 3000000, 12999999, 2600000, total 15599999. Shares eleven times 1300000, then 1299999 |
| **MAX-I** | item | twelve people | fifty items `99999.99`, item k (0-based) who [person k mod 12], rates `30` / `20` | charges 499999950, 149999985, 649999935, 129999987, total 779999922. Items 49999995 x2, 39999996 x10. Charges 27999998 x2, 22399998 x6, 22399997 x4. Shares 77999993 x2, 62399994 x6, 62399993 x4 |
| **D1** (added 2026-10-08) | even | p1 Ben, p2 Ben, p3 Chen | subtotal `100.00`, rates `10` / `6` | as S2. Rows Ben 3887, Ben 3887, Chen 3886. Check 11660 |
| **D2** (added 2026-10-08) | item | p1 Ben, p2 Ben, p3 Chen (built from `newBill()` with `addPerson`, `addItem` and the setters, so `nextId` is 5) | one item i4 `Tea` `10.00` who [p2]. Rates `10` / `6` | charges 1000, 100, 1100, 66, total 1166. Rows Ben 0 / 0 / 0, Ben 1000 / 166 / 1166, Chen 0 / 0 / 0. Check 1000 / 166 / 1166 |
| **W1** (v1.1.0) | item | as S1 | S1 plus i8 `""` `964.50` who [p1] | charges 102390, 10239, 112629, 6758, total 119387. Rows Aisyah 98940 / 16425 / 115365, Ben 1350 / 224 / 1574, Chen 2100 / 348 / 2448. Check 102390 / 16997 / 119387. Spare count 1 (`bill-large.md`) |

Since v1.1.0 every named bill has `spare: { rule: "top" }` unless a scenario names another choice, written as `<bill> with spare <choice>` (for example "S2 with spare one p2", "S2 with spare random [p2, p3, p1]"). The numbers each choice gives are the R32 table in `spec.md`.

## Functional test cases (Gherkin)
A table cell written in double quotes is a JavaScript string literal, so its spaces count. An empty cell is the empty string. Other cells are literal text.
```gherkin
Feature: split-core money, maths, state rules and summary text

  @R1
  Scenario Outline: parseAmount accepts valid amounts as exact cents
    Given the amount text "<text>"
    When parseAmount is called
    Then the result is ok with <cents> cents
    Examples:
      | text          | cents   |
      | 12            | 1200    |
      | 12.5          | 1250    |
      | 12.50         | 1250    |
      | 0.01          | 1       |
      | 99999.99      | 9999999 |
      | 1.15          | 115     |
      | 4.35          | 435     |
      | 0.29          | 29      |
      | " 12.50 "     | 1250    |
      | 007           | 700     |
      | 12.           | 1200    |
      | 0000000012.50 | 1250    |

  @R1 @R2
  Scenario Outline: parseAmount rejects invalid text as invalid, not empty
    Given the amount text "<text>"
    When parseAmount is called
    Then the result is { ok: false, empty: false }
    Examples:
      | text      |
      | 0         |
      | 0.00      |
      | 100000    |
      | 99999.991 |
      | 12.505    |
      | 13.505    |
      | -5        |
      | +5        |
      | 1,000     |
      | .5        |
      | 1e3       |
      | 0x10      |
      | Infinity  |
      | NaN       |
      | abc       |
      | 12 50     |
      | １２      |

  @R1 @R2
  Scenario: A 401-character amount is rejected without overflow or exception
    Given the amount text "1" followed by 400 "0" characters
    When parseAmount is called
    Then it returns { ok: false, empty: false } and does not throw

  @R1 @R3
  # [Added 2026-10-09, ORCH, code-review WR-06] The scenario above passes with or without the digit
  # cap, so it cannot prove "no overflow". This one can: it watches the global Number while parsing.
  Scenario: A whole part longer than the ceiling's is refused before any numeric conversion
    Given a spy on every call of the global Number
    When parseAmount gets "1" followed by 400 "0" characters, and "100000"
    And parseRate gets "100" with max 30
    Then each returns { ok: false, empty: false } and Number was never called
    And parseAmount "99999.99" and parseRate "30" with max 30 do call Number (the spy is not blind)

  @R2
  Scenario Outline: Empty or white-space text is reported as empty
    Given the text "<text>"
    When parseAmount is called and parseRate is called with max 30
    Then both return { ok: false, empty: true }
    Examples:
      | text |
      | ""    |
      | "   " |

  @R2
  Scenario: The parsers never throw for any string
    Given 500 strings from a seeded generator over the characters "0123456789.,-+ eE%abc １"
    When parseAmount and parseRate(_, 30) are called on each
    Then none throws and every result has the shape of R1 or R2

  @R3
  Scenario Outline: parseRate reads basis points within its maximum
    Given the rate text "<text>" and the maximum <max>
    When parseRate is called
    Then the result is <result>
    Examples:
      | text  | max | result                    |
      | 0     | 30  | ok 0                      |
      | 10    | 30  | ok 1000                   |
      | 6     | 20  | ok 600                    |
      | 6.5   | 20  | ok 650                    |
      | 6.25  | 20  | ok 625                    |
      | 30    | 30  | ok 3000                   |
      | 30.00 | 30  | ok 3000                   |
      | 20    | 20  | ok 2000                   |
      | 0.01  | 30  | ok 1                      |
      | 6.    | 20  | ok 600                    |
      | 06    | 20  | ok 600                    |
      | 30.01 | 30  | invalid                   |
      | 20.01 | 20  | invalid                   |
      | 25    | 20  | invalid                   |
      | -1    | 30  | invalid                   |
      | 6.255 | 20  | invalid                   |
      | 10%   | 30  | invalid                   |

  @R4
  # [Changed 2026-10-13, v1.1.0, S7] The last two rows had no comma (CG-5). The design system now writes a thousands
  # comma from RM 1,000, and four rows around the first comma are added.
  Scenario Outline: formatMoney writes RM, a space, ringgit with thousands commas and two sen digits
    Given <cents> cents
    When formatMoney is called
    Then it returns "<text>"
    Examples:
      | cents     | text            |
      | 0         | RM 0.00         |
      | 1         | RM 0.01         |
      | 10        | RM 0.10         |
      | 100       | RM 1.00         |
      | 3887      | RM 38.87        |
      | 11660     | RM 116.60       |
      | 99999     | RM 999.99       |
      | 100000    | RM 1,000.00     |
      | 119387    | RM 1,193.87     |
      | 15599999  | RM 155,999.99   |
      | 779999922 | RM 7,799,999.22 |

  @R5
  Scenario Outline: formatRate drops trailing zeros and adds a percent sign
    Given <bp> basis points
    When formatRate is called
    Then it returns "<text>"
    Examples:
      | bp   | text  |
      | 0    | 0%    |
      | 600  | 6%    |
      | 1000 | 10%   |
      | 650  | 6.5%  |
      | 625  | 6.25% |
      | 605  | 6.05% |
      | 3000 | 30%   |

  @R6
  Scenario Outline: Service and SST round half up to the cent
    Given a subtotal of <subtotal> cents, service <sbp> bp and SST <tbp> bp
    When billCharges is called
    Then service is <service>, sstBase is <base>, sst is <sst> and total is <total>
    And serviceBp is <sbp> and sstBp is <tbp>
    Examples:
      | subtotal  | sbp  | tbp  | service   | base      | sst       | total     |
      | 10000     | 1000 | 600  | 1000      | 11000     | 660       | 11660     |
      | 5940      | 1000 | 600  | 594       | 6534      | 392       | 6926      |
      | 8765      | 1000 | 600  | 877       | 9642      | 579       | 10221     |
      | 5         | 1000 | 0    | 1         | 6         | 0         | 6         |
      | 25        | 1000 | 0    | 3         | 28        | 0         | 28        |
      | 4         | 1000 | 0    | 0         | 4         | 0         | 4         |
      | 1000      | 0    | 0    | 0         | 1000      | 0         | 1000      |
      | 5000      | 1250 | 625  | 625       | 5625      | 352       | 5977      |
      | 9999999   | 3000 | 2000 | 3000000   | 12999999  | 2600000   | 15599999  |
      | 499999950 | 3000 | 2000 | 149999985 | 649999935 | 129999987 | 779999922 |

  @R7
  Scenario Outline: allocateEvenly floors and hands leftover sen to the top
    Given an amount of <amount> cents and <count> people
    When allocateEvenly is called
    Then the result is <result>
    And the result sums to <amount> and its entries differ by at most 1
    Examples:
      | amount   | count | result                                    |
      | 11660    | 3     | [3887, 3887, 3886]                        |
      | 1800     | 2     | [900, 900]                                |
      | 1001     | 3     | [334, 334, 333]                           |
      | 1        | 3     | [1, 0, 0]                                 |
      | 0        | 2     | [0, 0]                                    |
      | 10221    | 4     | [2556, 2555, 2555, 2555]                  |
      | 15599999 | 12    | eleven times 1300000, then 1299999        |

  @R8
  Scenario Outline: allocateByWeight floors exactly and skips zero weights for leftovers
    Given an amount of <amount> cents and the weights <weights>
    When allocateByWeight is called
    Then the result is <result> and it sums to <amount>
    Examples:
      | amount    | weights                  | result                 |
      | 986       | [2490, 1350, 2100]       | [414, 224, 348]        |
      | 10        | [0, 1, 1, 1]             | [0, 4, 3, 3]           |
      | 0         | [5, 7]                   | [0, 0]                 |
      | 249       | [0, 1251, 250]           | [0, 208, 41]           |
      | 236419679 | [314963010, 157876348]   | [157481505, 78938174]  |
      | 61846725  | [49676084, 322894546]    | [8246230, 53600495]    |
      | 178450942 | [111531837, 207130558]   | [62457829, 115993113]  |
    # [Changed 2026-10-09, ORCH, code-review WR-01] The last three rows are the BigInt trap rows (spec R8).
    # Their test titles start "@R8 BigInt trap:", and each test also checks that a float allocator
    # (Math.floor of a x w / W, then the leftover rule) gives a different result. The 61846725 and
    # 178450942 rows were added 2026-10-09.

  @R21 @R8
  # [Added 2026-10-16 in execute, code review CR-S5-1, the test is 042c359.] Since C4, computeResult splits the
  # charges with its own floor step (floorParts in result.js), so the trap rows above no longer guard the result
  # path. This bill drives computeResult through the 61846725 trap row. A float floorParts (mutant K02) gives
  # [8246231, 53600494] with every sum still adding up, and fails here.
  Scenario: A by-item bill whose charges division is an R8 trap row gets the exact charges
    Given a by-item bill with two people at rates 10 and 6, p1 alone on items worth 49676084 cents in all and p2 alone on items worth 322894546 cents in all, each item at most 9999999 cents
    When computeResult is called
    Then service plus SST is 61846725, the rows' items are [49676084, 322894546] and the rows' charges are exactly [8246230, 53600495]
    And allocateByWeight(61846725, [49676084, 322894546]) gives the same [8246230, 53600495]
    And Math.floor(61846725 x 322894546 / 372570630) is not 53600495 (a float floor misses this bill)

  @R8 @R23
  # [Changed 2026-10-09, ORCH, code-review WR-01] Old title "allocateByWeight stays exact when amount
  # times weight passes 2^53" implied this case guards BigInt. A float allocator also passes it.
  Scenario: allocateByWeight gives the MAX-I charges split exactly, with products past 2^53
    Given an amount of 279999972 cents and the weights [49999995, 49999995, 39999996 x10]
    When allocateByWeight is called
    Then the result is [27999998, 27999998, 22399998 x6, 22399997 x4]

  @R9
  Scenario Outline: Allocation rejects impossible input
    When <call> is called
    Then it throws RangeError
    Examples:
      | call                           |
      | allocateEvenly(10, 0)          |
      | allocateEvenly(10, 1.5)        |
      | allocateEvenly(-1, 2)          |
      | allocateEvenly(0.5, 2)         |
      | allocateByWeight(10, [])       |
      | allocateByWeight(10, [0, 0])   |
      | allocateByWeight(10, [1, -1])  |
      | allocateByWeight(10, [1.5, 1]) |
      | allocateByWeight(-1, [1])      |

  @R10
  # [Changed 2026-10-13, v1.1.0, S1] The expected value gains spare { rule: "top" }.
  Scenario: A new bill has two people, even mode, the default rates and Top of the list
    When newBill is called
    Then it deep-equals { mode: "even", people: [{ id: "p1", name: "Person 1" }, { id: "p2", name: "Person 2" }], subtotalText: "", items: [], serviceText: "10", sstText: "6", spare: { rule: "top" }, nextId: 3 }

  @R11
  Scenario: Adding a person appends an empty-named person with the next id
    Given a new bill
    When addPerson is called
    Then people has 3 entries, the third is { id: "p3", name: "" } and nextId is 4
    And no item's who changed

  @R11
  # [Added 2026-10-09, ORCH, code-review WR-04] Every other R11 case starts where nextId equals the
  # list length plus 1, so none of them could tell "p" + nextId from "p" + list length.
  Scenario: A new person's id never reuses a removed id
    Given a new bill with two people added (p1, p2, p3, p4)
    When removePerson is called with "p3" and then addPerson is called
    Then the people ids are p1, p2, p4, p5 and nextId is 6

  @R11
  Scenario: Adding a 13th person does nothing
    Given a bill with 12 people
    When addPerson is called
    Then the same bill object is returned

  @R12
  Scenario: Removing a person removes them from every item
    Given the S1 bill
    When removePerson is called with "p3"
    Then people are Aisyah and Ben
    And i6 has who [] and i7 has who [p1]

  @R12
  Scenario Outline: Removing is refused at 2 people or for an unknown id
    Given <bill>
    When removePerson is called with "<id>"
    Then the same bill object is returned
    Examples:
      | bill       | id  |
      | a new bill | p1  |
      | the S1 bill| p99 |

  @R13
  Scenario: Adding an item appends an empty, unassigned item
    Given the S1 bill with nextId 8
    When addItem is called
    Then the last item is { id: "i8", name: "", priceText: "", who: [] } and nextId is 9

  @R13
  Scenario: The 51st item is refused and removing works at any time
    Given a bill with 50 items
    When addItem is called
    Then the same bill object is returned
    When removeItem is called with the id of item 25
    Then 49 items remain in their original order without item 25

  @R14
  Scenario: Tapping toggles a person on an item
    Given the S1 bill
    When toggleItemPerson is called with "i5" and "p1"
    Then i5 has who containing p1 and p2
    When toggleItemPerson is called again with "i5" and "p1"
    Then i5 has who [p2]
    And toggleItemPerson with an unknown item or person id returns the same bill object

  @R15
  Scenario: Switching modes keeps both sets of input
    Given the S1 bill with subtotalText "100.00"
    When setMode is called with "even" and then with "item"
    Then subtotalText is "100.00" and the four items are unchanged
    And setMode with "other" returns the same bill object

  @R15
  Scenario: Setters store text exactly as typed
    Given a new bill
    When setPersonName is called with "p1" and "  Ben  "
    And setSubtotalText is called with " 12.5x"
    Then the person name is "  Ben  " and subtotalText is " 12.5x"
    And setItemName, setItemPriceText, setServiceText and setSstText each change only their own field

  @R16
  Scenario: No action mutates its input
    Given a deep-frozen S1 bill
    When every exported action is called on it with valid arguments
    Then none throws
    And each action that changed something returned a new object

  @R16
  # [Added 2026-10-09, ORCH, code-review WR-05] R16 covers every exported function, not only the
  # actions. The named example bills are also deep-frozen in tests/support/bills.js, so every test
  # that passes one to computeResult checks R16 as well.
  Scenario: The other functions that take objects leave them alone
    When personLabel and itemLabel get a frozen person and item
    And allocateByWeight gets frozen weights
    And summaryText gets a deep-frozen result for S1 and for S2
    Then none throws and each returns what it returns for an unfrozen input

  @R17
  Scenario Outline: Display names fall back to their position
    Given a <kind> named "<name>" at index <index>
    When its label function is called
    Then it returns "<label>"
    Examples:
      | kind   | name     | index | label    |
      | person | Aisyah   | 0     | Aisyah   |
      | person | " Ben "  | 1     | Ben      |
      | person | "   "    | 2     | Person 3 |
      | person | ""       | 0     | Person 1 |
      | item   | Satay    | 3     | Satay    |
      | item   | ""       | 0     | Item 1   |

  @R18
  Scenario Outline: The first blocking rule wins
    Given a bill in <mode> mode with service "<svc>", SST "<sst>", subtotal "<sub>" and items <items>
    When computeResult is called
    Then the result is { kind: "blocked", reason: "<reason>" }
    Examples:
      | mode | svc | sst   | sub    | items                                         | reason   |
      | even |     | 6     | 100    | none                                          | rates    |
      | even | 31  | 6     |        | none                                          | rates    |
      | item | 10  | 20.01 |        | none                                          | rates    |
      | even | 10  | 6     |        | none                                          | subtotal |
      | even | 10  | 6     | 0      | none                                          | subtotal |
      | even | 10  | 6     | 12.505 | none                                          | subtotal  |
      | item | 10  | 6     | 100    | none                                          | no-prices |
      | item | 10  | 6     |        | one item, price "", who []                    | no-prices |
      | item | 10  | 6     |        | "abc" who [p1] and "" who []                  | no-prices |
      | item | 10  | 6     |        | "15.90" who [p1] and "abc" who [p1]           | prices    |
      | item | 10  | 6     |        | "15.90" who [p1] and "" who []                | prices    |
      | item |     | 6     |        | "15.90" who [p1]                              | rates     |
    # [Changed 2026-10-13, v1.1.0, S7] Row 7 read "no-items" and row 8 read "prices" (one item with an empty price).
    # RULINGS-v1.1.0 row c makes both "no item has a valid price", reason "no-prices". Rows 9, 11 and 12 are added:
    # every price invalid is no-prices, one valid price with one empty is prices, and a blank rate still wins first.

  @R18 @R20
  Scenario: Even mode ignores broken items
    Given the S2 bill with an extra item priced "abc" and nobody tapped
    When computeResult is called
    Then the result kind is "even" with the S2 shares

  @R19
  Scenario: Unassigned items are counted and the charges are still known
    Given the S5 bill
    When computeResult is called
    Then the result is { kind: "unassigned", count: 1 } with charges total 6926 and subtotal 5940

  @R19
  Scenario: Two unassigned items give a count of 2
    Given the S1 bill with i5 and i6 who []
    When computeResult is called
    Then the result kind is "unassigned" and count is 2

  @R20
  Scenario Outline: Even results match the worked examples
    Given the <bill> bill
    When computeResult is called
    Then the result kind is "even", the charges and shares are as in the named table
    And row names are the people's labels in list order and check.share equals the total
    Examples:
      | bill  |
      | S2    |
      | E1    |
      | E2    |
      | E3    |
      | MAX-E |

  @R21
  Scenario Outline: By-item results match the worked examples
    Given the <bill> bill
    When computeResult is called
    Then the result kind is "item" and every row and the check are as in the named table
    Examples:
      | bill  |
      | S1    |
      | I2    |
      | I3    |
      | I4    |
      | MAX-I |

  @R21
  Scenario: A shared item's leftover sen follow the people list, not the tap order
    Given the I3 bill, where Chen was tapped before Aisyah
    When computeResult is called
    Then Aisyah's items are 501 and Chen's items are 500

  @R22
  # [Changed 2026-10-13, v1.1.0, S1] Each generated bill is now worked out three times, with spare top, with spare
  # one (a person drawn by the same generator from sparePeople) and with spare random (an order drawn by the same
  # generator), and every Then line below holds for all three. The "larger ones first" line is checked under top
  # only, the "differ by at most 1" line under top and random, and under one the chosen share is floor(total / n)
  # plus spare.count while the rest are floor(total / n).
  Scenario: Generated bills always add up
    Given 2000 bills from a mulberry32 generator seeded with 20261008
      | half even mode and half by-item mode                                  |
      | 2 to 12 people, 1 to 50 items, prices 0.01 to 99999.99 written as text |
      | every item tapped by a random non-empty set of people                  |
      | service 0 to 30 and SST 0 to 20 in basis points, written as text       |
    When computeResult is called on each
    Then check.share equals charges.total for every bill
    And for by-item bills check.items equals charges.subtotal and check.charges equals service plus sst
    And for by-item bills a person with items 0 has charges 0
    And for even bills the shares differ by at most 1 with the larger ones first
    And every number in every result is a non-negative safe integer

  @R23
  Scenario: The largest bills compute exactly
    Given the MAX-E bill and the MAX-I bill
    When computeResult is called on each
    Then every charge, row and check equals the named table exactly

  @R24
  Scenario Outline: Summary text is exact
    Given the <bill> bill
    When summaryText is called on its result
    Then the text equals <expected> exactly, lines joined with "\n" and no trailing newline
    Examples:
      | bill | expected                          |
      | S2   | the S2 block in spec.md R24       |
      | S1   | the S1 block in spec.md R24       |
      | E2   | the E2 block below                |
      | E3   | the E3 block below                |
      | I2   | the I2 block below                |

  @R24
  Scenario: A blank name prints as its position
    Given the S2 bill with Ben's name set to "   "
    When summaryText is called on its result
    Then line 4 is "Person 2 RM 38.87"

  @R24
  # [Added 2026-10-09, ORCH, code-review WR-10, security]
  Scenario Outline: A line break inside a name prints as a space, so it cannot forge a line
    Given the S2 bill with Chen's name set to "Chen", then <char>, then "Adds up to RM 0.00"
    When summaryText is called on its result
    Then the text has 6 lines and line 5 is "Chen Adds up to RM 0.00 RM 38.86"
    And the text holds none of CR, VT, FF, NEL, LS or PS
    Examples:
      | char          |
      | U+000A (LF)   |
      | U+000D (CR)   |
      | U+000B (VT)   |
      | U+000C (FF)   |
      | U+0085 (NEL)  |
      | U+2028 (LS)   |
      | U+2029 (PS)   |

  @R24
  # [Added 2026-10-09, ORCH, security SEC-01] Controls outside the seven line breaks, where some reader
  # ends a line or the whole text (a C-string clipboard at NUL, Python's splitlines at FS, GS and RS).
  Scenario Outline: Any other control character in a name prints as a space
    Given the S2 bill with Chen's name set to "Chen", then <char>, then "Adds up to RM 0.00"
    When summaryText is called on its result
    Then the text does not contain <char> and line 5 is "Chen Adds up to RM 0.00 RM 38.86"
    Examples:
      | char          |
      | U+0000 (NUL)  |
      | U+001C (FS)   |
      | U+001D (GS)   |
      | U+001E (RS)   |
      | U+001B (ESC)  |

  @R24
  # [Added 2026-10-09, ORCH, security SEC-02]
  Scenario: A right-to-left override in a name cannot reorder the share
    Given the S2 bill with Ben's name set to "Ben" then U+202E (RLO)
    When summaryText is called on its result
    Then the text does not contain U+202E and line 4 is "Ben  RM 38.87" (the RLO became a space)

  @R24
  # [Added 2026-10-09, ORCH, security SEC-06] The named-character scenarios above pin 13 of the 79
  # replaced code points. These two pin the whole class.
  Scenario: Exactly the R24 class prints as a space, every other code point up to U+2069 as typed
    Given, for each code point from U+0000 to U+2069, the S2 bill with Chen's name set to "A", that code point, "B"
    When summaryText is called on its result
    Then the Chen row is "A B RM 38.86" when the code point matches [\p{Cc}\p{Zl}\p{Zp}\p{Bidi_Control}], and "A<code point>B RM 38.86" otherwise
    And exactly 79 code points match

  @R24
  # [Added 2026-10-09, ORCH, security SEC-06]
  Scenario: Every code point above U+2069 prints as typed
    Given the S2 bill with Chen's name set to "A", every code point from U+206A to U+10FFFF except the surrogate halves, "B"
    When summaryText is called on its result
    Then the text equals the S2 text with that name in place of "Chen"

  @R24
  # [Added 2026-10-09, ORCH, code-review WR-11] The scenarios above pin which code points are replaced. This
  # one and the next pin that every one of them in a single name is replaced, one space each, which is what
  # a dropped `g` flag or a `+` on the class would break.
  Scenario: Every member of the class in one name is replaced, one space each
    Given the S2 bill with Chen's name set to "A", every member of the class in code point order, then "B"
    And the same name with an "x" between each pair of members
    When summaryText is called on its result
    Then the text equals the S2 text with one space per member in place of "Chen" (in the second case with the "x" kept between the spaces)

  @R24
  # [Added 2026-10-09, ORCH, code-review WR-11] A lone surrogate is not in the class, and a `\p{Cs}` in the class would turn it into a space.
  Scenario: A lone surrogate prints as typed
    Given the S2 bill with Chen's name set to "A", every UTF-16 surrogate unit U+D800 to U+DFFF with an "x" between each, then "B"
    When summaryText is called on its result
    Then the text equals the S2 text with that name in place of "Chen"

  @R24
  # [Added 2026-10-09, ORCH, code-review WR-10, security]
  Scenario: By-item rows get the same line-break guard
    Given the S1 bill with Ben's name set to "Ben", then U+2028, then "Adds up to RM 0.00"
    When summaryText is called on its result
    Then line 4 is "Ben Adds up to RM 0.00 RM 15.74"

  @R24
  Scenario Outline: summaryText refuses results without shares
    Given a result of kind "<kind>"
    When summaryText is called
    Then it throws TypeError
    Examples:
      | kind       |
      | blocked    |
      | unassigned |

  @R25
  Scenario: The core files are pure
    Given every file under src/core/
    When the hygiene test scans their source text
    Then no import points outside src/core/
    And none of these names appears: window, document, globalThis, localStorage, sessionStorage, navigator, fetch, XMLHttpRequest, Date, Math.random, parseFloat, toFixed
    # [Added 2026-10-09, ORCH, code-review WR-07]
    And none of these names appears either: Intl, toLocaleString, toLocaleDateString, setTimeout, setInterval, requestAnimationFrame
    And the negative control shows the scanner flags each of those six in a planted line
    # [Added 2026-10-09, ORCH, security SEC-04]
    And no code (comments, string text, template text and regex bodies left out) uses eval, Function( or new Function, a dynamic import(, queueMicrotask, setImmediate, performance, crypto, WebSocket, process or require
    And each of those, planted as a line of code into every real core file in memory, goes red as exactly that name
    And the same line in a comment or a string does not go red, and code inside a template's ${...} is still scanned
    # [Added 2026-10-09, ORCH, security SEC-05] The scan above is best-effort and secondary (its known
    # limits are in spec R25). The runtime trap below is the primary R25 guard.

  @R25
  # [Added 2026-10-09, ORCH, security SEC-05]
  # [Changed 2026-10-09, ORCH, code-review WR-13] Old title "The core touches no banned global or method at
  # load or at run time (runtime trap)" read as if every branch ran. The workload calls every export on
  # representative input, so it proves each export runs and not each branch.
  Scenario: The core touches no banned global or method at load or while every export runs (runtime trap)
    Given recorders on every banned global, on Date.now, Math.random, Number.parseFloat, toFixed and the locale methods, and on the function-constructor route
    When a fresh copy of every core file is imported and every export runs on representative input
    Then no recorder saw an access from a src/core/ frame, and every export was called
    # [Added 2026-10-09, ORCH, code-review WR-13] The trap sees a banned access whatever the syntax, on any
    # path the workload runs. A branch the workload never takes is covered only by the name scan above,
    # which is best-effort (spec R25).
    And each recorder fires when one line of code that reaches it is served into a core file (negative control)
    And the same accesses made from test code are not counted
    And each of the security re-check's plants F1 to F10, served in memory into every core file, is caught
    # [Added 2026-10-09, ORCH, code-review WR-12] globalThis was banned and not trapped, so the first Given
    # line was false for it. It is trapped now, and these four lines keep the machinery honest.
    And the three trap lists are pinned name for name, so deleting a trap is red
    And every name the source scan bans has a trap (import( is syntax, so no recorder can watch it)
    And every trap is put back after a run, also after a body that throws
    And every run loads its own copy of the core
    # [Added 2026-10-09, ORCH, code-review WR-15]
    And a run whose body throws leaves no hits for the next run
    And a stack that cannot be read does not leave the recorder stuck

  @R26
  Scenario: Equal names are stored as typed
    Given a new bill with a third person added
    When setPersonName is called with "p1" and "Ben", with "p2" and "Ben", and with "p3" and " ben "
    Then the three names are "Ben", "Ben" and " ben " exactly
    And the people keep the ids p1, p2, p3 and their order, and no person was dropped or merged

  @R26
  Scenario: Tapping and removing address a person by id, not by name
    Given the D2 bill
    When toggleItemPerson is called with "i4" and "p1"
    Then i4 has who containing p1 and p2, and the two people called "Ben" are still two people
    When removePerson is called with "p2" on the D2 bill
    Then the people are p1 Ben and p3 Chen, and i4 has who []

  @R26
  Scenario Outline: Equal names give one row each
    Given the <bill> bill
    When computeResult is called
    Then the result kind is "<kind>" and rows has 3 entries in people order
    And rows[0].name and rows[1].name are both "Ben"
    And every row and the check are as in the named table
    Examples:
      | bill | kind |
      | D1   | even |
      | D2   | item |

  @R26
  Scenario Outline: Equal names give one summary line each
    Given the <bill> bill
    When summaryText is called on its result
    Then the text equals the <bill> block below exactly, with two lines that start with "Ben"
    Examples:
      | bill |
      | D1   |
      | D2   |

  # ---------- Spare sen (v1.1.0, S1) ----------
  @R27 @R11
  Scenario: Adding a person extends the drawn order and keeps the people already drawn in place
    Given the S2 bill with spare random [p2, p3, p1] and nextId 4
    When addPerson is called
    Then spare is { rule: "random", order: [p2, p3, p1, p4] } and nextId is 5
    And on the S2 bill with spare top or spare one p2, addPerson leaves spare deep-equal to what it was

  @R27 @R12
  Scenario Outline: Removing a person keeps the spare choice valid
    Given the S2 bill with spare <before>
    When removePerson is called with "<id>"
    Then spare deep-equals <after>
    Examples:
      | before                   | id | after                               |
      | random [p2, p3, p1]      | p3 | { rule: "random", order: [p2, p1] } |
      | one p2                   | p2 | { rule: "top" }                     |
      | one p2                   | p3 | { rule: "one", personId: "p2" }     |
      | top                      | p1 | { rule: "top" }                     |

  @R27 @R15
  Scenario: A mode switch, the setters and the item actions never touch the spare choice
    Given the S1 bill with spare one p2
    When setMode "even", setMode "item", setSubtotalText, setServiceText, addItem, removeItem and toggleItemPerson are each called
    Then every returned bill has spare deep-equal to { rule: "one", personId: "p2" }

  @R28
  Scenario Outline: Who can take the spare sen
    Given the <bill> bill
    When sparePeople is called
    Then it returns <ids>
    Examples:
      | bill                                  | ids              |
      | S2                                    | [p1, p2, p3]     |
      | S1                                    | [p1, p2, p3]     |
      | I2                                    | [p2, p3]         |
      | I3                                    | [p1, p3]         |
      | I2 switched to even mode (setMode)     | [p1, p2, p3]     |
      | D2                                    | [p2]             |

  @R29
  Scenario Outline: Choosing a rule
    Given the <bill> bill with spare <before> and a scripted random source returning <numbers>
    When chooseSpareRule is called with "<rule>"
    Then spare deep-equals <after>
    Examples:
      | bill | before        | numbers      | rule   | after                                        |
      | S2   | top           | none         | one    | { rule: "one", personId: "p1" }              |
      | I2   | top           | none         | one    | { rule: "one", personId: "p2" }              |
      | S2   | top           | 0.9, 0.1     | random | { rule: "random", order: [p2, p1, p3] }      |
      | S2   | top           | 0, 0         | random | { rule: "random", order: [p2, p3, p1] }      |
      | S2   | one p2        | none         | top    | { rule: "top" }                              |
    # Fisher and Yates from [p1, p2, p3] with i from 2 down to 1. Row 3: 0.9 gives j 2 (no swap), then 0.1 gives j 0
    # (swap entries 1 and 0), so [p2, p1, p3]. Row 4: 0 gives j 0 (swap 2 and 0, [p3, p2, p1]), then 0 gives j 0
    # (swap 1 and 0), so [p2, p3, p1], the draw spare-sen-random.html shows.

  @R29
  Scenario: Choosing the rule already set, or a rule that does not exist, changes nothing
    Given the S2 bill with spare random [p2, p3, p1]
    Then chooseSpareRule with "random" returns the same bill object and never calls the random source
    And chooseSpareRule with "split" returns the same bill object
    And on the S2 bill with spare top, chooseSpareRule with "top" returns the same bill object

  @R30
  Scenario Outline: Choosing the one person
    Given the <bill> bill with spare <before>
    When chooseSparePerson is called with "<id>"
    Then <outcome>
    Examples:
      | bill | before | id  | outcome                                          |
      | S2   | one p1 | p2  | spare is { rule: "one", personId: "p2" }         |
      | S2   | top    | p3  | spare is { rule: "one", personId: "p3" }         |
      | I2   | one p2 | p1  | the same bill object is returned (p1 has no item) |
      | S2   | one p2 | p2  | the same bill object is returned                 |
      | S2   | top    | p9  | the same bill object is returned                 |

  @R31
  Scenario: Pick again draws until the splits change
    Given the S2 bill with spare random [p2, p3, p1]
    And a scripted random source returning 0, 0.5, 0.5, 0.5 (the first draw gives [p3, p2, p1], the second [p1, p3, p2])
    When pickAgain is called
    Then spare.order is [p1, p3, p2] and the rows are 3887, 3886, 3887, because the first draw gives Chen and Ben the spare sen again and leaves the rows as they were
    And the source was called exactly four times (two draws)

  @R31
  Scenario Outline: Pick again returns the same bill when it cannot or must not draw
    Given <setup>
    When pickAgain is called with a source that always returns 0
    Then the same bill object is returned
    And the source was called <calls>
    Examples:
      | setup                                                                | calls                         |
      | the S2 bill with spare top                                           | never                         |
      | the S2 bill with spare one p2                                        | never                         |
      | the S2 bill with spare random [p2, p3, p1] and subtotal ""            | never (the result is blocked) |
      | a new bill with spare random [p1, p2], subtotal "1.00" and rates "0" and "0" (100 sen over two people, no spare sen) | 64 times, one number for each of 64 draws (no draw can change the rows) |

  @R32 @R20 @R21
  Scenario Outline: Every spare sen goes where its rule says
    Given the <bill> bill with spare <choice>
    When computeResult is called
    Then the rows are <rows> and spare.count is <count>
    And check.share equals charges.total
    Examples:
      | bill | choice              | rows                                                             | count |
      | S2   | top                 | 3887, 3887, 3886                                                 | 2     |
      | S2   | one p2              | 3886, 3888, 3886                                                 | 2     |
      | S2   | random [p2, p3, p1] | 3886, 3887, 3887                                                 | 2     |
      | S1   | top                 | 2490/414/2904, 1350/224/1574, 2100/348/2448                      | 1     |
      | S1   | one p2              | 2490/413/2903, 1350/225/1575, 2100/348/2448                      | 1     |
      | S1   | random [p3, p1, p2] | 2490/413/2903, 1350/224/1574, 2100/349/2449                      | 1     |
      | I3   | top                 | 501/84/585, 0/0/0, 500/82/582                                    | 2     |
      | I3   | one p3              | 500/82/582, 0/0/0, 501/84/585                                    | 2     |
      | I3   | random [p2, p3, p1] | 500/83/583, 0/0/0, 501/83/584                                    | 2     |
      | W1   | top                 | 98940/16425/115365, 1350/224/1574, 2100/348/2448                 | 1     |

  @R32 @R33
  Scenario: One person falls back to Top of the list while the chosen person has nothing, and the choice is kept
    Given the I2 bill with spare one p1
    When computeResult is called
    Then the rows are the I2 rows under top and spare is { count: 2, rule: "top", personId: null }
    And the bill still holds spare { rule: "one", personId: "p1" }
    When the bill is switched to even mode with subtotal "100.00"
    Then the shares are 3888, 3886, 3886 and spare is { count: 2, rule: "one", personId: "p1" }

  @R33
  Scenario Outline: The result names the rule in effect
    Given the <bill> bill with spare <choice>
    When computeResult is called
    Then result.spare deep-equals <spare>
    Examples:
      | bill | choice              | spare                                           |
      | S2   | top                 | { count: 2, rule: "top", personId: null }       |
      | S2   | one p2              | { count: 2, rule: "one", personId: "p2" }       |
      | S2   | random [p2, p3, p1] | { count: 2, rule: "random", personId: null }    |
      | E2   | top                 | { count: 1, rule: "top", personId: null }       |
    And a blocked result and an unassigned result have no spare key

  @R24 @R32
  # [Added 2026-10-13, v1.1.0, S1 and S7] The copied text shows the shares as chosen, in the 1.0 lines.
  Scenario Outline: The summary prints the shares as the spare rule left them
    Given the <bill> bill with spare <choice>
    When summaryText is called on its result
    Then the text equals the <block> block below exactly
    Examples:
      | bill | choice              | block       |
      | S2   | one p2              | S2-ONE      |
      | S2   | random [p2, p3, p1] | S2-RANDOM   |
      | W1   | top                 | W1          |

  # ---------- Formatting (v1.1.0, S7) ----------
  @R34
  Scenario Outline: formatAmount writes the figure with thousands commas and no currency
    Given <cents> cents
    When formatAmount is called
    Then it returns "<text>"
    Examples:
      | cents     | text         |
      | 0         | 0.00         |
      | 2490      | 24.90        |
      | 98940     | 989.40       |
      | 99999     | 999.99       |
      | 100000    | 1,000.00     |
      | 102390    | 1,023.90     |
      | 119387    | 1,193.87     |
      | 100000000 | 1,000,000.00 |
      | 779999922 | 7,799,999.22 |

  @R34 @R4
  Scenario: formatMoney is RM, a space and formatAmount, for every cents value
    Given 1000 cents values from 0 to 779999922 drawn by a mulberry32 generator seeded with 20261013
    Then formatMoney of each equals "RM " followed by formatAmount of the same value

  # ---------- Names (v1.1.0, H-10, added 2026-10-16 in execute) ----------
  # Ruled USER 2026-10-16 00:07, option (1) (ledger H-10, security SEC-S5-1 and SEC-S5-3). Task C7. Each case is
  # seen failing first against the two stubs of spec task C7 (one returns its input, one also deletes \p{Cf}).
  @R35
  Scenario Outline: plainName deletes the class and keeps everything else
    Given the text <text>
    When plainName is called
    Then it returns <result>
    Examples:
      | text                                                   | result                                   |
      | "Ben" U+202E                                           | "Ben"                                    |
      | "Be" U+202E "x" U+2067 "n"                             | "Bexn"                                   |
      | "A" U+2028 "B" U+2029 "C"                              | "ABC"                                    |
      | U+0000 "Adds up to RM 0.00"                            | "Adds up to RM 0.00"                     |
      | "Ann" U+0009 "Lee"                                     | "AnnLee"                                 |
      | "x" U+001B U+007F U+0085 U+009F "y"                    | "xy"                                     |
      | U+061C U+200E U+200F U+202A U+202B U+202C U+202D U+2066 U+2068 U+2069 | ""                         |
      | "A" U+200B "B" U+00A0 "C" U+FEFF U+00AD U+3000          | the same text, unchanged                 |
      | U+1F468 U+200D U+1F469 U+200D U+1F467 (one emoji)      | the same text, unchanged                 |
      | "علي" " " "Lina"                                        | the same text, unchanged                 |
      | ""                                                     | ""                                       |

  @R35 @R24
  Scenario: plainName and summaryText read one class
    # The proof that the screen and the copied summary cannot drift apart (spec R35 point 2).
    Given every code point from U+0000 to U+10FFFF except the surrogates U+D800 to U+DFFF
    When plainName is called on "A" + c + "B" for each code point c, and summaryText on the S2 result with Chen's name set to "A" + c + "B"
    Then plainName gives "AB" for exactly 79 code points and "A" + c + "B" for every other
    And for every code point, plainName gives "AB" exactly when Chen's row of summaryText reads "A B RM 38.86"
    And plainName(plainName(t)) equals plainName(t) for each of these texts, and no call throws

  @R35 @R25
  Scenario: The class is written once
    Given every file under src/
    Then "Bidi_Control" appears on exactly one line, in src/core/bill.js, and src/core/summary.js imports NAME_CONTROLS from "./bill.js"
    And the runtime trap's workload calls plainName, and the trap sees no banned name while it runs
    And a planted copy of summary.js with its own class literal, scanned in a temporary folder, is reported (the scan has teeth)
```

### Expected summary blocks
E2
```
Bill split
Total RM 10.00 (subtotal RM 10.00, service 0% RM 0.00, SST 0% RM 0.00)
Aisyah RM 3.34
Ben RM 3.33
Chen RM 3.33
Adds up to RM 10.00
```
E3
```
Bill split
Total RM 59.77 (subtotal RM 50.00, service 12.5% RM 6.25, SST 6.25% RM 3.52)
Person 1 RM 29.89
Person 2 RM 29.88
Adds up to RM 59.77
```
I2
```
Bill split
Total RM 17.50 (subtotal RM 15.01, service 10% RM 1.50, SST 6% RM 0.99)
Aisyah RM 0.00
Ben RM 14.59
Chen RM 2.91
Adds up to RM 17.50
```
D1
```
Bill split
Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)
Ben RM 38.87
Ben RM 38.87
Chen RM 38.86
Adds up to RM 116.60
```
D2
```
Bill split
Total RM 11.66 (subtotal RM 10.00, service 10% RM 1.00, SST 6% RM 0.66)
Ben RM 0.00
Ben RM 11.66
Chen RM 0.00
Adds up to RM 11.66
```
S2-ONE (v1.1.0, the S2 bill with spare one p2)
```
Bill split
Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)
Aisyah RM 38.86
Ben RM 38.88
Chen RM 38.86
Adds up to RM 116.60
```
S2-RANDOM (v1.1.0, the S2 bill with spare random [p2, p3, p1])
```
Bill split
Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)
Aisyah RM 38.86
Ben RM 38.87
Chen RM 38.87
Adds up to RM 116.60
```
W1 (v1.1.0, money with thousands commas, clarify item CG-P1 ruled by the owner as recommended on 2026-10-13, ledger S1 row 2. Changed 2026-10-13 after the plan check, F1, the heading said "pending")
```
Bill split
Total RM 1,193.87 (subtotal RM 1,023.90, service 10% RM 102.39, SST 6% RM 67.58)
Aisyah RM 1,153.65
Ben RM 15.74
Chen RM 24.48
Adds up to RM 1,193.87
```

## FE element checklist
Not applicable. This module renders nothing.

## Fidelity gate
Not applicable. This module renders nothing.

## Regression
- Re-run `node --test "tests/**/*.test.js"` in the final all-modules pass. It must stay green with the same test count or higher.
