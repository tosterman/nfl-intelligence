"""Real page disclosure, arithmetic display and accessibility checks."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
site = json.loads((ROOT / 'data/site.json').read_text())
report = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch()
        for width in (320, 390, 1280):
            for game_id in ('2026_01_ATL_PIT', '2026_01_SF_LA'):
                game = next(g for g in site['games'] if g['id'] == game_id)
                page = browser.new_page(viewport={'width': width, 'height': 844})
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto('http://localhost:3000/games/' + game_id, wait_until='networkidle')
                decline = page.get_by_role('button', name='Decline', exact=True)
                if decline.is_visible(): decline.click()
                section = page.locator('#total-explanation').locator('..')
                table = section.get_by_role('table')
                expect(table).to_be_hidden()
                summary = section.get_by_text('See the total calculation', exact=True)
                summary.focus()
                page.keyboard.press('Enter')
                expect(table).to_be_visible()
                expected = f"{game['snapshot']['prediction']['total']:.3f}"
                expect(table.locator('tfoot td')).to_have_text(expected)
                if game['neutral']:
                    row = table.get_by_role('row').filter(has_text='Efficiency venue')
                    expect(row.get_by_role('cell')).to_have_text('0.000')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.add_script_tag(path=str(ROOT / 'node_modules/axe-core/axe.min.js'))
                violations = page.evaluate("async () => (await axe.run(document.querySelector('#total-explanation').parentElement, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
                assert not violations, violations
                summary.focus()
                page.keyboard.press('Enter')
                expect(table).to_be_hidden()
                assert not errors, errors
                row = {'engine': engine, 'width': width, 'gameId': game_id, 'total': expected,
                       'keyboardDisclosure': True, 'overflow': False, 'wcagViolations': 0, 'pageErrors': []}
                report.append(row)
                print(json.dumps(row), flush=True)
                page.close()
        browser.close()
(ROOT / 'reviews/total-explanation-browser.json').write_text(json.dumps(report, indent=2) + '\n')
