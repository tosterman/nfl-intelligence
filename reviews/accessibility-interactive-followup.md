# Interactive accessibility follow-up

Chromium axe checks at 320px and 1440px covered the defense-sorted ratings page and performance page with the first diagnostic table and metric guide open. All four checks reported zero WCAG 2 A/AA and 2.1 AA violations. Color-contrast checks remained incomplete for clipped table content, SVG labels and decorative team marks. Zero reported violations is not full WCAG acceptance.

Direct computed-color checks at 320px found contrast ratios of 11.52:1 for the selected ratings link and 15.14:1 for representative visible diagnostic row-header and numeric cells. These checks verify those foreground/background pairs, not every clipped row or assistive-technology interaction. Earlier keyboard checks cover opening/closing tables and reaching the final column.

The summary JSON records incomplete counts and sample targets. The compressed full JSON preserves every automated result and its uncompressed SHA-256 identity. `accessibility-interactive-contrast.json` records the specific computed colors. No application changes were indicated by this bounded follow-up; broader assistive-technology and real-device acceptance remain open.
