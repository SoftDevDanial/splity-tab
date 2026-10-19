# Split brand

Made on 2026-10-10 at the owner's request ("Add a simple but decent looking logo for the examples apps", and "logo include in
their respective projects as well where needed"). Designed by the `logo-designer` agent, art directed by the orchestrator,
passed by the `logo-qa` agent. Drawn from the app's own tokens in `docs/design/system.md`.

## The mark
**"The shares add back to the total."** An equals sign whose top bar is cut once, two to one, its outer ends flush with the
whole bar below. It is the app's own idea, a calculator that shows its working: the shares above, the Total below, square
ink rules, no green. On a 48 grid: bars 9 thick, shares 24 and 12, cut 6, rows 15 apart. The favicon is the same geometry
divided by 3, pale bars on a square ink tile, every edge on a whole pixel at 16 and 32 px. Next to the word it also reads as
the spreadsheet formula "=Split", which is the same idea.

| Round | What happened |
|---|---|
| 1 | Tested against a plain equals sign, not-equal, the I Ching and Korean flag lines, a hamburger menu, a text-align icon, Morse code and a loading bar |
| QA | **PASS, 21 of 24**, no gate failed. Ownability and distinctiveness 1 each, because an equals sign is a typeable glyph. The cut is what makes it Split's |
| Fixes | The orchestrator locked the wordmark width (`textLength`, so it cannot clip on Linux fonts), corrected the description's arithmetic, the sheet's caption contrast and one WCAG comment |

## Files
| File | Use |
|---|---|
| `mark.svg`, `mark-black.svg` | the symbol in ink `#141917` |
| `mark-white.svg` | the symbol in `#F3F5F4` for dark grounds |
| `lockup-light.svg`, `lockup-dark.svg` | symbol and word for light pages and for dark pages (`#0d1117`, 17.3:1) |
| `favicon.svg` | the app's favicon from v1.1.0 (copy it into `src/` when it ships, the CSP already allows `img-src 'self'`) |
| `sheet.html` | the brand sheet |
| `badges/` | static README badges, each a fact at a named version, never a live status |
| `screens/showcase.png` | the README image, two real captures from the pixel gate |

## Rules
- The cut is the only thing that makes the mark Split's. Never centre it (that gives the I Ching broken line), never close
  it (that gives a stock "="), never make it narrower than 6 on the 48 grid. The short share is never shorter than 1.33 times
  its height.
- Use the lockup, not the bare mark, in the README and the showcase. The bare mark is for the favicon and an avatar only.
- Never put the bare mark alone in the app bar. Two bars at the top left read as a menu.
- The word "Split" is live text in the app's own system font stack, so it looks a little different on each platform. Never
  trace a system font into paths (that copies licensed outlines).
- Never claim the shares' ink adds up to the bar's ink (36 against 42). The idea is that the shares span the whole.
- A pale equals sign on a solid square is close to another organisation's well-known mark at favicon size. The cut is the
  difference, which is one more reason it must never close.
- The favicon goes into the app in v1.1.0, through the design phase. The v1.0 screens and goldens do not change.

## Use of the name and logo
The names "Danial's Splity Tab" and "Splity Tab" and the logo in every file here, and in `src/icon.svg`, are not covered by the MIT licence in `LICENSE`. They stay all rights reserved. A copy or fork of the code uses its own name and logo.
