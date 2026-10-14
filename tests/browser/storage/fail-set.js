// Storage driver D-a (qa.md How to run, research A3). Storage.prototype.setItem throws a test-made
// QuotaExceededError until a "test:storage" CustomEvent with detail false is dispatched on window, and then
// calls the original. Test-side only. It never touches localStorage at its top level, because an init script
// also runs in the blank first document, where storage access is denied.
(() => {
  const original = Storage.prototype.setItem;
  let failing = true;
  window.addEventListener("test:storage", (event) => {
    if (event.detail === false) failing = false;
  });
  Storage.prototype.setItem = function setItem(key, value) {
    if (failing) throw new DOMException("test quota", "QuotaExceededError");
    return original.call(this, key, value);
  };
})();
