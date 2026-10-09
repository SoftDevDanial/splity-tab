// Test-side platform control (CG-7), the missing API. navigator.clipboard reads as undefined, as it does
// in an insecure context. Nothing reaches the operating system clipboard.
Object.defineProperty(Navigator.prototype, "clipboard", { configurable: true, get: () => undefined });
