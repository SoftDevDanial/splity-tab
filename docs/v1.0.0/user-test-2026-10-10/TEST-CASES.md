# UAT: Split 1.0.0

> **Sitting 1 of 1.** Eight cases, one per scope section of `docs/v1.0.0/CHANGE-LEDGER.md`.
> Written from your seat: "I asked for X. Is X there, does it look right, can I use it?"
>
> **How to use this.** The app is already running. The orchestrator started it and gives you the address
> when it hands this over. Work the cases in order, because each one starts where the last one ended. On each
> case, record **your** verdict in the right-hand column. Every case gets a verdict, including the ones you
> could not do. `BLOCKED` means "I could not work out how to do this", and that is a real and useful answer.
>
> **The tester column is already filled in.** An agent drove every case before you. Its verdict is there so
> you can check it against yours. If it says PASS and you find FAIL, that is a finding about our testing,
> and one of the most valuable things you can give us. Nothing overwrites your verdict or the tester's.

**App URL:** `http://127.0.0.1:8732/` (running on this computer since 2026-10-10 14:51, started by the orchestrator)
**Starting state:** a new bill. Two name boxes read "Person 1" and "Person 2", **Even** is chosen, Subtotal is
empty, Service charge reads 10% and SST 6%. Nothing is saved yet in this browser for that address.
**Use a normal browser window, not a private or incognito one,** and always go to exactly the address above
(`localhost` is a different address to the browser and starts with an empty bill).
**Roughly how long:** 8 cases, about 20 minutes. A desktop browser is fine: the bill sits on the right. Narrow
the window to see the phone layout if you like. UAT-05 puts text on your clipboard, so copy anything you need first.

---

## Cases

### UAT-01: I can list the people at the table
**Scope:** C1 People · **Ledger status:** SHIPPED

**Problem.** You asked for a list of 2 to 12 people that you can rename, add to and remove from, so the
split uses the real names you will read out.

**Preconditions.** The starting state above.

**Steps.**
1. Click in the first name box ("Person 1"), select its text with **Ctrl+A** and type `Aisyah`.
2. Click in the second name box, select its text and type `Ben`.
3. Click **Add person** (the button with a plus, after the last name box. It moves along as people are added).
4. Type `Chen`.
5. Click **Add person** again.
6. Click the **×** at the right end of the new fourth name box.

**Expected result.** Before step 3, the **×** in both name boxes is greyed out and does nothing, because a split
needs two people. After step 3 a third box appears with the cursor already in it. It is empty, with a faint
"Person 3" hint that disappears when you type (unlike the first two boxes, whose "Person 1" and "Person 2" are
real text). Step 4 types into it. After step 5 a fourth box appears, and after step 6 it is gone again. You are
left with Aisyah, Ben and Chen, and every **×** is now active.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: both × greyed at the start and a click on them changed nothing. After Add person the cursor sat in the empty third box with its "Person 3" hint and `Chen` landed there. The fourth box went with its ×, leaving Aisyah, Ben and Chen with every × active | | |

---

### UAT-02: An even split gives everyone the same share, to the cent
**Scope:** C2 Even split · **Ledger status:** SHIPPED

**Problem.** You asked to type the bill subtotal once and see what each person owes, with the service charge
and SST added the way a Malaysian receipt adds them.

**Preconditions.** UAT-01 done: Aisyah, Ben and Chen, **Even** chosen.

**Steps.**
1. Click the **Subtotal** box (it has "RM" at its left).
2. Type `100.00`.
3. Read the **Bill summary** and **Shares** on the right (below the inputs on a narrow window).

**Expected result.** Bill summary: Subtotal RM 100.00, Service charge RM 10.00 with "10% of RM 100.00" under it,
SST RM 6.60 with "6% of RM 110.00" under it (SST is charged on the subtotal plus the service charge), and Total
RM 116.60. Shares: Aisyah RM 38.87, Ben RM 38.87, Chen RM 38.86.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: Subtotal RM 100.00, Service charge RM 10.00 "10% of RM 100.00", SST RM 6.60 "6% of RM 110.00", Total RM 116.60, shares 38.87, 38.87, 38.86 | | |

