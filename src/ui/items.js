// The Items block (C3, R11 to R14), shown in by-item mode only: one row per item (name, price, remove and
// a "who had it" toggle per person), then "Add item".
// createItems({ onName, onPrice, onPriceLeave, onToggle, onAdd, onRemove }) returns
// { el, update(bill, errors), focusName(index), focusAdd() }. It writes DOM and reports gestures.
import { LIMITS, itemLabel, personLabel } from "../core/bill.js";
import { el, isRepeatClick, setAttr, setText, setValue, rowsFor, reconcileChildren } from "./dom.js";
import { AMOUNT_ERROR, createErrorSlot } from "./field-error.js";
import { onFieldLeave } from "./field-leave.js";
import { icon } from "./icons.js";

export function createItems({ onName, onPrice, onPriceLeave, onToggle, onAdd, onRemove }) {
  const rows = new Map();
  let current = [];

  function createRow(id) {
    const name = el("input", { type: "text", maxlength: String(LIMITS.itemNameMax), autocomplete: "off" });
    const price = el("input", { type: "text", inputmode: "decimal", autocomplete: "off" });
    const remove = el("button", { class: "icon-btn", type: "button" }, icon("x"));
    const line = el("div", { class: "item-line" },
      el("span", { class: "field" }, name),
      el("span", { class: "field money" }, el("span", { class: "unit", "aria-hidden": "true" }, "RM"), price),
      remove);
    const who = el("div", { class: "who", role: "group" });
    name.addEventListener("input", () => onName(id, name.value));
    price.addEventListener("input", () => onPrice(id, price.value));
    onFieldLeave(price, (text) => onPriceLeave(id, text));
    remove.addEventListener("click", (event) => { if (!isRepeatClick(event)) onRemove(id); }); // as in people.js
    const makeToggle = (personId) => {
      const tap = el("button", { class: "tap", type: "button" });
      tap.addEventListener("click", () => onToggle(id, personId));
      return { el: tap };
    };
    return {
      el: el("li", { class: "item" }, line, who), name, price, remove, who, makeToggle, toggles: new Map(),
      error: createErrorSlot(line, price, { id: `price-error-${id}`, message: AMOUNT_ERROR }),
    };
  }

  const add = el("button", { class: "btn btn-outline", type: "button" }, icon("plus"), "Add item");
  add.addEventListener("click", onAdd);
  const list = el("ol", { class: "items" });
  const section = el("section", { class: "block", "aria-labelledby": "h-items" },
    el("h2", { class: "block-title", id: "h-items" }, "Items"), list, add);

  function updateToggles(row, item, people) {
    const toggles = rowsFor(row.toggles, people.map((person) => person.id), row.makeToggle);
    toggles.forEach((toggle, index) => {
      setText(toggle.el, personLabel(people[index], index));
      setAttr(toggle.el, "aria-pressed", String(item.who.includes(people[index].id)));
    });
    reconcileChildren(row.who, toggles.map((toggle) => toggle.el));
  }

  function update(bill, errors) {
    section.hidden = bill.mode !== "item";
    current = rowsFor(rows, bill.items.map((item) => item.id), createRow);
    current.forEach((row, index) => {
      const item = bill.items[index];
      const label = itemLabel(item, index);
      setValue(row.name, item.name);
      setAttr(row.name, "aria-label", `Item ${index + 1} name`);
      setAttr(row.name, "placeholder", `Item ${index + 1}`);
      setValue(row.price, item.priceText);
      setAttr(row.price, "aria-label", `Item ${index + 1} price in RM`);
      setAttr(row.remove, "aria-label", `Remove ${label}`);
      setAttr(row.who, "aria-label", `Who had ${label}`);
      row.error.set(errors.price[item.id]);
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

  return { el: section, update, focusName, focusAdd };
}
