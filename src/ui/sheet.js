// The Splits sheet (R50, PD-18, PD-20, PD-21), the receipt lifted from the strip below 1024 px. index.html holds the empty
// dialog.sheet-dlg#splitsDlg, and Splits in the strip opens it.
// createSheet(dialog, opener, { onCopy }) takes the dialog and Splits and returns { update(result, copyStatus) }. Call
// update at every render with what computeResult gives and the copy status (null, "ok" or "fail"). The sheet keeps the
// latest pair, fills itself from it when Splits is clicked and follows it while open. Closed, the dialog is empty, so its
// receipt (the card's renderer with SHEET_IDS) exists only while it is open.
import { closeOnBackdropClick, el, setAttr, swallowRepeatClicks } from "./dom.js";
import { icon } from "./icons.js";
import { createReceipt, SHEET_IDS } from "./receipt.js";

const DESKTOP = window.matchMedia("(min-width: 1024px)");

export function createSheet(dialog, opener, { onCopy }) {
  opener.append(icon("caret", "caret-up"));
  let latest = null; // [result, copyStatus] of the last render
  let shown = null; // { sheet, receipt } while open

  function fill() {
    const rbody = el("div", { class: "rbody" });
    const receipt = createReceipt(rbody, { ids: SHEET_IDS, onCopy });
    receipt.update(...latest);
    const close = el("button", { type: "button", class: "icon-btn", "aria-label": "Close" }, icon("x"));
    close.addEventListener("click", closeByClick);
    const sheet = el("div", { class: "glass dense sheet", tabindex: "-1" },
      el("div", { class: "foil", "aria-hidden": "true" }),
      el("div", { class: "sheet-top" }, el("span", { class: "grab", "aria-hidden": "true" }), close),
      el("div", { class: "sheet-scroll", id: "sheetScroll" }, rbody));
    dialog.append(sheet);
    return { sheet, receipt };
  }

  // Opening arms the guard because the sheet rises under the pointer, with its Copy summary where the second tap of a
  // double tap on Splits lands (PD-21).
  opener.addEventListener("click", () => {
    swallowRepeatClicks();
    shown = fill();
    dialog.showModal();
    setAttr(opener, "aria-expanded", "true");
    shown.sheet.focus(); // a screen reader starts at the receipt, and system.css draws no ring on the sheet
  });

  /** Empties the sheet once it is closed, and gives focus back to Splits unless `focusSplits` is false. Once per close. */
  function emptied(focusSplits) {
    if (shown === null || dialog.open) return;
    dialog.replaceChildren();
    shown = null;
    setAttr(opener, "aria-expanded", "false");
    if (focusSplits) opener.focus();
  }

  // Closing by a click arms the guard too, because whatever lies under the closed sheet must not get the rest of the
  // double click or double tap (PD-21).
  function closeByClick() {
    swallowRepeatClicks();
    dialog.close();
    emptied(true);
  }

  closeOnBackdropClick(dialog, closeByClick);
  // Escape closes the dialog natively, so its close event empties it. The HTML close steps queue that event as a task
  // after every close, by when a click or a width close has already emptied it at once, so it does nothing then.
  dialog.addEventListener("close", () => emptied(true));
  // PD-18. Splits is not shown from 1024 px, so there is nothing to give focus back to, and the app moves none.
  DESKTOP.addEventListener("change", () => {
    if (!DESKTOP.matches || !dialog.open) return;
    dialog.close();
    emptied(false);
  });

  function update(result, copyStatus) {
    latest = [result, copyStatus];
    shown?.receipt.update(result, copyStatus);
  }

  return { update };
}
