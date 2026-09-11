"""Team hub / matchup round trips on the real local app."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
report = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch()
        for width in (320, 1280):
            for team, name in [('pit', 'Steelers'), ('buf', 'Bills')]:
                page = browser.new_page(viewport={'width': width, 'height': 844})
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto('http://localhost:3000/teams/' + team, wait_until='networkidle')
                decline = page.get_by_role('button', name='Decline', exact=True)
                if decline.is_visible(): decline.click()
                for selector in ('a.trust-banner', 'table a.small-link'):
                    link = page.locator(selector).first
                    assert 'from=%2Fteams%2F' + team in link.get_attribute('href')
                    link.click()
                    back = page.locator('a.breadcrumb')
                    expect(back).to_contain_text('Back to ' + name + ' intelligence')
                    expect(back).to_have_attribute('href', '/teams/' + team)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    back.focus(); page.keyboard.press('Enter')
                    expect(page).to_have_url('http://localhost:3000/teams/' + team)
                assert not errors, errors
                report.append({'engine': engine, 'width': width, 'team': team, 'nextGameReturn': True, 'scheduleReturn': True, 'overflow': False, 'pageErrors': []})
                page.close()
        page = browser.new_page()
        response = page.goto('http://localhost:3000/games/2026_01_ATL_PIT?from=%2Fteams%2Fpit&from=%2Fteams%2Fatl', wait_until='networkidle')
        assert response.status == 200
        expect(page.locator('a.breadcrumb')).to_have_attribute('href', '/?week=1')
        report.append({'engine': engine, 'duplicateParameterFallback': True})
        browser.close()
(ROOT / 'reviews/team-return-browser.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
