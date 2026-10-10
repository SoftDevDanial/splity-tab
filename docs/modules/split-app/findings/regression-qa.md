---
module: split-app
kind: qa
run: regression
status: pass
counts: { pass: 340, fail: 0, untested: 1 }
---

# Regression QA: split (split-core and split-app), v1.0.0

## Verdict

PASS, with 1 untested item and 0 failures. Scenario items: 340 pass, 0 fail, 1 untested, of 341 in total.
split-core gives 179 of 179 pass. split-app gives 161 of 162 pass and 1 untested.
The untested item is R40 "Looks right" (split-app). Its pixel half passed (all 10 fidelity pairs, 0 mismatching pixels). Its FE element checklist half was not judged in this run.

Suites. Node 275 of 275 pass and 0 fail. Browser 427 passed, 0 failed, 0 errors.
Five hand-driven flows at 390 x 844 give 73 checks passing, 0 failing, and 8 observations. Driven checks D1 to D4 give 55 of 55 passing. Gates. The fidelity gate passed 10 of 10 pairs and the live gate passed 7 of 7 steps.

The counts in the frontmatter are for the scenario table only: both qa.md files, one item per scenario and one item per outline row.

## 1. Suites

Each suite ran once. The node run is in node-test.txt and the browser run is in pytest.txt.

| Suite | Command | Result | Time | Evidence |
|-------|---------|--------|------|----------|
| split-core unit tests | `node --test "tests/**/*.test.js"` | 275 tests, 275 pass, 0 fail, 0 skipped, 0 todo | 263 ms by the runner's own duration_ms | node-test.txt |
| split-app browser suite | `python -m pytest tests/browser -q -p no:cacheprovider` | 427 passed, 0 failed, 0 errors (427 collected) | 109.87s by pytest (110.9 s wall) | pytest.txt, junit.xml, pytest-collect.txt |

The first attempt at the node summary (run_suites.py) crashed after the node suite had finished, on a regex for the
reporter's summary lines. The saved node output is the node run's record, and the node suite was not run again.
The browser suite's server started and stopped with its port free (pytest.txt).

## 2. Scenario table

Counting. Each non-outline scenario is one item. Each Examples row of a scenario outline is one item, so a single outline with four rows counts as four. split-core qa.md has 54 scenarios (21 outlines) and gives 179 items. split-app qa.md has 78 scenarios (25 outlines) and gives 162 items. A scenario with several Then clauses is one item, and the note says where a clause rests on a driven check.

Covering tests are named as the file and the test name. A pattern with * stands for the parameters, and the count of ids is given in brackets. Every cited test was looked up in the saved outputs before its row was written (build_findings.py): node tests in node-test.txt, pytest tests in junit.xml, driven checks in their JSON files. The same table is in scenario-table.md.

