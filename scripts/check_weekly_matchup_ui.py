"""Verify real current weekly panels and expiry in local browsers."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
deadline = json.loads((ROOT / 'data/weekly-matchup-context.json').read_text())['freshUntil']
results = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch()
        for width in (320, 390, 1280):
            for game in ('2026_01_ATL_PIT', '2026_01_NE_SEA'):
                page = browser.new_page(viewport={'width': width, 'height': 844})
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto('http://localhost:3000/games/' + game, wait_until='networkidle')
                decline = page.get_by_role('button', name='Decline', exact=True)
                if decline.is_visible():
                    decline.click()
                expect(page.get_by_role('heading', name='This season · 2026', exact=True)).to_have_count(2)
                expect(page.get_by_text('No earlier games from this season qualify', exact=False)).to_have_count(2)
                expect(page.get_by_role('heading', name='Last season · 2025', exact=True)).to_have_count(2)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                if engine == 'chromium' and width == 390 and game == '2026_01_ATL_PIT':
                    page.locator('.explosive-panel').screenshot(path=str(ROOT / 'reviews/weekly-matchup-mobile.png'))
                page.clock.install(time=deadline - 1000)
                page.clock.pause_at(deadline - 500)
                page.clock.run_for(1500)
                expect(page.get_by_text('Current-season evidence has expired.', exact=False)).to_have_count(2)
                expect(page.get_by_role('heading', name='Last season · 2025', exact=True)).to_have_count(2)
                assert not errors, errors
                row = {'engine': engine, 'width': width, 'gameId': game, 'emptySample': True, 'expiry': True, 'overflow': False}
                results.append(row)
                print(json.dumps(row), flush=True)
                page.close()
        browser.close()
(ROOT / 'reviews/weekly-matchup-browser.json').write_text(json.dumps(results, indent=2) + '\n')
