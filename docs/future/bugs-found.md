# Bugs found and left for a later version

Issues that testing found after the build, that were written up instead of fixed before the seal, with why.

## A selected price can look unselected in Android-style phone browsers (v1.1.0)

**Found.** 2026-10-16, from the owner's cross on one expected line of UAT-04 at the v1.1.0 user acceptance test,
"The price is selected", measured afterwards by the test agent.
**Ledger.** v1.1.0 scope S7 row 59, findings U1 of the 2026-10-16 user test.

**What happens.** Ctrl+A in a price field does select the whole price, and typing replaces it. In Chrome's phone mode
the selection is painted Android-style, a dim teal block with the digits turning black. On the app's dark price field
that is a contrast of about 2.5 to 1, so it reads as the digits going dark rather than as a highlight. On a desktop the
selection is a clear blue with white digits. The app sets no selection colour of its own.

**Why it was not fixed before the seal.** It is cosmetic, it breaks no promise of the design, and a selection colour is
a design decision for the design phase.

**The fix, next version.** A selection colour in the design system for text on dark fields, then the pixel match.