| # | file | R# | scenario | row | covering test or driven check | verdict | note |
|---|------|----|----------|-----|-------------------------------|---------|------|
| 1 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "12" is 1200 | money.test.js :: @R1 parseAmount("12") is 1200 cents | PASS |  |
| 2 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "12.5" is 1250 | money.test.js :: @R1 parseAmount("12.5") is 1250 cents | PASS |  |
| 3 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "12.50" is 1250 | money.test.js :: @R1 parseAmount("12.50") is 1250 cents | PASS |  |
| 4 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "0.01" is 1 | money.test.js :: @R1 parseAmount("0.01") is 1 cents | PASS |  |
| 5 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "99999.99" is 9999999 | money.test.js :: @R1 parseAmount("99999.99") is 9999999 cents | PASS |  |
| 6 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "1.15" is 115 | money.test.js :: @R1 parseAmount("1.15") is 115 cents | PASS |  |
| 7 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "4.35" is 435 | money.test.js :: @R1 parseAmount("4.35") is 435 cents | PASS |  |
| 8 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "0.29" is 29 | money.test.js :: @R1 parseAmount("0.29") is 29 cents | PASS |  |
| 9 | split-core | R1 | parseAmount accepts valid amounts as exact cents | " 12.50 " is 1250 | money.test.js :: @R1 parseAmount(" 12.50 ") is 1250 cents | PASS |  |
| 10 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "007" is 700 | money.test.js :: @R1 parseAmount("007") is 700 cents | PASS |  |
| 11 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "12." is 1200 | money.test.js :: @R1 parseAmount("12.") is 1200 cents | PASS |  |
| 12 | split-core | R1 | parseAmount accepts valid amounts as exact cents | "0000000012.50" is 1250 | money.test.js :: @R1 parseAmount("0000000012.50") is 1250 cents | PASS |  |
| 13 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "0" | money.test.js :: @R1 @R2 parseAmount("0") is invalid, not empty | PASS |  |
| 14 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "0.00" | money.test.js :: @R1 @R2 parseAmount("0.00") is invalid, not empty | PASS |  |
| 15 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "100000" | money.test.js :: @R1 @R2 parseAmount("100000") is invalid, not empty | PASS |  |
| 16 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "99999.991" | money.test.js :: @R1 @R2 parseAmount("99999.991") is invalid, not empty | PASS |  |
| 17 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "12.505" | money.test.js :: @R1 @R2 parseAmount("12.505") is invalid, not empty | PASS |  |
| 18 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "13.505" | money.test.js :: @R1 @R2 parseAmount("13.505") is invalid, not empty | PASS |  |
| 19 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "-5" | money.test.js :: @R1 @R2 parseAmount("-5") is invalid, not empty | PASS |  |
| 20 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "+5" | money.test.js :: @R1 @R2 parseAmount("+5") is invalid, not empty | PASS |  |
| 21 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "1,000" | money.test.js :: @R1 @R2 parseAmount("1,000") is invalid, not empty | PASS |  |
| 22 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | ".5" | money.test.js :: @R1 @R2 parseAmount(".5") is invalid, not empty | PASS |  |
| 23 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "1e3" | money.test.js :: @R1 @R2 parseAmount("1e3") is invalid, not empty | PASS |  |
| 24 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "0x10" | money.test.js :: @R1 @R2 parseAmount("0x10") is invalid, not empty | PASS |  |
| 25 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "Infinity" | money.test.js :: @R1 @R2 parseAmount("Infinity") is invalid, not empty | PASS |  |
| 26 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "NaN" | money.test.js :: @R1 @R2 parseAmount("NaN") is invalid, not empty | PASS |  |
| 27 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "abc" | money.test.js :: @R1 @R2 parseAmount("abc") is invalid, not empty | PASS |  |
| 28 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "12 50" | money.test.js :: @R1 @R2 parseAmount("12 50") is invalid, not empty | PASS |  |
| 29 | split-core | R1 R2 | parseAmount rejects invalid text as invalid, not empty | "１２" | money.test.js :: @R1 @R2 parseAmount("１２") is invalid, not empty | PASS |  |
| 30 | split-core | R1 R2 | A 401-character amount is rejected without overflow or exception |  | money.test.js :: @R1 @R2 a 401-character amount is invalid and does not throw | PASS |  |
| 31 | split-core | R1 R3 | A whole part longer than the ceiling's is refused before any numeric conversion |  | money.test.js :: @R1 @R3 a whole part longer than the ceiling's is refused before any numeric conversion | PASS | the test spies on Number, and its positive controls show the spy is not blind |
| 32 | split-core | R2 | Empty or white-space text is reported as empty | "" | money.test.js :: @R2 "" is reported as empty by both parsers | PASS |  |
| 33 | split-core | R2 | Empty or white-space text is reported as empty | "   " | money.test.js :: @R2 "   " is reported as empty by both parsers | PASS |  |
| 34 | split-core | R2 | The parsers never throw for any string |  | money.test.js :: @R2 the parsers never throw and always return a well-formed result | PASS | 500 seeded strings; the test alphabet has one space where qa.md lists two (see observation 12) |
| 35 | split-core | R3 | parseRate reads basis points within its maximum | "0", max 30 is 0 bp | money.test.js :: @R3 parseRate("0", 30) is 0 bp | PASS |  |
| 36 | split-core | R3 | parseRate reads basis points within its maximum | "10", max 30 is 1000 bp | money.test.js :: @R3 parseRate("10", 30) is 1000 bp | PASS |  |
| 37 | split-core | R3 | parseRate reads basis points within its maximum | "6", max 20 is 600 bp | money.test.js :: @R3 parseRate("6", 20) is 600 bp | PASS |  |
| 38 | split-core | R3 | parseRate reads basis points within its maximum | "6.5", max 20 is 650 bp | money.test.js :: @R3 parseRate("6.5", 20) is 650 bp | PASS |  |
| 39 | split-core | R3 | parseRate reads basis points within its maximum | "6.25", max 20 is 625 bp | money.test.js :: @R3 parseRate("6.25", 20) is 625 bp | PASS |  |
| 40 | split-core | R3 | parseRate reads basis points within its maximum | "30", max 30 is 3000 bp | money.test.js :: @R3 parseRate("30", 30) is 3000 bp | PASS |  |
| 41 | split-core | R3 | parseRate reads basis points within its maximum | "30.00", max 30 is 3000 bp | money.test.js :: @R3 parseRate("30.00", 30) is 3000 bp | PASS |  |
| 42 | split-core | R3 | parseRate reads basis points within its maximum | "20", max 20 is 2000 bp | money.test.js :: @R3 parseRate("20", 20) is 2000 bp | PASS |  |
| 43 | split-core | R3 | parseRate reads basis points within its maximum | "0.01", max 30 is 1 bp | money.test.js :: @R3 parseRate("0.01", 30) is 1 bp | PASS |  |
| 44 | split-core | R3 | parseRate reads basis points within its maximum | "6.", max 20 is 600 bp | money.test.js :: @R3 parseRate("6.", 20) is 600 bp | PASS |  |
| 45 | split-core | R3 | parseRate reads basis points within its maximum | "06", max 20 is 600 bp | money.test.js :: @R3 parseRate("06", 20) is 600 bp | PASS |  |
| 46 | split-core | R3 | parseRate reads basis points within its maximum | "30.01", max 30 is invalid | money.test.js :: @R3 parseRate("30.01", 30) is invalid | PASS |  |
| 47 | split-core | R3 | parseRate reads basis points within its maximum | "20.01", max 20 is invalid | money.test.js :: @R3 parseRate("20.01", 20) is invalid | PASS |  |
| 48 | split-core | R3 | parseRate reads basis points within its maximum | "25", max 20 is invalid | money.test.js :: @R3 parseRate("25", 20) is invalid | PASS |  |
| 49 | split-core | R3 | parseRate reads basis points within its maximum | "-1", max 30 is invalid | money.test.js :: @R3 parseRate("-1", 30) is invalid | PASS |  |
| 50 | split-core | R3 | parseRate reads basis points within its maximum | "6.255", max 20 is invalid | money.test.js :: @R3 parseRate("6.255", 20) is invalid | PASS |  |
| 51 | split-core | R3 | parseRate reads basis points within its maximum | "10%", max 30 is invalid | money.test.js :: @R3 parseRate("10%", 30) is invalid | PASS |  |
| 52 | split-core | R4 | formatMoney writes RM, a space, ringgit and two sen digits | 0 is "RM 0.00" | money.test.js :: @R4 formatMoney(0) is "RM 0.00" | PASS |  |
| 53 | split-core | R4 | formatMoney writes RM, a space, ringgit and two sen digits | 1 is "RM 0.01" | money.test.js :: @R4 formatMoney(1) is "RM 0.01" | PASS |  |
| 54 | split-core | R4 | formatMoney writes RM, a space, ringgit and two sen digits | 10 is "RM 0.10" | money.test.js :: @R4 formatMoney(10) is "RM 0.10" | PASS |  |
| 55 | split-core | R4 | formatMoney writes RM, a space, ringgit and two sen digits | 100 is "RM 1.00" | money.test.js :: @R4 formatMoney(100) is "RM 1.00" | PASS |  |
| 56 | split-core | R4 | formatMoney writes RM, a space, ringgit and two sen digits | 3887 is "RM 38.87" | money.test.js :: @R4 formatMoney(3887) is "RM 38.87" | PASS |  |
| 57 | split-core | R4 | formatMoney writes RM, a space, ringgit and two sen digits | 11660 is "RM 116.60" | money.test.js :: @R4 formatMoney(11660) is "RM 116.60" | PASS |  |
| 58 | split-core | R4 | formatMoney writes RM, a space, ringgit and two sen digits | 15599999 is "RM 155999.99" | money.test.js :: @R4 formatMoney(15599999) is "RM 155999.99" | PASS |  |
| 59 | split-core | R4 | formatMoney writes RM, a space, ringgit and two sen digits | 779999922 is "RM 7799999.22" | money.test.js :: @R4 formatMoney(779999922) is "RM 7799999.22" | PASS |  |
| 60 | split-core | R5 | formatRate drops trailing zeros and adds a percent sign | 0 is "0%" | money.test.js :: @R5 formatRate(0) is "0%" | PASS |  |
| 61 | split-core | R5 | formatRate drops trailing zeros and adds a percent sign | 600 is "6%" | money.test.js :: @R5 formatRate(600) is "6%" | PASS |  |
| 62 | split-core | R5 | formatRate drops trailing zeros and adds a percent sign | 1000 is "10%" | money.test.js :: @R5 formatRate(1000) is "10%" | PASS |  |
| 63 | split-core | R5 | formatRate drops trailing zeros and adds a percent sign | 650 is "6.5%" | money.test.js :: @R5 formatRate(650) is "6.5%" | PASS |  |
| 64 | split-core | R5 | formatRate drops trailing zeros and adds a percent sign | 625 is "6.25%" | money.test.js :: @R5 formatRate(625) is "6.25%" | PASS |  |
| 65 | split-core | R5 | formatRate drops trailing zeros and adds a percent sign | 605 is "6.05%" | money.test.js :: @R5 formatRate(605) is "6.05%" | PASS |  |
| 66 | split-core | R5 | formatRate drops trailing zeros and adds a percent sign | 3000 is "30%" | money.test.js :: @R5 formatRate(3000) is "30%" | PASS |  |
| 67 | split-core | R6 | Service and SST round half up to the cent | subtotal 10000, service 1000, SST 600, total 11660 | result.test.js :: @R6 billCharges(10000, 1000, 600) totals 11660 | PASS | the test checks service, base, SST and total together with both rates |
| 68 | split-core | R6 | Service and SST round half up to the cent | subtotal 5940, service 1000, SST 600, total 6926 | result.test.js :: @R6 billCharges(5940, 1000, 600) totals 6926 | PASS | the test checks service, base, SST and total together with both rates |
| 69 | split-core | R6 | Service and SST round half up to the cent | subtotal 8765, service 1000, SST 600, total 10221 | result.test.js :: @R6 billCharges(8765, 1000, 600) totals 10221 | PASS | the test checks service, base, SST and total together with both rates |
| 70 | split-core | R6 | Service and SST round half up to the cent | subtotal 5, service 1000, SST 0, total 6 | result.test.js :: @R6 billCharges(5, 1000, 0) totals 6 | PASS | the test checks service, base, SST and total together with both rates |
| 71 | split-core | R6 | Service and SST round half up to the cent | subtotal 25, service 1000, SST 0, total 28 | result.test.js :: @R6 billCharges(25, 1000, 0) totals 28 | PASS | the test checks service, base, SST and total together with both rates |
| 72 | split-core | R6 | Service and SST round half up to the cent | subtotal 4, service 1000, SST 0, total 4 | result.test.js :: @R6 billCharges(4, 1000, 0) totals 4 | PASS | the test checks service, base, SST and total together with both rates |
| 73 | split-core | R6 | Service and SST round half up to the cent | subtotal 1000, service 0, SST 0, total 1000 | result.test.js :: @R6 billCharges(1000, 0, 0) totals 1000 | PASS | the test checks service, base, SST and total together with both rates |
| 74 | split-core | R6 | Service and SST round half up to the cent | subtotal 5000, service 1250, SST 625, total 5977 | result.test.js :: @R6 billCharges(5000, 1250, 625) totals 5977 | PASS | the test checks service, base, SST and total together with both rates |
| 75 | split-core | R6 | Service and SST round half up to the cent | subtotal 9999999, service 3000, SST 2000, total 15599999 | result.test.js :: @R6 billCharges(9999999, 3000, 2000) totals 15599999 | PASS | the test checks service, base, SST and total together with both rates |
| 76 | split-core | R6 | Service and SST round half up to the cent | subtotal 499999950, service 3000, SST 2000, total 779999922 | result.test.js :: @R6 billCharges(499999950, 3000, 2000) totals 779999922 | PASS | the test checks service, base, SST and total together with both rates |
| 77 | split-core | R7 | allocateEvenly floors and hands leftover sen to the top | 11660 over 3 | allocate.test.js :: @R7 allocateEvenly(11660, 3) | PASS |  |
| 78 | split-core | R7 | allocateEvenly floors and hands leftover sen to the top | 1800 over 2 | allocate.test.js :: @R7 allocateEvenly(1800, 2) | PASS |  |
| 79 | split-core | R7 | allocateEvenly floors and hands leftover sen to the top | 1001 over 3 | allocate.test.js :: @R7 allocateEvenly(1001, 3) | PASS |  |
| 80 | split-core | R7 | allocateEvenly floors and hands leftover sen to the top | 1 over 3 | allocate.test.js :: @R7 allocateEvenly(1, 3) | PASS |  |
| 81 | split-core | R7 | allocateEvenly floors and hands leftover sen to the top | 0 over 2 | allocate.test.js :: @R7 allocateEvenly(0, 2) | PASS |  |
| 82 | split-core | R7 | allocateEvenly floors and hands leftover sen to the top | 10221 over 4 | allocate.test.js :: @R7 allocateEvenly(10221, 4) | PASS |  |
| 83 | split-core | R7 | allocateEvenly floors and hands leftover sen to the top | 15599999 over 12 | allocate.test.js :: @R7 allocateEvenly(15599999, 12) | PASS |  |
| 84 | split-core | R8 | allocateByWeight floors exactly and skips zero weights for leftovers | 986 over [2490,1350,2100] | allocate.test.js :: @R8 allocateByWeight(986, [2490,1350,2100]) | PASS |  |
| 85 | split-core | R8 | allocateByWeight floors exactly and skips zero weights for leftovers | 10 over [0,1,1,1] | allocate.test.js :: @R8 allocateByWeight(10, [0,1,1,1]) | PASS |  |
| 86 | split-core | R8 | allocateByWeight floors exactly and skips zero weights for leftovers | 0 over [5,7] | allocate.test.js :: @R8 allocateByWeight(0, [5,7]) | PASS |  |
| 87 | split-core | R8 | allocateByWeight floors exactly and skips zero weights for leftovers | 249 over [0,1251,250] | allocate.test.js :: @R8 allocateByWeight(249, [0,1251,250]) | PASS |  |
| 88 | split-core | R8 | allocateByWeight floors exactly and skips zero weights for leftovers | 236419679 over [314963010,157876348] | allocate.test.js :: @R8 BigInt trap: allocateByWeight(236419679, [314963010,157876348]) | PASS |  |
| 89 | split-core | R8 | allocateByWeight floors exactly and skips zero weights for leftovers | 61846725 over [49676084,322894546] | allocate.test.js :: @R8 BigInt trap: allocateByWeight(61846725, [49676084,322894546]) | PASS |  |
| 90 | split-core | R8 | allocateByWeight floors exactly and skips zero weights for leftovers | 178450942 over [111531837,207130558] | allocate.test.js :: @R8 BigInt trap: allocateByWeight(178450942, [111531837,207130558]) | PASS |  |
| 91 | split-core | R8 R23 | allocateByWeight gives the MAX-I charges split exactly, with products past 2^53 |  | allocate.test.js :: @R8 @R23 allocateByWeight gives the MAX-I charges split exactly, with products past 2^53 | PASS |  |
| 92 | split-core | R9 | Allocation rejects impossible input | allocateEvenly(10, 0) | allocate.test.js :: @R9 allocateEvenly(10, 0) throws RangeError | PASS |  |
| 93 | split-core | R9 | Allocation rejects impossible input | allocateEvenly(10, 1.5) | allocate.test.js :: @R9 allocateEvenly(10, 1.5) throws RangeError | PASS |  |
| 94 | split-core | R9 | Allocation rejects impossible input | allocateEvenly(-1, 2) | allocate.test.js :: @R9 allocateEvenly(-1, 2) throws RangeError | PASS |  |
| 95 | split-core | R9 | Allocation rejects impossible input | allocateEvenly(0.5, 2) | allocate.test.js :: @R9 allocateEvenly(0.5, 2) throws RangeError | PASS |  |
| 96 | split-core | R9 | Allocation rejects impossible input | allocateByWeight(10, []) | allocate.test.js :: @R9 allocateByWeight(10, []) throws RangeError | PASS |  |
| 97 | split-core | R9 | Allocation rejects impossible input | allocateByWeight(10, [0, 0]) | allocate.test.js :: @R9 allocateByWeight(10, [0, 0]) throws RangeError | PASS |  |
| 98 | split-core | R9 | Allocation rejects impossible input | allocateByWeight(10, [1, -1]) | allocate.test.js :: @R9 allocateByWeight(10, [1, -1]) throws RangeError | PASS |  |
| 99 | split-core | R9 | Allocation rejects impossible input | allocateByWeight(10, [1.5, 1]) | allocate.test.js :: @R9 allocateByWeight(10, [1.5, 1]) throws RangeError | PASS |  |
| 100 | split-core | R9 | Allocation rejects impossible input | allocateByWeight(-1, [1]) | allocate.test.js :: @R9 allocateByWeight(-1, [1]) throws RangeError | PASS |  |
| 101 | split-core | R10 | A new bill has two people, even mode and the default rates |  | bill.test.js :: @R10 a new bill has two people, even mode and the default rates | PASS |  |
| 102 | split-core | R11 | Adding a person appends an empty-named person with the next id |  | bill.test.js :: @R11 adding a person appends an empty-named person with the next id | PASS |  |
| 103 | split-core | R11 | A new person's id never reuses a removed id |  | bill.test.js :: @R11 a new person's id comes from nextId, so it never reuses a removed id | PASS |  |
| 104 | split-core | R11 | Adding a 13th person does nothing |  | bill.test.js :: @R11 the twelfth person is accepted and the thirteenth does nothing | PASS |  |
| 105 | split-core | R12 | Removing a person removes them from every item |  | bill.test.js :: @R12 removing a person removes them from every item | PASS |  |
| 106 | split-core | R12 | Removing is refused at 2 people or for an unknown id | a new bill, p1 | bill.test.js :: @R12 removing is refused at 2 people or for an unknown id | PASS | one test covers both rows |
| 107 | split-core | R12 | Removing is refused at 2 people or for an unknown id | the S1 bill, p99 | bill.test.js :: @R12 removing is refused at 2 people or for an unknown id | PASS | one test covers both rows |
| 108 | split-core | R13 | Adding an item appends an empty, unassigned item |  | bill.test.js :: @R13 adding an item appends an empty, unassigned item | PASS |  |
| 109 | split-core | R13 | The 51st item is refused and removing works at any time |  | bill.test.js :: @R13 the 51st item is refused and removing works at any time | PASS |  |
| 110 | split-core | R14 | Tapping toggles a person on an item |  | bill.test.js :: @R14 tapping toggles a person on an item + bill.test.js :: @R14 an unknown item or person id returns the same bill | PASS |  |
| 111 | split-core | R15 | Switching modes keeps both sets of input |  | bill.test.js :: @R15 switching modes keeps both sets of input | PASS | the same test checks that setMode with other returns the same object |
| 112 | split-core | R15 | Setters store text exactly as typed |  | bill.test.js :: @R15 setters store text exactly as typed + bill.test.js :: @R15 each setter changes only its own field | PASS |  |
| 113 | split-core | R16 | No action mutates its input |  | bill.test.js :: @R16 no action mutates a deep-frozen bill and changes return new objects | PASS |  |
| 114 | split-core | R16 | The other functions that take objects leave them alone |  | allocate.test.js :: @R16 allocateByWeight leaves frozen weights alone + bill.test.js :: @R16 @R17 the labels leave a frozen person or item alone + summary.test.js :: @R16 summaryText leaves a deep-frozen result alone | PASS |  |
| 115 | split-core | R17 | Display names fall back to their position | person "Aisyah" at 0 is "Aisyah" | bill.test.js :: @R17 person named "Aisyah" at index 0 is "Aisyah" | PASS |  |
| 116 | split-core | R17 | Display names fall back to their position | person " Ben " at 1 is "Ben" | bill.test.js :: @R17 person named " Ben " at index 1 is "Ben" | PASS |  |
| 117 | split-core | R17 | Display names fall back to their position | person "   " at 2 is "Person 3" | bill.test.js :: @R17 person named "   " at index 2 is "Person 3" | PASS |  |
| 118 | split-core | R17 | Display names fall back to their position | person "" at 0 is "Person 1" | bill.test.js :: @R17 person named "" at index 0 is "Person 1" | PASS |  |
| 119 | split-core | R17 | Display names fall back to their position | item "Satay" at 3 is "Satay" | bill.test.js :: @R17 item named "Satay" at index 3 is "Satay" | PASS |  |
| 120 | split-core | R17 | Display names fall back to their position | item "" at 0 is "Item 1" | bill.test.js :: @R17 item named "" at index 0 is "Item 1" | PASS |  |
| 121 | split-core | R18 | The first blocking rule wins | row 1, rates | result.test.js :: @R18 blocking row 1 is "rates" | PASS |  |
| 122 | split-core | R18 | The first blocking rule wins | row 2, rates | result.test.js :: @R18 blocking row 2 is "rates" | PASS |  |
| 123 | split-core | R18 | The first blocking rule wins | row 3, rates | result.test.js :: @R18 blocking row 3 is "rates" | PASS |  |
| 124 | split-core | R18 | The first blocking rule wins | row 4, subtotal | result.test.js :: @R18 blocking row 4 is "subtotal" | PASS |  |
| 125 | split-core | R18 | The first blocking rule wins | row 5, subtotal | result.test.js :: @R18 blocking row 5 is "subtotal" | PASS |  |
| 126 | split-core | R18 | The first blocking rule wins | row 6, subtotal | result.test.js :: @R18 blocking row 6 is "subtotal" | PASS |  |
| 127 | split-core | R18 | The first blocking rule wins | row 7, no-items | result.test.js :: @R18 blocking row 7 is "no-items" | PASS |  |
| 128 | split-core | R18 | The first blocking rule wins | row 8, prices | result.test.js :: @R18 blocking row 8 is "prices" | PASS |  |
| 129 | split-core | R18 | The first blocking rule wins | row 9, prices | result.test.js :: @R18 blocking row 9 is "prices" | PASS |  |
| 130 | split-core | R18 R20 | Even mode ignores broken items |  | result.test.js :: @R18 @R20 even mode ignores broken items | PASS |  |
| 131 | split-core | R19 | Unassigned items are counted and the charges are still known |  | result.test.js :: @R19 unassigned items are counted and the charges are still known | PASS |  |
| 132 | split-core | R19 | Two unassigned items give a count of 2 |  | result.test.js :: @R19 two unassigned items give a count of 2 | PASS |  |
| 133 | split-core | R20 | Even results match the worked examples | S2 | result.test.js :: @R20 @R23 even result for S2 | PASS |  |
| 134 | split-core | R20 | Even results match the worked examples | E1 | result.test.js :: @R20 @R23 even result for E1 | PASS |  |
| 135 | split-core | R20 | Even results match the worked examples | E2 | result.test.js :: @R20 @R23 even result for E2 | PASS |  |
| 136 | split-core | R20 | Even results match the worked examples | E3 | result.test.js :: @R20 @R23 even result for E3 | PASS |  |
| 137 | split-core | R20 | Even results match the worked examples | MAX-E | result.test.js :: @R20 @R23 even result for MAX-E | PASS |  |
| 138 | split-core | R21 | By-item results match the worked examples | S1 | result.test.js :: @R21 @R23 by-item result for S1 | PASS |  |
| 139 | split-core | R21 | By-item results match the worked examples | I2 | result.test.js :: @R21 @R23 by-item result for I2 | PASS |  |
| 140 | split-core | R21 | By-item results match the worked examples | I3 | result.test.js :: @R21 @R23 by-item result for I3 | PASS |  |
| 141 | split-core | R21 | By-item results match the worked examples | I4 | result.test.js :: @R21 @R23 by-item result for I4 | PASS |  |
| 142 | split-core | R21 | By-item results match the worked examples | MAX-I | result.test.js :: @R21 @R23 by-item result for MAX-I | PASS |  |
| 143 | split-core | R21 | A shared item's leftover sen follow the people list, not the tap order |  | result.test.js :: @R21 a shared item's leftover sen follow the people list, not the tap order | PASS |  |
| 144 | split-core | R22 | Generated bills always add up |  | invariants.test.js :: @R22 generated bills always add up | PASS |  |
| 145 | split-core | R23 | The largest bills compute exactly | MAX-E and MAX-I | result.test.js :: @R20 @R23 even result for MAX-E + result.test.js :: @R21 @R23 by-item result for MAX-I + result.test.js :: @R23 MAX-I charges are exact at the bound | PASS |  |
| 146 | split-core | R24 | Summary text is exact | S2 | summary.test.js :: @R24 summary text for S2 is exact | PASS |  |
| 147 | split-core | R24 | Summary text is exact | S1 | summary.test.js :: @R24 summary text for S1 is exact | PASS |  |
| 148 | split-core | R24 | Summary text is exact | E2 | summary.test.js :: @R24 summary text for E2 zero rates is exact | PASS |  |
| 149 | split-core | R24 | Summary text is exact | E3 | summary.test.js :: @R24 summary text for E3 decimal rates is exact | PASS |  |
| 150 | split-core | R24 | Summary text is exact | I2 | summary.test.js :: @R24 summary text for I2 zero share is exact | PASS |  |
| 151 | split-core | R24 | A blank name prints as its position |  | summary.test.js :: @R24 a blank name prints as its position | PASS |  |
| 152 | split-core | R24 | A line break inside a name prints as a space, so it cannot forge a line | LF | summary.test.js :: @R24 a LF inside a name prints as a space, so it cannot forge a line | PASS |  |
| 153 | split-core | R24 | A line break inside a name prints as a space, so it cannot forge a line | CR | summary.test.js :: @R24 a CR inside a name prints as a space, so it cannot forge a line | PASS |  |
| 154 | split-core | R24 | A line break inside a name prints as a space, so it cannot forge a line | VT | summary.test.js :: @R24 a VT inside a name prints as a space, so it cannot forge a line | PASS |  |
| 155 | split-core | R24 | A line break inside a name prints as a space, so it cannot forge a line | FF | summary.test.js :: @R24 a FF inside a name prints as a space, so it cannot forge a line | PASS |  |
| 156 | split-core | R24 | A line break inside a name prints as a space, so it cannot forge a line | NEL | summary.test.js :: @R24 a NEL inside a name prints as a space, so it cannot forge a line | PASS |  |
| 157 | split-core | R24 | A line break inside a name prints as a space, so it cannot forge a line | LS | summary.test.js :: @R24 a LS inside a name prints as a space, so it cannot forge a line | PASS |  |
| 158 | split-core | R24 | A line break inside a name prints as a space, so it cannot forge a line | PS | summary.test.js :: @R24 a PS inside a name prints as a space, so it cannot forge a line | PASS |  |
| 159 | split-core | R24 | Any other control character in a name prints as a space | NUL | summary.test.js :: @R24 a NUL inside a name prints as a space, so no reader can cut the summary there | PASS |  |
| 160 | split-core | R24 | Any other control character in a name prints as a space | FS | summary.test.js :: @R24 a FS inside a name prints as a space, so no reader can cut the summary there | PASS |  |
| 161 | split-core | R24 | Any other control character in a name prints as a space | GS | summary.test.js :: @R24 a GS inside a name prints as a space, so no reader can cut the summary there | PASS |  |
| 162 | split-core | R24 | Any other control character in a name prints as a space | RS | summary.test.js :: @R24 a RS inside a name prints as a space, so no reader can cut the summary there | PASS |  |
| 163 | split-core | R24 | Any other control character in a name prints as a space | ESC | summary.test.js :: @R24 a ESC inside a name prints as a space, so no reader can cut the summary there | PASS |  |
| 164 | split-core | R24 | A right-to-left override in a name cannot reorder the share |  | summary.test.js :: @R24 a right-to-left override in a name cannot reorder the share | PASS |  |
| 165 | split-core | R24 | Exactly the R24 class prints as a space, every other code point up to U+2069 as typed |  | summary.test.js :: @R24 exactly the R24 class prints as a space, every other code point up to U+2069 as typed | PASS |  |
| 166 | split-core | R24 | Every code point above U+2069 prints as typed |  | summary.test.js :: @R24 every code point above U+2069 prints as typed | PASS |  |
| 167 | split-core | R24 | Every member of the class in one name is replaced, one space each |  | summary.test.js :: @R24 every member of the class in one name is replaced, one space each | PASS |  |
| 168 | split-core | R24 | A lone surrogate prints as typed |  | summary.test.js :: @R24 a lone surrogate is not in the class, so it prints as typed | PASS |  |
| 169 | split-core | R24 | By-item rows get the same line-break guard |  | summary.test.js :: @R24 by-item rows get the same line-break guard | PASS |  |
| 170 | split-core | R24 | summaryText refuses results without shares | kind blocked | summary.test.js :: @R24 results without shares are refused with TypeError | PASS | one test covers both rows |
| 171 | split-core | R24 | summaryText refuses results without shares | kind unassigned | summary.test.js :: @R24 results without shares are refused with TypeError | PASS | one test covers both rows |
| 172 | split-core | R25 | The core files are pure |  | hygiene.test.js :: @R25 the scan sees the core files + hygiene.test.js :: @R25 the scanner catches what it should (negative control) + hygiene.test.js :: @R25 the code-only scan reads code, and skips comments, strings, template text and regex bodies + hygiene.test.js :: @R25 allocate.js uses no banned name + hygiene.test.js :: @R25 bill.js uses no banned name + hygiene.test.js :: @R25 money.js uses no banned name + hygiene.test.js :: @R25 result.js uses no banned name + hygiene.test.js :: @R25 summary.js uses no banned name + hygiene.test.js :: @R25 allocate.js imports only from src/core/ + hygiene.test.js :: @R25 bill.js imports only from src/core/ + hygiene.test.js :: @R25 money.js imports only from src/core/ + hygiene.test.js :: @R25 result.js imports only from src/core/ + hygiene.test.js :: @R25 summary.js imports only from src/core/ + hygiene.test.js :: @R25 the core files do import each other (the import scan is not blind) + hygiene.test.js :: @R25 const run = (text) => eval(text); served into each core file goes red as eval + hygiene.test.js :: @R25 const make = (body) => Function(body); served into each core file goes red as Function + hygiene.test.js :: @R25 const build = (body) => new Function(body); served into each core file goes red as Function + hygiene.test.js :: @R25 const load = (name) => import(name); served into each core file goes red as import( + hygiene.test.js :: @R25 const soon = (fn) => queueMicrotask(fn); served into each core file goes red as queueMicrotask + hygiene.test.js :: @R25 const later = (fn) => setImmediate(fn); served into each core file goes red as setImmediate + hygiene.test.js :: @R25 const now = () => performance.now(); served into each core file goes red as performance + hygiene.test.js :: @R25 const pick = () => crypto.getRandomValues(new Uint32Array(1))[0]; served into each core file goes red as crypto + hygiene.test.js :: @R25 const open = (url) => new WebSocket(url); served into each core file goes red as WebSocket + hygiene.test.js :: @R25 const env = () => process.env.SPLIT; served into each core file goes red as process + hygiene.test.js :: @R25 const load = (name) => require(name); served into each core file goes red as require | PASS |  |
| 173 | split-core | R25 | The core touches no banned global or method at load or while every export runs (runtime trap) |  | hygiene.test.js :: @R25 runtime trap: the core touches no banned global or method while it loads and while every export runs + hygiene.test.js :: @R25 runtime trap: every trap fires for core code and not for test code (negative control) + hygiene.test.js :: @R25 runtime trap: the trap lists are exactly the pinned ones, so no trap is dropped unseen + hygiene.test.js :: @R25 runtime trap: every name the source scan bans has a trap + hygiene.test.js :: @R25 runtime trap: every trap is put back after a run, also after a body that throws + hygiene.test.js :: @R25 runtime trap: every run loads its own copy of the core + hygiene.test.js :: @R25 runtime trap: a run whose body throws leaves no hits for the next run + hygiene.test.js :: @R25 runtime trap: a stack that cannot be read does not leave the recorder stuck + hygiene.test.js :: @R25 runtime trap catches the security re-check's F1 plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F2 plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F3 plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F4 plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F4b plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F5 plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F6 plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F6b plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F7 plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F8 plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F9 plant in every core file + hygiene.test.js :: @R25 runtime trap catches the security re-check's F10 plant in every core file | PASS |  |
| 174 | split-core | R26 | Equal names are stored as typed |  | bill.test.js :: @R26 equal names are stored as typed and nobody is merged | PASS |  |
| 175 | split-core | R26 | Tapping and removing address a person by id, not by name |  | bill.test.js :: @R26 tapping and removing address a person by id, not by name | PASS |  |
| 176 | split-core | R26 | Equal names give one row each | D1, even | result.test.js :: @R26 D1: two people called Ben give two even rows | PASS |  |
| 177 | split-core | R26 | Equal names give one row each | D2, item | result.test.js :: @R26 D2: two people called Ben give two by-item rows, only the tapped one pays | PASS |  |
| 178 | split-core | R26 | Equal names give one summary line each | D1, even | summary.test.js :: @R24 summary text for D1 equal names, even is exact + summary.test.js :: @R26 equal names print one line each | PASS |  |
| 179 | split-core | R26 | Equal names give one summary line each | D2, item | summary.test.js :: @R24 summary text for D2 equal names, by item is exact + summary.test.js :: @R26 equal names print one line each | PASS |  |
| 180 | split-app | R1 | The entry point loads only its own files |  | tests/browser/test_app.py :: test_R1_entry_point_loads_only_its_own_files | PASS |  |
| 181 | split-app | R1 | The page works from a sub-path, as on GitHub Pages |  | tests/browser/test_app.py :: test_R1_page_works_from_a_sub_path | PASS |  |
| 182 | split-app | R2 | Cold boot is a new bill with no seed |  | tests/browser/test_app.py :: test_R2_cold_boot_is_a_new_bill_with_no_seed | PASS |  |
| 183 | split-app | R2 | No sample data ships |  | tests/browser/test_app.py :: test_R2_no_sample_data_ships | PASS |  |
| 184 | split-app | R3 | The rendered markup matches its golden | S3, cold boot, bill-empty | tests/browser/test_app.py :: test_R3_rendered_markup_matches_its_golden[S3-None-bill-empty] | PASS |  |
| 185 | split-app | R3 | The rendered markup matches its golden | S2 seeded, bill-even | tests/browser/test_app.py :: test_R3_a_restored_bill_matches_its_golden[S2] + tests/browser/test_app.py :: test_R3_rendered_markup_matches_its_golden_by_gestures[S2-build_s2-bill-even] | PASS | the seeded walk is the scenario; the gesture-built walk is the same golden built by hand |
| 186 | split-app | R3 | The rendered markup matches its golden | S1 seeded, bill-items | tests/browser/test_app.py :: test_R3_a_restored_bill_matches_its_golden[S1] + tests/browser/test_app.py :: test_R3_rendered_markup_matches_its_golden_by_gestures[S1-build_s1-bill-items] | PASS |  |
| 187 | split-app | R3 | The rendered markup matches its golden | S5 seeded, bill-unassigned | tests/browser/test_app.py :: test_R3_a_restored_bill_matches_its_golden[S5] + tests/browser/test_app.py :: test_R3_rendered_markup_matches_its_golden_by_gestures[S5-build_s5-bill-unassigned] | PASS |  |
| 188 | split-app | R4 | Person rows carry their names and labels |  | tests/browser/test_app.py :: test_R4_person_rows_carry_their_names_and_labels + tests/browser/test_app.py :: test_R3_a_restored_bill_matches_its_golden[S1] | PASS | names typed by gestures, the same rows; the seeded S1 walk matches bill-items.html |
| 189 | split-app | R4 R5 | A blank name falls back to its position everywhere but the field |  | tests/browser/test_app.py :: test_R4_a_blank_name_falls_back_to_its_position_but_not_in_the_field + tests/browser/test_app.py :: test_R5_a_person_label_follows_the_name_into_every_toggle + tests/browser/test_app.py :: test_R5_a_blank_name_reads_as_its_position_in_the_shares_row | PASS | toggles and shares row checked on the gesture-built S1 bill |
| 190 | split-app | R5 | Renaming a person updates every place on each keystroke |  | tests/browser/test_app.py :: test_R5_renaming_a_person_updates_the_remove_name_on_each_keystroke + tests/browser/test_app.py :: test_R5_a_new_name_reaches_the_copied_text + driven_checks.py (driven), group 'D1 R5 rename per keystroke, S1 seed', 19 checks | PASS | the suite checks the remove name on each key and the final toggles; D1 drives the toggles and shares row on each key |
| 191 | split-app | R5 | Renaming an item updates its accessible names |  | tests/browser/test_app.py :: test_R5_renaming_an_item_updates_its_accessible_names | PASS |  |
| 192 | split-app | R6 | Add person until the limit |  | tests/browser/test_app.py :: test_R6_add_person_until_the_limit | PASS | the cursor and the specimen properties are compared to the S8 button in states.html |
| 193 | split-app | R7 | Remove a person and they leave every item |  | tests/browser/test_app.py :: test_R7_removing_a_person_takes_them_off_every_item + tests/browser/test_app.py :: test_R7_removing_a_person_can_leave_an_item_without_anyone + tests/browser/test_app.py :: test_R7_remove_a_person | PASS | built by gestures, the same screen as the S1 seed |
| 194 | split-app | R7 | A repeat press on the last Remove removes that row and adds nothing | S2, Remove Chen | tests/browser/test_app.py :: test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing[S2-person-3-of-3-*] (12 ids) | PASS | sizes 360x640, 390x844, 1280x800; gestures single, mouse double, mouse triple, touch double |
| 195 | split-app | R7 | A repeat press on the last Remove removes that row and adds nothing | S8, Remove Mei Ling | tests/browser/test_app.py :: test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing[S8-person-12-of-12-*] (12 ids) | PASS | sizes 360x640, 390x844, 1280x800; gestures single, mouse double, mouse triple, touch double |
| 196 | split-app | R7 | A repeat press on the last Remove removes that row and adds nothing | S1, Remove Satay | tests/browser/test_app.py :: test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing[S1-item-4-of-4-*] (12 ids) | PASS | sizes 360x640, 390x844, 1280x800; gestures single, mouse double, mouse triple, touch double |
| 197 | split-app | R7 | A repeat press on the last Remove removes that row and adds nothing | S1 with only its last item, Remove Satay | tests/browser/test_app.py :: test_R7_a_repeat_press_on_the_last_remove_removes_that_row_and_adds_nothing[S1-only-item-*] (12 ids) | PASS | sizes 360x640, 390x844, 1280x800; gestures single, mouse double, mouse triple, touch double |
| 198 | split-app | R34 | After a double click or double tap on a middle Remove, focus is where one click puts it | S1, Remove Char kuey teow | tests/browser/test_app.py :: test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it[item-2-of-4-*] (2 ids) | PASS | mouse double click and touch double tap |
| 199 | split-app | R34 | After a double click or double tap on a middle Remove, focus is where one click puts it | S2 with five people, Remove P2 | tests/browser/test_app.py :: test_R34_after_a_double_click_on_remove_focus_is_where_one_click_puts_it[person-2-of-5-*] (2 ids) | PASS | mouse double click and touch double tap |
| 200 | split-app | R7 | A press of its own is never held back |  | tests/browser/test_app.py :: test_R7_a_separate_click_on_what_slid_under_the_pointer_is_not_held_back + tests/browser/test_app.py :: test_R7_the_guard_of_a_remove_click_ends_at_the_next_press + tests/browser/test_app.py :: test_R7_after_a_remove_click_a_double_click_on_a_name_still_selects_the_word | PASS |  |
| 201 | split-app | R6 | A repeat press on Add person adds one person and keeps it | middle of the button | tests/browser/test_app.py :: test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it[*-centre] (36 ids) | PASS | people 2, 3, 4, 5 by sizes and gestures |
| 202 | split-app | R6 | A repeat press on Add person adds one person and keeps it | 22 px in from the right edge | tests/browser/test_app.py :: test_R6_a_repeat_press_on_add_person_adds_one_person_and_keeps_it[*-right-edge] (36 ids) | PASS | people 2, 3, 4, 5 by sizes and gestures |
| 203 | split-app | R12 | A repeat press on Add item adds one item and never reaches the page | middle of the button | tests/browser/test_app.py :: test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page[*-centre] (18 ids) | PASS | items 1 and 4 by sizes and gestures, with the body recorder |
| 204 | split-app | R12 | A repeat press on Add item adds one item and never reaches the page | 22 px in from the right edge | tests/browser/test_app.py :: test_R12_a_repeat_press_on_add_item_adds_one_item_and_never_reaches_the_page[*-right-edge] (18 ids) | PASS | items 1 and 4 by sizes and gestures, with the body recorder |
| 205 | split-app | R7 R12 | A repeat press on a chip under a pending price error never removes the item | widths 375 and 390 | tests/browser/test_app.py :: test_R7_a_repeat_press_on_a_chip_under_a_pending_price_error_never_removes_the_item[*] (6 ids) | PASS | widths 375 and 390 with mouse double, mouse triple and touch double |
| 206 | split-app | R42 | Two people may have the same name |  | tests/browser/test_app.py :: test_R42_duplicate_names_are_accepted_and_act_on_their_own_row + tests/browser/test_app.py :: test_R42_duplicate_names_through_the_whole_flow + tests/browser/test_app.py :: test_R42_the_draft_keeps_both_people_with_the_same_name | PASS |  |
| 207 | split-app | R8 | Switching modes keeps both sets of input |  | tests/browser/test_app.py :: test_R8_switching_modes_keeps_the_subtotal + tests/browser/test_app.py :: test_R8_switching_modes_keeps_both_sets_of_input + tests/browser/test_app.py :: test_R8_the_panel_follows_each_mode + tests/browser/test_app.py :: test_R8_both_sets_of_input_survive_a_reload | PASS |  |
| 208 | split-app | R8 | Arrow keys move between the modes |  | tests/browser/test_app.py :: test_R8_arrow_keys_move_between_the_modes | PASS |  |
| 209 | split-app | R9 | The subtotal field drives the even split |  | tests/browser/test_app.py :: test_R9_subtotal_field_has_its_unit_label_and_input_mode + tests/browser/test_app.py :: test_R9_a_subtotal_drives_the_even_split | PASS |  |
| 210 | split-app | R10 | An inline error waits for the field to be left | subtotal | tests/browser/test_app.py :: test_R10_an_inline_error_waits_for_the_field_to_be_left[subtotal] | PASS |  |
| 211 | split-app | R10 | An inline error waits for the field to be left | item-price | tests/browser/test_app.py :: test_R10_an_inline_error_waits_for_the_field_to_be_left[item-price] | PASS |  |
| 212 | split-app | R10 | An inline error waits for the field to be left | service | tests/browser/test_app.py :: test_R10_an_inline_error_waits_for_the_field_to_be_left[service] | PASS |  |
| 213 | split-app | R10 | An inline error waits for the field to be left | sst | tests/browser/test_app.py :: test_R10_an_inline_error_waits_for_the_field_to_be_left[sst] | PASS |  |
| 214 | split-app | R10 | An empty field never shows an error |  | tests/browser/test_app.py :: test_R10_an_empty_field_never_shows_an_error + tests/browser/test_app.py :: test_R10_an_empty_rate_never_shows_an_error | PASS |  |
| 215 | split-app | R10 | Typing invalid text in a focused field does not show the error early |  | tests/browser/test_app.py :: test_R10_typing_bad_text_in_a_focused_field_shows_no_error_early | PASS |  |
| 216 | split-app | R10 | A restored invalid field shows its error at once |  | tests/browser/test_app.py :: test_R10_a_restored_bad_field_shows_its_error_at_once | PASS |  |
| 217 | split-app | R10 | An error survives a mode switch |  | tests/browser/test_app.py :: test_R10_an_error_survives_a_mode_switch | PASS |  |
| 218 | split-app | R10 R13 | A press below an invalid field lands on the control it started on | subtotal | tests/browser/test_app.py :: test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[subtotal-mouse] + tests/browser/test_app.py :: test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[subtotal-touch] | PASS | a mouse press and a touch tap |
| 219 | split-app | R10 R13 | A press below an invalid field lands on the control it started on | item-price | tests/browser/test_app.py :: test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[item-price-mouse] + tests/browser/test_app.py :: test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[item-price-touch] | PASS | a mouse press and a touch tap |
| 220 | split-app | R10 R13 | A press below an invalid field lands on the control it started on | service | tests/browser/test_app.py :: test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[service-mouse] + tests/browser/test_app.py :: test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[service-touch] | PASS | a mouse press and a touch tap |
| 221 | split-app | R10 R13 | A press below an invalid field lands on the control it started on | sst | tests/browser/test_app.py :: test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[sst-mouse] + tests/browser/test_app.py :: test_R10_a_press_below_an_invalid_field_lands_on_the_control_it_started_on[sst-touch] | PASS | a mouse press and a touch tap |
| 222 | split-app | R13 | A tap on a person below an invalid, unflagged price toggles them and then shows the error |  | tests/browser/test_app.py :: test_R13_a_tap_below_an_invalid_price_toggles_that_person_and_then_shows_the_error[mouse] + tests/browser/test_app.py :: test_R13_a_tap_below_an_invalid_price_toggles_that_person_and_then_shows_the_error[touch] | PASS |  |
| 223 | split-app | R10 | The error waits for the release, and only a press holds it back |  | tests/browser/test_app.py :: test_R10_the_error_waits_for_the_mouse_button_to_come_up + tests/browser/test_app.py :: test_R10_pressing_empty_space_also_waits_for_the_release + tests/browser/test_app.py :: test_R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press[mouse] + tests/browser/test_app.py :: test_R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press[touch] + tests/browser/test_app.py :: test_R10_a_keyboard_blur_shows_the_error_at_once_even_after_a_press[held] | PASS |  |
| 224 | split-app | R11 | Item rows carry their names and labels |  | tests/browser/test_app.py :: test_R11_item_rows_carry_their_names_and_labels + tests/browser/test_app.py :: test_R3_a_restored_bill_matches_its_golden[S1] | PASS | names typed by gestures, the same rows; the seeded S1 walk matches bill-items.html |
| 225 | split-app | R12 | Add an item, remove one, and reach the limit |  | tests/browser/test_app.py :: test_R12_add_an_item_remove_one_and_reach_the_limit | PASS | the cursor and the specimen properties are compared |
| 226 | split-app | R13 | Tapping a person on an item |  | tests/browser/test_app.py :: test_R13_tapping_a_person_on_an_item + tests/browser/test_app.py :: test_R13_tapping_a_person_changes_the_shares | PASS |  |
| 227 | split-app | R14 | A price error sits in the item line |  | tests/browser/test_app.py :: test_R14_a_price_error_sits_in_the_item_line | PASS |  |
| 228 | split-app | R34 | Focus after adding or removing | cold boot, Add person, Person 3 name | tests/browser/test_app.py :: test_R34_focus_moves_to_the_name_field_at_the_removed_position[Ben-Chen] | PASS | the test's first assertion, from a cold boot |
| 229 | split-app | R34 | Focus after adding or removing | S1, Remove Ben, Person 2 name (Chen) | driven_r34.py (driven), group 'D4 R34 focus after a click, S1 seed', rows starting 'row b:', 3 checks | PASS | driven on the S1 seed (D4); the suite test removes Ben from a three-person bill |
| 230 | split-app | R34 | Focus after adding or removing | S1, Remove Chen, Person 2 name (Ben) | driven_r34.py (driven), group 'D4 R34 focus after a click, S1 seed', rows starting 'row c:', 3 checks | PASS | driven on the S1 seed (D4); the suite test removes Chen from a three-person bill |
| 231 | split-app | R34 | Focus after adding or removing | S1, Add item, Item 5 name | driven_r34.py (driven), group 'D4 R34 focus after a click, S1 seed', rows starting 'row d:', 3 checks + tests/browser/test_app.py :: test_R34_focus_after_adding_or_removing_an_item[Add item-Item 5 name] | PASS | driven on the S1 seed (D4) with the suite test on the same bill |
| 232 | split-app | R34 | Focus after adding or removing | S1, Remove Char kuey teow, Item 2 name (Mee goreng mamak) | driven_r34.py (driven), group 'D4 R34 focus after a click, S1 seed', rows starting 'row e:', 3 checks + tests/browser/test_app.py :: test_R34_focus_after_adding_or_removing_an_item[Remove Char kuey teow-Item 2 name] | PASS | driven on the S1 seed (D4) with the suite test on the same bill |
| 233 | split-app | R34 | Focus after adding or removing | S1, Remove Satay, Item 3 name | driven_r34.py (driven), group 'D4 R34 focus after a click, S1 seed', rows starting 'row f:', 3 checks + tests/browser/test_app.py :: test_R34_focus_after_adding_or_removing_an_item[Remove Satay, 10 sticks-Item 3 name] | PASS | driven on the S1 seed (D4) with the suite test on the same bill |
| 234 | split-app | R34 | Focus after adding or removing | cold boot, By item, one item, Remove Item 1, Add item | tests/browser/test_app.py :: test_R34_removing_the_last_item_focuses_add_item | PASS |  |
| 235 | split-app | R33 | Typing never loses its place | Person 1 name, Aisyah | tests/browser/test_app.py :: test_R33_typing_in_a_person_name_keeps_focus_and_caret | PASS |  |
| 236 | split-app | R33 | Typing never loses its place | Item 1 name, Nasi | tests/browser/test_app.py :: test_R33_typing_in_an_item_field_keeps_focus_and_caret[<lambda>-Nasi] | PASS |  |
| 237 | split-app | R33 | Typing never loses its place | Item 1 price in RM, 15.90 | tests/browser/test_app.py :: test_R33_typing_in_an_item_field_keeps_focus_and_caret[<lambda>-15.90] | PASS |  |
| 238 | split-app | R33 | Typing never loses its place | Subtotal, 100.00 | tests/browser/test_app.py :: test_R33_typing_in_an_amount_or_a_rate_keeps_focus_and_caret[subtotal] | PASS |  |
| 239 | split-app | R33 | Typing never loses its place | Service charge, 12.5 | tests/browser/test_app.py :: test_R33_typing_in_an_amount_or_a_rate_keeps_focus_and_caret[service-charge] | PASS |  |
| 240 | split-app | R33 | IME composition survives a render |  | tests/browser/test_app.py :: test_R33_ime_composition_survives_a_render | PASS |  |
| 241 | split-app | R15 | The Charges block and its defaults |  | tests/browser/test_app.py :: test_R15_charges_block_and_its_defaults | PASS |  |
| 242 | split-app | R15 | A rate error names both ids and its range |  | tests/browser/test_app.py :: test_R15_a_rate_error_names_both_ids_and_its_range | PASS |  |
| 243 | split-app | R15 R19 | A charge of 0 is allowed and still shown |  | tests/browser/test_app.py :: test_R19_a_charge_of_zero_is_allowed_and_still_shown | PASS |  |
| 244 | split-app | R16 | The panel follows every keystroke and stays quiet |  | tests/browser/test_app.py :: test_R16_the_panel_follows_every_keystroke_and_stays_quiet + tests/browser/test_app.py :: test_R16_the_status_is_the_only_live_element_and_only_while_the_table_is | PASS |  |
| 245 | split-app | R17 | When the shares cannot be worked out | rate-empty | tests/browser/test_app.py :: test_R17_when_the_shares_cannot_be_worked_out[rate-empty] | PASS |  |
| 246 | split-app | R17 | When the shares cannot be worked out | rate-too-high | tests/browser/test_app.py :: test_R17_when_the_shares_cannot_be_worked_out[rate-too-high] | PASS |  |
| 247 | split-app | R17 | When the shares cannot be worked out | subtotal-empty | tests/browser/test_app.py :: test_R17_when_the_shares_cannot_be_worked_out[subtotal-empty] | PASS |  |
| 248 | split-app | R17 | When the shares cannot be worked out | no-items | tests/browser/test_app.py :: test_R17_when_the_shares_cannot_be_worked_out[no-items] | PASS |  |
| 249 | split-app | R17 | When the shares cannot be worked out | item-unpriced | tests/browser/test_app.py :: test_R17_when_the_shares_cannot_be_worked_out[item-unpriced] | PASS |  |
| 250 | split-app | R17 | When the shares cannot be worked out | item-bad-price | tests/browser/test_app.py :: test_R17_when_the_shares_cannot_be_worked_out[item-bad-price] | PASS |  |
| 251 | split-app | R18 | Items that still need a person |  | tests/browser/test_app.py :: test_R18_items_that_still_need_a_person | PASS |  |
| 252 | split-app | R19 | The bill summary shows its working | S2 | tests/browser/test_app.py :: test_R19_the_bill_summary_shows_its_working[S2] | PASS |  |
| 253 | split-app | R19 | The bill summary shows its working | S1 | tests/browser/test_app.py :: test_R19_the_bill_summary_shows_its_working[S1] | PASS |  |
| 254 | split-app | R20 | The even split from a cold boot (key flow 1) |  | tests/browser/test_app.py :: test_R20_the_even_split_from_a_cold_boot | PASS |  |
| 255 | split-app | R21 | The by-item split from gestures (key flow 2) |  | tests/browser/test_app.py :: test_R21_the_by_item_split_from_gestures | PASS | the table heads are checked as +Charges and =Share, the text the golden renders (observation 3) |
| 256 | split-app | R21 | Someone who had nothing is still listed |  | tests/browser/test_app.py :: test_R21_someone_who_had_nothing_is_still_listed | PASS |  |
| 257 | split-app | R22 | Copy summary puts the exact text on the clipboard | S2 | tests/browser/test_app.py :: test_R22_copy_summary_puts_the_exact_text_on_the_clipboard[S2] | PASS |  |
| 258 | split-app | R22 | Copy summary puts the exact text on the clipboard | S1 | tests/browser/test_app.py :: test_R22_copy_summary_puts_the_exact_text_on_the_clipboard[S1] | PASS |  |
| 259 | split-app | R23 | The browser blocks the clipboard |  | tests/browser/test_app.py :: test_R23_the_browser_blocks_the_clipboard + driven_checks.py (driven), group 'D3 R23 browser blocks the clipboard, S2 seed', 8 checks | PASS | the suite checks the status and the panel; D3 also checks the draft, the form and the shares rows |
| 260 | split-app | R23 | The clipboard API is missing |  | tests/browser/test_app.py :: test_R23_the_clipboard_api_is_missing | PASS |  |
| 261 | split-app | R24 | The status lives as long as the table |  | tests/browser/test_app.py :: test_R24_the_status_lives_as_long_as_the_table + tests/browser/test_app.py :: test_R24_the_status_is_not_saved | PASS |  |
| 262 | split-app | R25 | Every change is saved | type A into Person 1 name | tests/browser/test_app.py :: test_R25_every_change_is_saved[name] | PASS |  |
| 263 | split-app | R25 | Every change is saved | click Add person | tests/browser/test_app.py :: test_R25_every_change_is_saved[add-person] | PASS |  |
| 264 | split-app | R25 | Every change is saved | type 1 into Subtotal | tests/browser/test_app.py :: test_R25_every_change_is_saved[subtotal] | PASS |  |
| 265 | split-app | R25 | Every change is saved | click By item | tests/browser/test_app.py :: test_R25_every_change_is_saved[mode] | PASS |  |
| 266 | split-app | R25 | Every change is saved | click By item, then Add item | tests/browser/test_app.py :: test_R25_every_change_is_saved[add-item] | PASS |  |
| 267 | split-app | R25 | Every change is saved | replace SST with 8 | tests/browser/test_app.py :: test_R25_every_change_is_saved[sst] | PASS |  |
| 268 | split-app | R25 | Leaving a field or copying does not save |  | tests/browser/test_app.py :: test_R25_leaving_a_field_or_copying_does_not_save | PASS |  |
| 269 | split-app | R26 | Come back later (key flow 3) |  | tests/browser/test_app.py :: test_R26_come_back_later | PASS |  |
| 270 | split-app | R26 | Odd but readable drafts load | G1 | tests/browser/test_app.py :: test_R26_odd_but_readable_drafts_load[G1] | PASS |  |
| 271 | split-app | R26 | Odd but readable drafts load | G2 | tests/browser/test_app.py :: test_R26_odd_but_readable_drafts_load[G2] | PASS |  |
| 272 | split-app | R26 | Odd but readable drafts load | G3 | tests/browser/test_app.py :: test_R26_odd_but_readable_drafts_load[G3] | PASS |  |
| 273 | split-app | R27 | An unreadable draft starts a new bill with a note | B1 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B1] | PASS |  |
| 274 | split-app | R27 | An unreadable draft starts a new bill with a note | B2 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B2] | PASS |  |
| 275 | split-app | R27 | An unreadable draft starts a new bill with a note | B3 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B3] | PASS |  |
| 276 | split-app | R27 | An unreadable draft starts a new bill with a note | B4 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B4] | PASS |  |
| 277 | split-app | R27 | An unreadable draft starts a new bill with a note | B5 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B5] | PASS |  |
| 278 | split-app | R27 | An unreadable draft starts a new bill with a note | B6 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B6] | PASS |  |
| 279 | split-app | R27 | An unreadable draft starts a new bill with a note | B7 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B7] | PASS |  |
| 280 | split-app | R27 | An unreadable draft starts a new bill with a note | B8 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B8] | PASS |  |
| 281 | split-app | R27 | An unreadable draft starts a new bill with a note | B9 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B9] | PASS |  |
| 282 | split-app | R27 | An unreadable draft starts a new bill with a note | B10 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B10] | PASS |  |
| 283 | split-app | R27 | An unreadable draft starts a new bill with a note | B11 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B11] | PASS |  |
| 284 | split-app | R27 | An unreadable draft starts a new bill with a note | B12 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B12] | PASS |  |
| 285 | split-app | R27 | An unreadable draft starts a new bill with a note | B13 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B13] | PASS |  |
| 286 | split-app | R27 | An unreadable draft starts a new bill with a note | B14 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B14] | PASS |  |
| 287 | split-app | R27 | An unreadable draft starts a new bill with a note | B15 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B15] | PASS |  |
| 288 | split-app | R27 | An unreadable draft starts a new bill with a note | B16 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B16] | PASS |  |
| 289 | split-app | R27 | An unreadable draft starts a new bill with a note | B17 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B17] | PASS |  |
| 290 | split-app | R27 | An unreadable draft starts a new bill with a note | B18 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B18] | PASS |  |
| 291 | split-app | R27 | An unreadable draft starts a new bill with a note | B19 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B19] | PASS |  |
| 292 | split-app | R27 | An unreadable draft starts a new bill with a note | B20 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B20] | PASS |  |
| 293 | split-app | R27 | An unreadable draft starts a new bill with a note | B21 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B21] | PASS |  |
| 294 | split-app | R27 | An unreadable draft starts a new bill with a note | B22 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B22] | PASS |  |
| 295 | split-app | R27 | An unreadable draft starts a new bill with a note | B23 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B23] | PASS |  |
| 296 | split-app | R27 | An unreadable draft starts a new bill with a note | B24 | tests/browser/test_app.py :: test_R27_an_unreadable_draft_starts_a_new_bill_with_a_note[B24] | PASS |  |
| 297 | split-app | R27 | Dismissing the note |  | tests/browser/test_app.py :: test_R27_dismissing_the_note_moves_focus_to_the_first_name + tests/browser/test_app.py :: test_R27_the_note_is_not_touched_by_start_over | PASS |  |
| 298 | split-app | R28 | The app works without storage | read-localStorage | tests/browser/test_app.py :: test_R28_the_app_works_without_storage[read-localStorage] | PASS |  |
| 299 | split-app | R28 | The app works without storage | getItem | tests/browser/test_app.py :: test_R28_the_app_works_without_storage[getItem] | PASS |  |
| 300 | split-app | R28 | The app works without storage | setItem | tests/browser/test_app.py :: test_R28_the_app_works_without_storage[setItem] | PASS |  |
| 301 | split-app | R29 | The dialog opens with the safe choice focused |  | tests/browser/test_app.py :: test_R29_the_dialog_opens_with_the_safe_choice_focused | PASS |  |
| 302 | split-app | R30 | Leaving the dialog without starting over | cancel | tests/browser/test_app.py :: test_R30_leaving_the_dialog_without_starting_over[cancel] | PASS |  |
| 303 | split-app | R30 | Leaving the dialog without starting over | escape | tests/browser/test_app.py :: test_R30_leaving_the_dialog_without_starting_over[escape] | PASS |  |
| 304 | split-app | R30 | Leaving the dialog without starting over | backdrop-corner | tests/browser/test_app.py :: test_R30_leaving_the_dialog_without_starting_over[backdrop-corner] | PASS |  |
| 305 | split-app | R30 | Leaving the dialog without starting over | backdrop-over-a-field | tests/browser/test_app.py :: test_R30_leaving_the_dialog_without_starting_over[backdrop-over-a-field] | PASS |  |
| 306 | split-app | R29 | A repeat press on New bill leaves the dialog open | 360x640, 390x844, 1280x800 by 3 gestures | tests/browser/test_app.py :: test_R29_a_repeat_press_on_new_bill_leaves_the_dialog_open[*] (9 ids) | PASS | mouse double, mouse triple and touch double |
| 307 | split-app | R30 | After a double click on New bill one deliberate click still closes it | cancel | tests/browser/test_app.py :: test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[cancel] | PASS |  |
| 308 | split-app | R30 | After a double click on New bill one deliberate click still closes it | backdrop | tests/browser/test_app.py :: test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[backdrop] | PASS |  |
| 309 | split-app | R30 | After a double click on New bill one deliberate click still closes it | escape | tests/browser/test_app.py :: test_R30_after_a_double_click_on_new_bill_one_deliberate_click_still_closes_it[escape] | PASS |  |
| 310 | split-app | R29 | The keyboard and the next press are not held back |  | tests/browser/test_app.py :: test_R29_opening_by_keyboard_and_opening_again_straight_away_is_not_held_back + tests/browser/test_app.py :: test_R29_the_guard_of_opening_ends_at_the_next_press | PASS |  |
| 311 | split-app | R31 | Start over (key flow 4) |  | tests/browser/test_app.py :: test_R31_start_over | PASS |  |
| 312 | split-app | R31 | Start over clears the copy status |  | tests/browser/test_app.py :: test_R31_start_over_clears_the_copy_status | PASS |  |
| 313 | split-app | R31 | Start over clears the error flags | subtotal | tests/browser/test_app.py :: test_R31_start_over_clears_the_error_flags[subtotal] | PASS |  |
| 314 | split-app | R31 | Start over clears the error flags | item-price | tests/browser/test_app.py :: test_R31_start_over_clears_the_error_flags[item-price] | PASS |  |
| 315 | split-app | R31 | Start over clears the error flags | service | tests/browser/test_app.py :: test_R31_start_over_clears_the_error_flags[service] | PASS |  |
| 316 | split-app | R31 | Start over clears the error flags | sst | tests/browser/test_app.py :: test_R31_start_over_clears_the_error_flags[sst] | PASS |  |
| 317 | split-app | R32 | Tab order follows the golden | S3 | tests/browser/test_app.py :: test_R32_tab_order_follows_the_golden_and_every_stop_shows_its_ring[S3] + tests/browser/test_app.py :: test_R32_the_ring_check_has_teeth | PASS |  |
| 318 | split-app | R32 | Tab order follows the golden | S1 | tests/browser/test_app.py :: test_R32_tab_order_follows_the_golden_and_every_stop_shows_its_ring[S1] + tests/browser/test_app.py :: test_R32_the_ring_check_has_teeth | PASS |  |
| 319 | split-app | R32 | Tab order follows the golden | S7 | tests/browser/test_app.py :: test_R32_tab_order_follows_the_golden_and_every_stop_shows_its_ring[S7] + tests/browser/test_app.py :: test_R32_the_ring_check_has_teeth | PASS |  |
| 320 | split-app | R35 | No horizontal overflow at phone and desktop sizes | S1-360 | tests/browser/test_app.py :: test_R35_no_horizontal_overflow_and_the_layout_of_each_size[S1-360] | PASS |  |
| 321 | split-app | R35 | No horizontal overflow at phone and desktop sizes | S2-360 | tests/browser/test_app.py :: test_R35_no_horizontal_overflow_and_the_layout_of_each_size[S2-360] | PASS |  |
| 322 | split-app | R35 | No horizontal overflow at phone and desktop sizes | S3-360 | tests/browser/test_app.py :: test_R35_no_horizontal_overflow_and_the_layout_of_each_size[S3-360] | PASS |  |
| 323 | split-app | R35 | No horizontal overflow at phone and desktop sizes | S5-360 | tests/browser/test_app.py :: test_R35_no_horizontal_overflow_and_the_layout_of_each_size[S5-360] | PASS |  |
| 324 | split-app | R35 | No horizontal overflow at phone and desktop sizes | S1-390 | tests/browser/test_app.py :: test_R35_no_horizontal_overflow_and_the_layout_of_each_size[S1-390] | PASS |  |
| 325 | split-app | R35 | No horizontal overflow at phone and desktop sizes | S1-1280 | tests/browser/test_app.py :: test_R35_no_horizontal_overflow_and_the_layout_of_each_size[S1-1280] | PASS |  |
| 326 | split-app | R35 | No horizontal overflow at phone and desktop sizes | S3-1280 | tests/browser/test_app.py :: test_R35_no_horizontal_overflow_and_the_layout_of_each_size[S3-1280] | PASS |  |
| 327 | split-app | R35 | No horizontal overflow at phone and desktop sizes | M1-360 | tests/browser/test_app.py :: test_R35_no_horizontal_overflow_and_the_layout_of_each_size[M1-360] | PASS |  |
| 328 | split-app | R35 | Sizes the design gives at 360 x 780 |  | tests/browser/test_app.py :: test_R35_sizes_the_design_gives_at_360_by_780 | PASS |  |
| 329 | split-app | R35 | Content width at 1280 x 800 |  | tests/browser/test_app.py :: test_R35_content_width_of_the_header_and_the_note_at_1280_by_800 | PASS |  |
| 330 | split-app | R36 | Motion follows the user's setting | reduce | tests/browser/test_app.py :: test_R36_motion_follows_the_users_setting[reduce-0s] | PASS |  |
| 331 | split-app | R36 | Motion follows the user's setting | no-preference | tests/browser/test_app.py :: test_R36_motion_follows_the_users_setting[no-preference-0.12s, 0.12s] | PASS |  |
| 332 | split-app | R37 | Names are shown as text, never as markup |  | tests/browser/test_app.py :: test_R37_names_are_shown_as_text_and_never_as_markup + tests/browser/test_app.py :: test_R37_no_banned_api_in_the_shipped_files + tests/browser/test_app.py :: test_R37_the_banned_api_scan_has_teeth | PASS |  |
| 333 | split-app | R38 | The Content Security Policy is exact and never violated |  | tests/browser/test_app.py :: test_R38_policy_is_exact_and_nothing_inline | PASS | the console rule for the whole suite is enforced by the open_app fixture on every browser test |
| 334 | split-app | R38 | The strict policy blocks nothing the app needs | S3, cold boot | tests/browser/test_app.py :: test_R38_strict_policy_blocks_nothing_the_app_needs | PASS |  |
| 335 | split-app | R38 | The strict policy blocks nothing the app needs | S1 seed | driven_checks.py (driven), group 'D2 R38 strict policy, S1 seed', 6 checks | PASS | the suite test checks only the cold boot row |
| 336 | split-app | R38 | The strict policy blocks nothing the app needs | S2 seed with the New bill dialog open | driven_checks.py (driven), group 'D2 R38 strict policy, S2 seed with the dialog open', 7 checks | PASS | the suite test checks only the cold boot row |
| 337 | split-app | R39 | Nothing leaves the device |  | tests/browser/test_app.py :: test_R39_nothing_leaves_the_device_by_the_static_scan + tests/browser/test_app.py :: test_R39_the_network_scan_has_teeth + tests/browser/test_app.py :: test_R39_a_whole_session_makes_only_same_origin_gets | PASS |  |
| 338 | split-app | R39 | The SVG icons come from createElementNS |  | tests/browser/test_app.py :: test_R39_icons_come_from_createElementNS_and_the_page_holds_its_icons | PASS |  |
| 339 | split-app | R40 | Looks right |  | run_gates.py (driven), tests/browser/fidelity/run.py, 10 pairs, pixel gate | UNTESTED | The pixel half passed: the fidelity gate ran through its own code (run_gates.py, the unchanged tests/browser/fidelity/run.py with its evidence folder moved into this folder) and all 10 pairs match with 0 mismatching pixels. The other half, every FE element checklist row passes, needs a per-element review of styles.json, the fidelity finder's step, which this regression did not run. Not counted as a pass. |
| 340 | split-app | R40 | The runner uses the Python that runs pytest |  | tests/browser/test_app.py :: test_R40_the_runner_uses_the_python_that_runs_pytest | PASS |  |
| 341 | split-app | R41 | Works right |  | run_gates.py (driven), tests/browser/live_e2e.py, 7 steps | PASS | the cold-boot live gate passed all 7 steps; its artifacts are in gates/live-e2e |

