---
module: split-core
kind: security
status: pass
counts: { critical: 0, high: 0, medium: 0, low: 0, info: 1 }
date: 2026-10-15
head: 21a7bd2
scope: "v1.1.0 step 5. git diff v1.0.0..HEAD -- src/core (spare.js new, the spare divisions and result.spare in result.js, spare in bill.js, formatAmount and the thousands comma in money.js) against spec.md v1.1.0 (R24, R25, R27 to R34, Contracts, Threat model and its residuals), run in Node and through the app in Chromium and WebKit"
evidence: docs/modules/split-core/qa/security/20261015-222146/
latest: { run: "v1.1.0 regression --full", date: 2026-10-16, head: 64b882c, code: b0992b4, status: pass, counts: { critical: 0, high: 0, medium: 0, low: 0, info: 0 }, evidence: docs/modules/split-core/qa/security/20261016-032409/, section: "v1.1.0 regression --full, 2026-10-16" }
---
# Security audit: split-core (v1.1.0, step 5)

Role. Security finder (read-only on the product). HEAD `21a7bd2`, and `src/core/` is unchanged since `d58f4ce`. Node v24.11.1. The browser runs that pass through core are in the split-app evidence folder `docs/modules/split-app/qa/security/20261015-222146/`.
The 1.0 verdict and its re-check are in git history (`git show 21a7bd2:docs/modules/split-core/findings/security.md`). SEC-01 to SEC-06 of 1.0 were closed there, and the runs below show the summary guard still holds.

## Verdict
**PASS. 0 CRITICAL, 0 HIGH, 0 MEDIUM, 0 LOW, 1 INFO.** Every required mitigation of the threat model holds when run. The spare sen code adds no way to lose or invent a sen, to pollute a prototype or to loop. The one INFO backs the code review's CR-S5-1 with a measurement. The charges split is exact today, so CR-S5-1 is a test gap and not a wrong share.

## INFO (not counted against the verdict)

### SEC-S5-5. The charges division is exact past 2^53 under every rule, measured against BigInt
- **Threat** row "Correct shares" (float drift, precision past 2^53). **Symbols** `floorParts` and `divide` in `src/core/result.js`, which take every floor part from `allocateByWeight` in `src/core/allocate.js` (BigInt).
- 40,000 seeded by-item bills (2 to 12 people, 1 to 50 items, prices up to 99,999.99, rates up to 30% and 20%). Under Top of the list the charges column equals `allocateByWeight(service + sst, items)` in 40,000 of 40,000, 950 of them with a product past 2^53. Under all three rules (120,000 results) the R22 sums hold, every value is a safe non-negative integer, and a person with no items has no charges. 0 failures.
- So today's code is exact. The code review's CR-S5-1 (a float floor in that division passes all 379 tests) stays a test gap, routed there, not repeated here.
- **Evidence** `c1_core.mjs`, `c1_core-results.json` (`precision`).

Related, filed once under split-app as SEC-S5-4. `setMode`, `addItem` and `toggleItemPerson` carry the input's `spare` object by reference, as they carry people and items. The choice actions build a new `spare` from known fields, as the threat row says. Only the app's decoder (`readSpare`, D13) keeps a hostile `spare` out, and it does (`c1_core-results.json`, `integrity`).