---

### UAT-03: The shares always add back up to the total
**Scope:** C5 Shares that add up · **Ledger status:** SHIPPED

**Problem.** You asked that the shares never drift a cent away from the receipt, and that the app shows the
check so nobody has to add it up at the table. Cents that do not divide evenly go one each to the people at
the top of the list.

**Preconditions.** UAT-02 done: the subtotal is 100.00.

**Steps.**
1. Read the line under the shares.
2. Click the **Subtotal** box, select its text and type `10.05`.
3. Read the Bill summary and the shares.
4. Select the text in the **Subtotal** box and type `100.00` again.

**Expected result.** At step 1 a green tick and "Adds up to" sit next to RM 116.60, the same as the Total
(38.87 + 38.87 + 38.86). At step 3: Service charge RM 1.01 (10% of RM 10.05 is 1.005, rounded half up), SST RM
0.66, Total RM 11.72, and the shares read Aisyah RM 3.91, Ben RM 3.91, Chen RM 3.90, with "Adds up to RM 11.72".
After step 4 everything is back to UAT-02.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: tick and "Adds up to RM 116.60". At 10.05: RM 1.01, RM 0.66, Total RM 11.72, shares 3.91, 3.91, 3.90, "Adds up to RM 11.72". Back to UAT-02 after step 4 | | |

---

### UAT-04: I can change or switch off the charges
**Scope:** C4 Charges · **Ledger status:** SHIPPED

**Problem.** You asked for service charge and SST that start at 10% and 6% and can be changed, including
switched off when the receipt already includes them.

**Preconditions.** UAT-03 done: subtotal 100.00, Service charge 10, SST 6.

**Steps.**
1. Click the **Service charge** box under "Charges", select its text and type `0`.
2. Read the Bill summary and the shares.
3. Select the text in the **Service charge** box and type `31`.
4. Press **Tab**. (The cursor moves on to the SST box and selects its 6. That is normal Tab behaviour.)
5. Click the **Service charge** box, select its text and type `10`.

**Expected result.** Under the two boxes a grey hint reads "Set a charge to 0 if your bill already includes
it." At step 2: Service charge RM 0.00, SST RM 6.00 ("6% of RM 100.00"), Total RM 106.00, shares Aisyah RM 35.34,
Ben RM 35.33, Chen RM 35.33. After step 4 red text under the box reads "Enter a rate from 0 to 30", the Bill
summary goes away and Shares says "Check the charges to see the shares." After step 5 the red text is gone and
the bill is back to RM 116.60.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: hint exact. At 0: RM 0.00, RM 6.00, Total RM 106.00, shares 35.34, 35.33, 35.33. At 31 then Tab: "Enter a rate from 0 to 30" in red, no Bill summary, "Check the charges to see the shares." Back to RM 116.60 at 10 | | |

---

### UAT-05: One tap copies a summary I can paste into the group chat
**Scope:** C6 Copy summary · **Ledger status:** SHIPPED

**Problem.** You asked for one tap that copies the split as plain text, ready for the group chat.

**Preconditions.** UAT-04 done: the even split of 100.00 at 10% and 6%. Open any place you can paste text,
such as Notepad or a chat box you will not send.

**Steps.**
1. Click **Copy summary**, the dark button under the shares.
2. Read the line under the button.
3. Paste into Notepad (or your chat box) with **Ctrl+V**.

**Expected result.** Under the button: "Summary copied". The pasted text is exactly these six lines (some
paste targets add an empty line of their own at the end, which is not the app):
```
Bill split
Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)
Aisyah RM 38.87
Ben RM 38.87
Chen RM 38.86
Adds up to RM 116.60
```

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS, paste step not driven: "Summary copied", and the copied text equals the six lines byte for byte. The tester may not touch the real clipboard (rule CG-7), so it read the text from a stand-in instead of pasting | | |

