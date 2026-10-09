// The bill panel (C2, C3, C5, R16 to R21). createPanel(tape) fills the static div.tape and returns
// { update(result) }. The panel is quiet on purpose: it carries no live region (R16).
import { el, setText, reconcileChildren } from "./dom.js";

const BLOCKED_MESSAGE = {
  rates: "Check the charges to see the shares.",
  subtotal: "Enter the subtotal to see the shares.",
  "no-items": "Add an item to see the shares.",
  prices: "Give every item a price to see the shares.",
};

export function createPanel(tape) {
  const message = el("p", { class: "result-msg" });
  const title = el("h2", { class: "tape-title", id: "h-shares" }, "Shares");
  const shares = el("section", { class: "tape-section", "aria-labelledby": "h-shares" }, title);

  function update(result) {
    setText(message, BLOCKED_MESSAGE[result.reason] ?? "");
    reconcileChildren(shares, [title, message]);
    reconcileChildren(tape, [shares]);
  }

  return { update };
}
