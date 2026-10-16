// The Splits sheet (R50, PD-18, PD-20, PD-21), the receipt lifted from the strip below 1024 px. index.html holds the empty
// dialog.sheet-dlg#splitsDlg, and Splits in the strip opens it.
// createSheet(dialog, opener, receiptHandlers) takes the dialog, Splits and the handlers createReceipt takes besides the
// ids, and returns { update(result, copyStatus), spareChip(), makeRoom(height) }. Call update at every render with what
// computeResult gives and the copy status (null, "ok" or "fail"). The sheet keeps the latest pair, fills itself from it
// when Splits is clicked and follows it while open. Closed, the dialog is empty, so its receipt (the card's renderer with
// SHEET_IDS) exists only while it is open. spareChip() gives its spare chip while one is shown, otherwise null, and
// makeRoom serves P1 (R52).
import { closeOnBackdropClick, el, setAttr, swallowRepeatClicks } from "./dom.js";
import { icon } from "./icons.js";
import { DESKTOP } from "./media.js";
import { createReceipt, SHEET_IDS } from "./receipt.js";

const ROOM_UNDER_SPLITS = 16; // px between the last split and P1 (spare-sen.md, 271 px of room for a P1 255 px tall)
const ROOM_ABOVE_P1 = 12; // px g2's scroll keeps between the splits and P1's top edge (R52, g2's rule)

export function createSheet(dialog, opener, receiptHandlers) {
  opener.append(icon("caret", "caret-up"));
  let latest = null; // [result, copyStatus] of the last render
  let shown = null; // { sheet, scroll, receipt } while open

  function fill() {
    const rbody = el("div", { class: "rbody" });
    const receipt = createReceipt(rbody, { ...receiptHandlers, ids: SHEET_IDS });
    receipt.update(...latest);
    const close = el("button", { type: "button", class: "icon-btn", "aria-label": "Close" }, icon("x"));
    close.addEventListener("click", closeByClick);
    const scroll = el("div", { class: "sheet-scroll", id: "sheetScroll" }, rbody);
    const sheet = el("div", { class: "glass dense sheet", tabindex: "-1" },
      el("div", { class: "foil", "aria-hidden": "true" }),
      el("div", { class: "sheet-top" }, el("span", { class: "grab", "aria-hidden": "true" }), close), scroll);
    dialog.append(sheet);
    return { sheet, scroll, receipt };
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

  /**
   * R52 while P1 is open over the sheet. Pads the scroll area's bottom by P1's `height` in px and 16, and when the last
   * split would sit under P1 scrolls by the overlap, never further than putting the Splits heading at the top of the
   * scroll area (g2's rule, so the splits stay in view). makeRoom(null) clears the padding. Does nothing while closed.
   */
  function makeRoom(height) {
    if (shown === null) return;
    const { scroll } = shown;
    if (height === null) {
      scroll.style.removeProperty("padding-bottom");
      return;
    }
    scroll.style.setProperty("padding-bottom", `${height + ROOM_UNDER_SPLITS}px`);
    const list = scroll.querySelector("ul.r-splits"), head = scroll.querySelector("div.r-head");
    const overlap = list.getBoundingClientRect().bottom - (innerHeight - height - ROOM_ABOVE_P1);
    const headBelowTop = head.getBoundingClientRect().top - scroll.getBoundingClientRect().top;
    if (overlap > 0) scroll.scrollTop += Math.min(overlap, headBelowTop);
  }

  return { update, spareChip: () => shown?.receipt.spareChip() ?? null, makeRoom };
}
