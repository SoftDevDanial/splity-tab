// The receipt in the card (R17). blockedReceipt(reason) gives the nodes of a blocked result, the form a cold boot
// shows (R2): the bare Total, the mark and the reason the splits cannot be worked out yet. Text only (R16, quiet).
import { el } from "./dom.js";
import { icon } from "./icons.js";

const BLOCKED_MESSAGE = {
  rates: "Check the charges to see the splits.",
  subtotal: "Enter the subtotal to see the splits.",
  "no-prices": "Add each item and tap who had it to see the splits.",
  prices: "Give every item a price to see the splits.",
};

/** @param {"rates" | "subtotal" | "no-prices" | "prices"} reason a blocked result's reason @returns {HTMLElement[]} */
export function blockedReceipt(reason) {
  return [
    el("div", { class: "r-total" }, el("span", { class: "r-label" }, "Total")),
    el("div", { class: "r-empty" }, icon("mark"), el("p", {}, BLOCKED_MESSAGE[reason])),
  ];
}
