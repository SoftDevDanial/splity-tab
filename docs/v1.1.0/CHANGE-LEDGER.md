# CHANGE LEDGER - v1.1.0

> The version's ONE attribution record and the human's only complete view of what happened.
> `STATE.md` is *situation*, handoffs are *resume points*, `findings/` are *evidence*. **None of them is
> the record.** `sdlc:uat` derives its cases from the **scope sections** below and its handover from
> **Needs the human**, so an item that is not here never reaches the human.
>
> **Rules (constitution, The CHANGE LEDGER):** updated at **every close** · corrections are **additive and
> dated**, never a silent rewrite · **staleness check** at every phase boundary.

**Version:** v1.1.0 · **Opened:** 2026-10-10 at the v1.0.0 seal, from the owner's UAT verdicts and rulings
(`docs/v1.0.0/user-test-2026-10-10/`, `docs/v1.0.0/SEAL.md`) · **Sealed:** not yet

> **This version is not delegated.** The owner asked to run the design phase with him. Decisions he makes are
> tagged USER, decisions the orchestrator makes in between are tagged ORCH and stay reversible.

## At a glance

| scope | title | status | tag | open items |
|---|---|---|---|---|
| S1 | The user decides who takes the spare sen | OPEN | USER | 0 |
| S2 | The by-item table fits a 360 px phone (H-02) | OPEN | USER | 0 |
| S3 | Holding Enter on Remove adds no blank item (SEC-04) | OPEN | USER | 0 |
| S4 | A bill that cannot be saved says so | OPEN | USER | 0 |
| S5 | Tested in Safari's engine too | OPEN | USER | 0 |
| S6 | The logo in the app | OPEN | USER | 0 |
| S7 | A livelier look, chosen from five directions | OPEN, G2 accepted, lock and goldens next | USER | 0 |
| S8 | A name that is free to use | OPEN, name ruled | USER | 0 |
| S9 | Several bills, written up as a future implementation (document only) | OPEN | USER | 0 |

---

## Scope sections

### S1 - The user decides who takes the spare sen
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** UAT-03 and UAT-F1, owner: "if it cannot be evenly split, the number in summary should show the extras then let the user decide to put to who or have a button or random split. So user can split manually or randomly or even have 1 person pay the extras". Approved for 1.1.0: "3.  Yes."

When a bill does not divide to the sen, the spare sen are shown, and the user can give them to one person, split them at random, or keep the top-of-the-list rule.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's UAT request | 2026-10-10 seal | Brainstorm delta, design, plan to follow | USER | Open |

### S2 - The by-item table fits a 360 px phone (H-02)
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** H-02, ruled by the owner on 2026-10-09 ("Fix the v1.0 limits"). Needs a design change to the table.

On a small phone the shares table never scrolls sideways, however big the bill.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Carried from v1.0.0 | 2026-10-10 seal | Design round, then plan | USER | Open |

### S3 - Holding Enter on Remove adds no blank item (SEC-04)
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** SEC-04 (v1.0.0 ledger row 48), D-01 item 1, owner: "i agree with all."

Holding Enter down on an item's × removes that item and nothing else.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Carried from v1.0.0. Fix in hand from the security re-check: a capture keydown listener in swallowRepeatClicks that cancels event.repeat | 2026-10-10 seal | Plan, then build | USER | Open |

### S4 - A bill that cannot be saved says so
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** D-01 item 2, owner: "i agree with all." (move into 1.1.0)

If the browser blocks or fills its storage, the page tells the user the bill is not being saved on this device.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Carried from v1.0.0 (accepted limit) | 2026-10-10 seal | Copy and state in the design round, then plan | USER | Open |

### S5 - Tested in Safari's engine too
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** D-01 item 7, owner: "i agree with all." (move into 1.1.0)

The browser tests and the gates also run in WebKit, the engine of Safari on iPhone, since the app is used on a phone at the table.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Carried from v1.0.0 (only Chromium was tested) | 2026-10-10 seal | Plan, then build | USER | Open |

