"""Exercise the real homepage across kickoff without refreshing the page."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
kickoff = datetime(2026, 9, 11, 0, 35, tzinfo=timezone.utc)
results = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch()
        for width in (390, 1280):
            page = browser.new_page(viewport={'width': width, 'height': 900})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.clock.install(time=kickoff - timedelta(seconds=2))
            page.clock.pause_at(kickoff - timedelta(seconds=1))
            page.goto('http://localhost:3000/?week=1', wait_until='networkidle')
            featured = page.locator('.spotlight a[href*="/games/"]')
            expect(featured).to_have_attribute('href', __import__('re').compile('SF_LA'))
            card = page.locator('.game-card[href*="2026_01_SF_LA"]')
            expect(card.locator('.card-top')).to_contain_text('Model forecast')
            page.clock.run_for(1000)
            expect(card.locator('.card-top')).to_contain_text('Awaiting verified result')
            expect(featured).not_to_have_attribute('href', __import__('re').compile('SF_LA'))
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.clock.fast_forward(7 * 86400000)
            expect(page.locator('.spotlight')).to_have_count(0)
            assert not errors, errors
            results.append({'engine': engine, 'width': width, 'kickoffStatusTransition': True,
                            'spotlightMovesWithoutReload': True, 'noElapsedFallback': True, 'pageErrors': errors})
            page.close()
        browser.close()
(ROOT / 'reviews/slate-timing-browser.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results))
