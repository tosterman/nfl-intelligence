"""Browser layout checks for synthetic populated samples, using actual app CSS."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
fragment = (ROOT / 'release-recovery/weekly-matchup-fixture.html').read_text(encoding='utf-8')
results = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch()
        for width in (320, 390, 1280):
            page = browser.new_page(viewport={'width': width, 'height': 844})
            page.goto('http://localhost:3000', wait_until='networkidle')
            styles = page.locator('link[rel="stylesheet"]').evaluate_all('async (els) => (await Promise.all(els.map(async el => (await fetch(el.href)).text()))).join("\\n")')
            assert len(styles) > 1000, 'Application stylesheet missing'
            # A separate document prevents the development app's existing React
            # and hot-reload scripts from replacing the static fixture DOM.
            page.close()
            page = browser.new_page(viewport={'width': width, 'height': 844})
            page.set_content('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Weekly layout fixture</title><base href="http://localhost:3000/"><style>' + styles + '</style></head><body>' + fragment + '</body></html>', wait_until='networkidle')
            assert page.locator('.panel').first.evaluate('(el) => getComputedStyle(el).backgroundColor') == 'rgb(23, 26, 31)', 'Application panel styles not applied'
            expect(page.get_by_text('Synthetic samples for browser testing.', exact=False)).to_be_visible()
            expect(page.get_by_role('table')).to_have_count(4)
            expect(page.get_by_text('11 / 129 plays', exact=True)).to_have_count(1)
            expect(page.get_by_text('7 / 120 plays', exact=True)).to_have_count(1)
            first_cells = page.get_by_role('table').first.locator('tbody tr').first.locator('td')
            expect(first_cells.nth(0)).to_contain_text('11 / 129 plays')
            expect(first_cells.nth(1)).to_contain_text('7 / 120 plays')
            expect(page.get_by_text('0 / 0 possessions', exact=True)).to_have_count(2)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.add_script_tag(path=str(ROOT / 'node_modules/axe-core/axe.min.js'))
            violations = page.evaluate("async () => (await axe.run(document, {runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
            assert not violations, violations
            if engine == 'chromium' and width == 390:
                page.screenshot(path=str(ROOT / 'reviews/weekly-populated-fixture.png'), full_page=True)
            row = {'engine': engine, 'width': width, 'syntheticFixture': True, 'tables': 4, 'overflow': False, 'wcagViolations': 0}
            results.append(row)
            print(json.dumps(row), flush=True)
            page.close()
        browser.close()
(ROOT / 'reviews/weekly-populated-browser.json').write_text(json.dumps(results, indent=2) + '\n')
