"""Verify real collected Highmark weather on the pending-forecast game page."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
GAME = '2026_02_DET_BUF'
weather = json.loads((ROOT / 'data/weather.json').read_text())['games'][GAME]
assert weather['status'] == 'available'
report = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch()
        for width in (320, 390, 1280):
            page = browser.new_page(viewport={'width': width, 'height': 844})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto('http://localhost:3000/games/' + GAME, wait_until='networkidle')
            decline = page.get_by_role('button', name='Decline', exact=True)
            if decline.is_visible(): decline.click()
            section = page.locator('#kickoff-weather').locator('..')
            expect(section).to_contain_text(str(weather['temperature']) + '°' + weather['temperatureUnit'])
            summary = section.get_by_text('Weather source & limitations', exact=True)
            summary.focus(); page.keyboard.press('Enter')
            expect(section).to_contain_text('The postal house number remains unresolved')
            expect(section.get_by_role('link', name='Bills’ officially linked stadium map')).to_have_attribute('href', 'https://map.concept3d.com/?id=2167')
            expect(section).to_contain_text('Weather has no numerical adjustment in this model')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.add_script_tag(path=str(ROOT / 'node_modules/axe-core/axe.min.js'))
            violations = page.evaluate("async () => (await axe.run(document.querySelector('#kickoff-weather').parentElement, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
            assert not violations, violations
            if engine == 'chromium' and width == 390:
                section.screenshot(path=str(ROOT / 'reviews/highmark-weather-mobile.png'))
            assert not errors, errors
            report.append({'engine': engine, 'width': width, 'gameId': GAME, 'sourceHash': weather['sourceHash'], 'overflow': False, 'wcagViolations': 0})
            page.close()
        browser.close()
(ROOT / 'reviews/highmark-weather-browser.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
