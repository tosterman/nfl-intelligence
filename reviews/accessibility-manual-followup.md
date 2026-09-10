# Follow-up on chart and table audit uncertainty

At 320px in Chromium and WebKit, computed calibration-label fill is `rgb(184,193,205)` against the panel's `rgb(23,26,31)` background. Standard sRGB relative-luminance calculation gives a 9.591:1 contrast ratio. The containing panel screenshot was visually inspected: axis labels and explanatory text remain visible. An SVG-only screenshot clipped overflow at its capture boundary, so the panel capture was used to inspect the actual surrounding layout.

The performance-by-phase table was focused and scrolled with ArrowRight. After the browser completed scrolling, both engines reached `scrollLeft=59` for a 301px table inside a 242px region. The final column's full bounds were inside the region. Its screenshot was inspected. The earlier instantaneous check observed an unfinished animation at 29px; waiting for the final geometry resolved the harness failure without changing the application.

These results resolve the specific chart-text contrast and rightmost-column reachability questions from this bounded follow-up. They do not convert every axe incomplete result into a pass: decorative team badge rendering, other clipped regions, assistive-technology use, and physical-device acceptance retain their own scope. Exact measured results are in `accessibility-manual-followup.json`. No production CSS or model data changed.
