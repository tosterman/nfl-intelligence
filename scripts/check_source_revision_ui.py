"""Verify exact-source explanations on real local revision histories."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    site = json.loads((ROOT / 'data/site.json').read_text())
    games = [game for game in site['games'] if game.get('snapshot')]
    evidence = json.loads((ROOT / 'data/source-record-changes.json').read_text())
    revisions = {row['gameId']: row['fields'] for row in evidence['revisions']}
    results = []
    with sync_playwright() as p:
        for engine in ('chromium', 'webkit'):
            browser = getattr(p, engine).launch()
            for width in (320, 1280):
                page = browser.new_page(viewport={'width': width, 'height': 900})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                for game in games:
                    response = page.goto(f"http://localhost:3000/games/{game['id']}", wait_until='networkidle')
                    assert response.status == 200
                    control = page.get_by_text('Which schedule records changed?', exact=True)
                    assert control.count() == 1, game['id']
                    decline = page.get_by_role('button', name='Decline', exact=True)
                    if decline.is_visible(): decline.click()
                    control.click()
                    panel = control.locator('..')
                    text = panel.inner_text()
                    assert 'do not establish what changed the prediction' in text
                    assert 'older file’s original collection time is unknown' in text
                    expected_others = evidence['changedRecords'] - (game['id'] in revisions)
                    assert f'{expected_others} other existing game records were revised' in text
                    if game['id'] not in revisions:
                        assert 'schedule record did not change' in text
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    assert not errors, errors
                    results.append({'engine': engine, 'width': width, 'gameId': game['id'], 'passed': True})
                    if engine == 'chromium' and width == 320 and game['id'] == '2026_01_ATL_PIT':
                        panel.screenshot(path=str(ROOT / 'reviews/source-revision-mobile.png'))
                page.close()
                print(f'Passed {engine} at {width}px', flush=True)
            browser.close()
    (ROOT / 'reviews/source-revision-browser.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'Passed {len(results)} game, browser and viewport checks')


if __name__ == '__main__': main()
