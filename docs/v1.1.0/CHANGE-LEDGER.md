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
| S7 | A livelier look, chosen from five directions | OPEN, round 1 done | USER | 1 (H-03) |
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
- **Ruling:** (pending)

---

## Field reference

| field | values | why |
|---|---|---|
| Status | `OPEN` · `SHIPPED` · `PARTIAL` · `NOT SHIPPED` | Whether the scope actually landed, as a field, not prose. |
| Tag | `IN SCOPE` · `ORCH` · `USER` · `DEFERRED` | Who owns the decision. `ORCH` items are reversible; the human may overturn any of them. |
| Proof | measurement + where it lives | Without it, "Solved" is a claim. |
| Who | `USER` · `ORCH` · `LANE` (+ which agent) · `IN SCOPE` | Who authored the change. |
| Outcome | `Solved` · `PARTIAL` · `DEFERRED → vX.Y.Z` · `WITHDRAWN` · `NEEDS THE HUMAN` | `WITHDRAWN` keeps a wrong finding visible, so the record never reads cleaner than reality. |
