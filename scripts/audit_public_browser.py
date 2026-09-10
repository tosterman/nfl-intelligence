"""Read-only public browser audit; requires installed Playwright browsers and axe-core."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='https://nfl-intelligence-one.vercel.app')
    parser.add_argument('--output', default='reviews/public-browser-audit.json')
    args = parser.parse_args()
    results = []
    axe = Path('node_modules/axe-core/axe.min.js').resolve()
    with sync_playwright() as p:
        for engine, widths in [('chromium', [320, 390, 1440]), ('webkit', [390, 1440])]:
            browser = getattr(p, engine).launch(headless=True)
            for width in widths:
                context = browser.new_context(viewport={'width': width, 'height': 900})
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(args.url, wait_until='networkidle')
                links = page.locator('a[href]').evaluate_all('(links) => links.map(a => a.getAttribute("href"))')
                game = next(h for h in links if h.startswith('/games/'))
                team = next((h for h in links if h.startswith('/teams/')), '/teams/PHI')
                for route in ['/', '/ratings', '/performance', '/methodology', game, team]:
                    errors.clear()
                    response = page.goto(args.url.rstrip('/') + route, wait_until='networkidle')
                    page.add_script_tag(path=str(axe))
                    accessibility = page.evaluate('''async () => {
                      const r = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}});
                      return {violations: r.violations.map(v => ({id:v.id, impact:v.impact, description:v.description, nodes:v.nodes.map(n => ({target:n.target, summary:n.failureSummary}))})), incomplete: r.incomplete.map(v => ({id:v.id, nodes:v.nodes.length})), passes:r.passes.length};
                    }''')
                    geometry = page.evaluate('''() => ({viewport: innerWidth, documentWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth, h1: document.querySelectorAll('h1').length})''')
                    result = {'engine': engine, 'width': width, 'route': route, 'status': response.status if response else None, 'errors': list(errors), 'geometry': geometry, **accessibility}
                    results.append(result)
                    print(json.dumps({k:result[k] for k in ['engine','width','route','status','errors','geometry']} | {'violations': [v['id'] for v in accessibility['violations']]}), flush=True)
                context.close()
            browser.close()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'checkedAt': datetime.now(timezone.utc).isoformat(), 'url':args.url, 'results':results}, indent=2)+'\n', encoding='utf-8')
    if any(r['status'] != 200 or r['errors'] or r['violations'] or r['geometry']['documentWidth'] > r['geometry']['clientWidth'] or r['geometry']['h1'] != 1 for r in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
