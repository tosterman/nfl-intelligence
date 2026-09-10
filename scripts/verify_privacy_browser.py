"""Verify local privacy preference synchronization and keyboard focus."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def main():
    results = []
    with sync_playwright() as p:
        for engine in ('chromium', 'webkit'):
            browser = getattr(p, engine).launch()
            context = browser.new_context(viewport={'width': 320, 'height': 800})
            first, second = context.new_page(), context.new_page()
            for page in (first, second):
                page.goto('http://localhost:3000/ratings', wait_until='networkidle')
                expect(page.get_by_role('button', name='Decline', exact=True)).to_be_visible()
            first.get_by_role('button', name='Privacy settings', exact=True).focus()
            first.keyboard.press('Enter')
            expect(first.get_by_role('button', name='Decline', exact=True)).to_be_focused()
            second.get_by_role('button', name='Decline', exact=True).click()
            banner = first.get_by_role('complementary', name='Analytics privacy choice')
            expect(banner).not_to_be_visible()
            second.evaluate('localStorage.setItem("unrelated-setting", "changed")')
            expect(banner).not_to_be_visible()
            first.reload(wait_until='networkidle')
            expect(banner).not_to_be_visible()
            settings = first.get_by_role('button', name='Privacy settings', exact=True)
            settings.focus()
            first.keyboard.press('Enter')
            decline = first.get_by_role('button', name='Decline', exact=True)
            expect(decline).to_be_focused()
            first.keyboard.press('Enter')
            expect(banner).not_to_be_visible()
            expect(settings).to_be_focused()
            second.evaluate('localStorage.setItem("nfl-analytics-consent", "invalid")')
            expect(banner).to_be_visible()
            first.reload(wait_until='networkidle')
            expect(banner).to_be_visible()
            first.get_by_role('button', name='Decline', exact=True).click()
            second.evaluate('localStorage.clear()')
            expect(banner).to_be_visible()
            first.get_by_role('button', name='Allow analytics', exact=True).click()
            expect(banner).not_to_be_visible()
            expect(second.get_by_role('complementary', name='Analytics privacy choice')).not_to_be_visible()
            settings.focus()
            first.keyboard.press('Enter')
            expect(decline).to_be_focused()
            with first.expect_navigation(wait_until='networkidle'):
                first.keyboard.press('Enter')
            expect(banner).not_to_be_visible()
            assert first.evaluate('localStorage.getItem("nfl-analytics-consent")') == 'no'
            results.append({'engine': engine, 'width': 320, 'passed': [
                'cross-tab decline closes banner', 'unrelated storage preserves decline',
                'decline survives reload', 'keyboard settings opens with decline focused',
                'saving decline without reload returns focus to settings', 'invalid choice is undecided live and after reload',
                'clearing storage restores choice prompt', 'already-open settings activation focuses decline',
                'allow synchronizes across tabs', 'revoking allow reloads with decline retained'],
                'documentWidth': first.evaluate('document.documentElement.scrollWidth')})
            assert results[-1]['documentWidth'] == 320
            browser.close()
    output = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'url': 'http://localhost:3000/ratings',
              'sourceHash': hashlib.sha256((ROOT / 'src/components/privacy.tsx').read_bytes()).hexdigest(),
              'results': results, 'limitations': 'Local browser emulation; no real-device or human screen-reader acceptance. Does not test provider ingestion.'}
    (ROOT / 'reviews/privacy-choice-browser.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results))


if __name__ == '__main__':
    main()

