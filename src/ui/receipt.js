// The receipt (C2, C3, C5, R16 to R21): what computeResult(bill) gives, drawn into a div.rbody. One renderer serves the
// card's #rbody and, from task A12, the Splits sheet's (PD-20), which is why the ids are a parameter.
// createReceipt(rbody, { ids, onCopy }) fills `rbody` and returns { update(result, copyStatus) }. `ids` names the parts
// that carry an id (CARD_IDS on the card, the sheet gives only its heading's), `copyStatus` is null, "ok" or "fail".
// Every figure comes from split-core, formatted by split-core. Text only, and quiet: the status paragraph is the one live
// element in it (R16).
import { formatAmount, formatMoney, formatRate } from "../core/money.js";
import { showCopyStatus } from "./copy-status.js";
import { el, reconcileChildren } from "./dom.js";
import { icon, seal } from "./icons.js";

export const CARD_IDS = { total: "rTotal", head: "splitsH", list: "splits", proof: "addsUp", copy: "copyBtn", status: "cardStatus" };

// R17 and R18's messages are also the strip's (R49), so they live here once.
export const BLOCKED_MESSAGE = {
  rates: "Check the charges to see the splits.",
  subtotal: "Enter the subtotal to see the splits.",
  "no-prices": "Add each item and tap who had it to see the splits.",
  prices: "Give every item a price to see the splits.",
};

// PD-17: from seven people an even list takes two columns from 1024 px (the CSS), with half the rows in each.
const MOST_ROWS_IN_ONE_COLUMN = 6;

/** True for an even or by-item result, the only ones with splits, Copy summary and a status (R17, R18, R22). */
export const hasSplits = (result) => result.kind === "even" || result.kind === "item";

export function unassignedMessage(count) {
  return count === 1
    ? "1 item still needs a person. Tap who had it to see the splits."
    : `${count} items still need a person. Tap who had each one to see the splits.`;
}

/** The attributes with an id only when one is given, because in the sheet only the heading has one (PD-20). */
const withId = (attrs, id) => (id ? { ...attrs, id } : attrs);

const billLine = (label, cents) => el("div", {}, el("dt", {}, label), el("dd", {}, formatMoney(cents)));

/** R19: the Total, the three bill lines with no working, and the dashed rule, for every result but a blocked one. */
function totalAndLines({ total, subtotal, serviceBp, service, sstBp, sst }, ids) {
  return [
    el("div", { class: "r-total" }, el("span", { class: "r-label" }, "Total"),
      el("p", withId({ class: "r-amount" }, ids.total), el("span", { class: "cur" }, "RM "), formatAmount(total))),
    el("dl", { class: "r-lines" }, billLine("Subtotal", subtotal), billLine(`Service ${formatRate(serviceBp)}`, service),
      billLine(`SST ${formatRate(sstBp)}`, sst)),
    el("div", { class: "r-rule", "aria-hidden": "true" }),
  ];
}

/** R21: a row's working. The hidden words make it read "Items 24.90 + charges 4.14" to a screen reader. */
const rowWorking = ({ items, charges }) => el("span", { class: "wk" },
  el("span", { class: "sr" }, "Items "), `${formatAmount(items)} + `, el("span", { class: "sr" }, "charges "), formatAmount(charges));

/** R20, R21: the heading, the splits list and the proof row of an even or by-item result. */
function splitsAndProof(result, ids) {
  const byItem = result.kind === "item";
  const many = !byItem && result.rows.length > MOST_ROWS_IN_ONE_COLUMN;
  const list = el("ul", withId({ class: many ? "r-splits many" : "r-splits", "aria-labelledby": ids.head }, ids.list),
    ...result.rows.map((row) => el("li", {}, el("span", { class: "nm" }, row.name), el("span", { class: "amt" }, formatMoney(row.share)),
      byItem && rowWorking(row))));
  if (many) list.style.setProperty("--rows", String(Math.ceil(result.rows.length / 2)));
  const { check } = result;
  return [
    el("div", { class: "r-head" }, el("h2", { id: ids.head }, "Splits"), byItem && el("span", { "aria-hidden": "true" }, "items + charges")),
    list,
    el("div", { class: "r-check" }, seal(), el("span", { class: "lbl-proof" }, "Adds up to"),
      el("span", withId({ class: "amt" }, ids.proof), formatMoney(check.share)),
      byItem && el("span", { class: "wk" }, `${formatAmount(check.items)} + ${formatAmount(check.charges)}`)),
  ];
}

export function createReceipt(rbody, { ids, onCopy }) {
  // Copy summary and its status paragraph are made once and kept, so the button keeps keyboard focus when the figures
  // change and the live paragraph is the same node for as long as there are splits. Everything else is drawn anew.
  const copy = el("button", withId({ type: "button", class: "btn btn-primary btn-block r-copy" }, ids.copy), icon("copy"), "Copy summary");
  copy.addEventListener("click", onCopy);
  const status = el("p", withId({ class: "status", role: "status" }, ids.status));

  function update(result, copyStatus) {
    if (result.kind === "blocked") {
      reconcileChildren(rbody, [el("div", { class: "r-total" }, el("span", { class: "r-label" }, "Total")),
        el("div", { class: "r-empty" }, icon("mark"), el("p", {}, BLOCKED_MESSAGE[result.reason]))]);
    } else if (result.kind === "unassigned") {
      reconcileChildren(rbody, [...totalAndLines(result.charges, ids),
        el("div", { class: "r-msg" }, icon("warning-circle"), el("p", {}, unassignedMessage(result.count)))]);
    } else {
      showCopyStatus(status, copyStatus);
      reconcileChildren(rbody, [...totalAndLines(result.charges, ids), ...splitsAndProof(result, ids), copy, status]);
    }
  }

  return { update };
}
