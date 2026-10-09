// MUTANT M5 of src/ui/dialog.js (scratch copy, never in src/): the New bill click no longer arms the guard (I-1).
import { swallowRepeatClicks } from "./dom.js";

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
  dialog.addEventListener("close", () => opener.focus());

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
