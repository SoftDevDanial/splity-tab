// The Split block (R8), two radios "Even" and "By item" in the golden's switch, with no legend (the group is named
// by its heading). createMode({ onMode(mode) }) returns { el, update(bill) }. The arrow keys and the labels are native
// radio behaviour.
import { el } from "./dom.js";

export function createMode({ onMode }) {
  const radio = (id, value) => {
    const input = el("input", { type: "radio", name: "mode", id, value });
    input.addEventListener("change", () => onMode(value));
    return input;
  };
  const even = radio("modeEven", "even");
  const item = radio("modeItem", "item");
  const block = el("div", { class: "blk split", id: "splitBlk", role: "group", "aria-labelledby": "splitH" },
    el("h2", { class: "blk-h", id: "splitH" }, "Split"),
    el("div", { class: "mode-sw" },
      even, el("label", { for: "modeEven" }, "Even"),
      item, el("label", { for: "modeItem" }, "By item")));

  function update(bill) {
    even.checked = bill.mode === "even";
    item.checked = bill.mode === "item";
  }

  return { el: block, update };
}
