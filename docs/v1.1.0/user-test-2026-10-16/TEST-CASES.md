# UAT, Danial's Splity Tab 1.1.0

> **Sitting 1 of 2.** Cases derived **one per scope section** of `./docs/v1.1.0/CHANGE-LEDGER.md`. S1 has two cases,
> one on an even bill and one by item, because you ruled the By item side separately ("Yes, every spare sen") and one
> case would run past thirty steps. S6 and S8 share one case, the name and the logo, as the spec does. S5 has seven,
> UAT-09 to UAT-15, because its own ruling (S5 row 2) asks for cases you run on your own iPhone. Each walks another
> scope's claim again in Safari. Sitting 1 is UAT-01 to UAT-08 at your desk. Sitting 2 is UAT-09 to UAT-15 on your iPhone.
> Written from the requester's seat. *"I asked for X. Is X there, does it look right, can I use it?"*
>
> **This file is the record.** You work from `TEST-SHEET.html` beside it, which holds the same cases. Your marks,
> verdicts and notes come back through the sheet's "Results for the chat" and are written here word for word, with the date.

**App URL.** Sitting 1, `http://127.0.0.1:8742/` on this PC, started for you by the orchestrator. Sitting 2, the orchestrator gives you the address for your iPhone when you start this sitting.
**Starting state.** Nothing saved for this address in Chrome. The top bar shows the mark and "Splity Tab" at the left and **New bill** at the right. On the left a glass card reads "Total", a faint receipt mark and "Enter the subtotal to see the splits." On the right, People holds two fields, "Person 1" and "Person 2", each with a faint x, and **Add person** at its top right. Charges shows Service charge 10 % and SST 6 % with the hint "Set a charge to 0 if your bill already includes it." Split has Even chosen, and Subtotal is an empty field with a grey "0.00".
**Roughly how long.** 15 cases. Sitting 1 about 60 minutes, sitting 2 about 60 minutes.

**Before you begin.**
- Work the cases in order. Each one starts where the last one ended.
- Use Chrome for sitting 1, since UAT-06 uses Chrome's own settings. Keep the window maximised. The desktop layout needs at least 1024 px of width. It was designed at 1280 x 800, so on a shorter window the page itself may scroll a little, which is not a fault.
- UAT-04 checks a 360 px phone width. Chrome will not make a window narrower than about 500 px, so that case uses Chrome's device toolbar (F12, then Ctrl+Shift+M) and tells you each setting. Use only that toolbar, never the Console.
- Every money figure here was worked out from the app's rules, not read from the app. Service charge is a share of the subtotal, SST a share of subtotal plus service, each rounded half up to the sen, and each split is in whole sen with the spare sen given by the rule you chose. Where a design file or the review's captures hold the same bill, the figures agree.
- UAT-01 pastes the copied summary into Notepad. It is the only case that uses your clipboard. On the iPhone, Safari treats this PC's Wi-Fi address as not secure, so Copy summary cannot work there and no iPhone case presses it.
- Status. Every scope still reads OPEN in the ledger. SHIPPED is written at the seal, so OPEN here means built and reviewed, waiting for your verdict.
- Tester. The automated UAT pre-run agent runs every case before you. Its rows are empty until it has run. A green tester row proves the script can be run, not that the feature works.

## Verdict guide

| Verdict | What it means | Example from this version |
|---|---|---|
| **PASS** | Every line you checked matches the sheet, or a cross you marked does not matter to you. | **UAT-01, step 4.** The card read Aisyah RM 38.86, Ben RM 38.88 and Chen RM 38.86, exactly as listed. |
| **FAIL** | A line does not match and it matters. The line gets a cross and the note says what you saw. | **UAT-04, step 6.** Aisyah's RM 1,153.65 in the Splits sheet was cut at its right edge, where the sheet says every figure shows whole. |
| **BLOCKED** | You could not run it. The note says why. The control was not where the sheet said, the start could not be reached, or the result was not something you could see. | **UAT-06, step 2.** Chrome's page had no **Add** beside "Not allowed to save data on your device", so the address could not be blocked. |
| **NOTE** | Any verdict can carry a note. A note on a PASS becomes a finding for a later version. | **UAT-09.** "Pass, but I want no white ring after a tap" becomes your ruling on open item A1 (H-11). |

There are only three verdicts. The sheet itself shows two states that nobody chooses. **NOT RUN** means no
verdict yet, and the case comes back at the next sitting. **RETEST** means it failed, was fixed, and is
handed back, with the first verdict kept beside the new one.

**Line marks.** Every line under *You should see* gets a tick (it matches) or a cross (it does not). A case
can PASS with a cross when you decide the difference does not matter. The cross stays on record.

---

## Cases

### UAT-01

**Choose who takes the spare sen, on an even bill**

| | |
|---|---|
| **Scope** | S1 The user decides who takes the spare sen · OPEN, built · sitting 1 |
| **Problem** | At the 1.0 test you asked that when a bill cannot be split evenly, the summary shows the extras and lets you decide who pays them, "1 person pay the extras" or at random. 1.1.0 shows the spare sen on the receipt with a chip that opens the Spare sen choice. Top of the list is the 1.0 rule and stays the default. One person gives every spare sen to the person you pick. At random gives each spare sen to a different person, kept until you press Pick again. The copied summary follows the choice. The By item side is UAT-03. |
| **Before you start** | The starting state above. Click the **Person 1** field, press Ctrl+A and type `Aisyah`. Click the **Person 2** field, press Ctrl+A and type `Ben`. Click **Add person** and type `Chen`. Click the **Subtotal** field and type `100`. |

| # | Do this | You should see |
|---|---|---|
| 1 | Look at the receipt card on the left. | The Total reads RM 116.60<br>Subtotal RM 100.00<br>Service 10% RM 10.00<br>SST 6% RM 6.60<br>The heading "Splits"<br>Aisyah RM 38.87<br>Ben RM 38.87<br>Chen RM 38.86<br>Adds up to RM 116.60<br>"2 sen left over"<br>A chip "Top of the list" at the right of that line<br>**Copy summary** under it |
| 2 | Click the **Top of the list** chip. | A panel "Spare sen" opens just right of the card, its bottom level with the chip<br>A **Close** x sits at its top right<br>Under the title it reads "2 sen left over"<br>Three choices, "Top of the list", "One person", "At random"<br>Top of the list is chosen<br>The card stays in view, a little dimmed |
| 3 | Click **One person**. | One person is chosen<br>Under it three pills, "Aisyah", "Ben", "Chen"<br>Aisyah is ticked at once<br>On the card Aisyah reads RM 38.88<br>Ben reads RM 38.86<br>Chen reads RM 38.86<br>Adds up to reads RM 116.60<br>The chip reads "One person, Aisyah" |
| 4 | Click the **Ben** pill. | Ben is ticked and Aisyah is not<br>Aisyah reads RM 38.86<br>Ben reads RM 38.88<br>Chen reads RM 38.86<br>Adds up to reads RM 116.60<br>The chip reads "One person, Ben" |
| 5 | Click **Close**, the x at the top right of the panel. | The panel closes<br>The card still shows the splits of step 4 |
| 6 | Click **Copy summary** on the card. | "Summary copied" with a check shows under the button |
| 7 | Open Notepad and press **Ctrl+V**. | Six lines appear<br>"Bill split"<br>"Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)"<br>"Aisyah RM 38.86"<br>"Ben RM 38.88"<br>"Chen RM 38.86"<br>"Adds up to RM 116.60" |
| 8 | Go back to Chrome and click the **One person, Ben** chip. | The panel opens with One person chosen<br>Ben is ticked |
| 9 | Click **At random**. | At random is chosen<br>The pills are gone<br>A **Pick again** button sits under At random<br>Two of the three splits read RM 38.87 and one reads RM 38.86<br>Adds up to reads RM 116.60<br>The card's spare line shows two chips, "Pick again" and "At random"<br>"Summary copied" is gone from under Copy summary |
| 10 | Click **Pick again** in the panel. | A different person now reads RM 38.86<br>The other two read RM 38.87<br>Adds up to reads RM 116.60 |
| 11 | Press **Esc**. | The panel closes<br>The card shows the splits of step 10 |
| 12 | Press **F5**. | The page loads again<br>Aisyah, Ben and Chen are in People and the Subtotal reads 100<br>The card shows the same splits as in step 11<br>The spare line still shows "Pick again" and "At random" |
| 13 | Click **Pick again** on the card, left of the At random chip. | A different person now reads RM 38.86<br>The other two read RM 38.87<br>Adds up to reads RM 116.60 |
| 14 | Click the **At random** chip. | The panel opens with At random chosen and Pick again under it |
| 15 | Click **Top of the list**. | Top of the list is chosen<br>Pick again is gone from the panel<br>Aisyah reads RM 38.87<br>Ben reads RM 38.87<br>Chen reads RM 38.86<br>The chip reads "Top of the list" and Pick again is gone from the card |
| 16 | Press **Esc**. | The panel closes |
| **Note** | At random is a real draw, so who reads RM 38.86 in steps 9 to 13 cannot be listed. Write it down after each step. Pick again always changes it, and two spare sen always go to two different people. Close Notepad without saving after step 7. The choice is saved with the bill, which is why step 12 keeps the draw. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched in headless Chromium at 1280 x 800. The copied summary was read from a clipboard stand-in's one write in place of Notepad and was the six lines exactly. The draws went to Chen at step 9, Ben at step 10, Ben again after the reload at step 12 and Aisyah at step 13. A headless browser does not act on F5, so step 12 used the browser's own reload. Only you can check the paste into the real Notepad and the F5 key. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-02

