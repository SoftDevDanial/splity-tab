# Design brief: Danial's Splity Tab, v1.1.0

**Phase:** design (sdlc:design, steps 1 to 3) · **Date:** 2026-10-10 · **Run with the owner** (not delegated)
**Sources:** `docs/brainstorm/brainstorm.md` (1.0 rules plus the v1.1.0 delta), `docs/v1.1.0/CHANGE-LEDGER.md`, the 1.0
goldens in `docs/design/` (for content and rules only, not for looks)

## Who uses it
The person who paid a restaurant bill in Malaysia, at the table, phone in one hand and the receipt in the other.
Others are waiting. They type a few numbers, then read out or paste the shares into the group chat.

## The one job of the key screen
Turn a receipt into shares everyone trusts, at a glance, and show that they add back up to the total.

## Three feeling words
**Sharp, quick, social.** (Chosen by the orchestrator, the owner said "Decide for me".)

## What the owner asked for
- "Futuristic but minimal", "Like discord and stuff like that."
- 1.0 was "great" but "so dull. Need to spice it up so it looks nicer."
- "Doesnt need to be functionable, as long as i can see the design. Including popups and modals or anything that
  requires a button click." Quick prototypes, design first. Working is fine if it is faster.

## Hard constraints
- **Platform:** a static web page. Phone first at 390 x 844, must work from 360 px, deliberate at 1280 px.
- **One theme per direction, light or dark.** No theme switcher (non-goal).
- **No network.** No web fonts, no CDN, no remote images. System font stacks only (for example
  `ui-sans-serif, system-ui, "Segoe UI", Roboto, sans-serif` and `ui-monospace, "Cascadia Mono", Consolas, monospace`).
  Icons only from Phosphor (MIT), inlined as SVG paths. The 1.0 app already inlines Phosphor's x, plus, copy and
  check paths in `src/ui/icons.js`.
- **Accessibility:** WCAG AA text contrast (record the ratio of body text and the accent on its background), a visible
  keyboard focus, touch targets of at least 44 px, reduced motion respected.
- **Money** as `RM 38.87` with tabular figures. Real copy from the brainstorm. People Aisyah, Ben and Chen.
- **Avoid the AI defaults:** a purple-to-blue gradient glow, acid green on black, cream paper with a serif and a
  terracotta accent, glass on every card.

## Logo
The mark stays: `docs/brand/mark.svg`, an equals sign whose top bar is cut once, two to one. It may take the
direction's colours. The wordmark is live text "Splity Tab" set in the direction's type. No "Danial", no "D". The
page title is "Danial's Splity Tab". Never centre or close the cut (`docs/brand/BRAND.md`).

## Inventory (what every direction shows)
| ID | Screen, popup or state | Traces to | Content |
|---|---|---|---|
| K1 | **Bill screen, by item, with shares (KEY SCREEN)** | C1 C3 C4 C5 C6 C9 | Aisyah, Ben, Chen. Nasi lemak ayam RM 15.90 (Aisyah), Char kuey teow RM 13.50 (Ben), Mee goreng mamak RM 12.00 (Chen), Satay, 10 sticks RM 18.00 (Aisyah and Chen). Subtotal RM 59.40, service 10% RM 5.94 (10% of RM 59.40), SST 6% RM 3.92 (6% of RM 65.34), total RM 69.26. Shares Aisyah RM 24.90 + RM 4.14 = RM 29.04, Ben RM 13.50 + RM 2.24 = RM 15.74, Chen RM 21.00 + RM 3.48 = RM 24.48. Adds up to RM 59.40, RM 9.86, RM 69.26. "1 sen left over" with Top of the list chosen |
| K2 | Bill screen, even split | C2 C9 | Subtotal RM 100.00, service RM 10.00, SST RM 6.60, total RM 116.60. Shares RM 38.87, RM 38.87, RM 38.86. "2 sen left over", Top of the list |
| P1 | Spare sen choice | C9 | The three choices. **One person** opens a picker of the people. **At random** shows "Pick again". The shares change to match (for K2: one person Ben gives 38.86, 38.88, 38.86, and random gives two different people one sen each) |
| M1 | New bill dialog | C8 | "Start a new bill?" "This clears the people, items and amounts." Buttons "Start new bill" and "Cancel" |
| S1 | First open | C1 C2 | "Person 1", "Person 2", Even, empty Subtotal, 10% and 6%, "Enter the subtotal to see the shares." |
| S2 | Amount error | C2 | "Enter an amount like 12.50" under the field |
| S3 | Items still need a person | C3 | "1 item still needs a person. Tap who had it to see the shares." |
| S4 | Copy status | C6 | "Summary copied" and "Could not copy. Your browser blocked the clipboard." |
| S5 | Save warning | C10 | "This bill is not being saved on this device. It will be lost when you close this tab." |
| S6 | Saved bill could not be read | C7 | "Your saved bill could not be read, so a new one was started." with a dismiss button |
| S7 | 12 people reached | C1 | Add person disabled |
| W1 | 360 px by-item table | C3 | Fits a 360 px screen with no sideways scroll, also when an amount reaches RM 1,193.87 |

**Key screen:** K1.

## Prototype rules
- One self-contained HTML file per direction: inline CSS and JS, colours as CSS custom properties, no network.
- Clickable through the design's own controls: the mode switch, the spare-sen choices and picker, New bill and its
  buttons, Esc and the backdrop to close, Copy summary showing its status.
- States with no natural trigger (S1 to S7, W1) sit behind a small fixed bar labelled "Prototype states", clearly not
  part of the design.
- Figures may be precomputed. They must match the inventory exactly.

## The five directions (the starting ground, chosen by the orchestrator)
| Dir | Name | Thesis | Theme and accent |
|---|---|---|---|
| A | Night Console | A chat-app-native dark console: the people read like a member list, the shares like messages from a bot you trust | Dark, layered slate surfaces, one indigo accent |
| B | Glass Receipt | The receipt becomes one floating holographic card, the only glass on the page, with the total softly lit | Dark navy field, cyan hairlines, monospace figures |
| C | Daylight Instrument | Futuristic in daylight: a precise instrument panel with oversized tabular numerals and crisp 1 px rules | Light, cool white, electric cobalt |
| D | Share Orbit | The split is a shape: the shares form a segmented ring around the total, and each person owns a segment | Dark charcoal, one warm coral accent, a muted colour per person |
| E | Command Line | Keyboard-first and monospaced, columns aligned like a terminal, the add-item row like a command palette | Light pale graphite, ink text, one signal orange |

Each direction is a genuinely different bet, not a colour swap. Output: `round-1/<a|b|c|d|e>.html`, then
`round-1/compare.html` by the orchestrator, with the orchestrator's recommendation.