## 3. Driven checks

These cover the parts of scenarios that no passing suite test covers exactly, and the two gates that the suite does not run.
Each was driven on the real page (headless Chromium, real clicks and keys), or by the gate's own code.

| Check | Script and output | Covers | Checks | Result | What was seen |
|-------|-------------------|--------|--------|--------|---------------|
| D1 | driven_checks.py, driven-checks.json | R5, renaming on each keystroke, S1 seed | 19 | PASS | Typing " Wei" after Chen. On each key all four toggles, the shares row and the remove button read the trimmed label. Line 5 of the copied text is "Chen Wei RM 24.48". |
| D2 (S1) | driven_checks.py, driven-checks.json | R38, strict policy, S1 seed | 6 | PASS | Body background rgb(238, 240, 238). Three people rows and two Charges inputs. The S1 table and check row. No style attribute under body. No CSP message and no page error. |
| D2 (S2) | driven_checks.py, driven-checks.json | R38, strict policy, S2 seed with the dialog open | 7 | PASS | Dialog open, the same background, the S2 table and check row under it, no style attribute, no CSP message, no page error. |
| D3 | driven_checks.py, driven-checks.json | R23, blocked clipboard keeps the bill, S2 seed | 8 | PASS | Status "Could not copy. Your browser blocked the clipboard." with class "status status-failure". The draft text, the form state, the shares rows, the check row and the panel (less the status line) are unchanged. |
| D4 | driven_r34.py, driven-r34.json | R34, focus rows b to f, S1 seed | 15 (3 per row) | PASS | Focus lands on Person 2 name (Chen), Person 2 name (Ben), Item 5 name (empty), Item 2 name (Mee goreng mamak) and Item 3 name (Mee goreng mamak). |
| G1 (R40) | run_gates.py, gates/fidelity/20261010-130500 | R40, Looks right, pixel half | 10 pairs | 10 of 10 PASS | Every pair has dimensions_match true and 0 mismatching pixels (bill-empty, bill-even, bill-items, bill-unassigned and new-bill-dialog at 390 x 844 and 1280 x 800). The per-element checklist half was not judged here. |
| G2 (R41) | run_gates.py, gates/live-e2e/20261010-130537 | R41, Works right, cold-boot live gate | 7 steps | PASS | Steps 1 to 7 pass: cold boot, even split, copy, by item and copy, come back, start over and reload, and step 7, which covers zero console errors, zero page errors, no Content Security Policy violation, and same-origin GETs only. |

