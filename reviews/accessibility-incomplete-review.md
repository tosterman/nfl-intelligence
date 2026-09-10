# Review of inconclusive accessibility findings

The public audit's five `aria-prohibited-attr` findings all came from the slate's filter container. The detailed local investigation identifies `<div class="filters" aria-label="Filter games">`: a generic div does not reliably support that accessible name. It now has `role="group"`, retaining the existing labeled buttons and `aria-pressed` state.

Chromium and WebKit both verified the named group, keyboard Enter activation of Close matchups, Space activation of All games, and the corresponding pressed-state changes. Both now report zero violations and zero incomplete results for this ARIA rule. Evidence: `filter-accessibility-fix.json`. This is browser verification, not a human screen-reader acceptance test.

The detailed JSON also retains contrast uncertainties from four local pages at 390 pixels. Ratings: 32 badge SVG backgrounds and 32 partially obscured table cells. Matchup: gradients, badge SVGs and occluded/overlapping content. Performance: overlapping backgrounds and SVG content. Slate: 32 badge SVG backgrounds. The checker could not establish those background colors; these are neither proven contrast failures nor accepted passes. Human visual review and targeted contrast measurements remain necessary, including scrolled and consent-banner states. No contrast rule was disabled and no text was hidden merely to silence the checker.

The group-role correction is on the development branch pending production release.
