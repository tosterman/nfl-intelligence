"""Real slate layout plus isolated actual-component weather timing checks."""
import json, subprocess
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parents[1]
folder = root / 'release-recovery'
folder.mkdir(exist_ok=True)
subprocess.run(['node', '-e', "require('esbuild').buildSync({entryPoints:['tests/fixtures/slate-weather-clock.tsx'],bundle:true,outfile:'release-recovery/slate-weather-clock.js',platform:'browser',jsx:'automatic',define:{'process.env.NODE_ENV':JSON.stringify('production')}})"], cwd=root, check=True)
fixture = folder / 'slate-weather-clock.html'
fixture.write_text('<html><body><div id="root"></div><script src="slate-weather-clock.js"></script></body></html>')
report = []
with sync_playwright() as p:
    for engine in ('chromium', 'webkit'):
        browser = getattr(p, engine).launch()
        for width in (320, 390, 1280):
            page = browser.new_page(viewport={'width': width, 'height': 844})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto('http://localhost:3000/?week=1', wait_until='networkidle')
            decline = page.get_by_role('button', name='Decline', exact=True)
            if decline.is_visible(): decline.click()
            weather = page.locator('.slate-weather')
            assert weather.count() > 0
            expect(weather.first).to_contain_text('Kickoff weather')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.add_script_tag(path=str(root / 'node_modules/axe-core/axe.min.js'))
            violations = page.evaluate("async () => (await axe.run(document.querySelector('.game-grid'), {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations")
            assert not violations, violations
            if engine == 'chromium' and width == 390:
                weather.first.locator('..').screenshot(path=str(root / 'reviews/slate-weather-mobile.png'))
            assert not errors, errors
            report.append({'engine': engine, 'width': width, 'weatherCards': weather.count(), 'overflow': False, 'wcagViolations': 0})
            page.close()
        page = browser.new_page()
        start = datetime(2026, 9, 11, 12, tzinfo=timezone.utc)
        page.clock.install(time=start)
        page.clock.pause_at(start)
        page.goto(fixture.as_uri())
        expect(page.locator('.slate-weather')).to_contain_text('72°F')
        page.clock.run_for(10000)
        expect(page.locator('.slate-weather')).to_contain_text('72°F')
        page.clock.run_for(1)
        expect(page.locator('.slate-weather')).to_contain_text('outdated')
        expect(page.locator('.slate-weather')).not_to_contain_text('72°F')
        page.clock.run_for(9999)
        expect(page.locator('.slate-weather')).to_have_count(0)
        report.append({'engine': engine, 'inclusiveExpiry': True, 'kickoffClosure': True})
        browser.close()
(root / 'reviews/slate-weather-browser.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
