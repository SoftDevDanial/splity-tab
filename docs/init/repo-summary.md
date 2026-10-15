# Repo summary, Danial's Splity Tab (the Split project)

Written at the v1.0.0 review on 2026-10-10 and brought up to v1.1.0 at its review on 2026-10-16, once the v1.1.0
build was judged ready for the owner's test. The folder and the module names still say "split". The app's name is
Danial's Splity Tab, and the header shows "Splity Tab".

## What it is
A bill splitter for one shared restaurant bill in Malaysia, on one web page, phone first. List 2 to 12 people, then
either type the subtotal for an even split or list the items and tap who had each one. The app adds service charge
and SST (10% and 6% by default, both editable), splits the total in whole sen so the splits always add back up to it,
and shows that check. When the total does not divide to the sen, a line says how many sen are left over, and the user
picks who pays them, Top of the list, One person, or At random with Pick again. Copy summary puts a plain-text summary
on the clipboard for the group chat. One draft is kept in the browser's `localStorage`, and a note says so when the
browser refuses to save. No account, no server, no network call, no dependencies, no build step.

The look is "Glass Console", a dark slate page with an indigo accent and one glass receipt card, picked by the owner
from five directions. On a phone People and Charges fold into one row each, the Total, Splits and Copy summary sit in
a strip at the bottom, and Splits opens the receipt in a sheet. From 1024 px the card sits beside the inputs and the
page does not scroll.

## Where things are
| Path | What it holds |
|---|---|
| `index.html` | the page shell, the icon sprite, the header mark and the three dialogs, with a strict Content Security Policy |
| `src/core/` | `split-core`: money parsing and formatting (`money.js`), the bill and its edits (`bill.js`, including `plainName` for names), the sen allocation (`allocate.js`), the result with the spare sen (`result.js`), the spare sen choices and draws (`spare.js`) and the copied text (`summary.js`). All pure, whole sen only, no random source of its own |
| `src/main.js` | boots the page, holds the bill, wires every gesture to a `split-core` edit, saves the draft and shows the save warning |
| `src/draft.js` | encodes, decodes and saves the draft (version 2, version 1 still read), treats stored text as untrusted |
| `src/errors.js` | when an inline error shows (on leaving a field, at once for a restored bad field) |
| `src/ui/` | one file per block (people, charges, the Split switch, subtotal, items, the receipt, the strip, the Splits sheet, the spare sen choice, sections, notes, the New bill dialog), plus `dom.js` and `repeat.js` with the repeat-press guard |
| `src/system.css`, `src/icon.svg` | the approved design's stylesheet, byte for byte, and the tab icon |
| `tests/` | Node unit tests (406) and Python Playwright browser tests (742 per engine, Chromium and WebKit), the fidelity runner and its seeds, the live gate, the clipboard stand-ins and the storage drivers |
| `docs/brainstorm/`, `docs/design/` | what was asked for (with the v1.1.0 delta) and the approved screens, 15 goldens (immutable outside the design phase) |
| `docs/modules/<module>/` | each module's spec, test contract, build notes, findings and evidence |
| `docs/v1.0.0/`, `docs/v1.1.0/` | each version's change ledger, every scope, decision, finding and fix, dated, with who decided. v1.0.0 also holds its UAT and `SEAL.md` |
| `docs/regression/`, `docs/review/` | the full re-checks and the stakeholder review drives |
| `docs/future/several-bills.md` | several bills at once, written up as a future design only |
| `docs/brand/` | the 1.0 logo, README badges and showcase image (they change to 1.1.0 at its seal) |
| `docs/progress/` | the run's state, its log, the handoffs and the process ledger |

## How to run and test it
Serve the folder (`python -m http.server 8000 --bind 127.0.0.1`) and open `http://127.0.0.1:8000/`. Unit tests
`node --test "tests/**/*.test.js"`, browser tests `python -m pytest tests/browser -q`, and the same in WebKit with
`--engine webkit`. `CLAUDE.md` and the README have the live gate and the pixel gate.

## What to know before changing it
- Money is whole sen everywhere, and only `src/core/` does money maths or draws a spare sen order. The UI formats with
  `split-core` and never rounds. It passes `Math.random` into the two core functions that draw, and nowhere else.
- Tests never touch the system clipboard. Every browser context loads `tests/browser/clipboard/recorder.js` or
  `reject.js`.
- `swallowRepeatClicks` in `src/ui/dom.js` and `isRepeatPress` in `src/ui/repeat.js` are deliberate. They stop the rest
  of a double click, a double tap (by time and place, 500 ms and 22 px) or a held key from landing on whatever moves
  under the pointer. Every regression of 1.0 came from that area, so change it with the repeat tests running in both
  engines.
- Names are kept plain. Control, line separator and bidi characters are removed at the name fields and when a draft is
  read, so the screen and the copied summary always say the same.
- WebKit is not Safari on an iPhone. Touch timing, the on-screen keyboard, VoiceOver and Safari's storage clean-up are
  checked by the owner on his phone.
- Only `index.html`, `src/` and a `.nojekyll` file are ever published.