The gates ran through their own code with their evidence folder moved into this folder, so the normal evidence folders under docs/modules/split-app/qa/ were not written. The verdicts are the gates' own verdict files.

## 4. Five hand-driven flows at 390 x 844

Served by `python -m http.server` on a free loopback port from the project root. Each flow runs in one browser context with empty storage (no seed), the suite's clipboard recorder, and only real clicks, typed keys and key presses. The final run is flows.json. The earlier attempts are kept beside it, as observation 1 explains.

| Flow | Checks | Result | What was seen |
|------|--------|--------|---------------|
| 1 even split | 13 | PASS | Aisyah, Ben and Chen typed by hand, Subtotal 100.00. Aisyah RM 38.87, Ben RM 38.87, Chen RM 38.86, "Adds up to" RM 116.60. Default charges 10 and 6. Summary Service RM 10.00 (10% of RM 100.00) and SST RM 6.60 (6% of RM 110.00). Copy summary gives the status "Summary copied", the recorder holds the S2 block exactly, with one write. Screenshot flow1-even-split-end.png. |
| 2 by item | 12 | PASS | Four items typed with prices and taps, and who had each as expected. Shares Aisyah RM 29.04, Ben RM 15.74 and Chen RM 24.48. The three add up to the Total RM 69.26 (6926 sen). The items column adds up to RM 59.40 and the charges column to RM 9.86. Screenshot flow2-by-item-end.png. |
| 3 a wrong price | 18 | PASS | "abc" typed in a price gives no error while typing, and the panel says "Give every item a price". Tab shows the error "Enter an amount like 12.50" with aria-invalid true, and the panel still waits. Fixed to 10.00, the error goes, focus stays, the bill summary shows (RM 10.00, 1.00, 0.66, total 11.66) and the panel asks for a person. Tapping Aisyah gives Aisyah RM 10.00, RM 1.66, RM 11.66. Screenshots flow3-error-shown.png and flow3-wrong-price-end.png. |
| 4 come back | 15 | PASS | Reload leaves the form, the stored draft and the shares as they were. New bill opens a modal dialog with Cancel focused. Cancel closes it, keeps the bill and the stored draft, and returns focus to New bill. Start new bill gives people Person 1 and Person 2, an empty subtotal, Even, charges 10 and 6, the even message, and the stored draft is the new bill. Screenshots flow4-reloaded.png and flow4-come-back-end.png. |
| 5 double presses | 23 | PASS | A: a double click on Add person from a cold boot adds exactly one person (3 rows, nextId 4, focus on Person 3 name). B: with eight people and the four S1 items, "abc" typed in item 1's price and left, a double click on the item 2 chip that lies under its own Remove (the first of 24 points, at 329.5, 733). The items stay at four with the same ids. The first click toggled one chip (Farid on), and the repeat press removed nothing. Screenshots flow5a-double-add-person.png and flow5b-double-click-chip-end.png. |

