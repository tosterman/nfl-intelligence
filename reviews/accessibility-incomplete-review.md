# Review of inconclusive accessibility findings

The public audit's five `aria-prohibited-attr` findings all came from the slate's filter container. The detailed local investigation identifies `<div class="filters" aria-label="Filter games">`: a generic div does not reliably support that accessible name. It now has `role="group"`, retaining the existing labeled buttons and `aria-pressed` state.

Chromium and WebKit both verified the named group, keyboard Enter activation of Close matchups, Space activation of All games, and the corresponding pressed-state changes. Both now report zero violations and zero incomplete results for this ARIA rule. Evidence: `filter-accessibility-fix.json`. This is browser verification, not a human screen-reader acceptance test.

The detailed JSON also retains contrast uncertainties from four local pages at 390 pixels. Ratings: 32 badge SVG backgrounds and 32 partially obscured table cells. Matchup: gradients, badge SVGs and occluded/overlapping content. Performance: overlapping backgrounds and SVG content. Slate: 32 badge SVG backgrounds. The checker could not establish those background colors; these are neither proven contrast failures nor accepted passes. Human visual review and targeted contrast measurements remain necessary, including scrolled and consent-banner states. No contrast rule was disabled and no text was hidden merely to silence the checker.

The group-role correction is on the development branch pending production release.


## Targeted rendered contrast and chart readability

A subsequent local Chromium pass measured 45 visible text elements: all 32 ratings badges, 11 calibration-chart labels, and two matchup-gradient metadata elements. The minimum nominal foreground/background contrast was 4.883:1; none fell below 4.5:1. All measured elements had fully opaque ancestor chains. Backgrounds were sampled at visible glyph pixels using paired original/text-transparent screenshots; this does not measure anti-aliased text readability or chart graphics. Initial off-center captures had ten zero-glyph results because content was obscured; they were not accepted as passes. Centered recapture measured all 45 with no unmeasured targets. Exact results and source hashes are in `rendered-text-contrast.json`.

Independent UX review also identified the chart's scaled labels as too small. Enlarged tick/caption fonts and adjusted plot margins now keep the smallest label at approximately 12.5 CSS pixels at320, 15.6 at390, and13.9 at1440. Chromium and WebKit verified these sizes and no document overflow at all three widths. The320 layout was visually inspected. The accessible values table remains available. Evidence: `calibration-label-browser.json`.

This closes the tested badge/chart-label/gradient contrast uncertainty. Partially obscured numeric cells, consent-overlay states, chart non-text contrast, keyboard/screen-reader and real-device acceptance remain separate checks. No contrast rule was disabled, and no user-visible text was removed to obtain passing measurements.