---

### UAT-06: I can split by item, and a shared item is split between the people who had it
**Scope:** C3 Split by item · **Ledger status:** SHIPPED (one accepted limit, below)

**Problem.** You asked for the case where mental maths fails: people ordered different things. You list each
item with its price and tap who had it. The charges are then shared in proportion to what each person ate. The
shares only show once every item has someone, because a part split would not add up to the receipt.

**Preconditions.** UAT-05 done. Aisyah, Ben and Chen.

**Steps.**
1. Click **By item** (next to Even).
2. Click **Add item**. The cursor goes into the new item's name box.
3. Type `Nasi lemak ayam`, press **Tab**, type `15.90`.
4. Read the Shares area.
5. Under that item, click **Aisyah**.
6. Click **Add item**, type `Char kuey teow`, press **Tab**, type `13.50`, then click **Ben** under it.
7. Click **Add item**, type `Mee goreng mamak`, press **Tab**, type `12.00`, then click **Chen** under it.
8. Click **Add item**, type `Satay, 10 sticks`, press **Tab**, type `18.00`, then click **Aisyah** and **Chen** under it.
9. Read the Bill summary and the shares.

**Expected result.** At step 4 Shares reads "1 item still needs a person. Tap who had it to see the shares." A
tapped name turns dark. At step 9: Bill summary Subtotal RM 59.40, Service charge RM 5.94, SST RM 3.92, Total RM
69.26. The shares table has three small column heads, "Items", "+ Charges" and "= Share" (the names column has
no head):

| | Items | + Charges | = Share |
|---|---|---|---|
| Aisyah | RM 24.90 | RM 4.14 | RM 29.04 |
| Ben | RM 13.50 | RM 2.24 | RM 15.74 |
| Chen | RM 21.00 | RM 3.48 | RM 24.48 |
| Adds up to | RM 59.40 | RM 9.86 | RM 69.26 |

The satay's split is not printed on its own. Check it from the Items column: Aisyah's RM 24.90 is RM 15.90 +
RM 9.00, and Chen's RM 21.00 is RM 12.00 + RM 9.00, half of the satay's RM 18.00 each.

**Known limit, already ruled by you.** On a phone 360 px wide, a by-item bill whose items pass about RM 650
makes the shares table scroll sideways. You chose to fix it in 1.1.0 (2026-10-09). The bill in this case fits.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: the step 4 message exact, tapped names turn dark, the bill summary and every cell of the table as listed. The table fits at 390 and 360 px | | |

---

### UAT-07: My bill is still there when I come back
**Scope:** C7 Draft kept · **Ledger status:** SHIPPED

**Problem.** You asked for the bill to survive a reload or a closed tab on the same device, and for switching
between Even and By item to lose nothing.

**Preconditions.** UAT-06 done: By item, four items, shares showing. Keep at least one other tab open, so
closing this one does not close the browser.

**Steps.**
1. Close the app's browser tab.
2. Open a new tab and go to exactly `http://127.0.0.1:8732/` again.
3. Read the page.
4. Click **Even**.

**Expected result.** After step 2, **By item** is still chosen, with the four items, their prices, the same
names tapped and the same shares as UAT-06. After step 4 the Subtotal box still holds 100.00 and the shares
read RM 38.87, RM 38.87 and RM 38.86 again.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: after closing the page and opening a new one, By item with the same four items, taps and shares. After Even: 100.00 and 38.87, 38.87, 38.86 | | |

---

### UAT-08: I can start a new bill, but only on purpose
**Scope:** C8 New bill · **Ledger status:** SHIPPED

**Problem.** You asked for a way to clear everything for the next meal, behind a question so one slip cannot
wipe a bill.

**Preconditions.** UAT-07 done.

**Steps.**
1. Click **New bill** (top right).
2. Read the box that opens.
3. Click **Cancel**.
4. Click **New bill** again.
5. Click on the dimmed page outside the box, for example near the top-left corner of the page.
6. Click **New bill** again.
7. Click **Start new bill**.
8. Click **By item**.