**The new look, on the bill with items**

| | |
|---|---|
| **Scope** | S7 A livelier look, chosen from five directions · OPEN, built · sitting 1 |
| **Problem** | You said both designs were "so dull" and asked for five directions. You picked Night Console's colours on Glass Receipt's layout, with no glow, the items scrolling inside their own frame, People and Charges folding on a phone and "Splits" in place of "Shares". This case looks at the desktop. The phone layout shows in UAT-04 and UAT-09. |
| **Before you start** | UAT-01 done. Click **By item** in the Split row. Click **Add item**, type `Nasi lemak ayam`, press Tab, type `15.90` and click **Aisyah** under it. Click **Add item**, type `Char kuey teow`, press Tab, type `13.50` and click **Ben**. Click **Add item**, type `Mee goreng mamak`, press Tab, type `12.00` and click **Chen**. Click **Add item**, type `Satay, 10 sticks`, press Tab, type `18.00`, then click **Aisyah** and **Chen**. Scroll the item list when a row's buttons are below its edge. Then point at the item list and scroll it back up to the top, so Nasi lemak ayam shows first. |

| # | Do this | You should see |
|---|---|---|
| 1 | Look at the receipt card on the left. | The Total reads RM 69.26<br>Subtotal RM 59.40<br>Service 10% RM 5.94<br>SST 6% RM 3.92<br>"Splits", with "items + charges" at the right<br>Aisyah RM 29.04<br>Under it 24.90 + 4.14<br>Ben RM 15.74<br>Under it 13.50 + 2.24<br>Chen RM 24.48<br>Under it 21.00 + 3.48<br>Adds up to RM 69.26 in indigo, with a seal at its left<br>Under it 59.40 + 9.86<br>"1 sen left over"<br>The chip "Top of the list"<br>**Copy summary** is a solid indigo button |
| 2 | Look at the page as a whole. | The page is dark slate with no bright glow behind the card<br>The card is glass with a thin indigo line along its top edge<br>The card is at the left, and People, Charges, Split and Items run down the right<br>By item has an indigo edge and Even has none<br>Aisyah under Nasi lemak ayam has a check and an indigo edge |
| 3 | Point at the item list and scroll down with the mouse wheel. | Only the item list moves, inside its rounded frame<br>The card stays where it is<br>"Satay, 10 sticks" shows in full with Aisyah and Chen ticked |
| 4 | Under "Mee goreng mamak", click **Chen**. | Chen is no longer ticked<br>An amber bar shows at the left of Mee goreng mamak<br>The card still reads Total RM 69.26<br>Subtotal RM 59.40<br>Service 10% RM 5.94<br>SST 6% RM 3.92<br>Under them a warning circle and "1 item still needs a person. Tap who had it to see the splits."<br>No splits and no Copy summary show |
| 5 | Click **Chen** again. | Chen is ticked<br>The amber bar is gone<br>The card shows the splits of step 1 again |
| **Note** | On a very tall screen all four items may fit, then the list in step 3 does not move. Say so in your note. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | BLOCKED | Blocked by the script, not the app. Every line matched except step 2 line 5 and step 3 line 1, and every figure was exact. The Before you start left the item list scrolled to its end, so at step 2 Aisyah under Nasi lemak ayam was out of view and at step 3 the wheel down moved nothing. With the list wheeled back to the top, Aisyah showed a check and an indigo edge, and a wheel down then moved only the list while the page and the card stayed still. The script was repaired after the run with the tester's own words and seen working in its extra capture. It was not run again. Headless Chromium at 1280 x 800. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-03

**By item, only people on an item can take the spare sen**

| | |
|---|---|
| **Scope** | S1 The user decides who takes the spare sen, by item · OPEN, built · sitting 1 |
| **Problem** | For By item you ruled "Yes, every spare sen". One person takes every spare sen of the bill, and only people on at least one item can be chosen, so someone who had nothing never pays a sen of other people's food. Someone on no item is listed at RM 0.00. |
| **Before you start** | UAT-02 done. The card shows the splits of its step 1, with "1 sen left over" and Top of the list. |

| # | Do this | You should see |
|---|---|---|
| 1 | Click **Add person**, at the top right of People. | A fourth field shows "Person 4" in grey, with the cursor in it<br>Each item has a fourth button "Person 4", not ticked<br>The card lists "Person 4" with RM 0.00<br>Under it 0.00 + 0.00 |
| 2 | Type `Dan`. | The field reads Dan<br>The card row reads Dan RM 0.00<br>Each item's fourth button reads Dan<br>Aisyah still reads RM 29.04 |
| 3 | Click the **Top of the list** chip on the card. | The Spare sen panel opens<br>Under the title it reads "1 sen left over"<br>Top of the list is chosen |
| 4 | Click **One person**. | Three pills, "Aisyah", "Ben", "Chen"<br>There is no pill for Dan<br>Aisyah is ticked<br>The chip reads "One person, Aisyah" |
| 5 | Click the **Ben** pill. | Aisyah reads RM 29.03<br>Under it 24.90 + 4.13<br>Ben reads RM 15.75<br>Under it 13.50 + 2.25<br>Chen reads RM 24.48<br>Under it 21.00 + 3.48<br>Dan reads RM 0.00<br>Under it 0.00 + 0.00<br>Adds up to reads RM 69.26<br>Under it 59.40 + 9.86<br>The chip reads "One person, Ben" |
| 6 | Press **Esc**. | The panel closes |
| 7 | Under "Char kuey teow", click **Dan**. | Dan is ticked beside Ben<br>Aisyah reads RM 29.03<br>Under it 24.90 + 4.13<br>Ben reads RM 7.88<br>Under it 6.75 + 1.13<br>Chen reads RM 24.48<br>Under it 21.00 + 3.48<br>Dan reads RM 7.87<br>Under it 6.75 + 1.12<br>Adds up to reads RM 69.26<br>Under it 59.40 + 9.86 |
| 8 | Click the **One person, Ben** chip. | The panel opens with One person chosen<br>Four pills, "Aisyah", "Ben", "Chen", "Dan"<br>Ben is ticked |
| 9 | Click **Top of the list**. | The pills are gone<br>Aisyah reads RM 29.04<br>Under it 24.90 + 4.14<br>Ben reads RM 7.87<br>Under it 6.75 + 1.12<br>Chen reads RM 24.48<br>Under it 21.00 + 3.48<br>Dan reads RM 7.87<br>Under it 6.75 + 1.12<br>Adds up to reads RM 69.26<br>Under it 59.40 + 9.86<br>The chip reads "Top of the list" |
| 10 | Press **Esc**. | The panel closes |
| 11 | In Dan's field, click the **x** at its right. | Dan's field is gone<br>Dan is gone from every item and from the card<br>Aisyah reads RM 29.04<br>Ben reads RM 15.74<br>Under it 13.50 + 2.24<br>Chen reads RM 24.48<br>Adds up to reads RM 69.26 |
| **Note** | The item list may need a scroll up to bring Char kuey teow into view at step 7. Once Dan shares an item he may take the spare sen, as step 8 shows. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched in headless Chromium at 1280 x 800. Dan had no pill until he shared Char kuey teow. Step 7 needed the item list scrolled up 120 px to reach Dan under Char kuey teow, as the case note says. Nothing here was out of its reach. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-04

**A big bill fits a 360 px phone, and a price that does not fit its field**

| | |
|---|---|
| **Scope** | S2 The by-item table fits a 360 px phone (H-02) · OPEN, built · sitting 1 |
| **Problem** | In 1.0 the by-item table scrolled sideways on a small phone once the bill grew. You ruled "Fix the v1.0 limits". The splits now never scroll sideways, at any bill size. This case also holds open item A2 (H-12), which only your eyes can rule on. |
| **Before you start** | UAT-03 done. Press F12, then Ctrl+Shift+M. In the toolbar above the page set Dimensions to Responsive, type `360` in the width box and `780` in the height box. The pointer may show as a grey circle there, which is the toolbar's touch mode. Click as usual. |

