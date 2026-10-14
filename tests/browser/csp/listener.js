// Test-side platform observation (R38). An init script of every context the suite opens the app in.
// Records each Content Security Policy violation of the page in window.testCspViolations, the detector that works
// the same in Chromium and WebKit, whose console texts differ. The app gets no hook and never reads it.
(() => {
  window.testCspViolations = [];
  document.addEventListener("securitypolicyviolation", (event) => {
    window.testCspViolations.push({ violatedDirective: event.violatedDirective, blockedURI: event.blockedURI });
  });
})();
