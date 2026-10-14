// People and Charges as folding sections (R48). Each is a div.blk.sec holding a header row (h2.sec-h with
// button.sec-btn) and the body (div.sec-body, div.sec-in, then the section's content). Below 1024 px the CSS shows
// the row and hides a folded body. From 1024 px it hides the row and shows the body whatever data-open says.
// createPeopleSection(content, onToggle) and createChargesSection(content, onToggle) return { el, update(bill, open) }.
// The caller keeps the open state. onToggle() must flip it and render, and update(bill, open) shows it. A row opened
// by a click, Enter or Space then reveals its body, an open by Start new bill does not (it resets the view as at load).
import { LIMITS, personLabel } from "../core/bill.js";
import { parseRate, formatRate } from "../core/money.js";
import { el, setAttr, setText, reconcileChildren } from "./dom.js";
import { icon } from "./icons.js";

const MOTION_ALLOWED = window.matchMedia("(prefers-reduced-motion: no-preference)");

/**
 * R48 (3), the 200 ms height reveal of system.md, one Web Animation and no inline style (PD-22). Overflow is clipped by
 * a discrete keyframe value rather than a style write, so the rows below are pushed down and never drawn over.
 * The curve is the caret's turn in system.css, so the body and the caret move together. Returns the animation or null.
 */
function reveal(body) {
  if (!MOTION_ALLOWED.matches) return null;
  const height = `${body.getBoundingClientRect().height}px`;
  return body.animate([
    { height: "0px", opacity: 0, overflow: "hidden" },
    { height, opacity: 1, overflow: "hidden" },
  ], { duration: 200, easing: "cubic-bezier(0.2, 0.8, 0.2, 1)" });
}

function createSection({ key, name, innerClass, content, onToggle }) {
  const text = el("span", { class: "sec-txt" });
  const summary = el("span", { class: "sec-sum", id: `${key}Sum` }, text);
  const row = el("button", {
    type: "button", class: "sec-btn", id: `${key}Btn`, "aria-expanded": "false",
    "aria-controls": `${key}Body`, "aria-labelledby": `${key}Name`, "aria-describedby": `${key}Sum`,
  }, el("span", { class: "sec-name", id: `${key}Name` }, name), summary, icon("caret", "sec-caret"));
  const body = el("div", { class: "sec-body", id: `${key}Body` }, el("div", { class: innerClass }, ...content));
  const section = el("div", { class: "blk sec", id: `${key}Blk`, "data-open": "false" }, el("h2", { class: "sec-h" }, row), body);
  let revealing = null;

  // A button, so Enter and Space arrive here as clicks too.
  row.addEventListener("click", () => {
    onToggle();
    if (row.getAttribute("aria-expanded") === "true") revealing = reveal(body);
  });

  function setOpen(open) {
    setAttr(section, "data-open", String(open));
    setAttr(row, "aria-expanded", String(open));
    if (!open) revealing?.cancel(); // folding is instant, even halfway through a reveal
  }

  return { el: section, row, summary, text, setOpen };
}

/**
 * The People summaries in the order they are tried (R48 (2)). Every label, then the first k labels and
 * "and {n - k} more" for k from n - 1 down to 1, then "{n} people".
 * @param {string[]} labels the people's labels in list order
 * @returns {string[]}
 */
function peopleSummaries(labels) {
  const fewer = labels.slice(1).map((_, index) => {
    const shown = labels.length - 1 - index;
    return `${labels.slice(0, shown).join(", ")} and ${labels.length - shown} more`;
  });
  return [labels.join(", "), ...fewer, `${labels.length} people`];
}

/**
 * People (R48 (2)). The summary is the longest of `peopleSummaries` that shows whole in the row, measured at every
 * render and whenever the summary's box changes width (a resize, or the row coming back below 1024 px).
 */
export function createPeopleSection(content, onToggle) {
  const section = createSection({ key: "people", name: "People", innerClass: "sec-in people-in", content, onToggle });
  let summaries = [];

  function fit() {
    for (const candidate of summaries) {
      setText(section.text, candidate);
      if (section.summary.scrollWidth <= section.summary.clientWidth) return;
    }
  }
  new ResizeObserver(fit).observe(section.summary);

  function update(bill, open) {
    section.setOpen(open);
    summaries = peopleSummaries(bill.people.map(personLabel));
    fit();
  }

  return { el: section.el, update };
}

/**
 * What the Charges row says (R48 (2)). Both rates as they count when both pass their parsers, otherwise which rate to
 * check. An empty rate fails too (core R18 (a)), so a blank rate never reads as 0 (RULINGS-v1.1.0).
 * @returns {{ bad: boolean, text: string }}
 */
function chargesSummary(bill) {
  const service = parseRate(bill.serviceText, LIMITS.serviceMaxPercent);
  const sst = parseRate(bill.sstText, LIMITS.sstMaxPercent);
  if (service.ok && sst.ok) return { bad: false, text: `Service ${formatRate(service.bp)}, SST ${formatRate(sst.bp)}` };
  if (!service.ok && !sst.ok) return { bad: true, text: "Check both rates" };
  return { bad: true, text: service.ok ? "Check SST" : "Check service charge" };
}

/** Charges (R48 (2)). The summary follows the rate texts on every render, not the error timing of R10. */
export function createChargesSection(content, onToggle) {
  const section = createSection({ key: "charges", name: "Charges", innerClass: "sec-in", content, onToggle });
  const marker = icon("warning-circle");

  function update(bill, open) {
    section.setOpen(open);
    const { bad, text } = chargesSummary(bill);
    section.row.classList.toggle("is-bad", bad);
    reconcileChildren(section.summary, bad ? [marker, section.text] : [section.text]);
    setText(section.text, text);
  }

  return { el: section.el, update };
}