| # | Do this | You should see |
|---|---|---|
| 1 | Look at the page in the 360 px frame. Scroll the page to see all four items. | The top bar shows the mark, "Splity Tab" and **New bill**<br>People is one folded row reading "Aisyah, Ben, Chen" with a caret<br>Charges is one folded row reading "Service 10%, SST 6%"<br>Split has By item chosen<br>Items shows **Add item** and the four items<br>The strip at the bottom reads "Total RM 69.26"<br>**Splits** and **Copy summary** sit in the strip<br>Nothing scrolls sideways |
| 2 | Click **Add item**. | A fifth row "Item 5" with an empty price, the cursor in its name<br>An amber bar at its left<br>The strip reads "Give every item a price to see the splits."<br>Copy summary in the strip is faint |
| 3 | Press **Tab**. | The cursor is in the Item 5 price field |
| 4 | Type `964.50`. | The price field shows 964.50 whole<br>The strip shows a warning circle and "1 item still needs a person. Tap who had it to see the splits." |
| 5 | Scroll the item list until Item 5's buttons show, then click **Aisyah** under Item 5. | Aisyah is ticked<br>The strip reads "Total RM 1,193.87" on one line<br>Copy summary in the strip is bright<br>Nothing scrolls sideways |
| 6 | Click **Splits** in the strip. | The Splits sheet rises over the dimmed page<br>Total RM 1,193.87<br>Subtotal RM 1,023.90<br>Service 10% RM 102.39<br>SST 6% RM 67.58<br>"Splits" with "items + charges"<br>Aisyah RM 1,153.65<br>Under it 989.40 + 164.25<br>Ben RM 15.74<br>Under it 13.50 + 2.24<br>Chen RM 24.48<br>Under it 21.00 + 3.48<br>Adds up to RM 1,193.87<br>Under it 1,023.90 + 169.97<br>"1 sen left over" with "Top of the list"<br>Every figure shows whole, none cut at its edge |
| 7 | Click **Close**, the x at the top right of the sheet. | The sheet closes |
| 8 | Click the **Item 5** price field. | The cursor is in it |
| 9 | Press **Ctrl+A**. | The price is selected |
| 10 | Type `99999.99`. | The field takes the new price |
| 11 | Press **Tab**. | The price field shows "99999.9", its last digit cut off<br>The strip reads "Total RM 116,669.25" on one line<br>Nothing scrolls sideways |
| 12 | Click **Splits**. | Total RM 116,669.25<br>Subtotal RM 100,059.39<br>Service 10% RM 10,005.94<br>SST 6% RM 6,603.92<br>Aisyah RM 116,629.03<br>Under it 100,024.89 + 16,604.14<br>Ben RM 15.74<br>Under it 13.50 + 2.24<br>Chen RM 24.48<br>Under it 21.00 + 3.48<br>Adds up to RM 116,669.25<br>Under it 100,059.39 + 16,609.86<br>"1 sen left over" with "Top of the list"<br>Every figure shows whole, none cut at its edge |
| 13 | Click **Close**. | The sheet closes |
| 14 | Press **Ctrl+Shift+M**, then **F12**. | The developer tools close<br>The desktop layout is back, with the card at the left |
| **Note** | **You are being asked to rule on this (open item A2, H-12).** Step 11 shows a price of 99999.99 as "99999.9" at 360 px until the field is focused. The splits and the strip show every figure whole, so no promise is broken, and the field's width is the approved design's. Option 1, keep it and add a line to the README's limits. Option 2, a design change in v1.2.0, a wider price field or a smaller font at 360 px. We recommend option 1, a five-figure price for one dish is rare. Write your choice in your note. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line it could drive matched in headless Chromium. It has no Chrome device toolbar or developer tools, so only you can check the toolbar settings in the Before you start and step 14. A 360 x 780 window stood in for the device toolbar and was set back to 1280 x 800 at step 14. The strip read Total RM 1,193.87 and later RM 116,669.25 on one line, the Splits sheet showed every figure whole and the page stayed 360 px wide. Step 11 showed 99999.9 with the last digit cut (text 91 px in a 76 px field), which is your ruling on A2. Steps 1 and 5 needed scrolls, now written into them. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-05

**Holding Enter on an item's x removes that item and nothing else**

| | |
|---|---|
| **Scope** | S3 Holding Enter on Remove adds no blank item (SEC-04) · OPEN, built · sitting 1 |
| **Problem** | In 1.0, holding Enter on the x of the last item removed it, and the key's repeats then pressed Add item, so a blank item appeared. You agreed to fix it. The repeats of a held key are now ignored after a press that changes the layout. Step 12 holds Enter on New bill, which the same guard covers. |
| **Before you start** | UAT-04 done, the desktop layout. |

| # | Do this | You should see |
|---|---|---|
| 1 | Click **New bill**, at the top right. | A dialog in the middle reads "Start a new bill?"<br>Under it "This clears the people, items and amounts."<br>A red **Start new bill** with **Cancel** at its right<br>The page behind is dimmed |
| 2 | Click **Start new bill**. | The dialog closes<br>People holds "Person 1" and "Person 2"<br>Split is back on Even with an empty Subtotal<br>The card reads "Total" and "Enter the subtotal to see the splits." |
| 3 | Click **By item**. | The Subtotal field is gone<br>Items shows **Add item** and no item rows<br>The card reads "Add each item and tap who had it to see the splits." |
| 4 | Click **Add item**. | A row "Item 1" with an empty price, the cursor in its name<br>An amber bar at its left<br>Buttons "Person 1" and "Person 2" under it, not ticked |
| 5 | Type `Teh tarik`. | The name reads Teh tarik |
| 6 | Press **Tab**. | The cursor is in Teh tarik's price field |
| 7 | Type `3.50`. | The card reads Total RM 4.08<br>Subtotal RM 3.50<br>Service 10% RM 0.35<br>SST 6% RM 0.23<br>A warning circle and "1 item still needs a person. Tap who had it to see the splits." |
| 8 | Press **Tab**. | A focus ring is round the x at the right of Teh tarik |
| 9 | Hold **Enter** down for about two seconds, then let go. | Teh tarik is gone<br>No item rows show, and no blank "Item 1" row appeared<br>A focus ring is on **Add item**<br>The card reads "Add each item and tap who had it to see the splits." |
| 10 | Click **New bill**. | The dialog opens |
| 11 | Click **Cancel**. | The dialog closes<br>Items still shows no rows |
| 12 | Hold **Enter** down for about two seconds, then let go. | The dialog opens and stays open<br>A focus ring is on Cancel |
| 13 | Press **Esc**. | The dialog closes<br>Split is still By item with no item rows |
| **Note** | After Cancel the app puts focus on New bill, which is why Enter in step 12 opens the dialog. Before the fix the held key would then have pressed the dialog's buttons too. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched in headless Chromium at 1280 x 800. A held Enter (one press, then 33 repeats over 2 s) removed Teh tarik only and left a focus ring on Add item. A held Enter on New bill opened the dialog, the dialog never closed while the key was held, and the ring sat on Cancel. Only you can check a held key on your own keyboard. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-06

**When the browser will not save, the app says so**

| | |
|---|---|
| **Scope** | S4 A bill that cannot be saved says so · OPEN, built · sitting 1 |
| **Problem** | In 1.0, when the browser blocked or filled its storage, the bill was lost with no message. Now a warning shows while saving fails, also from the first screen when the browser blocks storage outright, and it goes once saving works. Here you block storage for this address in Chrome. A private window and Safari's 7-day clean-up cannot show the warning, because the browser reports every save as working. That is a known limit in the README, and UAT-14 looks at it on your iPhone. |
| **Before you start** | UAT-05 done. Click **Add item**, type `Teh tarik`, press Tab, type `3.50` and click **Person 1** under it. The card reads Total RM 4.08 and Person 1 RM 4.08. |

