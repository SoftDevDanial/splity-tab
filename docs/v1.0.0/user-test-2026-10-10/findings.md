# UAT findings: Split 1.0.0, sitting 1 (2026-10-10)

The owner's verdicts are 8 of 8 PASS. The tester agreed on every verdict. Each finding below is keyed by its case
and routed (the README's post-review routing: LITE for a script or wording fix, FULL for a new scope).

| id | case | what the owner said | routing | status |
|---|---|---|---|---|
| UAT-F1 | UAT-03 | "if it cannot be evenly split, the number in summary should show the extras then let the user decide to put to who or have a button or random split. So user can split manually or randomly or even have 1 person pay the extras" | FULL: a new 1.1.0 scope (brainstorm row, design, plan, build, finders) | Proposed for 1.1.0, waiting for his yes |
| UAT-F2 | UAT-06 | "You did not include what the service charge and sst. Be as accurate and precise as possible when doing test cases." | LITE: script rule | Taken for every later script |
| UAT-F3 | UAT-06 | "the charges for ben is 2.25 and aiyah is 4.13 when in test cases ben is 2.24 and aisyah is 4.14 ( check if this is a bug or a simple logic mistake)" | Investigated, below | Not reproduced, waiting for his answer |

## UAT-F2: script precision
The case listed Service charge RM 5.94 and SST RM 3.92 but not the line under each ("10% of RM 59.40", "6% of RM
65.34"). From now on every expected result lists every figure and every line the screen shows for that step.

## UAT-F3: Ben 2.25 and Aisyah 4.13
**What the rule says.** The brainstorm shares the charges (RM 9.86) in proportion to each person's items, rounds
each part down, and gives the cents left over one each to the people highest in the list. Worked by hand:
Aisyah 986 x 2490 / 5940 = 413.3, Ben 224.1, Chen 348.6. Rounded down that is 413 + 224 + 348 = 985, so one sen is
left, and it goes to the person at the top of the list.

**What the app shows.** The same steps, re-run in Chromium 149, Chrome 154 and Edge 154 (`evidence-uat-f3/`):
Aisyah RM 4.14, Ben RM 2.24, Chen RM 3.48, shares RM 29.04, RM 15.74, RM 24.48. That matches the script.

**Where 2.25 and 4.13 come from.** They appear exactly when Ben is above Aisyah in the people list, because the
leftover sen then goes to Ben. In that case the shares also change, to Ben RM 15.75 and Aisyah RM 29.03. On the
same row, a share is always the items plus the charges (`src/core/result.js`), so the screen cannot show the
script's shares beside those charges.

**Verdict.** No bug found. Either Ben was on top of the list in the owner's session, or the figures were misread.
The owner's screen was not captured, so the cause stays unconfirmed. This is also exactly the choice UAT-F1 asks
to hand to the user, so the 1.1.0 scope would make the leftover sen visible and let the user pick who takes it.

**Calibration note.** Tester and owner both said PASS, but the owner reported different figures. That disagreement
is recorded here and not resolved away.

## Owner comments on both apps (2026-10-10)
Recorded word for word in the CHANGE-LEDGER. Logo not seen in the apps, both designs too plain,
a better test-case layout with a design round run with him, and UAT material in the public showcase. Routing is
agreed with him in the conversation that follows.
