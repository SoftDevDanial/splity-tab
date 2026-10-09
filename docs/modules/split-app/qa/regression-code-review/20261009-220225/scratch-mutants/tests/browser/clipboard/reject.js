// Test-side platform control (CG-7), the failure path. The clipboard write is refused the way a browser
// that blocks the permission refuses it. Nothing reaches the operating system clipboard.
(() => {
  if (typeof Clipboard === "function") {
    Clipboard.prototype.writeText = function writeText() {
      return Promise.reject(new DOMException("Write permission denied.", "NotAllowedError"));
    };
  }
})();