| # | Do this | You should see |
|---|---|---|
| 1 | Open a new Chrome tab, type `chrome://settings/content/siteData` in the address bar and press **Enter**. | The settings page "On-device site data" opens |
| 2 | Under "Customized behaviors", click **Add** beside "Not allowed to save data on your device". | A small box "Add a site" opens with a "Site" field |
| 3 | Type `http://127.0.0.1:8742` and click **Add**. | "http://127.0.0.1:8742" is listed under "Not allowed to save data on your device" |
| 4 | Click the app's tab and press **F5**. | A note sits in the top bar between "Splity Tab" and New bill<br>It starts with an amber warning triangle<br>It reads "This bill is not being saved on this device. It will be lost when you close this tab."<br>It has no close button<br>People holds "Person 1" and "Person 2"<br>Split is on Even with an empty Subtotal<br>The card reads "Enter the subtotal to see the splits." |
| 5 | Click the **Subtotal** field and type `50`. | The Total reads RM 58.30<br>Subtotal RM 50.00<br>Service 10% RM 5.00<br>SST 6% RM 3.30<br>Person 1 RM 29.15<br>Person 2 RM 29.15<br>Adds up to RM 58.30<br>The warning is still there |
| 6 | Go back to the settings tab, click the three dots beside "http://127.0.0.1:8742" and click **Remove**. | "http://127.0.0.1:8742" is no longer listed |
| 7 | Click the app's tab and press **F5**. | No warning shows<br>Split is on By item<br>Teh tarik at 3.50 with Person 1 ticked<br>The Total reads RM 4.08<br>Subtotal RM 3.50<br>Service 10% RM 0.35<br>SST 6% RM 0.23<br>Person 1 RM 4.08<br>Under it 3.50 + 0.58<br>Person 2 RM 0.00<br>Under it 0.00 + 0.00<br>Adds up to RM 4.08<br>Under it 3.50 + 0.58 |
| **Note** | Reload at step 7 before you change anything. Once the block is gone, a change in the page that was still open saves that page's bill over the one saved before. If Teh tarik does not come back at step 7, Chrome dropped the saved data when you blocked it. Mark that line with a cross and say so in your note. Chrome may spell "Customized behaviors" the British way. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line it could drive matched. It cannot open Chrome's settings page, so only you can check steps 1, 2, 3 and 6. A storage stand-in, a page whose every localStorage access throws, took the place of the block. The warning sat in the top bar between Splity Tab and New bill, with the amber triangle, the exact text and no close button, over a new bill at RM 58.30 and RM 29.15 each. With the block lifted, Teh tarik came back at RM 4.08 with 3.50 + 0.58. It could not see whether Chrome keeps the saved bill during a block. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-07

**The name on the tab, and the logo in the header and on the tab**

| | |
|---|---|
| **Scope** | S6 The logo in the app, with S8 A name that is free to use · OPEN, built · sitting 1 |
| **Problem** | At the 1.0 seal you asked "Wheres the logo. I dont see it being used for both". The mark you approved, the receipt with a torn foot, now shows in the header and as the tab icon, light indigo on a dark tab and dark navy on a light one. "SplitIO" was taken, and you ruled "Danial's Splity Tab", with no Danial and no D in the logo. The full name is the page title and the header shows Splity Tab. The README header still shows 1.0 until the seal, see open item A6. A home-screen icon is not built in 1.1.0. |
| **Before you start** | UAT-06 done, Chrome on the app's tab. Windows is in dark mode (Settings, Personalization, Colors, Choose your mode, Dark). Chrome follows Windows, which is its default. |

| # | Do this | You should see |
|---|---|---|
| 1 | Look at the header. | A mark sits left of "Splity Tab"<br>It is an indigo receipt outline with two bars inside and a torn bottom edge<br>It holds no letter and no D<br>The header reads "Splity Tab", without "Danial's" |
| 2 | Point at the app's tab and wait a moment. | A card under the tab shows the name "Danial's Splity Tab" |
| 3 | Look at the icon on the app's tab. | It is the same mark as the header<br>It is light indigo on the dark tab |
| 4 | Switch Windows to light mode (Settings, Personalization, Colors, Choose your mode, Light). | Windows and Chrome turn light<br>The app's page stays dark, it has one dark look |
| 5 | Click the app's tab and press **F5**. | The tab icon is now dark navy<br>The mark is easy to see on the light tab |
| 6 | Switch Windows back to dark mode. | Windows and Chrome turn dark |
| 7 | Press **F5**. | The tab icon is light indigo again |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | BLOCKED | Blocked by its seat, not the app. Step 1 matched, the mark left of Splity Tab, an indigo receipt outline with bars inside and a torn foot, no letter, and the header without Danial's. Steps 2 to 7 need the tab strip, the tab hover card and Windows light and dark mode, so only you can check them. The page title reads Danial's Splity Tab. Two captures render the file src/icon.svg in dark (light indigo) and in light (dark navy), which shows the file and not the tab. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-08

**Several bills, written up for later**

| | |
|---|---|
| **Scope** | S9 Several bills, written up as a future implementation (document only) · OPEN, written · sitting 1 |
| **Problem** | At the 1.0 test you said several bills could be "future implementation" and asked for it "as a doc only so that we can showcase it". The note is written and nothing of it is built. This case is a read of the note. |
| **Before you start** | UAT-07 done. The note is [several-bills.md]({workspace}\examples\split\docs\future\several-bills.md). |

| # | Do this | You should see |
|---|---|---|
| 1 | Open several-bills.md in Notepad (right-click it, Open with, Notepad). | The title reads "Future implementation: several bills"<br>The status reads "not built. A design note for a later version." |
| 2 | Read down the headings. | "Why this note exists"<br>"What the user would get"<br>"How it could work"<br>"What it would change"<br>"Not decided" |
| 3 | Close Notepad and look at the app's top bar. | Only **New bill** sits at the right<br>There is no list of bills and no second bill anywhere |
| **Note** | The note leaves two calls to you for when it is picked up, whether a finished bill is marked as paid and how the list sorts. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched. The note was read with a file reader in place of Notepad. The title, the status and the five headings in order match, and only New bill sits in the top bar. Only you can check how it opens in Notepad itself. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-09

**Every screen on your iPhone, and the white ring after a tap**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S7 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | Every iPhone browser runs Safari's engine, and 1.0 was tested only in Chrome's. The automated runs now cover Safari's engine too, but not a real iPhone, its touch, its keyboard or its settings. Your ruling for S5 asked for cases on your own iPhone, UAT-09 to UAT-15. This one walks the phone layout and the Splits sheet's glass. It also holds open item A1 (H-11), which only your eyes can rule on. |
| **Before you start** | Sitting 2 starts here, on your iPhone in Safari. The orchestrator gives you the address for your iPhone when you start this sitting. Use a normal tab, never a Private one. Block All Cookies (Settings, Apps, Safari) is off. Nothing is saved for that address on the iPhone, so the app opens on its first screen. |

| # | Do this | You should see |
|---|---|---|
| 1 | Open the address in Safari. | The mark and "Splity Tab" sit at the top left<br>**New bill** sits at the top right<br>The "People" row is open, its caret up<br>Two fields, "Person 1" and "Person 2", each with a faint x<br>**Add person** under them<br>A "Charges" row reads "Service 10%, SST 6%" with a caret<br>"Split" with Even chosen and By item beside it<br>"Subtotal" with "RM" and a grey "0.00"<br>The strip at the bottom reads "Enter the subtotal to see the splits."<br>**Splits** with an up caret sits in the strip<br>**Copy summary** in the strip is faint |
| 2 | Tap **Add person**. | A third field shows "Person 3" in grey, with the cursor in it<br>The keyboard opens<br>All three x are now bright |
| 3 | Tap **Done** (or the check mark) at the right of the bar above the keyboard. | The keyboard closes |
| 4 | Tap the **Subtotal** field. | A number keyboard opens |
| 5 | Type `100`. | The field reads 100 |
| 6 | Tap **Done** above the keyboard. | The keyboard closes<br>The strip reads "Total RM 116.60"<br>Copy summary in the strip is bright |
| 7 | Tap the **Charges** row. | It opens, "Service charge" with 10 and %<br>"SST" with 6 and %<br>"Set a charge to 0 if your bill already includes it."<br>Its caret turns up |
| 8 | Tap the **Charges** row again. | It folds and reads "Service 10%, SST 6%" |
| 9 | Tap **Splits**. | A sheet rises over the dimmed page<br>A grab bar at its top centre and a **Close** x at its top right<br>Total RM 116.60<br>Subtotal RM 100.00<br>Service 10% RM 10.00<br>SST 6% RM 6.60<br>The heading "Splits"<br>Person 1 RM 38.87<br>Person 2 RM 38.87<br>Person 3 RM 38.86<br>Adds up to RM 116.60<br>"2 sen left over" with the chip "Top of the list"<br>**Copy summary** at the bottom of the sheet<br>The page behind shows faintly through the sheet's glass<br>No ring is drawn round the sheet |
| 10 | Tap the **Top of the list** chip. | The Spare sen panel rises from the bottom over the sheet<br>A **Close** x at its top right<br>It reads "2 sen left over"<br>Three choices, "Top of the list", "One person", "At random"<br>Top of the list is chosen<br>A thin light ring is drawn round Top of the list, see the note |
| 11 | Tap **One person**. | Three pills, "Person 1", "Person 2", "Person 3"<br>Person 1 is ticked |
| 12 | Tap **Close** on the Spare sen panel. | The panel goes down<br>Person 1 reads RM 38.88<br>Person 2 reads RM 38.86<br>Person 3 reads RM 38.86<br>Adds up to reads RM 116.60<br>The chip reads "One person, Person 1"<br>A thin light ring is drawn round the One person, Person 1 chip, see the note |
| 13 | Tap **Close** on the sheet. | The sheet goes down<br>The strip reads "Total RM 116.60"<br>Splits has focus. Note whether a ring is drawn round it |
| 14 | Tap **New bill**. | A dialog reads "Start a new bill?"<br>Under it "This clears the people, items and amounts."<br>A red **Start new bill** across the dialog, with **Cancel** under it<br>A thin light ring is drawn round Cancel, see the note |
| 15 | Tap **Cancel**. | The dialog closes<br>The three people are still there<br>The strip reads "Total RM 116.60" |
| **Note** | **You are being asked to rule on this (open item A1, H-11).** In Safari's engine a tap that opens a popup or closes the Spare sen panel draws a thin light ring, the keyboard ring, on the control the app focuses, Top of the list in step 10, the spare sen chip in step 12 and Cancel in step 14. The design and Chrome draw none. A keyboard user gets the same ring on purpose. Option 1, keep it, a line in the test notes, nothing to build. Option 2, remove it, which goes back to the plan or the design because it changes how focus is set. We recommend option 1, it is Safari's own rule and it helps a keyboard user. If you see a ring anywhere else, say where. Write your choice in your note. If Safari zooms in on a tap, pinch the page back to its normal size. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | FAIL | Failed on step 13 line 3 only, a fault in the script. It expected a ring round Splits and none was drawn (not focus-visible) at either height, because the case's order does not draw one. At step 12 a ring was drawn round the One person, Person 1 chip, which the script did not list. A probe shows the ring on Splits comes only when the sheet is closed straight after it opens, not after the Spare sen panel has been used as in this case. The rings at steps 10 and 14 were drawn and were light indigo, rgb(163, 170, 255), not white. Everything else it could drive matched at 390 x 664 and 390 x 844, every figure exact. Step 12 and step 13 line 3 were repaired after the run with the tester's words, and the ring-order probe confirms the new wording. They were not run again. It ran Safari's engine on Windows, not an iPhone, so only you can check the keyboard, the Done key and Safari's settings. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-10

