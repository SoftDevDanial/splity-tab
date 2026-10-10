# D Share Orbit, round 1 notes

**File** `d.html`, one self-contained page. Checks and screenshots in `checks/d/` (run `python -B checks/d/check_d.py`).

## The bet
The split is a shape. A segmented ring sits around the total and each person owns one segment, drawn clockwise from the top in list order. Arc length is exactly the share over the total (the gaps are taken out first, so the visible ring splits in true proportion). Everything around the ring stays quiet so the ring is the one memorable thing.

**What it costs.** On a phone the ring comes first, so the inputs sit below it and you scroll down to type. On desktop the ring panel is sticky beside the editor, so this cost goes away there.

**Design read.** A single purpose phone utility for one person at a restaurant table, in a dark orbit language, built with native CSS, system fonts and a hand drawn SVG ring. Dials are variance 5, motion 4, density 4.

## How a segment is tied to its person (never colour alone)
| Tie | Where |
|---|---|
| Order | Segments run clockwise from the top in list order, the same order as the shares list and the People list |
| Tag | Each segment carries the person's initial (numbers when initials repeat, as with Person 1 and Person 2) |
| Mini orbit | Each share row starts with a small ring that lights only that person's arc, with the same tag in the middle |
| Callouts | From 640 px wide, a leader line runs from each segment to the name and share |
| Hover | Hovering a row or a segment lights that segment and its leader and dims the rest |

## Tokens
| Role | Token | Hex |
|---|---|---|
| Page | `--bg` | #1C1C1F |
| Ring panel | `--surface` | #252529 |
| Fields and chips | `--raised` | #2E2E33 |
| Text | `--ink` | #EEECE8 |
| Secondary text | `--ink-muted` | #ABA9A4 |
| Control border | `--line-strong` | #80808A |
| Accent, chosen and main action | `--coral` | #FF7566 |
| Errors and the save warning | `--amber` | #F2C55C |
| People 1 to 3 | `--p1` `--p2` `--p3` | #79B8A7 teal, #93A1E0 periwinkle, #C99FCF mauve (12 in all) |

Coral is a bright pink coral, well away from the terracotta and brass defaults. It does two jobs only. It fills Copy summary (the main action) and it marks what is chosen (the checked mode, a tapped person, the chosen spare sen option, the spare sen marks on the ring and the "+1 sen" labels). Errors use amber so they never read as the accent.

Type is the system UI stack with tabular figures. Weights 400, 600 and 700. Shape rule is pills for everything you press, 12 px for fields, 20 px for panels. The mark keeps its geometry. Only its colours change (the two shares take the first two person colours, the total bar is ink).

## How every inventory row is reached
| ID | How |
|---|---|
| K1 | Default view |
| K2 | The mode switch, Even (the K1 bill keeps RM 100.00 as its even subtotal) |
| P1 | The spare sen button under the shares ("Top of the list"). One person opens the people picker. At random closes and shows Pick again on the line. Esc, the close button and the backdrop close it |
| M1 | New bill in the header. Start new bill gives S1. Esc, Cancel and the backdrop close it |
| S1 | Start new bill, or Prototype states |
| S2 to S7, W1 | Prototype states (the dashed tab on the left edge). S4 success also comes from Copy summary |

## Check results
| Check | Result |
|---|---|
| Console and page errors | 0 at 390, 360, 1280 and with reduced motion |
| Network requests | 0 |
| Sideways scroll at 360 | none in K1, K2, P1, M1, S1 to S7 and W1, and no element past the viewport |
| Text collisions in share rows | none, including W1 at 360 |
| Ring arcs against shares | worst gap 0.00001 of the ring (K1, K1 one person Ben, K2, K2 one person Ben, S7, W1) |
| Figures | K1 29.04, 15.74, 24.48. One person Ben gives 29.03 and 15.75. K2 38.87, 38.87, 38.86. One person Ben gives 38.86, 38.88, 38.86. At random gave two different people one sen each on every draw, and the pair changed between draws |
| Contrast | ink on page 14.41, ink on panel 12.94, muted on panel 6.50, coral on page 6.47, coral on panel 5.81, text on Copy summary 6.47, amber on panel 9.39, control border 3.46, every person colour 6.12 or more on the panel |
| Long dashes and middle dots in the page | 0 |
| Icons | all nine Phosphor paths match the 1.0 source byte for byte |

## Suggestions (not built)
- A small sticky copy of the ring on phones while you scroll the inputs, so the result stays in view as you type.
- When the ring has 7 or more people, let a tap on a segment show that person's name and share in the centre for a moment.
- Let the summary text that Copy summary produces be previewed in a sheet before copying.
