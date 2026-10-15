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
localStorage.setItem("split.draft", '{"version":2,"bill":{"mode":"even","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"100.00","items":[],"serviceText":"10","sstText":"6","spare":{"rule":"one","personId":"p2"},"nextId":4}}');
