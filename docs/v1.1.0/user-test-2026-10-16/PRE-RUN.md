---
version: 1.1.0
kind: uat-pre-run
sitting: 1 and 2 of 2
ran_against: running-app @ http://127.0.0.1:8742/
run: pre-run/20261016-060541
counts: { pass: 9, fail: 1, blocked_product: 0, blocked_script: 1, blocked_seat: 4 }
---
# UAT pre-run, sittings 1 and 2

Written by the automated UAT pre-run agent on 2026-10-16. A green row here proves the script can be run in this seat. It is not proof that the feature works. The owner's verdict is the one that counts, and his column in `TEST-CASES.md` was not touched.

## How it ran

- Sitting 1 in headless Chromium 149 at 1280 x 800, one fresh context, dark colour scheme, motion allowed, real localStorage and the real clock. UAT-04 set the same context to 360 x 780 in place of Chrome's device toolbar (no toolbar touch mode, scale 1) and set it back to 1280 x 800 at its step 14.
- Sitting 2 in headless WebKit 26.5 with Playwright's iPhone 13 context (390 x 664, scale 3, touch, mobile) with taps on the touchscreen, then the whole sitting again in a fresh context at 390 x 844. WebKit on Windows is Safari's engine, not an iPhone.
- Every press was a real click, tap or key, and every point was hit-tested first, so the element under the point was the named control. Taps on separate steps were kept at least 0.8 s apart, a person's pace, because the app ignores a tap less than 0.5 s after the last one in the same place.
- A stand-in for `navigator.clipboard` recorded writes in every context. The system clipboard was never touched.
- The app was not started, stopped or changed. Each case log lists every gesture with its point, every stand-in and every scroll.
- Line counts below are the run's own records. UAT-01 also checks the six facts of the starting state.

## Results

Evidence paths are relative to `pre-run/20261016-060541/`. Sitting 2 has one folder per height, `h664` and `h844`.

