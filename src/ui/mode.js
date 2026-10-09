// The mode switch (C2, C3, R8): two radios, "Even" and "By item". createMode() returns { el, update(bill) }.
import { el } from "./dom.js";

function radio(id, value) {
  return el("input", { type: "radio", name: "mode", id, value });
}

export function createMode() {
  const even = radio("mode-even", "even");
  const item = radio("mode-item", "item");
  const fieldset = el("fieldset", { class: "mode" },
    el("legend", { class: "sr-only" }, "Split mode"),
    even, el("label", { for: "mode-even" }, "Even"),
    item, el("label", { for: "mode-item" }, "By item"));

  function update(bill) {
    even.checked = bill.mode === "even";
    item.checked = bill.mode === "item";
  }

  return { el: fieldset, update };
}