**Expected result.** At step 2 a box asks "Start a new bill?" with "This clears the people, items and amounts."
under it, and two buttons, **Start new bill** and **Cancel**. After step 3 and after step 5 the box closes and
the bill is unchanged. After step 7 the page is back to the starting state: "Person 1" and "Person 2", Even,
an empty Subtotal, 10 and 6, and Shares says "Enter the subtotal to see the shares." After step 8 there are no
items, only **Add item**, and Shares says "Add an item to see the shares."

**You are being asked to rule on this.** The approved design note for this box said a click outside it does
nothing. While you delegated the run, we made it act like Cancel (step 5), so every way out of the box behaves
the same and nothing is cleared. Options: keep it (our recommendation) / make an outside click do nothing.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: the question and both buttons as written. Cancel and a click outside the box both closed it with the saved bill unchanged. Start new bill gave the starting state, and By item showed no items with "Add an item to see the shares." | | |

---

## Verdict summary

| case | scope | tester | you | next step |
|---|---|---|---|---|
| UAT-01 | C1 People | PASS | | |
| UAT-02 | C2 Even split | PASS | | |
| UAT-03 | C5 Shares that add up | PASS | | |
| UAT-04 | C4 Charges | PASS | | |
| UAT-05 | C6 Copy summary | PASS (paste not driven) | | |
| UAT-06 | C3 Split by item | PASS | | |
| UAT-07 | C7 Draft kept | PASS | | |
| UAT-08 | C8 New bill | PASS | | |

The tester's PASS shows the script can be run. It is not the proof that the feature works. That is your verdict.
Pre-run evidence: `pre-run/20261010-145359/` (the driver, 235 checks at 1280 x 800 and the same 235 at 390 x 844,
a screenshot per case). Script wording repaired from the tester's notes before handover, no case was blocked.

**Legend.** `PASS` it does what the case says · `FAIL` it does not · `BLOCKED` you could not run it. Say
which: the control was not where the script said, the starting state was unreachable, or the result was not
something you could see.

---

# (a) OPEN: needs your decision

> Every fork we could not settle ourselves. Each one is a decision you make, not a status line. Read from
> `CHANGE-LEDGER.md`, Needs the human. Deferrals are listed too, because a deferral is a decision we made
> on your behalf, and you can overturn it.

### H-01: The choices made while you delegated the run
- **What it is.** You handed this run over ("Auto create with lifecycles for 2 projects"). Every product and
  design choice inside it was made for you: the money rules (SST on subtotal plus service, leftover cents to the
  top of the list, an item nobody had blocks the shares), the "Working shown" look, the clarify-gate answers
  (one of them, the click outside the New bill box, is in UAT-08), the planner's calls.
- **Why it needs you.** Requirements and design are yours to decide. An agent may only propose them.
- **Options.** Accept them as they are · reopen any one of them (it then becomes work for a later version).
- **Recommendation.** Skim `docs/design-explore/round-1/compare.html` (the three looks side by side) and
  `docs/design/RULINGS.md`. Those carry the most taste. Everything else is in the ledger.

### D-01: The limits we accepted for 1.0 on your behalf
- **What it is.** Each was found during this version and kept on purpose.
  - Holding **Enter** down on the **×** of the only item adds a blank item. Keyboard only, one click on its × undoes it. **Planned for 1.1.0.**
  - If the browser blocks or fills its storage, changes stay on screen but are not saved, with no message.
  - Another page on the same `github.io` address can read the saved bill, because that host gives every
    project of one account one shared address.
  - Two open tabs do not see each other's changes. The last one to save wins.
  - A double click on the **×** of the "could not be read" note moves the keyboard cursor to the top of the
    page. Nothing in the bill changes.
  - A name made only of invisible characters prints as a blank name in the copied summary.
  - Only Chrome's engine (Chromium) was tested. Safari and Firefox were not.
