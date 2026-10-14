// Storage driver D-c (qa.md How to run, research A3). Storage.prototype.getItem throws, so the boot read of
// the draft fails while the storage object itself is there. Test-side only, and it never touches localStorage.
(() => {
  Storage.prototype.getItem = function getItem() {
    throw new DOMException("test read", "SecurityError");
  };
})();
