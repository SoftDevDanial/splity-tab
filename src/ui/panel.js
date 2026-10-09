// The bill panel (C2, C3, C5, R16 to R21): Bill summary, then Shares. Every figure comes from the
// split-core result, formatted by split-core. createPanel(tape, { onCopy }) fills the static div.tape and
// returns { update(result, copyStatus) }, where copyStatus is null, "ok" or "fail" (R22 to R24).
// The panel is quiet on purpose (R16): the only live region in it is the copy status.
import { formatMoney, formatRate } from "../core/money.js";
import { el, setAttr, setText, reconcileChildren } from "./dom.js";
import { icon } from "./icons.js";

const BLOCKED_MESSAGE = {
  rates: "Check the charges to see the shares.",
  subtotal: "Enter the subtotal to see the shares.",
  "no-items": "Add an item to see the shares.",
  prices: "Give every item a price to see the shares.",
};
const COPY_STATUS = {
  ok: { text: "Summary copied", className: "status" },
  fail: { text: "Could not copy. Your browser blocked the clipboard.", className: "status status-failure" },
};

function unassignedMessage(count) {
  return count === 1
    ? "1 item still needs a person. Tap who had it to see the shares."
    : `${count} items still need a person. Tap who had each one to see the shares.`;
}

const op = (symbol) => el("span", { class: "op", "aria-hidden": "true" }, symbol);

function summaryRow(symbol, label, amount, working) {
  return el("div", { class: "row" },
    el("dt", {}, op(symbol), label), el("dd", { class: "amt" }, amount),
    working && el("dd", { class: "work" }, working));
}

function summaryList({ subtotal, serviceBp, service, sstBp, sstBase, sst, total }) {
  return el("dl", { class: "sum" },
    summaryRow("", "Subtotal", formatMoney(subtotal)),
    summaryRow("+", "Service charge", formatMoney(service), `${formatRate(serviceBp)} of ${formatMoney(subtotal)}`),
    summaryRow("+", "SST", formatMoney(sst), `${formatRate(sstBp)} of ${formatMoney(sstBase)}`),
    el("div", { class: "row total" },
      el("dt", {}, op("="), "Total"),
      el("dd", { class: "amt" }, el("span", { class: "final" }, formatMoney(total)))));
}

function checkRow(cells) {
  return el("tfoot", {}, el("tr", {}, el("th", { scope: "row" }, icon("check"), "Adds up to"), ...cells));
}

/** @param {{ rows: { name: string, share: number }[], check: { share: number } }} result an even result */
function evenTable(result) {
  const heads = el("thead", { class: "sr-only" }, el("tr", {},
    el("th", { scope: "col" }, "Person"), el("th", { scope: "col" }, "Share")));
  const body = el("tbody", {}, ...result.rows.map((row) => el("tr", {},
    el("th", { scope: "row" }, row.name), el("td", { class: "share" }, formatMoney(row.share)))));
  return el("table", { class: "shares", "aria-labelledby": "h-shares" }, heads, body,
    checkRow([el("td", { class: "share" }, formatMoney(result.check.share))]));
}

/** @param {{ rows: { name: string, items: number, charges: number, share: number }[], check: object }} result an item result */
function itemTable(result) {
  const heads = el("thead", {}, el("tr", {},
    el("th", { scope: "col" }, el("span", { class: "sr-only" }, "Person")),
    el("th", { scope: "col" }, "Items"),
    el("th", { scope: "col" }, op("+"), "Charges"),
    el("th", { scope: "col" }, op("="), "Share")));
  const body = el("tbody", {}, ...result.rows.map((row) => el("tr", {},
    el("th", { scope: "row" }, row.name), el("td", {}, formatMoney(row.items)),
    el("td", {}, formatMoney(row.charges)), el("td", { class: "share" }, formatMoney(row.share)))));
  const { check } = result;
  return el("table", { class: "shares", "aria-labelledby": "h-shares" }, heads, body,
    checkRow([el("td", {}, formatMoney(check.items)), el("td", {}, formatMoney(check.charges)),
      el("td", { class: "share" }, formatMoney(check.share))]));
}

export function createPanel(tape, { onCopy }) {
  const summaryTitle = el("h2", { class: "tape-title", id: "h-summary" }, "Bill summary");
  const summary = el("section", { class: "tape-section", "aria-labelledby": "h-summary" }, summaryTitle);
  const sharesTitle = el("h2", { class: "tape-title", id: "h-shares" }, "Shares");
  const shares = el("section", { class: "tape-section", "aria-labelledby": "h-shares" }, sharesTitle);
  const message = el("p", { class: "result-msg" });
  // The copy button and its status are made once and kept while the table is on screen, so the button
  // keeps keyboard focus when the figures change (R33) and the status survives edits (R24).
  const copy = el("button", { class: "btn btn-primary btn-large btn-block copy", type: "button" }, icon("copy"), "Copy summary");
  copy.addEventListener("click", onCopy);
  const status = el("p", { class: "status", role: "status" });

  function update(result, copyStatus) {
    const hasTable = result.kind === "even" || result.kind === "item";
    if (result.kind !== "blocked") reconcileChildren(summary, [summaryTitle, summaryList(result.charges)]);
    if (hasTable) {
      const shown = COPY_STATUS[copyStatus] ?? { text: "", className: "status" };
      setText(status, shown.text);
      setAttr(status, "class", shown.className);
      const table = result.kind === "even" ? evenTable(result) : itemTable(result);
      reconcileChildren(shares, [sharesTitle, table, copy, status]);
    } else {
      setText(message, result.kind === "blocked" ? BLOCKED_MESSAGE[result.reason] : unassignedMessage(result.count));
      reconcileChildren(shares, [sharesTitle, message]);
    }
    reconcileChildren(tape, result.kind === "blocked" ? [shares] : [summary, shares]);
  }

  return { update };
}