Flow 5 part B is the RG-CR-08 fix. It was probed at scrollY 0 on the 390 x 844 page, with the points measured in the same state the press was made in. probe-chips.json and probe-scout.json are the diagnostic runs that show why the bill has four items.

## 5. Observations

1. Flow attempts. Three earlier flow runs are kept beside flows.json. Attempt 1 (flows-attempt-1.json) failed on two defects in my script. One expectation ignored that R18 keeps the bill summary on screen while an item has no person, and one check had no "what" argument. Attempt 2 (flows-attempt-2-one-item.json) used a one-item bill, which has no item 2 whose Remove lies under its chips after an error, so part B found no point. Attempt 3 (flows-attempt-3-stale-scroll.json) measured the chips before a click had scrolled the page, so the points were stale. Each was fixed in the script. The app was not changed in any attempt.
2. The node summary parser in run_suites.py failed after the node suite had finished. The saved node output (node-test.txt) is the record and was used. The node suite was not run a second time.
3. The table heads read "+Charges" and "=Share" as text. The golden bill-items.html has the same markup, with the plus sign in a span marked aria-hidden and no space after it, so the app matches the golden. qa.md writes "+ Charges" as notation. Not a finding.
4. With an item priced and nobody tapped, the bill summary stays on screen with its totals, and the Shares section gives the "1 item still needs a person" message. R18 says exactly this, so it is expected.
5. The RG-CR-08 probe finds points only for item 2's Remove (the first at 329.5, 733). The double press there removed nothing, and the one chip it touched toggled once (Farid went on). That is one real click followed by a cancelled repeat press, which is the intended behaviour.
6. The fidelity harness renders with its own CSP bypass, as qa.md says. So the 10 pixel passes say nothing about the policy. The functional suite and the live gate keep the policy live and cover it.
7. The gate evidence for this run is under gates/ in this folder. The normal gate folders under docs/modules/split-app/qa/ (fidelity and live-e2e) were not written by this run. Earlier runs from today are still there, for example qa/fidelity/20261010-123651. If the orchestrator needs the gates in their normal place, they should be run there.
8. Two node test files, draft.test.js and errors.test.js, are not in the split-core qa.md file list. Their titles carry R10, R26, R27 and R28, and all of them pass, so they are extra coverage.
9. Several split-app rows are covered by a test that builds the S1 bill by gestures, where qa.md names the S1 seed. The seeded and the gesture-built bills show the same screen, since both match bill-items.html in the R3 walks, so these rows count as covered. The rows where a suite test did not check the seed's exact state were driven (D1, D2 and D4).
10. Nothing in the run wrote into qa/functional. SPLIT_EVIDENCE was unset for every suite run, and the suite wrote no failure screenshot.
11. The copy text checked by the suite and by flow 1 matches the S2 and S1 blocks in split-core spec R24.
12. The R2 never-throws test draws its characters from a seeded alphabet that has one space where qa.md lists two, before the fullwidth digit. The space is already in the alphabet, so the Then is still exercised over 500 strings. The row is PASS with this note. A reader who wants the exact alphabet should add the second space to the test, which this run did not change.

