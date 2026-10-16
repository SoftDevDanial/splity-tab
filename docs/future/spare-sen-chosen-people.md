# Future upgrade: give the spare sen to the people you choose

**Status.** Not built. An idea for a later version, to be brainstormed first.
**Asked for.** 2026-10-16, by the owner in his note on UAT-01 at the v1.1.0 test.
**Ledger.** v1.1.0, Off-scope and new, row 23.

## Why this note exists
When a bill does not divide to the sen, 1.1.0 shows the spare sen and lets the user give them to one person, split
them at random, or keep the top-of-the-list rule. The owner wants more control. He wants to pick a group of people and
decide how the spare sen fall among them. His first ask at the 1.0 test already said "So user can split manually or
randomly or even have 1 person pay the extras".

## His words (typos fixed, voice kept)
"I don't want one person. I want person based (I don't know what to name this), but the logic is, I can pick either 1
or multiple people's names to split the sen left over. For example, I can pick Aisyah and Ben. There should be a
counter to show the sen left over when picking the names. Also, there will be cases where, let's say, there's 5 sen
left over but only 2 people are picked. So there's still some left over, and there should be a way in this category to
split it randomly between the 2 names, or I can manually add the number of sen per person. For example, for Aisyah I
can put 3 and for Ben 2, which adds up to 5. There should be a warning, or maybe even a prevention, because we haven't
fully allocated the sen."

## What the user would get
- **A choice of people, not one person.** Pick one or several names to take the spare sen.
- **A counter.** It shows how many spare sen are still not given out while names are picked.
- **Two ways to share among the chosen people.** At random, or by hand, typing a number of sen per person (Aisyah 3,
  Ben 2, for 5 sen).
- **A guard.** A warning, or a block on the splits, while some spare sen are still not given out.

## What it would change
| Area | Change |
|---|---|
| Brainstorm | The spare sen choice gains a "chosen people" option, with random and manual shares |
| Design | The spare sen panel (picking names, the counter, per person fields, the warning) |
| split-core | A share rule over a chosen group, random or manual, that always adds up to the spare sen |
| split-app | The panel, the saved choice, and the warning while sen are left |

## Questions for the brainstorm
- What should this option be called? The owner did not have a name for it yet.
- Is the guard a warning, or does it stop the splits until every sen is given out?
- What happens to manual shares when the bill changes and the spare sen count changes?