## Threat model, each required mitigation
| Row | Verdict | Evidence |
|---|---|---|
| Correct shares, float drift and precision past 2^53 | **HOLDS.** See SEC-S5-5. The Node suite, BigInt trap rows included, passes 379 of 379 | `c1_core-results.json`, `node-test.tap` |
| Correct shares, the rounding rule | **HOLDS.** R22 sums under all three rules over 120,000 results, 0 failures | `c1_core-results.json` |
| Availability, odd and long strings | **HOLDS.** A 4.5M-character `subtotalText` goes through `computeResult` in 8 ms in Node and boots in 423 ms in Chromium and 284 ms in WebKit. No core call threw for any of the 101 hostile drafts the decoder accepted or for the bills built from them | split-app `n1_decoder-results.json` (`coreMs`, `coreThrew` absent), split-app `b1b_hostile_boot-<engine>.json` |
| Clipboard text integrity (R24) | **HOLDS** through the app in both engines. Names with NUL, U+2028, RLO and RLI give a summary of 3 plus one line per person, a space for each control and bidi character, and the real proof line last, copied from the card, the sheet and the strip, after At random and Pick again. In Node every accepted hostile draft's summary has no control, separator or bidi character and the right line count | split-app `b2_injection-<engine>.json`, `n1_decoder-results.json` |
| Object integrity (spare included) | **HOLDS.** Bills parsed from JSON with own `__proto__`, `constructor` and extra keys at every level, through `chooseSpareRule`, `chooseSparePerson`, `pickAgain`, `addPerson`, `removePerson`, `setMode`, `addItem` and `toggleItemPerson`, return bills with exactly the eight known keys on `Object.prototype`, and the choice actions return a `spare` with only `rule` and the field its rule needs. `Object.prototype` is unchanged. The by-reference `spare` of the non-choice actions is SEC-S5-4 of split-app | `c1_core-results.json` (`integrity`, `pollution`) |
| Correct shares under every spare rule | **HOLDS.** Sums above, the decoder checks the stored choice (D13) before core sees it, 101 of 101 | `c1_core-results.json`, split-app `n1_decoder-results.json` |
| Availability, Pick again | **HOLDS.** On a bill where no order can change the rows, `pickAgain` draws 64 times, returns the same reference and takes 1 ms. On the largest by-item bill (12 people, 50 items) with a source that always returns 0 it ends after 11 draws in 2 ms | `c1_core-results.json` (`pickAgain_*`) |
| Purity, the random source | **HOLDS.** Core reads no random source of its own. The hygiene runtime trap in the Node suite covers `spare.js` (379 of 379 pass). In the running app every `Math.random` call (10 in Chromium, 16 in WebKit) comes from `drawOrder` calling the `random` argument that `src/main.js` passes to `chooseSpareRule` and `pickAgain` | `node-test.tap`, split-app `b3_csp_network_style_random-<engine>.json` (`random_calls`) |

Accepted residuals, unchanged and not re-filed. A name can read like summary text (the row of `Adds up to RM 0.00` + NUL starts with "Adds up to" in every copy). A name can print as nothing. `Math.random` is not a secure source (split-app residual).

## Not done
- No mutation run of the core tests. The code review's mutants are the record for test teeth (CR-S5-1).

## Processes
Two foreground Node runs (`c1_core.mjs`, then `node --test` writing `node-test.tap` through its own reporter), each exited. No server, browser or background process. The browser runs that touch core are accounted for in the split-app verdict.

PROCESSES: none (checked with the Win32_Process and netstat sweep of 22:40 recorded in the split-app verdict).

## v1.1.0 regression --full, 2026-10-16

Role. Security finder (read-only on the product), the security half of `sdlc:regression --full` and of the step 5 re-check (ledger S7 row 46). HEAD `64b882c`, code as `b0992b4`. Scope `798f17f..HEAD -- src/core`, `BILL_FIELDS` in `billWith` (`bill.js`) and `withSpare` (`spare.js`) from `9277412`, `NAME_CONTROLS` and `plainName` from `abfbe3e`, `summaryText` reading that one class, and the comment commit `b0992b4`. Node v24.11.1. The browser runs that pass through core are in the split-app section of this date (`docs/modules/split-app/qa/security/20261016-032409/`). This section is written with `sed -i` on this file (two insertions, the `latest` front matter line and this section, no existing line changed).

### Verdict
**PASS. 0 CRITICAL, 0 HIGH, 0 MEDIUM, 0 LOW, 0 new INFO.** Every required mitigation of the threat model holds when run on today's tree. The one class is one definition read by both of its users, it deletes and replaces exactly the 79 code points the spec lists, and the field-list copies copy no hostile key.

### Step 5 findings, standing
| Id | Standing | Evidence |
|---|---|---|
| SEC-S5-5 INFO, the charges division is exact past 2^53 | **STANDS, re-measured.** 40,000 seeded by-item bills, the charges column under Top equals `allocateByWeight` in 40,000 of 40,000 (950 with a product past 2^53), the R22 sums hold over all three rules with 0 failures. CR-S5-1's trap test is now in the suite (`042c359`) | `c1_core-results.json` (`precision`), `node-test.tap` |
| SEC-S5-4 of split-app (filed there), `spare` by reference | unchanged, see the split-app section | `c1_core-results.json` (`integrity`) |