**On the phone, a double tap acts once**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with the double tap rule (H-04) on your iPhone · OPEN, built · sitting 2 |
| **Problem** | Safari's engine counts the second tap of a quick double tap as a new tap, so in testing it acted twice, a second person added or the next row removed. You ruled "Time + place". A tap less than half a second after the last one and within about a finger's width of it does nothing. A slower tap acts. This case also records what your iPhone does with a tap on the charges hint, which Safari's engine on Windows answers differently from Chrome's. |
| **Before you start** | UAT-09 done. Three people, Subtotal 100, the strip reads Total RM 116.60, People open. |

| # | Do this | You should see |
|---|---|---|
| 1 | Double-tap **Add person** quickly. | Exactly one new field shows "Person 4" in grey<br>The cursor is in it and the keyboard opens<br>Four fields in all |
| 2 | Tap **Done** above the keyboard. | The keyboard closes |
| 3 | Tap **Add person** once, wait about one second, then tap **Add person** again where it now sits. | Two more fields, "Person 5" and "Person 6"<br>Six fields in all |
| 4 | Tap **Done** above the keyboard. | The keyboard closes |
| 5 | Double-tap the **x** in the Person 6 field quickly. | Person 6 is gone<br>Five fields, Person 1 to Person 5<br>No new empty field appeared<br>The cursor is in Person 5 |
| 6 | Tap **Done** above the keyboard. | The keyboard closes |
| 7 | Double-tap **Splits** quickly. | The sheet opens and stays open<br>Total RM 116.60<br>Subtotal RM 100.00<br>Service 10% RM 10.00<br>SST 6% RM 6.60<br>Person 1 RM 23.32<br>Person 2 RM 23.32<br>Person 3 RM 23.32<br>Person 4 RM 23.32<br>Person 5 RM 23.32<br>Adds up to RM 116.60<br>No spare sen line<br>No "Summary copied" and no "Could not copy" line in the sheet |
| 8 | Tap **Close** on the sheet. | The sheet goes down |
| 9 | Double-tap **New bill** quickly. | The dialog opens and stays open |
| 10 | Double-tap **Cancel** quickly. | The dialog closes<br>The five people are still there<br>The strip reads "Total RM 116.60"<br>Charges is still folded<br>The keyboard does not open |
| 11 | Tap the **Charges** row. | It opens with Service charge 10 and SST 6 |
| 12 | Tap the **Service charge** field just right of the 10. | The cursor is after the 10 and a number keyboard opens |
| 13 | Type `5`. | The field reads 105<br>No red error shows yet |
| 14 | Tap the hint text "Set a charge to 0 if your bill already includes it." | The cursor stays in the Service charge field<br>No red error shows |
| 15 | Tap **Done** above the keyboard. | The keyboard closes<br>A red "Enter a rate from 0 to 30" with a warning circle shows under the field<br>The field has a red edge<br>The strip reads "Check the charges to see the splits."<br>Copy summary in the strip is faint |
| 16 | Tap the **Service charge** field just right of the 105. | The cursor is after the 105 |
| 17 | Tap the delete key once. | The field reads 10<br>The red error is gone |
| 18 | Tap **Done** above the keyboard. | The keyboard closes<br>The strip reads "Total RM 116.60" |
| **Note** | If Safari zooms in on a double tap, pinch the page back to its normal size before the next step. The zoom is Safari's own. Step 14 lists what Safari's engine does on Windows. Chrome's engine leaves the field and shows the error at that tap. Both are by design. If your iPhone shows the error at step 14, cross those two lines and say so in your note, it is a record, not a fault. If the keyboard does not open after a press on Add person or an x, cross that line and tap the next step's Done only when the keyboard is up. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line it could drive matched at 390 x 664 and 390 x 844. Each double tap acted once, one Person 4, one removal with the cursor in Person 5, the sheet and the dialog stayed open, and Cancel closed once with nothing behind it pressed and no copy. A slower second tap acted. The tap on the hint reached no mousedown or click, focus stayed in Service charge and no error showed, which is the WebKit result the case lists. Leaving the field showed Enter a rate from 0 to 30 with a red edge, with one Tab in place of Done. It has no iOS keyboard, so only you can check the keyboard lines and how real fingers land. It ran Safari's engine on Windows, not an iPhone. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-11

**On the phone, the field you type in never hides under the strip**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S7 and H-08 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | On a phone the strip sits fixed at the bottom. In Safari's engine, moving to the next field could leave it under the strip, partly or wholly hidden. You agreed to the fix, the app scrolls a focused field clear of the strip. Here you move down a list of prices with the arrows above the keyboard. |
| **Before you start** | UAT-10 done. Tap **New bill**, then **Start new bill**. Tap **By item**. Then four times, tap **Add item** and tap **Done** above the keyboard. |

| # | Do this | You should see |
|---|---|---|
| 1 | Look at the screen. | People is open with Person 1 and Person 2<br>Charges is folded<br>By item is chosen<br>Four rows, Item 1 to Item 4, each with a grey "0.00" and an amber bar<br>The strip reads "Add each item and tap who had it to see the splits." |
| 2 | Tap the **Item 1** price field. | The cursor is in Item 1's price and a number keyboard opens<br>The field shows in full, not under the strip and not under the keyboard |
| 3 | Type `15.90`. | The field reads 15.90 |
| 4 | Tap the down arrow on the bar above the keyboard. | The cursor is in the Item 2 name field<br>The field shows in full, not under the strip and not under the keyboard |
| 5 | Tap the down arrow. | The cursor is in Item 2's price<br>The field shows in full, not under the strip and not under the keyboard |
| 6 | Type `13.50`. | The field reads 13.50 |
| 7 | Tap the down arrow. | The cursor is in the Item 3 name field<br>The field shows in full, not under the strip and not under the keyboard |
| 8 | Tap the down arrow. | The cursor is in Item 3's price<br>The field shows in full, not under the strip and not under the keyboard |
| 9 | Type `12.00`. | The field reads 12.00 |
| 10 | Tap the down arrow. | The cursor is in the Item 4 name field<br>The field shows in full, not under the strip and not under the keyboard |
| 11 | Tap the down arrow. | The cursor is in Item 4's price<br>The field shows in full, not under the strip and not under the keyboard |
| 12 | Type `18.00`. | The field reads 18.00 |
| 13 | Tap **Done** above the keyboard. | The keyboard closes<br>The strip shows a warning circle and "4 items still need a person. Tap who had each one to see the splits."<br>Copy summary in the strip is faint |
| 14 | Under Item 1, tap **Person 1**. | Item 1's amber bar is gone<br>The strip reads "3 items still need a person. Tap who had each one to see the splits." |
| 15 | Under Item 2, tap **Person 2**. | The strip reads "2 items still need a person. Tap who had each one to see the splits." |
| 16 | Under Item 3, tap **Person 2**. | The strip reads "1 item still needs a person. Tap who had it to see the splits." |
| 17 | Under Item 4, scroll until its buttons show, then tap **Person 1**. | No amber bar is left<br>The strip reads "Total RM 69.26"<br>Copy summary in the strip is bright |
| 18 | Tap **Splits**. | Total RM 69.26<br>Subtotal RM 59.40<br>Service 10% RM 5.94<br>SST 6% RM 3.92<br>"Splits" with "items + charges"<br>Person 1 RM 39.53<br>Under it 33.90 + 5.63<br>Person 2 RM 29.73<br>Under it 25.50 + 4.23<br>Adds up to RM 69.26<br>Under it 59.40 + 9.86<br>"1 sen left over" with "Top of the list" |
| 19 | Tap **Close** on the sheet. | The sheet goes down |
| **Note** | The arrows on the bar above the keyboard move to the next text field and skip the buttons. A field can sit close above the strip, it only has to show in full. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line it could drive matched at 390 x 664 and 390 x 844. Moving down the fields, with Tab until the next text field in place of the keyboard's down arrow, left every focused field in full above the strip, the lowest one 12 px clear of it. The strip messages and the sheet figures were exact. Step 17 needed a scroll to reach Person 1 under Item 4, now written into the step. It has no on-screen keyboard, so only you can check the keyboard lines and the real arrows above the keyboard. It ran Safari's engine on Windows, not an iPhone. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-12