### S6 - The logo in the app
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** owner: "Wheres the logo. I dont see it being used for both"

The logo shows in the app's header and as the browser tab icon.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's comment. Corrects the v1.0.0 reading "no header mark in the app" | 2026-10-10 seal | Design round | USER | Open |

### S7 - A livelier look, chosen from five directions
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** owner: "Both designs are great but is just that its so dull. Need to spice it up so it looks nicer" and "Propose 5 designs for both app. Doesnt need to be working, i just want the design part." Then: "as long as i can see the design. Including popups and modals or anything that requires a button click"

A new look the owner picks from five clickable static directions, then a new golden set.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's comment | 2026-10-10 seal | Design round with him | USER | Open |
| 2 | Round 1, five clickable directions on the key screen with every popup and state reachable | 2026-10-10 design | A Night Console `da8a354`, B Glass Receipt `755447a`, C Daylight Instrument `9ce713c`, D Share Orbit `efb824b`, E Command Line `ceaaf87`, each by its own designer agent with render checks at 390, 360 and 1280 px (0 console errors, no sideways scroll at 360, every inventory figure asserted). round-1/compare.html `d1deb01` with the orchestrator's pick D, runner-up A. Prototype-only flags on the page: A, B and C draw "At random" from a fixed seed (C also steers its first draw), B's Prototype states tab covers a name field on a phone. Not in the brief: D's "+1 sen" label, E's bare figures in the Items and Charges columns | ORCH (designer agents) | Waiting for the owner's pick (H-03) |
| 3 | Owner's pick (H-03 ruling): a mix, D Share Orbit's layout in A Night Console's colours, with five changes | 2026-10-10 21:43 design | Round 2 brief `round-2/BRIEF.md`, one new direction F "Orbit Console". His words and the readings in H-03 | USER, ORCH on the readings | Round 2 next |
| 4 | F "Orbit Console" built on D (69 of 69 checks, `b1587bf`), then the owner corrected the base: B Glass Receipt, not D (H-03 correction 22:50). The orchestrator had mapped his comments to D, the direction it recommended | 2026-10-10 22:50 design | F kept as a record, not shown as his pick. Brief `round-2/BRIEF-G.md` for one new direction G "Glass Console" on B | ORCH (the misread), USER (the correction) | WITHDRAWN (F). G next |
| 5 | Direction G "Glass Console" built by one designer agent from `round-2/BRIEF-G.md`: B's layout and glass card in A's slate and indigo, no glow, Copy summary solid indigo (5.24 to 1), People, Charges, Split, Items, item list in its own frame, phone inputs first with a pinned strip and a Shares sheet, "1 sen left over" kept. Verified on disk: designer's check 0 fails, the orchestrator's own spot check at 1280, 390 and 360 (block order, no page scroll at 1280 x 800 in K1, K2, S7 and W2, the W2 list scrolling in its 291 px frame, strip pinned, Shares sheet and Esc, copy to the stand-in only, shares adding up to RM 69.26 in whole sen, 0 console errors, 0 network, no radial glow in the source). One catch, flagged: on a phone "1 sen left over" is only in the Shares sheet. round-2/compare.html (round 1 B and A beside G, every reading flagged) | 2026-10-10 23:55 design | `2d5f222` G, compare page this commit. Orchestrator's pick G | ORCH (designer agent) | Owner accepted G, row 6 |
| 6 | Owner's review of G (H-03 round 2 ruling): "i like it", with one phone change (People and Charges collapse into sections, Items gets the room) and one rename ("Shares" becomes "Splits"). "1 sen left over" stays in the sheet as built | 2026-10-11 00:01 design | `round-2/BRIEF-G2.md`, revision G2 "Glass Console, revised" built from G by one designer agent | USER, ORCH on the readings | G2 next |
| 7 | Revision G2 built by one designer agent: on the phone People and Charges fold into one row each with a summary (People open on a new bill, a row with an error opens, a folded one says "Check"), the desktop exactly G, "Splits" for "Shares" everywhere. The first item field at 390 moves from 599 to 335 px, the Subtotal from 564 to 300 px. Verified on disk: designer's 501 of 501, the orchestrator's own spot check at 1280, 390 and 360 (desktop positions equal to G, no page scroll, toggles by tap, Enter and Space, summaries, S1, the rate error, the rename, the sen line in the sheet, splits add up, 0 console errors, 0 network). New behaviour flagged: G2 adds the 1.0 rate error copy, which G lacked. Open for him: S6 opening People like S1 | 2026-10-11 00:50 design | `083c658` G2, compare page updated this commit. Orchestrator's pick G2 | ORCH (designer agent) | Owner reviewed, row 8 |
| 8 | Owner's review of G2: first "seems like nothing changed. Are you sure you gave the right one" and "The mobile version of splity didnt change shares to splits". Cause: at the Browser pane's 961 px the compare page stacked one column and its first phone frame was G, and the lower phone section still showed G labelled "my pick". G2 itself was right (checked in the page's own frame at 390: folded rows, "Splits"). Fixed by the orchestrator: compare.html puts G2 first, labels G "Before your phone note", the lower pick frame is G2, a reload hint added. Then: "Nevermind. I saw it. It looks good now." and "Both looks good. We can procceed as usual" | 2026-10-11 00:58 design | compare.html, this commit | USER, ORCH (the page fix) | G2 accepted. Design proceeds to step 5 |

### S8 - A name that is free to use
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** owner: "for split, change it to SplitIO. Also, if both names cant be used, then add Danials [app name] Or if theres a better way to make it uniquely to me."

A product name no other app or known software company uses, shown in the new wordmark and the logo lockup.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Name check: "SplitIO" is Split.io, the feature-flag company Harness bought in 2024. Not usable | 2026-10-10 seal | His fallback applies. Chosen with him in the design round | USER | Open |

### S9 - Several bills, written up as a future implementation (document only)
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** D-01 item 4, owner: "If they want to add a different bill, we can have this as future implementation. I think its a good thing to have this as future implementation and put this as a doc only so that we can showcase it. So we dont need to implement this but put this like a future implementation kind of doc."

A short document that describes how several bills could work later. No code.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's ruling | 2026-10-10 seal | Written in the brainstorm delta | USER | Open |

---

## Off-scope and new

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | The UAT script layout, owner: "i want steps and expected result in a table... Bigger fonts for UAT number... include some sort of verdict selection examples" | 2026-10-10 seal | Process, not app: the layout is designed in the same round as S7 and used for the 1.1.0 UAT | USER | Open |
| 2 | Owner's answers before the design round (2026-10-10 16:42): "1. Decide for me. Lets have a starting ground. We can work from there" "2. I like those futuristic type of apps or websites. Like discord and stuff like that. Futuristic but minimal." "3. I like that a lot." "4. Lets go with that first." "5. Danial's Splity Tab and Danial's Streaky Habit. Logo wise, dont need danial or even initial D. Danial is just to make it unique." "6. Sure" | 2026-10-10 brainstorm | Name set (S8), feeling words and the five directions chosen by the orchestrator as the starting ground, the past-day reach and the spare-sen line approved, three UAT sheet layouts. Name check: no app named "Splity" or "Splity Tab" found (nearest "Splitly"), and the "Danial's" prefix keeps both names unique | USER | Ruled |
| 3 | Brainstorm delta for v1.1.0 | 2026-10-10 brainstorm | Appended to docs/brainstorm/brainstorm.md: the name, the new and changed capabilities, the rules (USER where he decided, ORCH where the orchestrator settled details so design can start), the grill log rows. One theme may now be dark. Still system fonts and no network | USER, ORCH | Written |
| 4 | Design brief for v1.1.0 with the five directions | 2026-10-10 design | docs/design-explore/v1.1.0/BRIEF.md: who, the key screen's job, feeling words, his words, constraints, the logo rule, the inventory with exact figures, the prototype rules, five direction theses | ORCH | Written, design round next |
| 5 | UAT sheet layout chosen (row 1). Three layouts shown (A Markdown tables, B test sheet, C run console). Owner 2026-10-10 18:31: "I like C the most but, there are some stuff that i like about B. 1. The verdict info section 2. The margins 3. The checkbox on the what you should see or results... Maybe instead of a checkbox, we do a tick or x... I dont think verdict Pass with note is needed. Pass, Fail, Blocked ( maybe can other stuff). Note will always be able to put." Then 18:35: "Verdicts can be added if you think theres more that can be added. Research on what people put besides these 3... The verdict info is the guide cards". Then 18:46: remove the step highlight, verdict table colouring consistent with the theme, no tick in Pass or x in Fail, say the next step is filled by the agent. Then 19:27: "Change "How to give a verdict" to Verdict guide. Change Hide the guide to Hide and when clicked to Show. Besides that i am happy with the design... change T and Y at the left to T and U. U stands for user" | 2026-10-10 design | docs/design-explore/v1.1.0/uat-sheet/c2.html "C revised": C's one case at a time with B's guide cards, margins and verdict table, a tick or cross on every expected line, verdicts PASS, FAIL and BLOCKED with a note on any, NOT RUN and RETEST as states the sheet sets (ORCH, from a survey of TestRail, Azure Test Plans, Zephyr Scale and Xray. Not applicable and Paused left out, because every case comes from a promise of the version and the sittings already cover a half-run case), "Results for the chat" to hand verdicts back. TEST-CASES.md stays the record. Commits 94bda22, da8a354, c4e37f2 and the 19:27 edit | USER | Ruled. Used for the 1.1.0 UAT of both apps |

---

## Needs the human

### H-01 - The name (S8)
- **What:** "SplitIO" is taken. His fallback is his own name with the app name ("Danial's Split") or another way to make it his.
- **Why an agent cannot decide it:** the name of his public showcase piece is his.
- **Options:** decided in the design round, beside the wordmark.
- **Ruling:** (pending)
- **Ruling, added 2026-10-10:** "Danial's Splity Tab and Danial's Streaky Habit. Logo wise, dont need danial or even initial D." (Off-scope row 2). The logo and header show "Splity Tab".

### H-03 - Which design direction (S7)
(H-02 is the v1.0.0 finding named in S2, so this item is H-03.)
- **What:** round 1 gave five directions (round-1/compare.html).
- **Why an agent cannot decide it:** the look is his pick.
- **Options:** pick one direction, ask for a mix (one new direction in round 2), or reject all. If D, keep or drop its "+1 sen" label, which the brief does not list.
- **Recommendation:** D Share Orbit (the ring makes "it adds up" visible, it shows the spare sen, answer first on a phone, the most memorable desktop), keep "+1 sen". Runner-up A Night Console, which pairs with the Streaks pick if he wants both apps as one family.
- **Ruling, 2026-10-10 21:43 (owner's words):** "1. Color i like Night console, remove neon backgrounds. 2. For desktop version, Move charges above Split 3. By items, make it a a scrollable frame or something. I dont want the whole page to scroll, it should be scrolled within a div instead. 4. For mobile, make the receipt collapsed or maybe display on button press or tab change. Make it easier to input stuff. Right now, its pushed down. 5. Overall, looks good and i love the sen left over"
- **Clarified, 2026-10-10 21:49 (his answer):** "neon backgrounds" means **bright filled buttons**. The selected Even/By item, the spare-sen choice and Copy summary lose their solid bright fill and become an outline or a dark tint. Night Console's slate panes and indigo accent stay, and the person colours stay so the ring still matches the rows.
- **Readings (ORCH, reversible, flagged on the round 2 page):** (a) The comments are about D's layout (the ring, the right input column with Charges at its foot, the receipt above the inputs on a phone), so this is a mix, one new direction in round 2. (b) "Split" in point 2 is the Even/By item switch, so Charges moves to the top of the input column, above it. (c) Point 3 is the item list in By item mode, which scrolls inside its own frame so the page itself does not scroll at 1280 x 800. (d) Point 4 is built as a pinned bar on the phone with the Total, a Shares button that opens the receipt (ring, shares, bill) as a sheet, and Copy summary, so the inputs come first. (e) Point 5 keeps "+1 sen" beside a share and the "1 sen left over" line, which answers this item's second question.
- **Correction, 2026-10-10 22:50 (owner's words):** "My mistake. What i meant for splity is color night console but use glass receipt". So the base is **B Glass Receipt**, not D. The 21:49 clarification and readings (a) to (e) above were made against D and are superseded.
- **Clarified again, 2026-10-10 22:52 (his answer):** "neon backgrounds" means **only the glow**, the light pools behind the receipt. Copy summary keeps a solid fill, in indigo.
- **New readings (ORCH, reversible, flagged on the round 2 page):** (a) B's layout and its one glass receipt card, in Night Console's slate and indigo. (b) "Split" is B's Split section (the Even/By item switch), so on desktop the input column runs People, Charges, Split, Items. (c) The item list scrolls inside its own frame and the page does not scroll at 1280 x 800. (d) On a phone the inputs come first and the receipt opens from a pinned bar (Total, Shares, Copy summary) as a sheet. (e) "the sen left over" is B's "1 sen left over" line, which stays. D's "+1 sen" label is not carried over, so this item's second question lapses.
- **Round 2 recommendation (ORCH, 2026-10-10 23:55):** take G forward (`round-2/compare.html`). Put to him there: show "1 sen left over" on the phone strip as well (designer's suggestion, orchestrator recommends yes), and the designer readings (the light under the Total and the glow on the figure also removed, the foil as one indigo sheen, Add person and Add item in their heading rows, the charge hint beside the fields on a desktop, about two and a half items in view at 1280 x 800, Start new bill in A's red, tablets on the phone layout).
- **Round 2 ruling, 2026-10-11 00:01 (owner's words, after seeing G):** "For Splity, i like it. Small thing is the mobile. For people and charges, it should be collapsed from a section. These will not change often. The one that is heavily changed or added is the items"
- **His answer on the phone sen line (00:03):** "I dont understand. 1 sen left over is in shares ( oh yea, i dont like this, change this to Splits) which is at the bottom above copy summary on the left split selection. That looks good already". So the line stays in the sheet as built.
- **Readings (ORCH, reversible, flagged on the next compare page):** (f) The collapse is for the phone layout only (below 1024 px). The desktop stays as G, since he named the phone and it already fits 1280 x 800. (g) Both sections start collapsed with a one-line summary (the names, the two rates). On a new bill People starts open, because its names are placeholders. A section with an error opens, and a collapsed one shows that it holds an error. The Split switch, Items and the Subtotal never collapse. (h) "Splits" replaces the word "Shares" everywhere the person reads it (the bar button, the sheet's name, the receipt heading, S1's sentence), on every width. The "Split" heading of the Even and By item switch stays.
- **Final ruling, 2026-10-11 00:58 (owner's words):** "Nevermind. I saw it. It looks good now." then "Both looks good. We can procceed as usual". **G2 is the direction.** The S6 question (open People on a saved bill that could not be read) got no separate answer, so the orchestrator's recommendation applies (ORCH, reversible, People opens on S6 like S1), carried into the compose step.

---

## Field reference

| field | values | why |
|---|---|---|
| Status | `OPEN` · `SHIPPED` · `PARTIAL` · `NOT SHIPPED` | Whether the scope actually landed, as a field, not prose. |
| Tag | `IN SCOPE` · `ORCH` · `USER` · `DEFERRED` | Who owns the decision. `ORCH` items are reversible; the human may overturn any of them. |
| Proof | measurement + where it lives | Without it, "Solved" is a claim. |
| Who | `USER` · `ORCH` · `LANE` (+ which agent) · `IN SCOPE` | Who authored the change. |
| Outcome | `Solved` · `PARTIAL` · `DEFERRED → vX.Y.Z` · `WITHDRAWN` · `NEEDS THE HUMAN` | `WITHDRAWN` keeps a wrong finding visible, so the record never reads cleaner than reality. |
