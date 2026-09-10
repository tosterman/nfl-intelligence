# Matchup reading flow — September 10, 2026

Added a compact section index immediately below the score overview for pages with forecasts. Readers can jump to model outlook, weather, sportsbook comparison, personnel or price history. These are native fragment links with focusable destination headings; no client navigation bundle is added. Pages without forecasts omit the index because the destinations are not rendered.

Browser verification on Bears/Panthers found all five destinations present. Selecting Personnel set the URL fragment and moved document focus to `personnel-reports`; the destination heading landed 23.5 pixels below the viewport top. At the inspected desktop viewport, document width was 1118 pixels within a 1133-pixel viewport including scrollbar allocation. Screenshot review confirmed the index fits the existing visual hierarchy. Links have a minimum 44-pixel height and wrap on narrow layouts. The existing reduced-motion rule disables smooth scrolling. A new physical-mobile test was not performed for this change.

Production build passed. This navigation addresses discoverability of deep sections; it does not substitute for testing the full reading experience with actual fans or for improving the football model.
