"""Styled synthetic slate cards; no provider or production-data mutation."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
fragment = (ROOT / 'release-recovery/slate-market-fixture.html').read_text(encoding='utf-8')
results = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch()
        for width in (320, 390, 1280):
            page = browser.new_page(viewport={'width': width, 'height': 844})
            page.goto('http://localhost:3000', wait_until='networkidle')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Actual slate overflow'
            styles = page.locator('link[rel="stylesheet"]').evaluate_all('async els => (await Promise.all(els.map(async el => (await fetch(el.href)).text()))).join("\\n")')
            assert len(styles) > 1000
            page.close()
            page = browser.new_page(viewport={'width': width, 'height': 844})
            page.set_content('<!doctype html><html lang="en"><head><title>Market layout fixture</title><base href="http://localhost:3000/"><style>' + styles + '</style></head><body>' + fragment + '</body></html>', wait_until='networkidle')
            card = page.locator('.game-card')
            expect(card).to_have_count(1)
            assert card.locator('.card-stats').evaluate('el => getComputedStyle(el).display') == 'grid'
            expect(card).to_contain_text('2.0 pts stronger than spread')
            expect(card).to_contain_text('2.0 pts higher')
            expect(card).to_contain_text('Synthetic Sportsbook')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.add_script_tag(path=str(ROOT / 'node_modules/axe-core/axe.min.js'))
            violations = page.evaluate("async () => (await axe.run(document, {runOnly: {type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
            assert not violations, violations
            if engine == 'chromium' and width == 390:
                card.screenshot(path=str(ROOT / 'reviews/slate-market-mobile.png'))
            row = {'engine': engine, 'width': width, 'synthetic': True, 'overflow': False, 'wcagViolations': 0}
            results.append(row)
            print(json.dumps(row), flush=True)
            page.close()
        browser.close()
(ROOT / 'reviews/slate-market-layout.json').write_text(json.dumps(results, indent=2) + '\n')
