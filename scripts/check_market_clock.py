"""Browser test of actual market components with isolated fixed-time fixtures.
Requires Python Playwright browsers and the project's installed esbuild dependency.
No server, provider credentials, acquisition or production-file edits are needed.
"""
import json,subprocess
from datetime import datetime,timedelta,timezone
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[1]
folder=root/'release-recovery';folder.mkdir(exist_ok=True)
subprocess.run(['node','-e',"require('esbuild').buildSync({entryPoints:['tests/fixtures/market-clock.tsx'],bundle:true,outfile:'release-recovery/market-clock-fixture.js',platform:'browser',jsx:'automatic',define:{'process.env.NODE_ENV':JSON.stringify('production')}})"],cwd=root,check=True)
(folder/'market-clock-fixture.html').write_text('<html><head><meta charset="utf-8"></head><body><div id="root"></div><script src="market-clock-fixture.js"></script></body></html>')
start=datetime(2026,9,10,15,59,49,tzinfo=timezone.utc);out=[]
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch();page=b.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('https://**/*',lambda route:route.abort())
  page.clock.install(time=start);page.clock.pause_at(start+timedelta(seconds=1))
  page.goto((folder/'market-clock-fixture.html').as_uri(),wait_until='load')
  expect(page.get_by_label('Compare sportsbook')).to_have_count(1)
  live=page.get_by_role('status',name='Current market availability')
  assert live.count()==1,'Market changes need a persistent status region'
  expect(live).to_contain_text('spread available')
  expect(page.locator('#card')).to_contain_text('Model total:')
  row=page.get_by_role('row').filter(has_text='LAR spread').first
  expect(row.locator('td').last).to_contain_text('-3.5')
  expect(page.locator('#weather')).to_have_text('Weather fixture')
  expect(page.locator('#personnel')).to_have_text('Personnel fixture')
  page.clock.run_for(9500)
  expect(page.locator('#weather')).to_have_text('Weather fixture')
  expect(page.locator('#personnel')).to_contain_text('has expired')
  page.clock.run_for(1)
  expect(page.locator('#weather')).to_contain_text('outdated')
  page.clock.run_for(499)
  expect(row.locator('td').last).to_contain_text('-3.5')
  page.clock.run_for(1)
  expect(row.locator('td').last).to_contain_text('Not quoted')
  expect(page.locator('#card')).to_contain_text('Spread not quoted')
  expect(live).to_contain_text('spread unavailable')
  expect(live).to_contain_text('Model comparisons withheld')
  expect(page.locator('#card')).not_to_contain_text('Model total:')
  expect(page.locator('p').filter(has_text='The model inputs are stale.')).to_have_count(1)
  expect(page.get_by_role('row').filter(has_text='Total').first.locator('td').last).to_contain_text('48.5')
  page.clock.run_for(20000)
  expect(page.get_by_label('Compare sportsbook')).to_have_count(0)
  expect(page.locator('#card')).to_contain_text('No eligible prices')
  page.clock.run_for(40000)
  expect(page.locator('#card')).to_contain_text('Snapshot expired')
  page.clock.fast_forward(2*3600000)
  expect(page.locator('#card')).to_contain_text('Pregame closed')
  expect(live).to_contain_text('Pregame comparisons close at kickoff')
  assert not errors,errors
  out.append({'engine':engine,'inclusiveSixHourBoundary':True,'individualSpreadExpiry':True,'independentTotalExpiry':True,'modelFreshnessBoundary':True,'feedExpiry':True,'kickoffClosure':True,'persistentAvailabilityStatus':True,'personnelExactExpiry':True,'weatherInclusiveExpiry':True,'pageErrors':errors})
  b.close()
(root/'reviews/market-clock-fixture-browser.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
