"""Real local weather history disclosure and source display checks."""
import json
import gzip
import hashlib
from datetime import datetime
from itertools import product
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
current = json.loads((ROOT / 'data/weather.json').read_text())['games']
ledger = json.loads((ROOT / 'data/weather-ledger.json').read_text())
def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

def expected_issues(game_id):
    """Read the retained upstream periods independently of the UI artifact."""
    anchor = current[game_id]
    rows = [r for r in ledger if r['gameId'] == game_id and
            r['kickoff'] == anchor['kickoff'] and r['venue'] == anchor['venue'] and
            r['locationEvidence'] == anchor['locationEvidence'] and
            instant(r['issuedAt']) <= instant(anchor['issuedAt']) and
            instant(r['retrievedAt']) <= instant(anchor['retrievedAt'])]
    issues = {}
    for row in sorted(rows, key=lambda r: instant(r['retrievedAt'])):
        issues[instant(row['issuedAt'])] = row
    result = []
    for _, row in sorted(issues.items(), reverse=True):
        raw = gzip.decompress((ROOT / 'data/weather-sources' / (row['sourceHash'] + '.json.gz')).read_bytes())
        assert hashlib.sha256(raw).hexdigest() == row['sourceHash']
        period = next(p for p in json.loads(raw)['properties']['periods'] if
                      instant(p['startTime']) <= instant(anchor['kickoff']) < instant(p['endTime']))
        temp = period.get('temperature')
        wind = period.get('windSpeed')
        rain = (period.get('probabilityOfPrecipitation') or {}).get('value')
        result.append({'hash': row['sourceHash'], 'values': {
            'Temperature': 'Unavailable' if temp is None else str(temp) + '°' + period['temperatureUnit'],
            'Wind': (wind + (' ' + period['windDirection'] if period.get('windDirection') else '')) if wind else 'Unavailable',
            'Precipitation chance': 'Unavailable' if rain is None else str(rain) + '%',
            'Outlook': period.get('shortForecast') or 'Unavailable'}})
    assert result, 'The real page requires a retained forecast fixture'
    return result

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
            issues = expected_issues(game_id)
            changes = {} if len(issues) < 2 else {name: (issues[1]['values'][name], value)
                for name, value in issues[0]['values'].items() if issues[1]['values'][name] != value}
            if changes:
                for name, (before, after) in changes.items():
                    expect(section).to_contain_text(f'{name}: {before} → {after}')
                page.get_by_role('link', name='See the weather changes', exact=True).click()
                expect(page.locator('#weather-history')).to_be_focused()
            elif len(issues) == 1:
                expect(section).to_contain_text('first retained forecast issue')
            else:
                expect(section).to_contain_text('same conditions')
            expect(section).to_contain_text('historical outdoor forecasts')
            summary = section.locator('summary')
            expect(section.locator('.weather-history-issue').first).not_to_be_visible()
            summary.focus()
            page.keyboard.press('Enter')
            expect(section.locator('.weather-history-issue').first).to_be_visible()
            assert section.locator('.hash').all_text_contents() == [issue['hash'] for issue in issues]
            expect(section.locator('.weather-history-issue')).to_have_count(len(issues))
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.add_script_tag(path=str(ROOT / 'node_modules/axe-core/axe.min.js'))
            violations = page.evaluate("async () => (await axe.run(document.querySelector('.weather-history'), {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
            assert not violations, violations
            if width == 390 and engine == 'chromium' and game_id == '2026_01_DAL_NYG': section.screenshot(path=str(ROOT / 'reviews/weather-history-mobile.png'))
            summary.focus()
            page.keyboard.press('Enter')
            expect(section.locator('.weather-history-issue').first).not_to_be_visible()
            assert not errors, errors
            report.append({'engine':engine, 'width':width, 'gameId':game_id, 'upstreamSourceHashes':[issue['hash'] for issue in issues], 'changedFields':list(changes), 'keyboardDisclosure':True, 'overflow':False, 'wcagViolations':0})
            page.close()
        browser.close()
(ROOT / 'reviews/weather-history-browser.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
