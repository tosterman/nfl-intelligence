"""Browser regression: historical context does not require a model forecast."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    site = json.loads((ROOT / 'data/site.json').read_text())
    pending = [g for g in site['games'] if not g.get('snapshot')]
    games = [next(g for g in pending if g['week'] == week) for week in (1, 2, 18)]
    report = []
    with sync_playwright() as p:
        for name in ('chromium', 'webkit'):
            browser = getattr(p, name).launch()
            for width in (320, 1280):
                page = browser.new_page(viewport={'width': width, 'height': 900})
                for game in games:
                    page.goto(f"http://localhost:3000/games/{game['id']}", wait_until='networkidle')
                    assert page.locator('.explosive-panel').count() == 1, game['id']
                    assert page.locator('.red-zone-panel').count() == 1, game['id']
                    assert page.locator('#model-read').count() == 0
                    if game['status'] == 'final':
                        assert page.get_by_role('heading', name='No rewritten pregame prediction.', exact=True).count() == 1
                    else:
                        assert page.get_by_text('No model forecast available', exact=True).count() == 1
                        decline = page.get_by_role('button', name='Decline', exact=True)
                        if decline.is_visible():
                            decline.click()
                        for label, target in [('Big-play history', '#explosive-heading'), ('Inside the 20', '#red-zone-heading')]:
                            page.get_by_role('link', name=label, exact=True).click()
                            page.wait_for_url('**' + target)
                            assert page.locator(target).is_visible()
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    report.append({'engine': name, 'width': width, 'gameId': game['id'],
                                   'historicalPanels': 2, 'modelForecast': False, 'overflow': False})
                page.close()
            browser.close()
    (ROOT / 'reviews/pending-matchup-history.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Passed {len(report)} browser, viewport and game combinations')


if __name__ == '__main__': main()
