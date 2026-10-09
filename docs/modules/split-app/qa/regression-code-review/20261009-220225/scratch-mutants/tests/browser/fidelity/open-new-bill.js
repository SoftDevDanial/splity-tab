// Test-side only, never loaded by index.html. Passed to the harness as --candidate-after-load, which runs
// it inside an async function after the page has loaded.
// A scripted click makes Chromium treat the focus the app then moves to Cancel as keyboard focus and draw the
// ring, which a real mouse click does not, and the golden shows none. So focus is dropped once the dialog is open.
// Focus on Cancel itself is checked with real gestures by R29.
const nextFrame = () => new Promise((resolve) => requestAnimationFrame(() => resolve()));
document.querySelector("header .btn").click();
await nextFrame();
await nextFrame();
document.activeElement.blur();
await nextFrame();
await nextFrame();
