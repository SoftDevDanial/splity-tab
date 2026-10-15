---
module: split-core
kind: security
status: pass
counts: { critical: 0, high: 0, medium: 0, low: 0, info: 1 }
date: 2026-10-15
head: 21a7bd2
scope: "v1.1.0 step 5. git diff v1.0.0..HEAD -- src/core (spare.js new, the spare divisions and result.spare in result.js, spare in bill.js, formatAmount and the thousands comma in money.js) against spec.md v1.1.0 (R24, R25, R27 to R34, Contracts, Threat model and its residuals), run in Node and through the app in Chromium and WebKit"
evidence: docs/modules/split-core/qa/security/20261015-222146/
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
