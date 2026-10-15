// The notes in the top bar's div.notes#notes (R27, R46). The save warning comes first, then the "saved bill could
// not be read" note with Dismiss note (CG-P5). Each note is built once and only inserted or removed when its state
// flips, so a keystroke that saves (or fails to) never touches the live regions (SW7).
// createNotes(container, { onDismiss }) returns { update({ saveFailing, noteShown }) }.
import { el, reconcileChildren, swallowRepeatClicks } from "./dom.js";
import { icon } from "./icons.js";

export function createNotes(container, { onDismiss }) {
  const warning = el("div", { class: "note is-warn", role: "status" }, icon("warning"),
    el("p", {}, "This bill is not being saved on this device. It will be lost when you close this tab."));
  const dismiss = el("button", { type: "button", class: "icon-btn", id: "dismissNote", "aria-label": "Dismiss note" }, icon("x"));
  // The rows move up once the note is gone, so the rest of a double press would land on the People header row below
  // 1024 px and fold People, or on the top bar and take focus off New bill. The guard is armed first (R27, R7).
  dismiss.addEventListener("click", () => { swallowRepeatClicks(); onDismiss(); });
  const unreadable = el("div", { class: "note", role: "status" }, icon("warning-circle"),
    el("p", {}, "Your saved bill could not be read, so a new one was started."), dismiss);

  function update({ saveFailing, noteShown }) {
    reconcileChildren(container, [saveFailing && warning, noteShown && unreadable].filter(Boolean));
  }

  return { update };
}
