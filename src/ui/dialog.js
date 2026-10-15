// The New bill confirmation (C8, R29 to R31), wired around the static <dialog> of index.html.
// createDialog(dialog, opener, { onConfirm }): `opener` is the header button, `onConfirm` starts the new bill.
// The dialog opens with showModal() (the page behind goes inert), focus starts on Cancel, and every way
// out (Cancel, Esc, a click on the backdrop, Start new bill) ends with focus back on `opener`.

import { closeOnBackdropClick, swallowRepeatClicks } from "./dom.js";

export function createDialog(dialog, opener, { onConfirm }) {
  const [start, cancel] = dialog.querySelectorAll(".acts .btn");
  // Closing with a click arms the guard of dom.js, because the rest of a double click or double tap would land on
  // whatever is drawn under the pointer once the dialog is gone (R30: Cancel changes nothing). A cancelled press
  // also keeps focus on New bill.
  const closeByClick = () => {
    swallowRepeatClicks();
    dialog.close();
  };

  // Opening arms the same guard: the backdrop is drawn under the pointer now, so the second click of a double click
  // on New bill would land on it and shut the dialog again (I-1).
  opener.addEventListener("click", () => {
    swallowRepeatClicks();
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

  // Native showModal() lets Tab leave the two buttons for the document (measured in headless Chromium: Cancel,
  // body, Start new bill), so the app wraps Tab itself (PD-14). This comment is the one home of the measurement.
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

  closeOnBackdropClick(dialog, closeByClick); // CG-8 makes a backdrop click Cancel
}
