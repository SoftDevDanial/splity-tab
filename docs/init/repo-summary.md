# Repo summary: Split

Written at review on 2026-10-10, once the v1.0.0 build was approved for the owner's test.

## What it is
A bill splitter for one shared restaurant bill in Malaysia, on one web page. List 2 to 12 people, then either type
the subtotal for an even split or list the items and tap who had each one. The app adds service charge and SST
(10% and 6% by default, both editable), splits the total in whole cents so the shares always add back up to it,
shows that check, copies a plain-text summary for the group chat and keeps one draft in the browser's
`localStorage`. No account, no server, no network call, no dependencies, no build step.

## Where things are
| Path | What it holds |
|---|---|
| `index.html` | the page and its dialog, with a strict Content Security Policy |
| `src/core/` | `split-core`: money parsing and formatting (`money.js`), the bill and its edits (`bill.js`), the cent allocation (`allocate.js`), the result (`result.js`) and the copied text (`summary.js`), all pure, whole cents only |
| `src/main.js` | boots the page, holds the bill, wires every gesture to a `split-core` edit, saves the draft |
| `src/draft.js` | encodes, decodes and saves the draft, treats stored text as untrusted |
| `src/errors.js` | when an inline error shows (on leaving a field, at once for a restored bad field) |
| `src/ui/` | one file per block (people, mode, subtotal, items, charges, bill panel, note, dialog), plus `dom.js` with the repeat-press guard |
| `src/system.css` | the approved design's stylesheet plus one marked rule |
| `tests/` | Node unit tests (275) and Python Playwright browser tests (427), the live gate script and the clipboard stand-ins |
| `docs/brainstorm/`, `docs/design/` | what was asked for and the approved screens (immutable outside the design phase) |
| `docs/modules/<module>/` | each module's spec, test contract, build notes, findings and evidence |
| `docs/v1.0.0/CHANGE-LEDGER.md` | every scope, decision, finding and fix of this version, dated, with who decided |
| `docs/regression/`, `docs/review/` | the last full re-check and the stakeholder review drive |
| `docs/brand/` | the logo, README badges and showcase image |
| `docs/progress/` | the run's state, its log and the process ledger |

## How to run and test it
Serve the folder (`python -m http.server 8000 --bind 127.0.0.1`) and open it. Unit tests `node --test "tests/**/*.test.js"`,
browser tests `python -m pytest tests/browser -q`. The README has the gates.

## What to know before changing it
- Money is whole cents everywhere, and only `src/core/` does money maths. The UI formats with `split-core` and never rounds.
- Tests never touch the system clipboard. Every browser context loads `tests/browser/clipboard/recorder.js` or `reject.js` (CG-7).
- `swallowRepeatClicks` in `src/ui/dom.js` is deliberate: it stops the rest of a double click landing on whatever slides under the pointer. Two regressions came from changing it, so change it with the right-edge and chip tests running.
- Only `index.html`, `src/` and a `.nojekyll` file are ever published.
- v1.1.0 holds the two accepted limits: the by-item table at 360 px (H-02, a design change) and a held Enter on Remove (SEC-04).
