// The Items block (C3, R11 to R14, R18's marker, R56), div.blk.items-blk#itemsBlock, in the DOM in by-item mode only (R8,
// the caller places it): the heading row with "Add item", then the item frame, which scrolls inside itself and holds one
// li.item per item (name, price with its error, Remove, then a toggle per person).
// createItems({ onName, onPrice, onPriceLeave, onToggle, onAdd, onRemove }) returns
// { el, update(bill, errors), markFrame(), focusName(index), focusAdd() }. It writes DOM and reports gestures; the bill is
// changed by the caller.
import { LIMITS, itemLabel, personLabel } from "../core/bill.js";
import { el, isRepeatClick, swallowRepeatClicks, setAttr, setText, setValue, rowsFor, reconcileChildren } from "./dom.js";
import { AMOUNT_ERROR, createFieldError } from "./field-error.js";
import { onFieldLeave } from "./field-leave.js";
import { icon } from "./icons.js";

export function createItems({ onName, onPrice, onPriceLeave, onToggle, onAdd, onRemove }) {
  const rows = new Map();
  let current = [];

  function createRow(id) {
    const name = el("input", { type: "text", maxlength: String(LIMITS.itemNameMax), autocomplete: "off" });
    const price = el("input", { type: "text", placeholder: "0.00", inputmode: "decimal", autocomplete: "off" });
    const priceField = el("div", { class: "field money" }, el("span", { class: "unit", "aria-hidden": "true" }, "RM"), price);
    // Its id is the item's position (ie{j}, R14), so update names it before the row is first placed.
    const error = createFieldError(priceField, price, { id: "", message: AMOUNT_ERROR });
    const remove = el("button", { type: "button", class: "icon-btn" }, icon("x"));
    const taps = el("div", { class: "taps", role: "group" });
    name.addEventListener("input", () => onName(id, name.value));
    price.addEventListener("input", () => onPrice(id, price.value));
    onFieldLeave(price, (text) => onPriceLeave(id, text));
    // A Remove ignores a repeat press whether or not a click armed the guard (R7, RG-CR-08), as in people.js.
    remove.addEventListener("click", (event) => { swallowRepeatClicks(); if (!isRepeatClick(event)) onRemove(id); });
    const makeToggle = (personId) => {
      const label = el("span");
      const tap = el("button", { type: "button", class: "tap" }, icon("check"), label);
      tap.addEventListener("click", () => onToggle(id, personId));
      return { el: tap, label };
    };
    const row = el("div", { class: "item-row" }, el("div", { class: "field" }, name), priceField, remove, error.el);
    return { el: el("li", { class: "item" }, row, taps), name, price, remove, taps, error, makeToggle, toggles: new Map() };
  }

  const add = el("button", { type: "button", class: "btn btn-ghost", id: "addItem" }, icon("plus"), "Add item");
  // No Remove button slides under this button, but it arms the guard like Add person does, so the rule stays one rule
  // for every control that adds a row (RG-CR-01).
  add.addEventListener("click", () => { swallowRepeatClicks(); onAdd(); });
  const list = el("ul", { class: "frame", id: "itemList", "aria-labelledby": "itemsH" });
  const frame = el("div", { class: "frame-wrap", id: "frameWrap" }, list);
  const block = el("div", { class: "blk items-blk", id: "itemsBlock" },
    el("div", { class: "blk-head" }, el("h2", { class: "blk-h", id: "itemsH" }, "Items"), add), frame);

  /**
   * R56: `data-up` while the list is scrolled down from its top, `data-down` while more of it lies below what shows. The
   * caller runs it after every render, and the list's scroll and a change of the frame's size run it too. A frame that is
   * not displayed (no items, or not in the DOM) has neither.
   */
  function markFrame() {
    // A scroll offset can be fractional while the sizes are whole pixels, so under 1 px from an edge counts as at it.
    setAttr(frame, "data-up", list.scrollTop >= 1 ? "" : null);
    setAttr(frame, "data-down", list.scrollHeight - list.clientHeight - list.scrollTop >= 1 ? "" : null);
  }
  list.addEventListener("scroll", markFrame, { passive: true });
  new ResizeObserver(markFrame).observe(frame);

  function updateToggles(row, item, people) {
    const toggles = rowsFor(row.toggles, people.map((person) => person.id), row.makeToggle);
    toggles.forEach((toggle, index) => {
      setText(toggle.label, personLabel(people[index], index));
      setAttr(toggle.el, "aria-pressed", String(item.who.includes(people[index].id)));
    });
    reconcileChildren(row.taps, toggles.map((toggle) => toggle.el));
  }

  function update(bill, errors) {
    current = rowsFor(rows, bill.items.map((item) => item.id), createRow);
    current.forEach((row, index) => {
      const item = bill.items[index];
      const number = index + 1;
      const label = itemLabel(item, index);
      setValue(row.name, item.name);
      setAttr(row.name, "aria-label", `Item ${number} name`);
      setAttr(row.name, "placeholder", `Item ${number}`);
      setValue(row.price, item.priceText);
      setAttr(row.price, "aria-label", `${label} price in RM`);
      setAttr(row.remove, "aria-label", `Remove ${label}`);
      setAttr(row.taps, "aria-label", `Who had ${label}`);
      row.error.rename(`ie${number}`);
      row.error.set(errors.price[item.id]);
      row.el.classList.toggle("needs", item.who.length === 0); // R18, the amber bar on an item nobody had
      updateToggles(row, item, bill.people);
    });
    add.disabled = bill.items.length >= LIMITS.maxItems;
    reconcileChildren(list, current.map((row) => row.el));
  }

  /** R12, R34: puts the cursor in the name field of the item at `index`. */
  function focusName(index) {
    current[index]?.name.focus();
  }

  /** R34: after the last item is removed, focus goes to "Add item". */
  function focusAdd() {
    add.focus();
  }

  return { el: block, update, markFrame, focusName, focusAdd };
}
