# Round 2 brief, direction G: Danial's Splity Tab, v1.1.0

**Phase:** design (sdlc:design step 4) · **Date:** 2026-10-10 · **Ledger:** S7 row 4, H-03 correction
**Supersedes `BRIEF.md` for this app.** `BRIEF.md` mapped the owner's comments onto D Share Orbit, which was the
orchestrator's misread. F (`f.html`) was built from it and is kept only as a record. The round 1 brief
(`../BRIEF.md`) still applies: who, the key screen's job, hard constraints, logo, the whole inventory with its
exact figures.

## The owner's words
21:43: "1. Color i like Night console, remove neon backgrounds. 2. For desktop version, Move charges above Split
3. By items, make it a a scrollable frame or something. I dont want the whole page to scroll, it should be
scrolled within a div instead. 4. For mobile, make the receipt collapsed or maybe display on button press or tab
change. Make it easier to input stuff. Right now, its pushed down. 5. Overall, looks good and i love the sen left
over"

22:50: "My mistake. What i meant for splity is color night console but use glass receipt"

22:52, clarified: "neon backgrounds" means **only the glow** (the light pools behind the receipt). Copy summary keeps
a solid fill, in indigo.

## The direction: G "Glass Console"
**B Glass Receipt's layout and its one glass receipt card, in A Night Console's colours, with no glow.**

| Take | From | What |
|---|---|---|
| Layout and interactions | `round-1/b.html`, `b.md` | The one glass receipt card (the lit Total, Subtotal, Service, SST, the dashed rule, Shares with "items + charges", Adds up to, "1 sen left over", the spare-sen dropdown, Copy summary), the input column (People in two columns, the Split switch, Items with person chips, Charges), the picker, New bill, every state |
| Colours | `round-1/a.md` tokens, `a.html` | The slate layers (`--l0` to `--l5`, `--field`), text and muted text, control borders, indigo (`--accent` #5059DA, `--accent-ink` #A3AAFF), error and danger. The glass card becomes slate glass with indigo hairlines instead of navy with cyan |
| Mechanics you may reuse | `round-2/f.html` (F, built for the wrong base) | The item scroll frame, the phone pinned bar and Shares sheet, the live share computation in whole cents, the clipboard stand-in in its check script. Reuse the code, not the look |

## The five changes
1. **Night Console colours, no glow.** Remove every light pool and radial glow behind the receipt and on the page
   background. The glass card stays (it is the direction's one material). **Copy summary keeps a solid fill, in
   indigo**, with AA text on it. Other selected states may follow B's treatment, retinted to indigo.
2. **Desktop: Charges moves above Split.** The input column runs People, Charges, Split (the Even/By item switch),
   Items. (ORCH reading: "Split" is B's own section heading.)
3. **By item: the item list scrolls inside its own frame. The page does not scroll at 1280 x 800** in K1, K2, S7
   (12 people) or W2 (long bill). The frame shows that it scrolls.
4. **Phone: inputs come first.** The receipt no longer sits above the inputs. A bar pinned to the bottom carries the
   Total, a **Shares** button that opens the receipt card as a bottom sheet (Esc, backdrop and Close shut it), and
   Copy summary. The input order on the phone matches the desktop. (ORCH reading of "collapsed, button press or tab
   change". Flagged.)
5. **Keep "1 sen left over".** D's "+1 sen" label beside a share is not part of B and is not added. (Flagged.)

## Inventory for round 2
Everything in the round 1 inventory (K1, K2, P1, M1, S1 to S7, W1) with the exact figures, plus P2 **Shares sheet**
(phone) and W2 **Long bill** (prototype only, ten items, computed live, behind Prototype states).

## Prototype rules
- One self-contained file `round-2/g.html`, inline CSS and JS, colours as custom properties, no network.
- Every popup and sheet opens from the design's own controls. The "Prototype states" tab never covers content at
  390, 360 or 1280 px (round 1 flag: B's tab covered a name field on a phone), sits under any open popup's
  backdrop, and never overlaps the pinned bar.
- "At random" is a real random pick, not a fixed seed (round 1 flag: B used a seed).

## Output
`round-2/g.html`, `round-2/g.md` (what you took from where, every reading you made, contrast table, suggestions not
built), render checks in `round-2/checks/g/`.
