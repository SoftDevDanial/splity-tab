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
localStorage.setItem("split.draft", '{"version":2,"bill":{"mode":"item","people":[{"id":"p1","name":"Aisyah"},{"id":"p2","name":"Ben"},{"id":"p3","name":"Chen"}],"subtotalText":"","items":[{"id":"i4","name":"Nasi lemak ayam","priceText":"15.90","who":["p1"]},{"id":"i5","name":"Char kuey teow","priceText":"13.50","who":["p2"]},{"id":"i6","name":"Mee goreng mamak","priceText":"12.00","who":["p3"]},{"id":"i7","name":"Satay, 10 sticks","priceText":"18.00","who":["p1","p3"]}],"serviceText":"35","sstText":"6","spare":{"rule":"top"},"nextId":8}}');
