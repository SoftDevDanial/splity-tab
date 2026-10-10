# UAT pre-run: Split 1.0.0, sitting 1 of 1

**Tester:** sdlc-uat-tester (sonnet), 2026-10-10 14:53 to about 15:01, on the orchestrator's server
`http://127.0.0.1:8732/` (pid 9084). **Written by:** the orchestrator, from the tester's hand-back report. The tester
writes evidence only and never edits the script.

A tester PASS means the script can be run. It is not the proof that the feature works. That is the owner's verdict.

## Verdicts
All eight cases PASS at 1280 x 800, and again at 390 x 844. 235 of 235 checks in each (`results.json`, `results-390.json`).

| case | verdict | evidence |
|---|---|---|
| UAT-01 People | PASS | Both × disabled at the start and a click on them changed nothing. After Add person the cursor sat in the empty "Person 3 name" box with its placeholder, and `Chen` landed there. "Remove Person 4" removed the fourth box, leaving Aisyah, Ben and Chen with every × enabled |
| UAT-02 Even split | PASS | RM 100.00, RM 10.00 "10% of RM 100.00", RM 6.60 "6% of RM 110.00", RM 116.60. Shares 38.87, 38.87, 38.86 |
| UAT-03 Adds up | PASS | "Adds up to RM 116.60" with the tick. At 10.05: RM 1.01, RM 0.66 ("6% of RM 11.06"), RM 11.72, shares 3.91, 3.91, 3.90 |
| UAT-04 Charges | PASS | Hint exact. At 0: RM 0.00, RM 6.00, RM 106.00, shares 35.34, 35.33, 35.33. At 31 then Tab: "Enter a rate from 0 to 30", no Bill summary, "Check the charges to see the shares." Back to RM 116.60 at 10 |
| UAT-05 Copy summary | PASS, paste step not driven | "Summary copied". One write to the clipboard stand-in, equal byte for byte to the six lines. The real clipboard is never touched (CG-7) |
| UAT-06 By item | PASS | Step 4 message exact. Bill summary 59.40, 5.94, 3.92 (6% of 65.34), 69.26. Table and check row as scripted. Fits at 360 to 390 px |
| UAT-07 Draft kept | PASS | A new page in the same browser context showed By item with the same four items, taps and shares. After Even: 100.00 and 38.87, 38.87, 38.86 |
| UAT-08 New bill | PASS | Question and both buttons as written. Cancel and a click at the top-left corner both closed it with the saved draft byte-identical. Start new bill gave the starting state, By item showed no items and "Add an item to see the shares." |

**Instrument error, declared by the tester.** Its first desktop run marked UAT-06 FAIL because the text of the table
heads read "+Charges" and "=Share" (the gap is a CSS margin). The screen shows "+ Charges" and "= Share". It fixed its
check and re-ran from a fresh context. `results.json` is the re-run. The first run's output was not kept.

## Script notes (all applied by the orchestrator before handover, no step changed its action)
1. UAT-06 said the satay is split RM 9.00 each, which no screen prints. Now checked from the Items column.
2. UAT-07 could fail for the wrong reason in a private window, on `localhost` in place of `127.0.0.1`, or when the
   only tab is closed. Now said in the starting state and the preconditions.
3. UAT-01's new-box hint is faint and could read as a name. Reworded.
4. UAT-06's column heads and the names column with no head. Reworded.
5. The starting state now says 10% and 6%, as the boxes read.
6. UAT-04 step 4 now says Tab moves on to the SST box and selects its 6.
7. UAT-05 now says some paste targets add their own empty last line.
8. UAT-08 step 5 now says where to click outside the box.
9. UAT-01 step 3 now says Add person moves along as people are added.

## Processes
Three short runs, each with one headless Chromium closed in a finally block (the 1280 run twice, the 390 run once),
plus read-only process queries. A process listing afterwards found no Chromium, Playwright driver or driver.py of its
own. It started, stopped and configured no server, and left pid 9084 untouched. The OS clipboard was never touched.
