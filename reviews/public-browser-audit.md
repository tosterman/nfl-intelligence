# Public browser audit and mobile matchup correction

The retained JSON records 30 real public page visits: slate, ratings, performance, methodology, the first linked matchup and Philadelphia team page. Chromium used widths 320, 390 and 1440; WebKit used 390 and 1440. All returned HTTP 200 with one H1 and no captured JavaScript exceptions. Axe reported no violations for the selected WCAG A/AA rule tags, but returned incomplete color-contrast checks on 25 visits and aria-prohibited-attr checks on five visits. These require manual review; automated absence of violations does not establish WCAG conformance.

The audit correctly failed because the matchup expanded a 320-pixel document to 360 pixels. Its grid child inherited table minimum-content sizing. Setting `min-width: 0` on `.detail-stack` fixes the document overflow while retaining horizontal scrolling inside the comparison and history tables.

The corrected narrow layout then exposed a keyboard-accessibility failure in the comparison table. Its scroll container now has `tabIndex=0`, a region role and a descriptive accessible name. On the actual local site, Chromium and WebKit both verify a 320-pixel document, 244-pixel scroll containers with 300/540-pixel table contents, and a 40-pixel ArrowRight scroll after focusing the comparison region. Both local axe checks report zero violations, with color contrast still requiring manual review. Evidence is in `matchup-mobile-fix.json`.

This is bounded desktop-engine emulation, not testing on physical phones, a human screen-reader acceptance test, or field performance evidence. The local correction is pending production rollout after hosting capacity recovers. The failing public JSON intentionally remains unchanged so the production regression is not concealed by local verification.

Run `python scripts/audit_public_browser.py` to repeat the public audit; `--url` and `--output` can target a different deployment and evidence file. Installed Python Playwright, browser engines and the project's axe-core dependency are required.
