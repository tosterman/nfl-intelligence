"""Real local weather history disclosure and source display checks."""
import json
from itertools import product
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
report = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch()
        for width, game_id in product((320, 390, 1280), ('2026_01_ATL_PIT', '2026_01_DAL_NYG')):
            page = browser.new_page(viewport={'width': width, 'height': 844})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto('http://localhost:3000/games/' + game_id, wait_until='networkidle')
            decline = page.get_by_role('button', name='Decline', exact=True)
            if decline.is_visible(): decline.click()
            section = page.locator('.weather-history')
            if game_id == '2026_01_DAL_NYG':
                expect(section).to_contain_text('Wind: 2 mph W → 3 mph SW')
                page.get_by_role('link', name='See the weather changes', exact=True).click()
                expect(page.locator('#weather-history')).to_be_focused()
            else:
                expect(section).to_contain_text('same conditions')
            expect(section).to_contain_text('historical outdoor forecasts')
            summary = section.locator('summary')
            expect(section.locator('.weather-history-issue').first).not_to_be_visible()
            summary.focus()
            page.keyboard.press('Enter')
            expect(section.locator('.weather-history-issue').first).to_be_visible()
            for identity in section.locator('.hash').all_text_contents():
                assert len(identity) == 64 and all(c in '0123456789abcdef' for c in identity)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.add_script_tag(path=str(ROOT / 'node_modules/axe-core/axe.min.js'))
            violations = page.evaluate("async () => (await axe.run(document.querySelector('.weather-history'), {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
            assert not violations, violations
            if width == 390 and engine == 'chromium' and game_id == '2026_01_DAL_NYG': section.screenshot(path=str(ROOT / 'reviews/weather-history-mobile.png'))
            summary.focus()
            page.keyboard.press('Enter')
            expect(section.locator('.weather-history-issue').first).not_to_be_visible()
            assert not errors, errors
            report.append({'engine':engine, 'width':width, 'gameId':game_id, 'keyboardDisclosure':True, 'overflow':False, 'wcagViolations':0})
            page.close()
        browser.close()
(ROOT / 'reviews/weather-history-browser.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