**On the phone, a big bill never scrolls sideways**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S2 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | The 360 px check of UAT-04, on your own iPhone. A four-figure price and then a six-figure Total must fit with nothing scrolling sideways. The price field at 99999.99 is open item A2 (H-12), which you rule in UAT-04. Here you only look at it on your phone. |
| **Before you start** | UAT-11 done. Four items, the strip reads Total RM 69.26. |

| # | Do this | You should see |
|---|---|---|
| 1 | Tap **Add item**. | A row "Item 5" with a grey "0.00" and an amber bar<br>The cursor is in its name and the keyboard opens |
| 2 | Tap the down arrow above the keyboard. | The cursor is in Item 5's price<br>The field shows in full, not under the strip and not under the keyboard |
| 3 | Type `964.50`. | The field reads 964.50 |
| 4 | Tap **Done** above the keyboard. | The keyboard closes<br>Item 5's price shows 964.50 whole<br>The strip shows a warning circle and "1 item still needs a person. Tap who had it to see the splits." |
| 5 | Under Item 5, scroll until its buttons show, then tap **Person 1**. | The amber bar is gone<br>The strip reads "Total RM 1,193.87" on one line |
| 6 | Swipe left across the middle of the page. | Nothing moves sideways |
| 7 | Tap **Splits**. | Total RM 1,193.87<br>Subtotal RM 1,023.90<br>Service 10% RM 102.39<br>SST 6% RM 67.58<br>Person 1 RM 1,164.14<br>Under it 998.40 + 165.74<br>Person 2 RM 29.73<br>Under it 25.50 + 4.23<br>Adds up to RM 1,193.87<br>Under it 1,023.90 + 169.97<br>"1 sen left over" with "Top of the list"<br>Every figure shows whole, none cut at its edge |
| 8 | Tap **Close** on the sheet. | The sheet goes down |
| 9 | Tap the **Item 5** price field. | The cursor is in it and a number keyboard opens |
| 10 | Hold the delete key until the field is empty. | The field shows a grey "0.00" |
| 11 | Type `99999.99`. | The field takes the new price |
| 12 | Tap **Done** above the keyboard. | The keyboard closes<br>The strip reads "Total RM 116,669.25" on one line |
| 13 | Tap **Splits**. | Total RM 116,669.25<br>Subtotal RM 100,059.39<br>Service 10% RM 10,005.94<br>SST 6% RM 6,603.92<br>Person 1 RM 116,639.52<br>Under it 100,033.89 + 16,605.63<br>Person 2 RM 29.73<br>Under it 25.50 + 4.23<br>Adds up to RM 116,669.25<br>Under it 100,059.39 + 16,609.86<br>"1 sen left over" with "Top of the list"<br>Every figure shows whole, none cut at its edge |
| 14 | Tap **Close** on the sheet. | The sheet goes down |
| 15 | Swipe left across the middle of the page. | Nothing moves sideways |
| **Note** | Look at Item 5's price field after step 12 and say in your note whether it shows 99999.99 whole or cut, as at 360 px in UAT-04. It adds to your ruling on open item A2. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line it could drive matched at 390 x 664 and 390 x 844. The strip read RM 1,193.87 and RM 116,669.25 on one line and every sheet figure was whole and exact. It has no touch swipe, so at the two swipe lines it measured instead, and the page was 390 px wide in a 390 px viewport with nothing past its edge. For the A2 note, Item 5's 99999.99 shows cut after leaving the field (text 92 px in a 76 px field). Step 5 needed a scroll to reach Person 1 under Item 5, now written into the step. Only you can check the swipes and the keyboard lines on a real iPhone. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-13

**VoiceOver on a price field, before and after its error**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S7 and H-09 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | You ruled "Build to the golden" for the amount fields, so each price field points a screen reader at its error text at all times. Measured in Chrome's engine, a screen reader then reads "Enter an amount like 12.50" as a hint even before any error shows. You kept it as built and asked for an iPhone VoiceOver case. The last steps also check that closing the New bill dialog takes VoiceOver straight back to New bill. |
| **Before you start** | UAT-12 done. VoiceOver is off. With VoiceOver on, one tap reads an item and a double tap anywhere presses it. You turn it on in Settings, Accessibility, VoiceOver. |

| # | Do this | You should see |
|---|---|---|
| 1 | Scroll up to Item 1 and tap its price field. | The cursor is in it and a number keyboard opens |
| 2 | Hold the delete key until the field is empty. | The field shows a grey "0.00" |
| 3 | Type `13.505`. | The field reads 13.505 |
| 4 | Tap **Done** above the keyboard. | The keyboard closes<br>A red "Enter an amount like 12.50" with a warning circle shows under Item 1<br>Item 1's price field has a red edge<br>The strip reads "Give every item a price to see the splits." |
| 5 | Turn on VoiceOver in Settings, Accessibility, VoiceOver, and go back to Safari. | VoiceOver speaks as you move<br>Safari shows the app |
| 6 | Tap the **Item 1** price field once. | A frame is drawn round the field<br>VoiceOver reads "Item 1 price in RM"<br>It reads the value 13.505<br>It says it is a text field<br>It says the value is invalid<br>It reads "Enter an amount like 12.50" |
| 7 | Tap the **Item 2** price field once. | VoiceOver reads "Item 2 price in RM"<br>It reads the value 13.50<br>It says it is a text field<br>It reads "Enter an amount like 12.50", though no error shows there |
| 8 | Tap **New bill** once. | VoiceOver reads "New bill" and that it is a button |
| 9 | Double-tap anywhere on the screen. | The dialog opens<br>VoiceOver reads "Cancel" |
| 10 | Double-tap anywhere on the screen. | The dialog closes<br>VoiceOver reads "New bill" next<br>It reads nothing else between Cancel and New bill |
| 11 | Turn off VoiceOver. | VoiceOver is silent |
| **Note** | VoiceOver's order and wording vary a little. What matters is that the hint is read before any error shows, that an invalid value is called invalid, and that focus lands on Cancel and then on New bill. If VoiceOver reads the hint only after a pause, that is its setting Speak Hints. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | BLOCKED | Blocked by its seat, not the app. Steps 1 to 4 matched, 13.505, the red Enter an amount like 12.50 with its circle, the red edge and the strip message. Steps 5 to 11 need VoiceOver, so only you can check them. In their place it read the markup behind them, the label Item 1 price in RM, aria-invalid true, described by the error text, and Item 2 described by the same text while it is hidden. That is not what VoiceOver says. Plain taps put focus on Cancel and then back on New bill. At 390 x 664 Item 1's field was above the screen and needed a scroll, now written into step 1. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-14

**With Block All Cookies on, the app warns that nothing is saved, and the Private limit**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S4 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | The save warning of UAT-06, in Safari on your iPhone, with the setting that blocks storage there. Then the known limit. A Private tab reports every save as working and drops the bill when it closes, so no page can warn. The README says so. |
| **Before you start** | UAT-13 done, VoiceOver off. Five items, Item 1's price at 13.505 with its red error. |

