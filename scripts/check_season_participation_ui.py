"""Real-page seasonal disclosures, persisting each case before browser shutdown."""
import json
import os
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
report = []
target = ROOT / 'reviews/season-participation-browser.json'

def shutdown_timeout():
    print('Browser cleanup exceeded 20 seconds; completed case evidence is retained.', flush=True)
    os._exit(2)

with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch(timeout=20000)
        for width in (320, 1280):
            page = browser.new_page(viewport={'width': width, 'height': 844})
            page.set_default_timeout(20000)
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto('http://localhost:3000/games/2026_01_ATL_PIT', wait_until='networkidle')
            decline = page.get_by_role('button', name='Decline', exact=True)
            if decline.is_visible(): decline.click()
            details = page.locator('details.player-usage').first
            details.locator('summary').focus()
            page.keyboard.press('Enter')
            expect(details.get_by_role('heading', name='2026 season · Earlier weeks')).to_be_visible()
            expect(details.get_by_role('heading', name='Prior-season history')).to_be_visible()
            text = details.locator('.season-participation').inner_text()
            assert 'No verified earlier-week appearances' in text or 'not verified for this report' in text
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.add_script_tag(path=str(ROOT / 'node_modules/axe-core/axe.min.js'))
            violations = page.evaluate("async()=> (await axe.run(document.querySelector('details.player-usage'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
            assert not violations, violations
            assert not errors, errors
            row = {'engine': engine, 'width': width, 'keyboardDisclosure': True, 'separateSeasons': True,
                   'noHindsightSample': True, 'overflow': False, 'axeViolations': 0}
            report.append(row)
            target.write_text(json.dumps(report, indent=2)+'\n')
            print(json.dumps(row), flush=True)
            if engine == 'chromium' and width == 320:
                page.screenshot(path=str(ROOT / 'reviews/season-participation-mobile.png'))
            page.close()
        timer = threading.Timer(20, shutdown_timeout)
        timer.start()
        browser.close()
        timer.cancel()
print('All four browser cases and cleanup completed.', flush=True)
