"""Read-only browser acceptance against the intended sanitized benchmark."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
ORIGINS = ('http://localhost:3000', 'http://localhost:3001',
           'https://nfl-intelligence-one.vercel.app')


def check(origin, expected):
    results = []
    with sync_playwright() as playwright:
        for engine in ('chromium', 'webkit'):
            browser = getattr(playwright, engine).launch()
            try:
                page = browser.new_page(viewport={'width': 320, 'height': 812})
                page.add_init_script("localStorage.setItem('nfl-analytics-consent','no')")
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                response = page.goto(origin + '/performance', wait_until='networkidle')
                assert response and response.status == 200, 'Performance page did not return HTTP 200'
                assert page.url == origin + '/performance', 'Unexpected redirect'
                section = page.locator('.market-benchmark')
                expect(section).to_have_count(1)
                identity = section.locator('details').last
                identity.locator('summary').focus()
                page.keyboard.press('Enter')
                expect(identity).to_have_attribute('open', '')
                expect(identity.locator('code')).to_have_text(expected['reportHash'])
                count = expected['pairedGameCount']
                headline = (f'{count} completed games with at least one eligible comparison'
                            if count else 'No eligible completed comparisons yet')
                expect(section.locator('.lead')).to_have_text(headline)
                paired = [row for row in expected['books'] if row['pairedGames'] > 0]
                rows = section.locator('tbody tr')
                expect(rows).to_have_count(len(paired))
                for index, row in enumerate(paired):
                    expect(rows.nth(index).locator('th')).to_have_text(f"{row['book']} / {row['market']}")
                    cells = rows.nth(index).locator('td')
                    expect(cells.nth(0)).to_have_text(str(row['pairedGames']))
                    for column, key in ((1, 'modelMae'), (2, 'marketMae')):
                        # Compare the numerical display with its two-decimal tolerance.
                        displayed = float(cells.nth(column).inner_text())
                        assert abs(displayed - row[key]) <= .005000001, 'Displayed error differs from report'
                excluded = expected['excludedBookMarketCount']
                if excluded:
                    games = expected['excludedGameCount']
                    expect(section).to_contain_text(f'{excluded} sportsbook-and-market entries excluded across {games} ' + ('game.' if games == 1 else 'games.'))
                coverage = section.locator('details').first
                coverage.locator('summary').focus()
                page.keyboard.press('Enter')
                expect(coverage).to_have_attribute('open', '')
                expect(coverage.locator('li')).to_have_count(len(expected['books']))
                for index, row in enumerate(expected['books']):
                    entry = coverage.locator('li').nth(index)
                    expect(entry.locator('strong')).to_have_text(f"{row['book']} · {row['market'].title()}")
                    expect(entry).to_contain_text(f"{row['pairedGames']} paired · {row['excludedGames']} excluded")
                page.add_script_tag(path=str(ROOT / 'node_modules/axe-core/axe.min.js'))
                axe = page.evaluate("async()=>{const r=await axe.run(document.querySelector('.market-benchmark'));return {violations:r.violations.map(x=>({id:x.id,nodes:x.nodes.length})),incomplete:r.incomplete.map(x=>x.id)}}")
                overflow = page.evaluate('document.documentElement.scrollWidth>innerWidth')
                assert not overflow and not errors and not axe['violations'], 'Browser or accessibility check failed'
                results.append({'engine': engine, 'status': response.status,
                                'overflow': overflow, 'errors': errors, 'axe': axe})
            finally:
                browser.close()
    return {'checkedAt': datetime.now(timezone.utc).isoformat(),
            'url': origin + '/performance', 'reportHash': expected['reportHash'],
            'auditAt': expected['checkedAt'], 'coverageThrough': expected['coverageThrough'],
            'pairedGameCount': expected['pairedGameCount'],
            'scope': 'Intended report identity, rendered counts and paired errors, keyboard disclosures and scoped axe at 320px',
            'results': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', choices=ORIGINS, default=ORIGINS[0])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Remove this invocation's old proof before checking; a failed run cannot
    # leave a prior successful receipt at the requested output path.
    args.output.unlink(missing_ok=True)
    expected = json.loads((ROOT / 'data/market-benchmark.json').read_text())
    report = check(args.origin, expected)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))
