// P1, the spare sen choice (R52, PD-21, PD-23, CG-P7, CG-P8). index.html holds the empty dialog.pop#spareDlg, and a
// spare chip on the card or in the Splits sheet opens it.
// createSpareChoice(dialog, { onRule, card, shownChip, splits, makeRoom }) returns { open(), update(bill, result) }.
//   onRule(value) applies a choice, "top", "one" or "random". `card` is the card, P1 sits beside it from 1024 px.
//   shownChip() gives the spare chip shown at that moment or null, and `splits` is Splits, where focus goes when no chip
//   is shown. makeRoom(height) makes room in the Splits sheet under a P1 that tall, and makeRoom(null) gives it back.
// Call update at every render with the bill and computeResult(bill). P1 fills itself from the latest pair when it
// opens, follows it while open (rule 7) and is empty while closed, as the Splits sheet is. Its controls are kept while
// it is open, so an arrow key on a radio, which applies the choice and renders, leaves focus on that radio.
import { closeOnBackdropClick, el, setText, swallowRepeatClicks } from "./dom.js";
import { icon } from "./icons.js";
import { DESKTOP } from "./media.js";

// The three choices in P1's order. The chip on the receipt names the rule in effect with the same words (R51).
export const RULE_NAMES = { top: "Top of the list", one: "One person", random: "At random" };
const GAP_TO_CARD = 16; // px between the card's right edge and P1 (spare-sen.md, left 574 at 1280)

export function createSpareChoice(dialog, { onRule, card, shownChip, splits, makeRoom }) {
  let latest = null; // [bill, result] of the last render
  let shown = null; // { count, radios } while open

  function fill() {
    const close = el("button", { type: "button", class: "icon-btn", "aria-label": "Close" }, icon("x"));
    close.addEventListener("click", closeByClick);
    const count = el("p", { class: "pop-sub", id: "spareSub" });
    const radios = Object.keys(RULE_NAMES).map((value) => el("input", { type: "radio", name: "spareRule", value }));
    const choices = radios.map((radio) => el("label", { class: "choice" }, radio, el("span", { class: "dot", "aria-hidden": "true" }),
      el("span", {}, RULE_NAMES[radio.value])));
    dialog.append(el("div", { class: "in" }, el("div", { class: "pop-head" }, el("h2", { id: "spareTitle" }, "Spare sen"), close),
      count, el("div", { class: "choices" }, ...choices)));
    return { count, radios };
  }

  /** The count and the checked radio, the stored choice (CG-P7), from the latest render. */
  function draw() {
    const [bill, result] = latest;
    setText(shown.count, `${result.spare.count} sen left over`);
    for (const radio of shown.radios) {
      const chosen = radio.value === bill.spare.rule;
      if (radio.checked !== chosen) radio.checked = chosen;
    }
  }

  /**
   * R52's place. From 1024 px beside the card with its bottom level with the shown chip's bottom, through the CSSOM
   * (R38). Below 1024 px the CSS makes P1 a bottom sheet, so the place is cleared and the Splits sheet makes room under it.
   */
  function place() {
    const chip = shownChip();
    if (DESKTOP.matches && chip !== null) {
      dialog.style.setProperty("left", `${card.getBoundingClientRect().right + GAP_TO_CARD}px`);
      dialog.style.setProperty("bottom", `${document.documentElement.clientHeight - chip.getBoundingClientRect().bottom}px`);
    } else {
      dialog.style.removeProperty("left");
      dialog.style.removeProperty("bottom");
      makeRoom(dialog.offsetHeight);
    }
  }

  // Opening arms the guard of dom.js, because P1's light backdrop lies under the second click of a double click on the
  // desktop chip, and a click there would shut it again (PD-21).
  function open() {
    swallowRepeatClicks();
    shown = fill();
    draw();
    dialog.showModal();
    place(); // measured once it is shown
    shown.radios.find((radio) => radio.checked).focus();
  }

  /** Empties P1 once it is closed, gives the sheet its room back, and focuses the chip shown now, or Splits. Once per close. */
  function emptied() {
    if (shown === null || dialog.open) return;
    makeRoom(null);
    dialog.replaceChildren();
    dialog.style.removeProperty("left");
    dialog.style.removeProperty("bottom");
    shown = null;
    (shownChip() ?? splits).focus(); // PD-23, and CG-P8 when no chip is shown
  }

  // Closing by a click arms the guard too, so the rest of a double click cannot reach what lies under P1 (PD-21).
  function closeByClick() {
    swallowRepeatClicks();
    dialog.close();
    emptied();
  }

  closeOnBackdropClick(dialog, closeByClick);
  // Escape closes the dialog natively, so its close event empties it. After a click close it comes a task later and
  // does nothing, because the click has already emptied it.
  dialog.addEventListener("close", emptied);
  dialog.addEventListener("change", (event) => {
    if (event.target.name === "spareRule") onRule(event.target.value);
  });
  // P1 follows the width it is open at (PD-23): a crossing of 1024 px, and any other change of the viewport's size.
  const placeIfOpen = () => {
    if (shown !== null) place();
  };
  DESKTOP.addEventListener("change", placeIfOpen);
  window.addEventListener("resize", placeIfOpen);

  function update(bill, result) {
    latest = [bill, result];
    if (shown === null) return;
    draw();
    place(); // the chip may have moved and P1 may have grown
  }

  return { open, update };
}