## 6. Evidence

Folder: docs/modules/split-app/qa/regression-qa/20261010T124914/. The index is evidence.md.
Files in the folder when this report was built: build_findings.py, driven-checks-run.txt, driven-checks.json, driven-r34-run.txt, driven-r34.json, driven_checks.py, driven_r34.py, flows-attempt-1-run.txt, flows-attempt-1.json, flows-attempt-2-one-item-run.txt, flows-attempt-2-one-item.json, flows-attempt-3-stale-scroll-run.txt, flows-attempt-3-stale-scroll.json, flows-run.txt, flows.json, flows.py, gates-run.txt, gates-summary.json, harness_common.py, junit.xml, node-test.txt, probe-chips-after-error.png, probe-chips-run.txt, probe-chips.json, probe-scout-run.txt, probe-scout.json, probe_chips.py, probe_scout.py, pytest-collect.txt, pytest.txt, run_browser.py, run_gates.py, run_suites.py, scenario-table.json, scenario-table.md, suites-summary.json.
Screenshots: flows/ (8 files), driven/ (5 files) and probe-chips-after-error.png.
Gate outputs: gates/fidelity/20261010-130500/ (10 pair folders and run.log) and gates/live-e2e/20261010-130537/ (steps.log, summary.json, 7 screenshots, console.log, network.log and the clipboard files).

