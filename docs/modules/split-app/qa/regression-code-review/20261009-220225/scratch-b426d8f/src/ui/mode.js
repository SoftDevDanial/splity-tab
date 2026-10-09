// The mode switch (C2, C3, R8): two radios, "Even" and "By item".
// createMode({ onMode(mode) }) returns { el, update(bill) }. The arrow keys and the labels are native radio behaviour.
import { el } from "./dom.js";

export function createMode({ onMode }) {
  const radio = (id, value) => {
    const input = el("input", { type: "radio", name: "mode", id, value });
    input.addEventListener("change", () => onMode(value));
    return input;
  };
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
