# Direction A, Night Console

**File.** `a.html` (one file, inline CSS and JS, no network) · **Checks.** `checks/a/check_a.py`, `checks/a/results.json` and the screenshots beside them

## The bet
A chat-app-native dark console. The people read like a member list, the items are tapped like reactions, and the shares arrive as a message from the Splity Tab bot, with an embed, @mentions and a proof row that adds back up to the total.

**Design read.** A single-purpose utility for one person at a restaurant table, in a Discord-like layered dark language, built with native CSS, system fonts and Phosphor icons.
**Dials.** Variance 4 (columns of money must still line up), motion 4 (a few purposeful moves), density 5 (a calm form with a dense result).

**What it bets on.** Familiarity. Anyone who has used Discord, Slack or Telegram reads the screen at once. The bot message makes the result feel like an answer, and the proof row reads as the bot showing its working. Tapping who had an item feels like adding a reaction, which is quick and social.
**What it costs.** It leans on a borrowed idiom, so it reads as "Discord-like" before it reads as its own brand. Dark layered surfaces have low tonal steps, so it needs real borders on every control to stay accessible (it has them). On a phone the bot message sits below the inputs, so the shares are one scroll away at the table.

## One accent, one rule
Indigo means **chosen**, or **said by the bot**. The chosen mode, a tapped person, the chosen spare-sen option, Copy summary, the bot avatar and name, the embed bar, the @mentions and the proof row. Nothing else is indigo. Red appears only for errors and for "Start new bill", which clears data. Amber appears only on the save warning.

## Tokens
| Role | Token | Value |
|---|---|---|
| Top bar | `--l0` | `#0B0E13` |
| People pane | `--l1` | `#10141B` |
| Bill pane | `--l2` | `#151A23` |
| Chat pane, dialogs | `--l3` | `#1B212B` |
| Embeds | `--l4` | `#232A36` |
| Hover, avatar discs | `--l5` | `#2D3545` |
| Inset fields | `--field` | `#0E1219` |
| Control borders | `--line-strong` | `#6E7891` |
| Text | `--text` | `#E8EBF2` |
| Muted text | `--text-muted` | `#A7AFBF` |
| Indigo fill | `--accent` | `#5059DA` |
| Indigo as text | `--accent-ink` | `#A3AAFF` |
| Error text | `--error-ink` | `#FF8A8F` |
| Danger fill | `--danger` | `#C4313C` |

Type is the system UI stack with tabular figures (sizes 12 to 24 px, weights 400, 600, 700). Radius rule is 8 px for controls, fields, embeds and the dialog, 6 px for a surface nested in an embed, full pill for chips and segmented controls, a circle for avatars, 4 px for @mentions.

## Layout
| Width | Layout |
|---|---|
| Under 600 px | One column of zones, each on its own layer. People (member list), Bill (mode, items, charges), then the bot channel. The top bar and the save warning stay pinned. |
| 600 to 859 px | The same column, with a wider price field and a 40 px bot avatar. |
| 860 to 1199 px | Two panes. Inputs on the left (400 px), the bot channel on the right, each scrolling on its own. |
| 1200 px and up | Three panes like a chat client. Member list (248 px), Bill (400 px), bot channel (the rest). The mode switch moves into the top bar over the Bill column, like a channel header, so Charges and Copy summary both fit in 1280 x 800. |

## How each inventory row is reached
| ID | How |
|---|---|
| K1 | The default view on load |
| K2 | The "Even" half of the mode switch, or Prototype states, K2 |
| P1 | "One person" in the spare-sen control opens the people picker (a bottom sheet on phone, a popover on desktop). Esc, the backdrop and Close shut it. Choosing a person shows a chip with their name that reopens the picker. "At random" shows "Pick again". "Top of the list" returns to the default. The shares update and briefly glow where they changed |
| M1 | "New bill" in the top bar. Esc, the backdrop and Cancel close it. "Start new bill" resets to S1 |
| S1 | "Start new bill" in M1, or Prototype states, S1 |
| S2 | Type an invalid amount in any price or the subtotal, or Prototype states, S2 |
| S3 | Untap everyone on an item, or Prototype states, S3 |
| S4 | "Copy summary" shows "Summary copied" (no clipboard call). The failure line is in Prototype states |
| S5 | Prototype states, S5 |
| S6 | Prototype states, S6 (its X dismisses it) |
| S7 | "Add person" until 12, or Prototype states, S7 |
| W1 | Prototype states, W1 (adds a blank-named fifth item at RM 964.50 for Ben, so the total is RM 1,193.87) |

## Check results
- Console errors 0 at 390, 360, 1280 and 1024 (reduced motion).
- No sideways scroll at 360 for K1, K2, S1 to S7, W1, with P1 open, with M1 open, and with the prototype panel open.
- Every control is at least 44 x 44 px at 390, 360 and 1280.
- Every inventory figure is asserted in the script (K1, K2, P1 one person and random for K1 and K2, M1 copy, S1 to S7, W1).
- All ten icon paths equal Phosphor's exactly (four from `src/ui/icons.js`, six from the Phosphor core package).
- Contrast. Body text 13.55 to 1 on the chat pane (12.09 on an embed). Muted text 6.54 at its lowest. Indigo text 7.51 on the chat pane, 6.70 on an embed, 5.47 on the mention tint. Text on the indigo fill 5.24. Control borders 3.27 at their lowest. Focus ring 6.70 at its lowest. Full table in `checks/a/results.json`.

## Prototype shortcuts (not design decisions)
- The page computes the shares live in whole cents with the brainstorm rules, so typing, tapping, adding and removing all work. "At random" is a seeded draw, so the same draw repeats on reload.
- The brief has no result copy for by-item when a price is empty or invalid. The prototype reuses "Enter an amount like 12.50" in the bot message. A charge rate outside its range falls back to the default rate silently.
- At 1200 px and up the mode switch is placed into the top bar with fixed positioning. A build would move it in the markup instead.

## Suggestions (not built, not in the page)
1. Mark who received a spare sen next to their share, so the choice shows without comparing numbers.
2. A one-line description under each spare-sen option that names the outcome for this bill.
3. Show each person's current share inside the One person picker.
4. Render the copied summary as a code block inside the bot message, the way chat apps show plain text, so people see what will be pasted.
5. On phone, a pinned bar with the Total and Copy summary, like a chat composer, so the result stays in reach while editing items.
6. Decide the by-item copy for a missing or invalid price (see the shortcut above).