## 7. Processes

Every server and browser this run started. Each server printed STOPPED with its port free afterwards.

| Started by | Process | Pid | Port | Stopped |
|------------|---------|-----|------|---------|
| run_browser.py (pytest suite) | python -m http.server (fixture) | 13352 | 54748 | yes, port free |
| run_browser.py (pytest suite) | Chromium, opened and closed by the pytest session | not recorded by the suite | none | closed at session end |
| run_suites.py | node --test, no server or browser | none | none | n/a |
| driven_checks.py | python -m http.server | 21144 | 48732 | yes, port free |
| driven_checks.py | Chromium 149.0.7827.55 | 15616 | none | closed, none left |
| flows.py attempt 1 | python -m http.server | 16640 | 36765 | yes, port free |
| flows.py attempt 1 | Chromium | 8836 | none | closed, none left |
| flows.py attempt 2 | python -m http.server | 11912 | 63751 | yes, port free |
| flows.py attempt 2 | Chromium | 24396 | none | closed, none left |
| flows.py attempt 3 | python -m http.server | 13368 | 1899 | yes, port free |
| flows.py attempt 3 | Chromium | 4516 | none | closed, none left |
| flows.py final | python -m http.server | 23236 | 47616 | yes, port free |
| flows.py final | Chromium | 10796 | none | closed, none left |
| probe_chips.py | python -m http.server and Chromium | 4036 | 13458 | yes, port free, Chromium closed |
| probe_scout.py | python -m http.server and Chromium | 7112 | 4119 | yes, port free, Chromium closed |
| driven_r34.py | python -m http.server | 7644 | 18118 | yes, port free |
| driven_r34.py | Chromium 149.0.7827.55 | 480 | none | closed, none left |
| run_gates.py, fidelity gate | python -m http.server (run.py's StaticServer) | 2880 | 38267 | yes, port free |
| run_gates.py, fidelity gate | fidelity.py harness, one Chromium per pair (10 runs) | per run, not recorded | none | each run closed its browser |
| run_gates.py, live gate | python -m http.server | 17268 | 14669 | yes, port free |
| run_gates.py, live gate | Chromium | not recorded | none | closed by the gate |

Final check, run after the last script: a query for Playwright Chromium processes returned an empty list, so none was left running.
