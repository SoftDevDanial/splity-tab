# Design brief: Split

**Phase:** design (sdlc:design, step 1 and 2) · **Date:** 2026-10-08 · **Source:** `docs/brainstorm/brainstorm.md`

## Who uses it
The person who paid a restaurant bill, at the table, phone in one hand and the receipt in the other.
They are in a hurry and other people are waiting. They need to type a few numbers and read out or paste
the shares.

## The one job of the key screen
Turn a receipt into shares that everyone trusts. The person must be able to see, without doing any maths,
that the shares add back up to the receipt total.

## Three feeling words
**Fair, quick, exact.**

## Hard constraints
- **Platform:** a static web page. Primary viewport is a phone, 390 x 844. It must also work from 360 px
  wide and look deliberate on a 1280 px desktop (a centred column is fine).
- **One theme, light.** No theme switcher (non-goal). The fidelity gate renders in the light scheme.
- **No network dependencies.** No web fonts, no CDN, no images from the internet. The app ships with zero
  dependencies and must work offline, so designs use system font stacks only. Icons are optional. If
  used, they are Phosphor Icons (MIT) SVG paths inlined into the file, never hand-drawn.
- **Accessibility:** WCAG AA text contrast, visible keyboard focus, touch targets at least 44 px,
  reduced motion respected.
- **Money is shown as `RM 38.87`** (RM, a space, two decimals) with tabular figures so columns line up.
- **Real copy only.** All copy comes from the brainstorm. Sample people are Aisyah, Ben and Chen.

## References
The owner gave no references for this app. He dislikes generic AI-made looks (purple gradients, cream
paper with a serif and a terracotta accent, glass cards everywhere). Avoid those defaults.

## Inventory (step 2)
Everything below traces to a brainstorm capability. Nothing outside this list gets designed.

| ID | Screen or state | Traces to | Notes |
|---|---|---|---|
| S1 | **Bill screen, by item, with shares (KEY SCREEN)** | C1 C3 C4 C5 C6 | 3 people, 4 items, one item shared by two people. |
| S2 | Bill screen, even split, with shares | C1 C2 C4 C5 C6 | Same people, subtotal RM 100.00. |
| S3 | Bill screen, first open (empty) | C1 C2 C7 | Two people "Person 1" and "Person 2", no subtotal, the shares area explains what to do. |
| S4 | State: amount error | C2 C3 | Inline "Enter an amount like 12.50" under a field. |
| S5 | State: items still need a person | C3 C5 | Shares hidden, the result area counts the items left. |
| S6 | State: summary copied / copy failed | C6 | Short status message. |
| S7 | State: saved bill could not be read | C7 | Dismissible note at the top. |
| S8 | State: 12 people reached | C1 | Add person disabled. |
| M1 | New bill confirmation | C8 | "Start a new bill? This clears the people, items and amounts." |

**Key screen:** S1. If the by-item split is clear, the even split is a subset of it.

**Inventory confirmation:** confirmed by the orchestrator under the owner's delegation, 2026-10-08 (ORCH).
