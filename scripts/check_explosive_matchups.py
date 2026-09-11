"""Verify rendered matchup counts against the retained artifact on localhost."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    site = json.loads((ROOT / 'data/site.json').read_text())
    evidence = json.loads((ROOT / 'data/explosive-plays.json').read_text())
    games = [g for g in site['games'] if g.get('snapshot')]
    report = []
    with sync_playwright() as playwright:
        for engine in ('chromium', 'webkit'):
            browser = getattr(playwright, engine).launch()
            page = browser.new_page(viewport={'width': 320, 'height': 900})
            for game in games:
                errors = []
                handler = lambda error: errors.append(str(error))
                page.on('pageerror', handler)
                page.goto(f"http://localhost:3000/games/{game['id']}", wait_until='networkidle')
                decline = page.get_by_role('button', name='Decline', exact=True)
                if decline.is_visible():
                    decline.click()
                panel = page.locator('.explosive-panel')
                assert panel.count() == 1, game['id']
                expected = []
                for offense, defense in [(game['away'], game['home']), (game['home'], game['away'])]:
                    for kind in ('passing', 'rushing'):
                        for team, side in [(offense, 'offense'), (defense, 'defense')]:
                            counts = evidence['teams'][team][side][kind]
                            expected.append([f"{100 * counts['explosive'] / counts['plays']:.1f}%",
                                             f"{counts['explosive']} / {counts['plays']} credited plays"])
                actual = panel.locator('.explosive-rate').evaluate_all(
                    '(nodes) => nodes.map(n => [n.querySelector("strong").textContent, n.querySelector("small").textContent])')
                assert actual == expected, (game['id'], actual, expected)
                assert 'Each eligible play counts equally' in panel.inner_text()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                assert not errors, errors
                report.append({'gameId': game['id'], 'engine': engine, 'width': 320,
                               'verifiedRates': len(actual), 'pageErrors': errors, 'overflow': False})
                page.remove_listener('pageerror', handler)
            browser.close()
    (ROOT / 'reviews/explosive-matchup-count-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"Verified {len(report)} browser/game combinations and {sum(r['verifiedRates'] for r in report)} displayed rates")


if __name__ == '__main__':
    main()