| # | Do this | You should see |
|---|---|---|
| 1 | Open the Settings app, then Apps, then Safari, and turn on **Block All Cookies**. | The Block All Cookies switch is on |
| 2 | Go back to Safari, tap the address bar and tap **Go** on the keyboard. | The page loads again<br>A row under the top bar starts with an amber warning triangle<br>It reads "This bill is not being saved on this device. It will be lost when you close this tab."<br>It has no close button<br>People is open with Person 1 and Person 2<br>Split is on Even with an empty Subtotal<br>The strip reads "Enter the subtotal to see the splits." |
| 3 | Tap the **Subtotal** field. | A number keyboard opens |
| 4 | Type `50`. | The field reads 50 |
| 5 | Tap **Done** above the keyboard. | The strip reads "Total RM 58.30"<br>The warning is still there |
| 6 | In Settings, Apps, Safari, turn off **Block All Cookies**. | The Block All Cookies switch is off |
| 7 | Go back to Safari, tap the address bar and tap **Go**. | No warning shows<br>Split is on By item with five items<br>Item 1's price reads 13.505 with its red error<br>The strip reads "Give every item a price to see the splits." |
| 8 | Tap the tabs button, choose **Private** and tap **+** for a new Private tab. | A new Private tab opens |
| 9 | Type the app's address and tap **Go**. | The app's first screen shows, Person 1 and Person 2 with an empty Subtotal<br>No warning shows |
| 10 | Tap the **Subtotal** field. | A number keyboard opens |
| 11 | Type `100`. | The field reads 100 |
| 12 | Tap **Done** above the keyboard. | The strip reads "Total RM 116.60"<br>No warning shows |
| 13 | Tap the tabs button and close this Private tab with its x. | The Private tab is gone |
| 14 | Tap **+** for a new Private tab, type the app's address and tap **Go**. | The first screen shows again<br>The Subtotal is empty<br>No warning showed at any point in the Private tabs |
| 15 | Tap the tabs button, go back to your normal tabs and tap the app's tab. | The app shows its five items |
| **Note** | If iOS asks you to confirm at step 1, confirm the block. Reload at step 7 before you change anything, as in UAT-06. If the five items do not come back at step 7, Safari dropped the saved data when you blocked it. Mark that line with a cross and say so in your note. If Private Browsing is locked, unlock it with Face ID. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | BLOCKED | Blocked by its seat, not the app. Steps 2 to 7 matched with a storage stand-in in place of Block All Cookies at steps 1 and 6, a page whose every localStorage access throws. The warning row sat under the top bar with the triangle and the exact text, no close button, over a new bill at RM 58.30. With the block lifted the five items came back, Item 1 at 13.505 with its red error. Steps 8 to 15 need Private Browsing and the tab overview, and steps 1 and 6 need iOS Settings, so only you can check them. It could not see what Safari's own setting does to the saved bill. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-15

**The tab icon in Safari, in light and dark**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S6 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | The tab icon of UAT-07, in Safari on your iPhone. Safari 26 ignores the light and dark switch inside an icon, a Safari bug you accepted for 1.1.0, so the mark is expected in one colour in both modes. A home-screen icon is not built in 1.1.0. |
| **Before you start** | UAT-14 done, Safari on the app in a normal tab. The iPhone is in dark mode (Settings, Display and Brightness, Dark). |

| # | Do this | You should see |
|---|---|---|
| 1 | Tap the tabs button at the bottom of Safari. | The tab overview opens<br>The app's tab shows the mark beside "Danial's Splity Tab" |
| 2 | Open Settings, then Display and Brightness, and choose **Light**. | The iPhone turns light |
| 3 | Go back to Safari's tab overview. | The mark is the same colour as at step 1<br>The mark is easy to see on the light tab |
| 4 | Tap the app's tab. | The app shows again, still dark |
| 5 | Switch the iPhone back to the mode you use. | The iPhone is in your usual mode |
| **Note** | Say in your note which colour the mark is, light indigo or dark navy. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | BLOCKED | Blocked by its seat, not the app. Every step needs Safari's tab overview or iOS settings, so the whole case is yours alone. The page title does read Danial's Splity Tab. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

## Verdict summary

| case | sitting | scope | T tester | U user | crosses | next step |
|---|---|---|---|---|---|---|
| UAT-01 | 1 | S1 even | PASS | | | |
| UAT-02 | 1 | S7 | BLOCKED (script, step 2 line 5 and step 3 line 1, reworded, not run again) | | | |
| UAT-03 | 1 | S1 by item | PASS | | | |
| UAT-04 | 1 | S2, holds A2 (H-12) | PASS | | | |
| UAT-05 | 1 | S3 | PASS | | | |
| UAT-06 | 1 | S4 | PASS | | | |
| UAT-07 | 1 | S6 with S8 | BLOCKED (seat) | | | |
| UAT-08 | 1 | S9 | PASS | | | |
| UAT-09 | 2 | S5 with S7, holds A1 (H-11) | FAIL (step 13 line 3, reworded, not run again) | | | |
| UAT-10 | 2 | S5 with H-04 | PASS | | | |
| UAT-11 | 2 | S5 with S7 and H-08 | PASS | | | |
| UAT-12 | 2 | S5 with S2 | PASS | | | |
| UAT-13 | 2 | S5 with H-09 | BLOCKED (seat) | | | |
| UAT-14 | 2 | S5 with S4 | BLOCKED (seat) | | | |
| UAT-15 | 2 | S5 with S6 | BLOCKED (seat) | | | |

---

# (a) OPEN. Needs your decision

> Every fork we could not settle ourselves. Each one is a **decision you make**, not a status line.
> Read from `CHANGE-LEDGER.md` §Needs the human and the orchestrator's own rulings. **Deferrals are listed
> too.** A deferral is a decision we made on your behalf, so you can overturn it.

### A1. The white ring after a tap in Safari (H-11)

| | |
|---|---|
| **What it is** | In Safari's engine a tap that opens the New bill dialog or the Spare sen panel, or closes the Spare sen panel, draws a thin light ring, the keyboard focus ring, on the control the app focuses, Cancel, the chosen spare sen choice and the spare sen chip. The design and Chrome draw none. You see it in UAT-09. |
| **Why it needs you** | It is a visible difference from the approved design on your iPhone, and removing it changes how focus is set or changes the design. |
| **Options** | (1) Keep it. A line in the test notes and the ledger, nothing to build. (2) Remove it. Back to the plan or the design, for example telling Safari the focus did not come from a keyboard. |
| **Recommendation** | (1). It is Safari's own rule, the ring helps someone who uses a keyboard, and Streaks has the same item, so one ruling can cover both apps. |
| **Your ruling** | |

### A2. A price of 99999.99 does not fit its field at 360 px until focused (H-12)

| | |
|---|---|
| **What it is** | At 360 px a price of 99999.99 shows as "99999.9" in its field until the field has focus. The splits, the strip and the sheet show every figure whole, and 964.50 fits as promised. The field width is the approved design's. You see it in UAT-04, and on your iPhone in UAT-12. |
| **Why it needs you** | A wider field changes the approved design, which only the design phase can do. |
| **Options** | (1) Keep it, with a line in the README's limits. (2) A design change in v1.2.0, a wider price field or a smaller font at 360 px. |
| **Recommendation** | (1) for 1.1.0. A five-figure price for one dish is rare, and the value shows whole everywhere it is added up. |
| **Your ruling** | |

### A3. How your iPhone reaches the app for sitting 2

| | |
|---|---|
| **What it is** | Sitting 2 needs the app on your iPhone. The app runs on this PC at 127.0.0.1, an address only this PC can open. |
| **Why it needs you** | The first option opens a port on your home network for the length of the sitting, so it is your call. |
| **Options** | (1) The orchestrator serves the app on this PC's Wi-Fi address for sitting 2 only. Windows asks once whether to let Python through its firewall, and you answer that prompt. The server stops when the sitting ends. Over that address Safari treats the page as not secure, so Copy summary says "Could not copy. Your browser blocked the clipboard." there, and no case presses it. (2) The iPhone cases wait for the published page after the seal. |
| **Recommendation** | (1). The iPhone cases are the only check on a real phone, and they should inform the seal, not follow it. |
| **Your ruling** | |

### A4. A stray file outside the project

| | |
|---|---|
| **What it is** | An empty file, `{temp}\ref_a13`, made by an orchestrator slip on 15 October. It is logged in [out-of-project-artifacts.md]({workspace}\examples\split\docs\progress\out-of-project-artifacts.md). |
| **Why it needs you** | Agents never delete outside the project. You delete it by hand. |
| **Options** | (1) Delete it. (2) Leave it. |
| **Recommendation** | (1). It is 0 bytes and nothing uses it. |
| **Your ruling** | |

### A5. Long paths and local paths before the repository goes public