| case | title | tester verdict | observed | lines not matching | evidence |
|------|-------|----------------|----------|--------------------|----------|
| UAT-01 | Choose who takes the spare sen, on an even bill | PASS | 79 of 79 lines match, every figure as listed. The copied summary, read from the clipboard stand-in's one write instead of Notepad, was the six lines exactly. Draws, RM 38.86 went to Chen at step 9, Ben at step 10, Ben again after the reload at step 12, Aisyah at step 13. A headless browser does not act on F5, so step 12 used the browser's own reload. | none | UAT-01/log.txt, UAT-01/s02.png, UAT-01/s09.png, UAT-01/s12.png, UAT-01/s15.png |
| UAT-02 | The new look, on the bill with items | BLOCKED (script) | 33 of 35 lines match and every figure is exact. The "Before you start" leaves the item list scrolled to its end (scrollTop 200 of 200), so at step 2 Nasi lemak ayam is above the frame's top edge, and at step 3 the wheel down moves nothing. With the list wheeled back to its top, Aisyah under Nasi lemak ayam shows a check and an indigo edge, and a wheel down then moves only the list (0 to 200) while the page and the card stay still. | step 2 line 5, Aisyah under Nasi lemak ayam is out of view in the item frame. Step 3 line 1, the list was already at its end and nothing moved | UAT-02/log.txt, UAT-02/s02.png, UAT-02/s03.png, UAT-02/s03-extra-up.png |
| UAT-03 | By item, only people on an item can take the spare sen | PASS | 61 of 61 lines match. Dan had no pill until he shared Char kuey teow. Step 7 needed the item list scrolled up 120 px to reach Dan under Char kuey teow, as the case note says. | none | UAT-03/log.txt, UAT-03/s04.png, UAT-03/s05.png, UAT-03/s07.png, UAT-03/s11.png |
| UAT-04 | A big bill fits a 360 px phone, and a price that does not fit its field | PASS | 58 lines match, 2 not drivable (the developer tools). The strip read Total RM 1,193.87 and later RM 116,669.25 on one line, the Splits sheet showed every figure whole, the page stayed 360 px wide. Step 11 showed "99999.9" with the last digit cut (text 91 px in a 76 px field). Step 5 needed the item list scrolled 120 px to reach Aisyah under Item 5. | none | UAT-04/log.txt, UAT-04/s05.png, UAT-04/s06.png, UAT-04/s11-field.png, UAT-04/s12.png |
| UAT-05 | Holding Enter on an item's x removes that item and nothing else | PASS | 33 of 33 lines match. A held Enter (one press, then 33 repeats over 2 s) removed Teh tarik only and left a focus ring on Add item. A held Enter on New bill opened the dialog, it never closed while the key was held, and the ring sat on Cancel. | none | UAT-05/log.txt, UAT-05/s08-ring.png, UAT-05/s09.png, UAT-05/s12.png |
| UAT-06 | When the browser will not save, the app says so | PASS | 28 lines match, 4 not drivable (Chrome's settings page). With the storage stand-in the warning sat in the top bar between Splity Tab and New bill, with the amber triangle, the exact text and no close button, over a new bill. RM 58.30 and RM 29.15 each. With the block lifted, Teh tarik came back at RM 4.08 with 3.50 + 0.58. | none | UAT-06/log.txt, UAT-06/s04.png, UAT-06/s05.png, UAT-06/s07.png |
| UAT-07 | The name on the tab, and the logo in the header and on the tab | BLOCKED (seat) | Step 1's four lines match, the mark left of "Splity Tab", an indigo receipt outline with bars inside and a torn foot, no letter, the header without "Danial's". Steps 2 to 7 need the tab strip and Windows settings. The page title reads "Danial's Splity Tab". The two icon captures render the file `src/icon.svg` in dark (light indigo) and light (dark navy), the file and not the tab. | none, 9 not drivable | UAT-07/log.txt, UAT-07/s01-header-4x.png, UAT-07/icon-file-dark.png, UAT-07/icon-file-light.png |
| UAT-08 | Several bills, written up for later | PASS | 10 of 10 lines match. The note was read with a file reader in place of Notepad. Title, status and the five headings in order match. Only New bill sits in the top bar. | none | UAT-08/log.txt, UAT-08/s03.png |
| UAT-09 | Every screen on your iPhone, and the white ring after a tap | FAIL | 59 lines match at each height, 5 not drivable (keyboard and settings), every figure exact. At step 13 focus went to Splits but no ring was drawn (not focus-visible) at either height. At step 12 a ring was drawn round the "One person, Person 1" chip, which the script does not list. A probe shows the ring on Splits comes only when the sheet is closed straight after it opens, not after the Spare sen panel has been used as in this case. The rings at steps 10 and 14 were drawn, light indigo rgb(163, 170, 255) rather than white. | step 13 line 3, no ring round Splits | UAT-09/h664/log.txt, UAT-09/h664/s12.png, UAT-09/h664/s13-ring.png, UAT-09/h844/s13-ring.png, UAT-09/h664/s14-ring.png, UAT-09/ring-order-probe.txt |
| UAT-10 | On the phone, a double tap acts once | PASS (both heights) | 42 lines match, 8 not drivable (keyboard). Each double tap acted once, one Person 4, one removal with the cursor in Person 5, the sheet and the dialog stayed open, Cancel closed once with nothing behind it pressed, no copy. A slower second tap acted. The tap on the hint reached no mousedown or click, focus stayed in Service charge and no error showed, the WebKit result the case lists. Leaving the field (stand-in for Done, one Tab) showed "Enter a rate from 0 to 30" with a red edge. | none | UAT-10/h664/log.txt, UAT-10/h664/s05.png, UAT-10/h664/s07.png, UAT-10/h664/s15.png, UAT-10/h844/log.txt |
| UAT-11 | On the phone, the field you type in never hides under the strip | PASS (both heights) | 45 lines match, 10 not drivable (keyboard). Moving down the fields (stand-in for the keyboard's down arrow, Tab until the next text field) left every focused field in full above the strip, the lowest 12 px clear of it. Strip messages and sheet figures exact. Step 17 needed a scroll to reach Person 1 under Item 4. | none | UAT-11/h664/log.txt, UAT-11/h664/s10.png, UAT-11/h664/s18.png, UAT-11/h844/log.txt |
| UAT-12 | On the phone, a big bill never scrolls sideways | PASS (both heights) | 39 lines match, 7 not drivable. The strip read RM 1,193.87 and RM 116,669.25 on one line, every sheet figure whole and exact. The two swipe lines are not drivable (no touch drag), the page measured 390 px wide in a 390 px viewport with nothing past its edge. For the A2 note, Item 5's 99999.99 shows cut after leaving the field (text 92 px in a 76 px field). Step 5 needed a scroll to reach Person 1 under Item 5. | none | UAT-12/h664/log.txt, UAT-12/h664/s07.png, UAT-12/h664/s12-field.png, UAT-12/h664/s13.png, UAT-12/h844/log.txt |
| UAT-13 | VoiceOver on a price field, before and after its error | BLOCKED (seat) | Steps 1 to 4 match, 13.505, the red "Enter an amount like 12.50" with its circle, the red edge and the strip message. Steps 5 to 11 need VoiceOver. The markup behind them reads label "Item 1 price in RM", aria-invalid true, described by the error text, and Item 2 described by the same text while it is hidden. Plain taps put focus on Cancel and then back on New bill. At 390 x 664 Item 1's field was above the screen and needed a scroll. | none, 21 not drivable | UAT-13/h664/log.txt, UAT-13/h664/s04.png, UAT-13/h844/log.txt |
| UAT-14 | With Block All Cookies on, the app warns that nothing is saved, and the Private limit | BLOCKED (seat) | 14 lines match with the storage stand-in for steps 1 and 6. The warning row sat under the top bar with the triangle and the exact text, no close button, over a new bill, RM 58.30. With the block lifted the five items came back, Item 1 at 13.505 with its red error. Steps 8 to 15 need Private Browsing and the tab overview. | none, 16 not drivable | UAT-14/h664/log.txt, UAT-14/h664/s02.png, UAT-14/h664/s07.png, UAT-14/h844/log.txt |
| UAT-15 | The tab icon in Safari, in light and dark | BLOCKED (seat) | Every step needs Safari's tab overview or iOS settings. The page title reads "Danial's Splity Tab". | none, 7 not drivable | UAT-15/h664/log.txt, UAT-15/h664/app.png |

## Script defects

- **UAT-02, an expected result that is not observable** (step 2 line 5 and step 3 line 1). The "Before you start" ends with the item list scrolled to its end, because ticking Aisyah and Chen under Satay brings the list down. Add to the end of "Before you start" the sentence "Then point at the item list and scroll it back up to the top, so Nasi lemak ayam shows first." With that, step 2 line 5 is in view and step 3's wheel down moves the list.
- **UAT-09, an expected line that does not hold in this seat.** This is not one of the three kinds, so the case stays FAIL. Step 13 line 3 expects a ring round Splits. After the Spare sen panel round trip of steps 10 to 12 none is drawn, and step 12 draws one round the "One person, Person 1" chip instead (`UAT-09/ring-order-probe.txt`). Step 12 could add "A thin ring is drawn round the One person, Person 1 chip, see the note". Step 13 line 3 could read "Splits has focus. Note whether a ring is drawn round it". The case note and open item A1 name "Splits in step 13", which could become "the spare sen chip in step 12".

Not blocking, but each saves the owner a guess.

- **UAT-04 step 1.** At 360 x 780 Mee goreng mamak sits partly under the strip and Satay below the screen. Add "Scroll the page to see all four items."
- **UAT-04 step 5.** Item 5's buttons sit below the item list's edge after step 4. Write "Scroll the item list until Item 5's buttons show, then click Aisyah under Item 5."
- **UAT-11 step 17 and UAT-12 step 5.** Person 1 under Item 4, and later under Item 5, sat below the item list's edge at 390 x 664 and under the strip at 390 x 844. Add "Scroll until its buttons show" to both steps.
- **UAT-13 step 1.** At 390 x 664 Item 1's price field is above the screen after UAT-12. Write "Scroll up to Item 1 and tap its price field."
- **UAT-09 steps 10 and 14, the case note and A1.** The ring is light indigo, rgb(163, 170, 255), the app's focus colour. "White" may draw a cross. Write "a thin light ring".

## Product defects

None found. No drivable line pointed at the product. The one FAIL is a ring the design does not ask for and did not draw.

## Not drivable from the tester seat

- Chrome's device toolbar and developer tools (UAT-04 before you start and step 14). Stood in for by setting the viewport.
- Chrome's settings page (UAT-06 steps 1, 2, 3 and 6). Stood in for by a page whose every localStorage access throws, then lifted by loading the page without it.
- The tab hover card, the tab icon and Windows light and dark mode (UAT-07 steps 2 to 7).
- Notepad (UAT-01 step 7, read from the clipboard stand-in's record, and UAT-08 steps 1 and 2, read with a file reader). These lines count as checked.
- The iOS keyboard, its Done key and its arrows (every "keyboard opens", "keyboard closes" and "not under the keyboard" line in UAT-09 to UAT-14). Where a line depends on leaving the field, one Tab stood in for Done (UAT-10 step 15, UAT-12 steps 4 and 12, UAT-13 step 4). Tab until the next text field stood in for the down arrow (UAT-11, UAT-12 step 2).
- A touch swipe (UAT-12 steps 6 and 15), measured instead. Mobile WebKit has no wheel and the driver has no touch drag, so a scroll a person would make by swiping was stood in for by scrolling that control into view, logged in the case.
- VoiceOver (UAT-13 steps 5 to 11).
- iOS Settings, Block All Cookies (UAT-14 steps 1 and 6), stood in for as in UAT-06.
- Private Browsing and Safari's tab overview (UAT-14 steps 8 to 15, every step of UAT-15).

## Heights in sitting 2

- Every verdict is the same at 390 x 664 and 390 x 844.
- The Splits sheet fitted the screen at every open (535 to 553 px of content), so no sheet line needed a scroll at either height.
- UAT-11. The lowest focused price sat 12 px above the strip at both heights (bottom 544 with the strip at 556, and 724 with the strip at 736).
- UAT-11 step 17 and UAT-12 step 5. The button was below the item list's edge at 664 and under the strip at 844, so both heights need a scroll.
- UAT-13 step 1. Item 1's price field was above the screen at 664 only.

## Tester rows for TEST-CASES.md

The orchestrator asked that `TEST-CASES.md` is not edited in this run, so the tester rows are written here for it to copy in.

| case | Verdict | Note |
|---|---|---|
| UAT-01 | PASS | All lines match. Copy read from a clipboard stand-in, not Notepad. Draws Chen, Ben, Ben after reload, Aisyah. |
| UAT-02 | BLOCKED (script) | The list starts scrolled to its end, so step 2 line 5 is out of view and step 3 moves nothing. Fix in PRE-RUN.md. Every other line matches. |
| UAT-03 | PASS | All lines match. Step 7 needs the item list scrolled up, as the note says. |
| UAT-04 | PASS | Viewport 360 x 780 in place of the device toolbar. All drivable lines match. Steps 1 and 5 need a scroll. |
| UAT-05 | PASS | All lines match. |
| UAT-06 | PASS | Storage block stood in for Chrome's settings. All drivable lines match. |
| UAT-07 | BLOCKED (seat) | Step 1 matches. The tab and Windows settings are not drivable. |
| UAT-08 | PASS | Read with a file reader in place of Notepad. All lines match. |
| UAT-09 | FAIL | Step 13, no ring round Splits in WebKit at either height. A ring shows round the One person chip at step 12 instead. Everything else matches. |
| UAT-10 | PASS | Both heights. Keyboard lines not drivable. |
| UAT-11 | PASS | Both heights. Tab stood in for the down arrow. Step 17 needs a scroll. |
| UAT-12 | PASS | Both heights. Swipe lines not drivable, page measured 390 px wide. 99999.99 shows cut after leaving the field. |
| UAT-13 | BLOCKED (seat) | Steps 1 to 4 match. VoiceOver is not drivable. |
| UAT-14 | BLOCKED (seat) | Steps 2 to 7 match with a storage stand-in. Private Browsing is not drivable. |
| UAT-15 | BLOCKED (seat) | Nothing drivable. |

## PROCESSES

| what | PID | why | state at return | kill command |
|---|---|---|---|---|
| bash.exe with a Python prompt (python.exe) | bash 26088, python 20376 | started by mistake by a malformed command early in the run, looping on a console error | STOPPED (killed by PID at about 05:46) | none |
| driver runs (python.exe with Playwright, each launching one headless Chromium or WebKit) | not kept, foreground runs | the probes, the debug runs in scratch and the final runs (sitting 1, sitting 2 at 664 and at 844, the ring probe) | STOPPED, each under `timeout` (120 s to 560 s) and each closed its browser | none |
| Split server, `python -m http.server 8742` | 28416 | the orchestrator's | ALIVE, not touched | the orchestrator's |
| Streaks server, `python -m http.server 8741` | 11048 | the orchestrator's | ALIVE, not touched | the orchestrator's |

End sweep at 06:10 by name (python, chrome, headless, webkit, playwright, minibrowser, node, bash, sh, cmd), by command line (`split-uat`, `ms-playwright`, `playwright`, `sitting1`, `sitting2`, `probe`) and by listening ports 87xx. Only PIDs 28416 and 11048 and the sweep's own shell were found. Every wait in the run was bounded by `timeout` or a step count.