- **Why it needs you.** Deferring is a decision we made for you.
- **Options.** Keep each as a known limit · move any one into 1.1.0.
- **Recommendation.** Keep them. 1.1.0 already takes the table at 360 px (your ruling) and the held Enter.

---

# (b) SOLVED: in plain language

### A quick double click could change or wipe part of the bill
- **The problem.** Several buttons move the page under the pointer when they act. The second click of a double
  click then landed on whatever slid into place: a double click on Cancel tapped a name under the box, a double
  click on × removed two people, a double click on the last × added a blank person, and a double click on Add
  person added a person and took them away again.
- **What I did.** The second click of a double click on those buttons is ignored. A single click or a key press
  is never held back, and there is no timer.
- **Why this and not the others.** My first ruling was a half-second pause after the box closes. The code
  reviewer showed that counting the clicks of one gesture is safer, because it never blocks a quick deliberate
  click, so I took the reviewer's option over my own. Moving the buttons apart would change the approved design.
  The fix itself caused two new slips (the Add person one above, and a double click on a name under an item
  whose price had a red error removed the item). The full re-check caught both before you saw them, and both
  are fixed.

### A tap just below a wrong price was lost
- **The problem.** When you left a price box holding a wrong amount by tapping just below it, the red error
  line appeared at once and pushed the page down, so the tap missed.
- **What I did.** When you leave the box with a tap, the red line appears after you lift your finger.
- **Why this and not the others.** Showing errors later would break the rule that an error shows when you leave
  the box. Leaving room for the error at all times would change the approved design.

### A name could fake an extra line in the copied summary
- **The problem.** Hidden line-break, control or text-direction characters in a name could make the pasted
  summary show a fake extra line, such as a false "Adds up to", or reorder one person's share.
- **What I did.** The copied summary prints those characters as a space. The screen shows the name as typed.
- **Why this and not the others.** Refusing such names when you type them changes which names the app accepts,
  a product rule that is yours to set. Cleaning only the copied text closes the problem without touching what
  you typed.

### Damaged saved bill
- **The problem.** If what the browser saved cannot be read, the page could fail or show a wrong bill.
- **What I did.** The page treats the saved text as untrusted. Anything it cannot read starts a new bill and
  shows the note your brainstorm asked for, which you can dismiss.
- **Why this and not the others.** Repairing a half-read bill could show amounts you never typed.

### Your clipboard during planning
- **The problem.** On 2026-10-08 a planning check wrote "a" and then "b" to this computer's real clipboard,
  replacing what you had copied. That content could not be brought back.
- **What I did.** A standing rule: tests never touch the system clipboard, not even to save and restore it.
  They replace the copy function inside the test page instead. Every check since has followed it.
- **Why this and not the others.** Saving and restoring the clipboard still reads your data and can still lose
  it if a run stops halfway.

### What gets published
- **The problem.** The project folder holds build records, screenshots with local paths, and deliberately broken
  copies of the code used to prove the tests catch mistakes. Publishing the whole folder would expose all of it.
- **What I did.** Only the page and its code (`index.html`, `src/` and an empty `.nojekyll`) are ever published.
- **Why this and not the others.** Publishing the folder as is would be simpler, but the records are for you and
  the repository, not for visitors to the app.

### The version number
- **The problem.** The run started as 0.1.0.
- **What I did.** Renamed it 1.0.0 after you said "Make sure both app reach a stable 1.0 version."
- **Why this and not the others.** It is your label to set. Nothing else changed with it.

---

## Residuals you should know about, that are not cases

- The amount rules (wrong amounts like `abc`, `0`, `12.345` or `100000` show "Enter an amount like 12.50" when you
  leave the box), the 12-person and 50-item limits, the 20 and 40 character name limits, blank and duplicate
  names, removing a person from every item, the blocked-clipboard message and the unreadable-bill note are not in
  your script. The review drive checked each of them (`docs/review/20261010-144746/`).
- Safari and Firefox are **NOT RUN**. Only Chromium was tested.
