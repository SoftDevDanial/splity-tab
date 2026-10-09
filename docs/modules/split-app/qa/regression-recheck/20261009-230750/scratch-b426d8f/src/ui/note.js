// The "saved bill could not be read" note (R27), under the header. Dismissing it removes it from the DOM.
// createNote(header, { onDismiss }) returns { update(shown) }.
import { el } from "./dom.js";
import { icon } from "./icons.js";

export function createNote(header, { onDismiss }) {
  const dismiss = el("button", { class: "icon-btn", type: "button", "aria-label": "Dismiss note" }, icon("x"));
  dismiss.addEventListener("click", onDismiss);
  const wrap = el("div", { class: "note-wrap" }, el("div", { class: "note", role: "status" },
    el("p", {}, "Your saved bill could not be read, so a new one was started."), dismiss));

  function update(shown) {
    if (!shown) wrap.remove();
    else if (header.nextElementSibling !== wrap) header.after(wrap);
  }

  return { update };
}
