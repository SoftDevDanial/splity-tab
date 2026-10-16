# UAT findings, Split v1.1.0, user test 2026-10-16

Keyed by case id. Written by the orchestrator. Each finding is routed by the post-review rule (LITE or FULL) only after the owner decides. Nothing here is closed until the CHANGE LEDGER names it.

The pre-run found no product defect (ledger S7 row 56). Its one FAIL (UAT-09) and one BLOCKED (UAT-02) were script faults, repaired from the tester's own observations.

| id | case | found | what | routing |
|---|---|---|---|---|
| U1 | UAT-04 step 9 | 2026-10-16 18:17, the owner's cross on a PASS, then probe P-B of the Android run at 19:17 (`android-run/20261016-190750/probe-b/`) | The owner crossed "The price is selected". Ctrl+A does select the whole price in every variant measured (selectionStart 0, selectionEnd 6) and typing replaces it, as he ticked at steps 10 to 12. Under the device toolbar's mobile mode Chromium paints the selection Android-style, a dim teal block with the digits turning black (2.47 to 1), which on the dark field reads as the digits going dark, not as a highlight. The app sets no `::selection` style | ORCH. Script wording, no product defect. A `::selection` style for dark fields is a design note DEFERRED to v1.2.0's design pass (cosmetic, a real Android phone likely paints the same) |
| U2 | UAT-09 step 9 | 2026-10-16 19:17, the Android run (`android-run/20261016-190750/UAT-09/<seat>/glass-diff-*.png`) | The line "The page behind shows faintly through the sheet's glass" cannot be seen. The Splits sheet uses the design's dense glass, rgba(27, 33, 43, 0.92). Over two pages that differ by up to 222 of 255 levels, the sheet's pixels change by at most 1. The earlier WebKit pre-run passed the line on the CSS value alone, not on paint | ORCH. Script error, the app matches the design. The line is struck, the case's other checkable lines all match |

Owner verdicts on the cases are recorded in `TEST-CASES.md` and the sheet when he pastes them. A case he fails gets its row here with his words. His rulings on H-11 (UAT-09) and H-12 (UAT-04, UAT-12) go to the ledger's Needs the human.