### Threat model, each required mitigation (today's tree)
| Row | Verdict | Evidence |
|---|---|---|
| Correct shares, float drift and precision past 2^53 | **HOLDS.** See SEC-S5-5. The Node suite passes 406 of 406 | `c1_core-results.json`, `node-test.tap` |
| Correct shares, the rounding rule | **HOLDS.** R22 sums under all three rules over 120,000 results, 0 failures | `c1_core-results.json` |
| Availability, odd and long strings | **HOLDS.** `plainName` of 4.5M U+202E and an `x` takes 26 ms and returns `x`. It never threw on lone surrogates, the empty text or the 79. In the app, every hostile draft the decoder accepted went through core without a throw (split-app `n1_decoder-results.json` 101 of 101, `n2_decoder_h10-results.json` 173 of 173) | `c1_core-results.json` (`plainName`) |
| Clipboard text integrity (R24, with R35) | **HOLDS.** For every code point but the surrogates, `plainName("A" + c + "B")` is `AB` exactly for the 79 the spec lists (deleted 79, 0 wrong), and Ben's row of the S2 summary with that name reads `A B RM 38.87` exactly for those 79 and the name as given otherwise (0 wrong). The class is one `RegExp`, `NAME_CONTROLS` (`gu`), exported from `bill.js` and imported by `summary.js`, and the text scan finds `\p{Bidi_Control}` on one line under `src/`. In the app the copies hold no character of the class and equal the screen (split-app `b2_injection-head-settled-<engine>.json`) | `c1_core-results.json` (`plainName`), split-app `s1_static_scan.json` |
| Object integrity (spare included, `BILL_FIELDS`) | **HOLDS.** A bill parsed from JSON with own `__proto__`, `constructor` and `extra` at every level, through `chooseSpareRule`, `chooseSparePerson`, `pickAgain`, `addPerson`, `removePerson`, `setMode`, `addItem`, `toggleItemPerson`, `setPersonName` and `setItemName`. The 11 new bills hold exactly the eight known keys in `newBill` order on `Object.prototype`, none has an own `__proto__`, `constructor` or `extra`, the choice actions build a `spare` of known keys only, and `Object.prototype` is unchanged. `Object.keys(newBill())` is the known list. The by-reference `spare` of the other actions is split-app's SEC-S5-4 | `c1_core-results.json` (`integrity`, `bill_fields`, `pollution`) |
| Correct shares under every spare rule | **HOLDS.** Sums above, and the decoder checks the stored choice (D13) before core sees it (split-app `n1_decoder-results.json`) | `c1_core-results.json` |
| Availability, Pick again | **HOLDS.** On a bill where no order can change the rows, 64 draws, the same reference, 1 ms. With a source that always gives 0, 11 draws on 12 people and on the largest by-item bill | `c1_core-results.json` (`pickAgain_*`) |
| Purity, the random source | **HOLDS.** The runtime trap in the Node suite (406 of 406) covers `spare.js` and calls `plainName`. In the app all 18 `Math.random` calls per engine come from `drawOrder` | `node-test.tap`, split-app `b3_csp_network_style_random-<engine>.json` |

Residual 2 (a name can print as nothing) narrows in the app as the 2026-10-16 note says. A name of NEL alone, or of any class characters only, becomes "" and takes the position label (`personLabel` gives `Person 2` here, `Person 1` and `Person 6` in the app runs). U+200B and the like stay outside the class and the residual stands for them. Residual 1 is unchanged.

### New threats the delta brings, hunted
- The shared `g` flag on `NAME_CONTROLS`. With `lastIndex` set to 2 beforehand, `plainName` still gives `AB` and `summaryText` still replaces every class character, and `lastIndex` is 0 after each `replace`. `NAME_CONTROLS.test` on U+202E gives true and then false (the hazard of a shared `g` RegExp that code review CR-R3 raised and the owner's stop rule accepted). The text scan finds no `.test`, `.exec`, `.match`, `.search`, `.split`, `lastIndex` or `compile` use of it under `src/`, only the two `replace` calls. The `RegExp` is not frozen, so only code already running in the page could change it, which R37 and the CSP keep out. Nothing new to file.
- `BILL_FIELDS` and `Object.fromEntries`. The list is read once from `newBill()` at module load, holds only the eight fields, and `Object.fromEntries` defines own data properties, so even a key named `__proto__` would not reach a prototype. Measured above.
- `summary.js` now imports `bill.js`. No import cycle (`bill.js` imports neither `summary.js` nor `result.js`), reading only.

### Files of this run (listed on disk)
`docs/modules/split-core/qa/security/20261016-032409/` holds `c1_core.mjs` (the step 5 probe with its sections unchanged, plus (d) plainName and NAME_CONTROLS and (e) BILL_FIELDS, writing by a relative name), `c1_core-results.json` and `node-test.tap` (406 tests, 406 pass, 0 fail, written by Node's own `--test-reporter-destination`).

### Processes
Two foreground Node runs (`c1_core.mjs`, then `node --test` with a TAP and a dot reporter), each exited. No server, browser or background process for this module.
