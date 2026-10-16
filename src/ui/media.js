// The desktop width, the one query the app shares with system.css, whose rules show the card and hide the strip from
// 1024 px. The Splits sheet closes itself when it starts to match (R50) and P1 changes its place (R52), so both cross
// 1024 px on the same definition as the CSS.
export const DESKTOP = window.matchMedia("(min-width: 1024px)");