| | |
|---|---|
| **What it is** | Some failure screenshots in the history have paths long enough that a clone into a deep Windows folder fails on them, and the records hold local D:/ paths and your Windows user folder. The published page never serves them, but a public repository shows them. The same check is open for Streaks. |
| **Why it needs you** | It is your choice for publish prep, after the seals. |
| **Options** | (1) Shorter evidence names and scrubbed paths before the repository goes public. (2) Leave the failure screenshots out of the published history. (3) Publish them as they are. |
| **Recommendation** | No strong recommendation, it is a preference call. Scrubbing hides your user folder name. Keeping them keeps the records exactly as they happened. |
| **Your ruling** | |

### A6. Smaller calls we made for you

| | |
|---|---|
| **What it is** | (a) The planned QA and security re-check after the fixes was folded into the full regression, one run each instead of two. (b) A name field that receives only invisible control characters saves the same bill and clears "Summary copied". Accepted for 1.1.0, the fix goes to v1.2.0. (c) A Chinese or Japanese input method that holds a direction mark is cut short when the mark is removed. The name stays plain. Accepted, to v1.2.0. (d) Comments, test tidy-ups and qa wording wait for the v1.2.0 plan's doc and test pass, no behaviour changes. (e) The README header, lockup and badges stay at 1.0 until the seal, so the pictures show exactly what you seal. (f) The scope statuses move to SHIPPED at the seal. (g) Item names are kept plain too, not only person names. (h) Dismiss note now ignores the second press of a double click, so it no longer folds People on a phone. (i) Above six people the desktop card lists the splits in two columns. (j) A bad or blank rate or price blocks the receipt with its message and never counts as 0. (k) After a click on Cancel the focus reaches New bill a moment later, not at once. (l) The build's untracked leftovers are archived at publish prep, never deleted. |
| **Why it needs you** | Each one is ours and reversible. |
| **Options** | Accept all, or name the ones you want changed. |
| **Recommendation** | Accept all. None changes what you see in normal use. |
| **Your ruling** | |

---

# (b) SOLVED, in plain language

> Three beats each. **No R#, no file paths, no agent names, no test counts.** Those live in the batch docs.
> The third beat matters most, because it makes a decision cheap to overturn later.

### The by-item table on a small phone

| | |
|---|---|
| **The problem** | In 1.0 the by-item table scrolled sideways on a 360 px phone once the bill grew. |
| **What I did** | The new look moved the splits into a receipt that wraps each split's working under its name, so every figure fits at 360 px, up to a six-figure Total. |
| **Why this and not the others** | Shrinking the 1.0 table's text would have hit the readable floor before a large bill fitted. The one figure that still does not fit is a 99999.99 price inside its own field, open item A2. |

### Holding Enter on an item's x

| | |
|---|---|
| **The problem** | Holding Enter on the last item's x removed it, then the key's repeats pressed Add item and a blank item appeared. |
| **What I did** | After a press that changes the layout, the repeats of a held key are ignored until a fresh press. |
| **Why this and not the others** | A delay after each press would also slow a deliberate second press. Ignoring only the key's own repeats changes nothing for normal typing. |

### A double tap acts once

| | |
|---|---|
| **The problem** | Safari's engine counts the second tap of a double tap as a new tap, so it acted twice, a second person added or the next row removed. |
| **What I did** | Your ruling, "Time + place". A tap less than half a second after the last one and within about a finger's width of it does nothing. A mouse click and a key press work as in 1.0. |
| **Why this and not the others** | Time only would drop a quick tap somewhere else. Place only would drop a slow second tap on the same spot. The cost you accepted is that two deliberate fast taps on one spot count once. |

### The field under the phone strip

| | |
|---|---|
| **The problem** | In Safari's engine, moving to the next field could leave it under the strip at the bottom, one field wholly hidden. |
| **What I did** | Below the desktop width, when a focused field's bottom is under the strip, the app scrolls it just clear of the strip. |
| **Why this and not the others** | Accepting it as a Safari difference would break the rule that a focused control is always visible, and Safari on the iPhone is why its engine was added. |

### What a screen reader reads on a price field

| | |
|---|---|
| **The problem** | Built to the design, every price field points a screen reader at its error text, so "Enter an amount like 12.50" is read as a hint even before any error shows. |
| **What I did** | You kept it as built after a drawing of both states. UAT-13 checks it with VoiceOver. |
| **Why this and not the others** | Naming the error only while it shows would reopen the approved design for a hint that is correct before any error too. |

### Names stay plain

| | |
|---|---|
| **The problem** | An invisible direction mark pasted into a name made the People line run backwards on screen, while the copied summary stayed right. |
| **What I did** | Your ruling, option 1. Control and direction characters are removed from every name as it is typed or pasted and when a saved bill is read. Item names too. |
| **Why this and not the others** | Wrapping each name in invisible marks would keep the characters and put more invisible text in the page. Accepting it would leave the screen and the summary disagreeing. |

### A double press on Dismiss note

| | |
|---|---|
| **The problem** | On a phone, once the "could not be read" note was dismissed, the People row moved under the pointer, so the second press of a double click folded People. |
| **What I did** | Dismiss note now ignores the repeat press, as Add person and every x already did. |
| **Why this and not the others** | Leaving it as a known limit would break the rule that one double press acts once. No case here reaches it, because no real gesture makes a saved bill unreadable. The review drove it. |

### A save that fails now says so

| | |
|---|---|
| **The problem** | In 1.0, if the browser blocked or filled its storage, the bill was lost with no message. |
| **What I did** | A warning shows while saving fails, decided by the latest save, and from the first screen when the browser refuses storage outright, as you chose. It goes after the next save that works and cannot be dismissed. |
| **Why this and not the others** | A test write or a timer would add writes and delays for nothing the latest save does not already show. A private window and Safari's 7-day clean-up report every save as working, so the README states that limit instead of claiming a detector. |

### The spare sen choices

| | |
|---|---|
| **The problem** | The spare sen rule needed answers the request did not give, who can take them by item, what Pick again does when no draw changes anything, and what the chip says when the chosen person leaves. |
| **What I did** | Your answers. One person takes every spare sen, and by item only people on an item can be chosen. Pick again tries up to 64 draws, then leaves the splits. When the chosen person cannot take them, the chip names Top of the list, the rule in use. The copied summary shows a thousands comma, as on screen. |
| **Why this and not the others** | A person on no item paying a sen of other people's food felt wrong. An endless draw could hang. Hiding the fallback would make the chip lie about who pays. |

### The amber bar on a new item, and a late copy answer

| | |
|---|---|
| **The problem** | A new blank item shows the amber "needs a person" bar at once, and a copy whose answer came after a change showed nothing. |
| **What I did** | You kept both as built. |
| **Why this and not the others** | The bar tells you from the first moment what is missing. "Summary copied" after a change would claim figures the screen no longer shows. |

### The tab icon as its own file, and Safari's engine in every run

| | |
|---|---|
| **The problem** | The design carried the tab icon inside the page in a form the app's security rules block, and 1.0 was tested only in Chrome's engine. |
| **What I did** | The icon ships as its own small file, byte for byte the design's. Every behaviour test and the cold-start check now run in Safari's engine too. The pixel match stays in Chrome's, as you chose. |
| **Why this and not the others** | Loosening the security rules for one icon would weaken them for everything. Pixel matching in both engines was the other option. The white ring of A1 is what only a look in Safari could catch. |

### The old green page during the build

| | |
|---|---|
| **The problem** | You saw the 1.0 green and white page in the app's browser pane mid-build and stopped everything. |
| **What I did** | We checked the new design files against the archive, all equal, and showed you renders. The page you saw was a planned test of the unchanged 1.0 app. |
| **Why this and not the others** | That baseline proved the old checks before anything changed. We now warn you before such a run. |

---

## Residuals you should know about, that are not cases

- A private window and Safari's 7-day clean-up lose the bill with no warning. The browser reports nothing the page could show. The README says so, and UAT-14 shows it.
- Safari shows the tab icon in one colour in both modes. Safari's bug, accepted for 1.1.0, seen in UAT-15.
- No home-screen icon in 1.1.0. It needs a filled tile, against your no-tile ruling. Deferred to a later logo round.
- Two open tabs share one bill and the last save wins. Another page on the same github.io address can read the saved bill.
- Two deliberate taps on one spot less than half a second apart count once.
- A name field that receives only control characters clears "Summary copied" (A6 b). An input method holding a direction mark is cut short (A6 c).
- Two right-to-left names next to each other in the People line can show in right-to-left order. The app is English only.
- Dismiss note is NOT RUN as a case. No real gesture makes a saved bill unreadable, so the note cannot be reached without a console. The review and the regression drove it.
- Clearing the save warning without a reload is NOT RUN as a case. In the open page it would save that page's bill over the saved one. The review drove it with a stand-in.
- Firefox and Safari on a Mac are NOT RUN. The app reaching the desktop width with the Splits sheet open is NOT RUN as a case, the automated runs cover it.
