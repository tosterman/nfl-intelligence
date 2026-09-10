# Mobile and keyboard follow-up

Requested scope: actual CUA review at 390x844 and 320x700, desktop keyboard focus/order, and responsive game, performance, and ratings pages. No source edits were authorized for this sub-review.

## Execution status

**Not completed: browser surface unavailable in the follow-up session.** The prior review's browser ID 1 was unavailable. `cua.getState()` returned `apps: []` and `browsers: []`; `cua.createBrowserTab('iab', 'http://localhost:3000', {visible:false})` returned `Browser is not available: iab`. The parent reviewer was notified. No viewport override was applied, so none requires resetting. No new screenshots were captured. This report must not be represented as a mobile or keyboard pass.

The earlier desktop rendered review is documented in `2026-09-10-ux-audience.md`. That review remains useful evidence for desktop content and navigation, but is not evidence for responsive layouts or a complete keyboard sequence. Source changed during the follow-up; earlier defects require re-verification after the parent's fixes.

## Specific checks to run when browser access returns

1. **390x844 and 320x700 slate:** confirm document fits the viewport, side-by-side intro/week selector does not squeeze or overflow, toolbar search/sort fits, both teams and forecast labels remain readable, privacy consent does not obscure controls, and one can find the first matchup without excessive scrolling.
2. **Game detail:** verify full team names, venue/date, score versus probability distinction, limits, and contribution chart labels; confirm no chart or table forces page-wide horizontal scrolling.
3. **Performance:** verify 2-column mobile KPI layout, calibration chart labels and expanded table, retrospective disclaimer visibility, and season table scrolling.
4. **Ratings:** verify bounded horizontal table scroll with team context retained and readable offense/defense sign convention; test keyboard access to the scrollable region.
5. **Desktop keyboard:** begin at document top; Tab to skip link, Enter to main; then navigate main header, week control, feature link, filters, search, sort, cards, footer. Check visible focus, logical order, no traps, and focus after filter empty-state recovery.
6. **Expanded disclosures:** activate calibration table, interval assumptions, snapshot fingerprint, and privacy settings with keyboard only; verify sensible focus retention and no obscured focused element.
7. **Changed implementations:** verify displayed `LAR` alias, 11-of-16 close filter count announcement, and Week 2/search round-trip against the current code.

## Source-grounded concerns, not observed mobile defects

### A11Y-01 — P2 candidate: reopened privacy choices precede the focused opener

`src/components/privacy.tsx:41` renders the consent aside before the Privacy settings button at line 57. The opener only calls `setChoice(null)`; no focus movement accompanies the revealed choices. Therefore a keyboard user who activates the opener remains after the new choices in DOM order and ordinarily must Shift+Tab to find them. This is source-backed focus-order risk; parent runtime verification was requested. Move focus into the newly revealed region on deliberate reopening and restore focus when it closes. The initial passive banner need not steal focus.

### A11Y-02 — P2 candidate: horizontal ratings region lacks explicit keyboard entry

`src/app/ratings/page.tsx:25` wraps a wide table in a plain div. The wrapper has no tabIndex or named region and the table contains no interactive descendants. CSS enables overflow scrolling. Browser support for automatically focusing scroll containers varies, so keyboard access cannot be presumed. Parent runtime verification was requested. Provide a named focusable scrolling region with visible focus, or a responsive presentation that avoids lateral scrolling. Preserve table semantics.

### A11Y-03 — P3 recommendation: table row context and page title

Ratings column headers correctly use `scope="col"`; the team cell is an ordinary td. A team row header would improve repeated cell navigation context. Game details in the earlier live AX tree used the away team alone as h1 and the home team as h2, making heading navigation describe a team rather than the matchup. Prefer one descriptive matchup h1, e.g. `49ers at Rams`, while using non-heading labels within the scoreboard.

### A11Y-04 — positive source evidence after fixes

The current slate includes `role="status" aria-live="polite"` on `Showing X of Y games` (`src/components/slate.tsx:276`). This addresses the earlier missing result-announcement implementation, although actual assistive announcement was not tested. The HTML language is English; navigation, search, and sort are labeled; the calibration chart has a text-table alternative; ratings have column-header scopes. These should be retained.

- `globals.css` sets mobile week buttons to 26px and 24px under 380px. Increase comfortable hit areas if layout permits; these values alone are not a proven WCAG violation.
- Mobile limitations and several explanatory labels are 9–10px. Desktop already showed large numeric emphasis with very small caveats; actual mobile legibility needs verification.
- `.intro-row` remains a flex row at narrow widths, while its heading stays 43px under 380px and the week picker has fixed button widths. Test 320px carefully before claiming no overflow.
- Ratings use an overflow wrapper and nowrap table. This can be appropriate, but touch and keyboard usability must be verified in the rendered page.
- Source includes visible focus styling, a skip link, reduced-motion support, and labeled form controls. Their existence does not certify successful full keyboard or assistive-technology operation.

## Three highest-impact weekly-fan improvements

### 1. A useful team destination

Link ratings teams and game participants to a lightweight team view with the next matchup, full schedule, offense/defense baseline, and actual published snapshot changes. Preserve a chosen team locally only if the intended privacy behavior is clear. This gives fans a reason to return without adding unsupported football claims.

### 2. A weekly viewing guide based on declared criteria

Group games by kickoff window and provide `Closest projected games` and `Highest expected scoring` views using existing model data. Explain those criteria, keep uncertainty visible, and offer direct week selection. This turns model output into a concrete Sunday-planning job without claiming betting value or predicting entertainment with certainty.

### 3. A concise, shareable evidence summary

Put a short driver-based takeaway, expected margin, modeled outcome range, source refresh, and missing-input status alongside the score in the first detail viewport. Provide a stable exact-snapshot link for discussion. Keep the full statistical explanation below. This helps fans compare and discuss games while preserving the product's strongest attribute: candid uncertainty.
