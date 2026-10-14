// Storage driver D-b (qa.md How to run, research A3). The window.localStorage getter throws a test-made
// SecurityError until a "test:storage" CustomEvent with detail false is dispatched on window, and then returns
// the real storage (SW6). Test-side only. It reads the real getter's descriptor and never storage itself at its
// top level, because an init script also runs in the blank first document, where storage access is denied.
(() => {
  const real = Object.getOwnPropertyDescriptor(window, "localStorage")
    ?? Object.getOwnPropertyDescriptor(Window.prototype, "localStorage");
  let failing = true;
  window.addEventListener("test:storage", (event) => {
    if (event.detail === false) failing = false;
  });
  Object.defineProperty(window, "localStorage", {
    configurable: true,
    enumerable: true,
    get() {
      if (failing) throw new DOMException("test security", "SecurityError");
      return real.get.call(window);
    },
  });
})();
