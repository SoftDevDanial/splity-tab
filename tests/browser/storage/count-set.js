// The write counter (qa.md How to run). Wraps Storage.prototype.setItem, adds 1 to window.testSetItemCalls on
// each call and then calls the original, so a scenario can prove that a gesture "writes nothing".
// Test-side only, and it never touches localStorage at its top level.
(() => {
  const original = Storage.prototype.setItem;
  window.testSetItemCalls = 0;
  Storage.prototype.setItem = function setItem(key, value) {
    window.testSetItemCalls += 1;
    return original.call(this, key, value);
  };
})();
