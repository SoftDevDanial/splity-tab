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

| Test file | Covers |
|---|---|
| `tests/money.test.js` | R1, R2, R3, R4, R5 |
| `tests/allocate.test.js` | R7, R8, R9 |
| `tests/bill.test.js` | R10 to R17, R26 |
| `tests/result.test.js` | R6, R18 to R21, R23, R26 |
| `tests/invariants.test.js` | R22 |
| `tests/summary.test.js` | R24, R26 |
| `tests/hygiene.test.js` | R25 |

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
  Scenario Outline: formatMoney writes RM, a space, ringgit and two sen digits
    Given <cents> cents
    When formatMoney is called
    Then it returns "<text>"
    Examples:
      | cents     | text          |
      | 0         | RM 0.00       |
      | 1         | RM 0.01       |
      | 10        | RM 0.10       |
      | 100       | RM 1.00       |
      | 3887      | RM 38.87      |
      | 11660     | RM 116.60     |
      | 15599999  | RM 155999.99  |
      | 779999922 | RM 7799999.22 |

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

  @R8 @R23
  Scenario: allocateByWeight stays exact when amount times weight passes 2^53
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
  Scenario: A new bill has two people, even mode and the default rates
    When newBill is called
    Then it deep-equals { mode: "even", people: [{ id: "p1", name: "Person 1" }, { id: "p2", name: "Person 2" }], subtotalText: "", items: [], serviceText: "10", sstText: "6", nextId: 3 }

  @R11
  Scenario: Adding a person appends an empty-named person with the next id
    Given a new bill
    When addPerson is called
    Then people has 3 entries, the third is { id: "p3", name: "" } and nextId is 4
    And no item's who changed

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
      | even | 10  | 6     | 12.505 | none                                          | subtotal |
      | item | 10  | 6     | 100    | none                                          | no-items |
      | item | 10  | 6     |        | one item, price "", who []                    | prices   |
      | item | 10  | 6     |        | "15.90" who [p1] and "abc" who [p1]           | prices   |

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

## FE element checklist
Not applicable. This module renders nothing.

## Fidelity gate
Not applicable. This module renders nothing.

## Regression
- Re-run `node --test "tests/**/*.test.js"` in the final all-modules pass. It must stay green with the same test count or higher.
