# Direction E, Command Line

**File.** `e.html` (one self-contained page, no network). **Checks.** `checks/e/check_e.py` and its screenshots.

## Thesis
A keyboard tool for splitting a bill. Monospaced columns line up like terminal output, every action shows its key, and the items list is one command palette with a prompt row and an Enter key at its foot.

**Design read.** A single-purpose web app for the person who paid, seen by visitors, in a calm developer-tool language (command palette, keycaps, aligned mono columns), built with native CSS and system font stacks.
**Dials.** Variance 4 (columns must align), motion 3 (feedback only), density 6.

**What it bets on.** That "futuristic but minimal" can be read as precise and keyboard-first rather than dark and glowing. It is the only light, warm-accent direction and the only one where the input itself (the palette) is the memorable object.
**What it costs.** It is not "Discord" in mood. Light pale graphite is calmer than the dark directions, and the key hints add visual detail a phone user never presses. The shares sit below the inputs on a phone (command first, output under it), so a person scrolls to reach them.

## Tokens
| Role | Value | Use |
|---|---|---|
| Page | `#E7E9EC` | pale graphite ground |
| Surface | `#F6F7F8` | output pane, notes, dialogs |
| Field | `#FCFCFD` | palette, mode track, keycaps |
| Ink | `#16181D` | text, Total bar, Copy summary, chosen chips |
| Ink 2 | `#4A505A` | line numbers, units, working lines, hints |
| Signal | `#FF5B1A` | fill only (the Add item key, the wordmark cursor), always with ink text |
| Signal ink | `#A93700` | the prompt, the check in "Adds up to", the focus ring, the live palette edge |
| Error | `#B0153F` | inline errors only |

Orange means "live". It marks the cursor, the prompt, the Enter key and the proof, and nothing else. Type is the system mono stack for every figure, label and name, and the system sans for sentences (notes, messages, hints, dialog body). Radius rule is keycaps 4, controls 6, containers 10.

## How each inventory row is reached
| ID | Reached by |
|---|---|
| K1 | Default view |
| K2 | Mode switch "Even" (key E). The subtotal keeps 100.00 |
| P1 | Spare sen button on the "sen left over" line (key S). A palette opens (bottom sheet on a phone). Keys 1 to 3 or arrows and Enter. "One person" opens the people picker inside the same palette (Backspace goes back). "At random" shows "Pick again" (key R). Esc, the Esc key cap and the backdrop close it |
| M1 | "New bill" in the header (key N). Focus starts on Cancel. Esc and the backdrop close it. "Start new bill" gives S1 |
| S1 | Start new bill, or Prototype states |
| S2 | Type 0 in the subtotal and leave it, or an amount like 3.205 in the palette and press Enter. Also Prototype states |
| S3 | Add an item from the palette (it has nobody yet), or Prototype states |
| S4 | "Copy summary" (key C) shows "Summary copied" without touching the clipboard. The failure line is in Prototype states |
| S5, S6, S7, W1 | Prototype states (the striped tab on the left edge) |

## Decisions the owner may overturn
- **Bare figures in the Items and Charges columns.** The Share column and every Bill summary figure show "RM". The two working columns sit under their heads without it, the way terminal tables carry the unit once. This is what lets W1 fit at 360 px with "Adds up to" on one line.
- **The people picker shows each current share.** It explains why a person with RM 0.00 cannot be chosen (only shares above zero may take the spare sen).
- **W1 needs one more item to reach RM 1,193.87.** I used "Lobster set" RM 964.50 shared by all three, which gives a subtotal of RM 1,023.90 and a total of RM 1,193.87.
- **Blocked messages and rate errors** reuse the 1.0 copy ("Give every item a price to see the shares.", "Enter a rate from 0 to 30").
- **Esc inside a text field leaves the field**, so the single-key commands work again. Single keys never fire while typing.
- **The palette uses `:has()`** to light its edge only when the prompt row has focus (Chromium 105, Safari 15.4, Firefox 121).

## Check results (python -B checks/e/check_e.py)
- Every inventory figure matches (K1 rows and check row, K1 one person Ben 29.03 and 15.75, K2 38.87 38.87 38.86, K2 one person Ben 38.86 38.88 38.86, random gives two different people one sen each and 30 draws gave all 3 possible outcomes).
- Console and page errors 0. Network requests 0.
- No sideways scroll and no element past the edge at 360 px for K1, K2, K2 at random, W1, S2, S5 and S7.
- Keyboard. Tab reaches New bill at stop 1 and the spare sen control at stop 39. Enter opens P1, arrows and Enter pick One person, key 2 picks Ben. Keys S, N, E, I and / all work. Esc closes P1 and M1.
- Contrast. Ink on page 14.6, ink on surface 16.56, ink 2 on page 6.68, signal ink on page 5.34, signal ink on surface 6.05, ink on the signal key 5.72, on-ink on ink 16.28, error on page 5.71, control underline 3.45, focus ring on hover 4.86.
- Touch targets 44 px or more. Person chips are drawn 36 px tall with a 46 px hit area.
- Reduced motion turns off every animation.

## Suggestions (not built)
- Mark which share took a spare sen (a small "+1 sen" beside the figure), so "At random" is visible without comparing numbers.
- Preview the outcome under each spare sen choice in the palette.
- A "?" sheet listing every key, for people who want the whole map at once.
- Let the palette accept "Teh tarik 3.20 @ben" in one line, the way a real command line would.
- On a phone, a slim sticky bar with the Total and "Adds up to" that jumps to the shares.
