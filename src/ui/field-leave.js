// The "focus left this field" gesture for every field whose error appears on blur (R10 a, CG-3):
// Subtotal, item prices and both rates. onFieldLeave(input, handler) calls handler(input.value) when the
// field loses focus.
//
// Why it can wait (RD-3): the error the handler shows pushes everything under the field down by a line.
// If a press on a control under the field caused the blur, the press would end over whatever moved
// there, and the click that belongs to the control it started on would be lost. So a blur caused by a
// press waits until that press ends. Keyboard and every other blur run at once.
//
// The press starts at mousedown and ends at mouseup or pointercancel, not at pointerup: for a touch tap
// the browser sends pointerup first and the mouse events after it, and the focus change comes with
// those, so waiting for pointerup never waits (measured: the tap is still lost with touch). A drag
// (pointercancel) sends no mouseup. A key press also ends a press that never reported its end, so a
// keyboard blur can never be held back by a lost mouseup.
let pressed = false;
const waiting = [];

function endPress() {
  pressed = false;
  for (const run of waiting.splice(0)) run();
}

// Capture phase, so no handler of the page can stop these.
document.addEventListener("mousedown", () => { pressed = true; }, true);
document.addEventListener("mouseup", endPress, true);
document.addEventListener("pointercancel", endPress, true);
document.addEventListener("keydown", endPress, true);

/**
 * @param {HTMLInputElement} input
 * @param {(text: string) => void} handler called with the field's text, at once or when the press ends
 */
export function onFieldLeave(input, handler) {
  input.addEventListener("blur", () => {
    if (pressed) waiting.push(() => handler(input.value));
    else handler(input.value);
  });
}
