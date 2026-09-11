# Product review: elapsed games and mobile hierarchy

Independent NFL-fan, skeptical-bettor and mobile-UX review used actual Chromium
at 390px on localhost. It found Thursday's 49ers/Rams matchup still featured on
Friday because the retained schedule status remained scheduled. The same card
showed Model forecast alongside Pregame closed.

The spotlight now chooses the earliest future scheduled game with a forecast,
using kickoff time rather than stored status alone. It has no fallback to elapsed
games. Non-final games at or beyond kickoff say Awaiting verified result, without
inventing a live state or final score. The existing deadline-aware clock updates
both selection and card labels at kickoff and when a background tab resumes.

All 158 application tests and TypeScript checking passed. Four real-homepage
browser checks (Chromium/WebKit at 390/1280) advanced the clock across kickoff
without a reload: the label changed, spotlight moved, and advancing beyond the
slate removed the spotlight. No page errors or document overflow occurred.
The independent reviewer confirmed the live 390px page now features Falcons at
Steelers and correctly labels the elapsed game. The final screenshot was inspected.

The broader pre-fix accessibility/runtime baseline covered 30 route/browser/width
combinations: homepage, ratings, performance, methodology, matchup and team pages.
It found no automated WCAG-tagged axe violations, page errors or document overflow;
each page returned 200 and had one H1. Automated checks are not full accessibility
certification. Evidence: `local-product-accessibility.json`.

Remaining UX recommendation: compact the mobile matchup scoreboard/navigation.
The reviewer measured the ATL/PIT analysis starting around 1,339px down the page
after ten navigation links; the full page is long. This is a hierarchy improvement,
not a broken interaction. Existing historical/source definitions and section links
worked. Pre-fix captures use `current-home-*` and `current-atl-pit-*`; the corrected
homepage capture is `current-home-kickoff-fix.png`.
