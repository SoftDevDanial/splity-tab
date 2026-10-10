# Direction C, Daylight Instrument

**File.** `c.html` (one self-contained page, inline CSS and JS, no network, system fonts, Phosphor paths copied exactly)
**Checks.** `checks/c/check_c.py`, results in `checks/c/results.json`, screenshots beside it

## The bet
Futuristic in daylight. The bill reads like a precision instrument. One face holds the readout, with the Total in oversized light tabular numerals and every share in the same thin figures. Crisp 1 px rules divide the face, the breakdown cells and the control deck. Cobalt marks only the live signal (the mark, the scale, the proof row, Copy summary and the focus ring).

**Design read.** A single-purpose utility for one person at a restaurant table, shown to visitors, in a daylight precision-instrument language, built with native CSS, system display fonts and oversized light figures.
**Dials.** Variance 5, motion 3, density 4.

## The one bold thing
The numerals. "69.26" is 128 px at desktop and 60 px on a phone, weight 300, set in Segoe UI Variable Display where it exists and the platform face elsewhere. Everything else stays quiet, with sentence case labels, no all caps, no monospace data labels, no gradients and one shadow (a faint cobalt tint under the face).

## The supporting idea
The scale under the readout is the brand mark drawn to the bill's real proportions. The shares sit cut on the top row, the whole Total sits on the row below, both the same length, over a 1 px tick ruler. At 1024 px and up it runs the full width of the face with the mark's own 9 to 15 bar and gap ratio and a 6 px cut. With nothing to split it shows two dashed empty bars, an instrument at rest.

## Layout
| Width | Layout |
|---|---|
| Under 600 | One column. The face comes first (mode switch, Total, breakdown, scale, shares, spare sen, Copy summary), then the deck (People, Items or Subtotal, Charges). At 390 x 844 the whole readout down to Copy summary fits the first screen |
| 600 to 1023 | One column, 720 max |
| 1024 and up | A display over a control deck. The face has the Total on the left and the shares on the right, split by a 1 px rule, with the scale band across the bottom. The deck below has three modules split by 1 px rules |

## Tokens
Colours, type sizes, radii and spacing are custom properties on `:root`. Page `#ECF0F5`, face `#FAFBFD`, ink `#0C1424`, muted ink `#4B5568`, control border `#7D899B`, cobalt `#2445F5`, error `#C2262E`. Frames (face, dialog, sheet) are 14 px round, every control 8 px, data bars square.

## Contrast (WCAG, computed in the check script)
| Pair | Ratio |
|---|---|
| Body text, ink on page | 16.08 |
| Body text, ink on face | 17.77 |
| Muted ink on page | 6.56 |
| Muted ink on face | 7.25 |
| Cobalt accent on face | 6.25 |
| Cobalt accent on page | 5.65 |
| Copy summary text on cobalt | 6.15 |
| Selected toggle text on ink | 17.01 |
| Error on face | 5.62 |
| Control border on field (3 to 1 needed) | 3.51 |
| Control border on page (3 to 1 needed) | 3.10 |

## How every inventory row is reached
| ID | How |
|---|---|
| K1 | The default view |
| K2 | The Even half of the mode switch, or Prototype states, K2 |
| P1 | The spare sen button beside "1 sen left over" (it reads "Top of the list"). A bottom sheet on a phone, a popover from 768 px. One person opens the picker of people with a share above zero. At random shows Pick again. Esc and the backdrop close it |
| M1 | New bill in the header. Start new bill gives S1, Cancel keeps the bill. Esc and the backdrop close it |
| S1 | Start new bill in M1, or Prototype states, S1 |
| S2 | Type a bad amount in any amount field, or Prototype states, S2 (subtotal "100.005") |
| S3 | Untap everyone on an item, or Prototype states, S3 (the satay) |
| S4 | Copy summary shows "Summary copied" (no clipboard is touched). The failure is Prototype states, S4 Copy blocked |
| S5 | Prototype states, S5 (no dismiss, as the rules say) |
| S6 | Prototype states, S6, with a dismiss button |
| S7 | Add person up to 12, or Prototype states, S7 |
| W1 | Prototype states, W1. It adds a "Seafood platter" at RM 964.50 shared by all three, which brings the Total and the proof row to RM 1,193.87 |

The prototype handle is a thin yellow tab in the left gutter, so it never covers content, and it sits under every dialog backdrop.

## What it costs
- On a phone the readout sits above the inputs, like a calculator display over its keys. While typing an item price the shares are off screen until the person scrolls up.
- A light theme gives up the glow that makes the dark directions read as "Discord like" at a glance. The futuristic signal here is the thin type and the instrument scale, which is quieter.
- The thin figures lean on Segoe UI Variable Display and SF. On a platform without a light weight they render heavier and the effect softens.
- The scale repeats information the numbers already give. It earns its place as the logo idea made literal, but it is a second visual element next to the numerals.

## Motion
Changed figures drop in and flash cobalt for 0.44 s, so a spare sen choice shows exactly which shares moved. Scale segments slide to new proportions. Dialogs rise 6 px, the phone sheet slides up. All of it sits inside the reduced motion "no preference" media query, and with reduced motion on every change is instant.

## Suggestions (not built, the brief does not list them)
- A small "+1 sen" marker beside each share that received a spare sen, so the choice is visible without comparing numbers.
- A slim sticky Total and "Adds up to" strip on phones while the readout is scrolled away, to remove the cost above.
- A people count such as "3 of 12" beside the People heading, which would explain why Add person turns off at 12.
- Show the subtotal's working ("RM 15.90 + RM 13.50 ...") under the Subtotal cell on hover or focus.
