// Test-side platform control (CG-7). The default init script of every browser context.
// Replaces the clipboard write so a test never reaches the operating system clipboard, not even to read
// it. The app gets no hook and calls the real navigator.clipboard.writeText, which is what this replaces.
(() => {
  window.testClipboardText = null;
  window.testClipboardWrites = 0;
  if (typeof Clipboard === "function") {
    Clipboard.prototype.writeText = function writeText(text) {
      window.testClipboardText = String(text);
      window.testClipboardWrites += 1;
      return Promise.resolve();
    };
  }
})();
localStorage.setItem("split.draft", 'not json');
