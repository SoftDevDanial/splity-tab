// The New bill confirmation (C8, R29 to R31), wired around the static <dialog> of index.html.
// createDialog(dialog, opener, { onConfirm }): `opener` is the header button, `onConfirm` starts the new bill.
// The dialog opens with showModal() (the page behind goes inert), focus starts on Cancel, and every way
// out (Cancel, Esc, a click on the backdrop, Start new bill) ends with focus back on `opener`.

import { isRepeatClick } from "./dom.js";

// Closing with a click arms a guard, because the rest of a double click or double tap would land on whatever is
// drawn under the pointer once the dialog is gone (R30: Cancel changes nothing). It cancels the repeat presses and
// clicks at the document, before any control sees them (a cancelled press also keeps focus on New bill), and it is
// gone at the first press that is not a repeat. No timer.
function swallowRepeatClicks() {
  const guard = (event) => {
    if (!isRepeatClick(event)) {
      document.removeEventListener("mousedown", guard, true);
      document.removeEventListener("click", guard, true);
      return;
    }
    event.stopPropagation();
    event.preventDefault();
  };
  document.addEventListener("mousedown", guard, true);
  document.addEventListener("click", guard, true);
}

export function createDialog(dialog, opener, { onConfirm }) {
  const [start, cancel] = dialog.querySelectorAll(".dialog-actions .btn");
  const closeByClick = () => {
    swallowRepeatClicks();
    dialog.close();
  };

  opener.addEventListener("click", () => {
    dialog.showModal();
    cancel.focus();
  });
  cancel.addEventListener("click", closeByClick);
  start.addEventListener("click", () => {
    closeByClick();
    onConfirm();
  });
  // Esc, Cancel, Start and the backdrop all end in "close", so the focus rule lives here once. It is not
  // left to the browser, which returns focus only to a control that took focus on the opening click.
  dialog.addEventListener("close", () => opener.focus());

  // Native showModal() lets Tab leave the two buttons for the document (measured: Cancel, body, Start), so
  // the app wraps Tab itself (PD-14).
  dialog.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    if (event.shiftKey && document.activeElement === start) {
      event.preventDefault();
      cancel.focus();
    } else if (!event.shiftKey && document.activeElement === cancel) {
      event.preventDefault();
      start.focus();
    }
  });

  // Native showModal() ignores a click on the backdrop (CG-8 makes it Cancel). The backdrop belongs to the
  // dialog element, so a press on the dialog element at a point outside its box is a press on the backdrop.
  // A click goes to the common ancestor of where the press began and ended, so selecting the dialog text and
  // letting go over the backdrop also targets the dialog: only a press that began on the backdrop counts.
  const onBackdrop = (event) => {
    const box = dialog.getBoundingClientRect();
    return event.target === dialog
      && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom);
  };
  let pressBeganOnBackdrop = false;
  dialog.addEventListener("mousedown", (event) => { pressBeganOnBackdrop = onBackdrop(event); });
  dialog.addEventListener("click", (event) => {
    const began = pressBeganOnBackdrop;
    pressBeganOnBackdrop = false;
    if (began && onBackdrop(event)) closeByClick();
  });
}
