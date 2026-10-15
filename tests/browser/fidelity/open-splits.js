// Test-side only, never loaded by index.html. The fidelity harness runs it as --candidate-after-load, inside an async
// function after the page has loaded. It opens the Splits sheet, the state of splits-sheet.
// It presses controls, so it presses nothing unless the seed script put the clipboard stand-in in place (R40). The
// harness takes one file per render, so each after-load script carries this check itself.
if (window.testClipboardWrites !== 0 || (typeof navigator.clipboard?.writeText === "function"
  && Function.prototype.toString.call(navigator.clipboard.writeText).includes("[native code]"))) {
  throw new Error("clipboard stand-in missing");
}
const nextFrame = () => new Promise((resolve) => requestAnimationFrame(() => resolve()));
// A scripted click makes Chromium draw a keyboard focus ring where the app then puts focus, which a real mouse click
// does not and the golden does not show, so focus is dropped after each click (1.0 PD-16).
async function press(selector) {
  const control = document.querySelector(selector);
  if (!control) throw new Error(`${selector} is not on the page`);
  control.click();
  await nextFrame();
  await nextFrame();
  document.activeElement.blur();
  await nextFrame();
  await nextFrame();
}
await press("#splitsBtn");
