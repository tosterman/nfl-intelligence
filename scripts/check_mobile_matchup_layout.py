"""Measure mobile analysis placement and verify section navigation."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--baseline', action='store_true')
args = parser.parse_args()
baseline_path = ROOT / 'reviews/mobile-matchup-baseline.json'
baseline = {} if args.baseline else { (row['engine'], row['width'], row['gameId']): row for row in json.loads(baseline_path.read_text()) }
results = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        print(f'Launching {engine}', flush=True)
        browser = getattr(p, engine).launch()
        for width in (320, 390, 1280):
            page = browser.new_page(viewport={'width': width, 'height': 844})
            for game in ('2026_01_ATL_PIT', '2026_01_SF_LA'):
                print(f'Checking {engine} {width}px {game}', flush=True)
                page.goto(f'http://localhost:3000/games/{game}', wait_until='networkidle')
                y = page.locator('#model-read').evaluate('(el) => el.getBoundingClientRect().top + scrollY')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                row = {'engine': engine, 'width': width, 'gameId': game, 'modelReadY': y}
                if not args.baseline:
                    old = baseline[(engine, width, game)]['modelReadY']
                    row['pixelsEarlier'] = old - y
                    assert old - y >= 120 if width < 600 else abs(old - y) < 2, row
                    decline = page.get_by_role('button', name='Decline', exact=True)
                    if decline.is_visible(): decline.click()
                    links = page.get_by_role('navigation', name='Matchup sections').get_by_role('link')
                    for index in range(links.count()):
                        link = links.nth(index); target = link.get_attribute('href')
                        assert link.bounding_box()['height'] >= 44
                        link.focus(); page.keyboard.press('Enter')
                        page.wait_for_url('**' + target)
                        assert page.locator(target).is_visible()
                    if engine == 'chromium' and width == 390 and game == '2026_01_ATL_PIT':
                        page.evaluate('scrollTo(0, 0)')
                        page.screenshot(path=str(ROOT / 'reviews/mobile-matchup-compact.png'))
                results.append(row)
                print(json.dumps(row), flush=True)
            page.close()
        print(f'Closing {engine}', flush=True)
        browser.close()
        print(f'Closed {engine}', flush=True)
output = baseline_path if args.baseline else ROOT / 'reviews/mobile-matchup-layout.json'
output.write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results))
