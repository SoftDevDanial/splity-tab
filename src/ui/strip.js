// The strip (R49), the receipt docked at the bottom below 1024 px. index.html holds its frame. This module fills
// #stripInfo with the Total or the reason there is none, shows the copy status beside or under it, keeps Copy summary
// disabled unless there are splits (rule 5, disabled and never hidden), keeps the root's --strip-h at the strip's
// height, so the page's bottom padding and scroll-padding-bottom clear it (system.css), and scrolls a control that
// gets focus under the strip clear of it (focusScroll).
// createStrip(strip, { onCopy }) takes #strip and returns { update(result, copyStatus) }. `result` is what computeResult
// gives, `copyStatus` is null, "ok" or "fail". #splitsBtn is the sheet's (createSheet).
import { formatAmount } from "../core/money.js";
import { showCopyStatus } from "./copy-status.js";
import { el, reconcileChildren } from "./dom.js";
import { icon } from "./icons.js";
import { DESKTOP } from "./media.js";
import { BLOCKED_MESSAGE, hasSplits, unassignedMessage } from "./receipt.js";

/** What #stripInfo holds: the Total for a result with splits, else the receipt's message, with the icon when unassigned. */
function stripInfo(result) {
  if (hasSplits(result)) {
    return [el("span", { class: "s-label" }, "Total"),
      el("span", { class: "s-fig", id: "stripTotal" }, el("span", { class: "cur" }, "RM "), formatAmount(result.charges.total))];
  }
  const message = result.kind === "blocked"
    ? [BLOCKED_MESSAGE[result.reason]]
    : [icon("warning-circle"), unassignedMessage(result.count)];
  return [el("p", { class: "s-msg", id: "stripMsg" }, ...message)];
}

export function createStrip(strip, { onCopy }) {
  const info = strip.querySelector("#stripInfo");
  const status = strip.querySelector("#stripStatus");
  const copy = strip.querySelector("#stripCopy");
  copy.prepend(icon("copy"));
  copy.addEventListener("click", onCopy);

  /**
   * Sets the root's --strip-h to the strip's height as drawn, through the CSSOM (R38). From 1024 px the strip is not
   * displayed, so that is 0px, the value system.css gives there too.
   */
  function fit() {
    const height = `${strip.getBoundingClientRect().height}px`;
    if (document.documentElement.style.getPropertyValue("--strip-h") !== height) {
      document.documentElement.style.setProperty("--strip-h", height);
    }
  }
  // A width change can wrap the message or the status, and 1024 px hides the strip, with no render. Nothing fit()
  // changes is inside the strip, so the observer cannot loop.
  new ResizeObserver(fit).observe(strip, { box: "border-box" });

  const app = strip.closest(".app");
  /**
   * R49, the focus scroll, for the `focusin` event of any element. Below 1024 px, a control focused in the page behind
   * the strip whose bottom edge is under the strip's top edge is scrolled the least distance that shows it, which the
   * root's scroll-padding-bottom stops 12 px above the strip. The strip's own controls and the dialogs (outside div.app,
   * drawn above the strip) are left alone, and so is every control from 1024 px, where there is no strip.
   */
  function focusScroll(event) {
    const control = event.target;
    if (DESKTOP.matches || !app.contains(control) || strip.contains(control)) return;
    // The browser's own focus scroll is not enough. WebKit leaves a control that is already on screen where it is, even
    // under the strip, and ignores scroll-padding-bottom, which scrollIntoView reads in both engines (F-A11-1).
    if (control.getBoundingClientRect().bottom > strip.getBoundingClientRect().top) control.scrollIntoView({ block: "nearest" });
  }
  document.addEventListener("focusin", focusScroll);

  function update(result, copyStatus) {
    reconcileChildren(info, stripInfo(result));
    showCopyStatus(status, copyStatus);
    copy.disabled = !hasSplits(result);
    fit(); // at once, so the page is padded right from the first render, before the observer's first call
  }

  return { update };
}
