"""Live-data boundary drill: requires the retained SF/LA edition and eligible stored odds."""
from datetime import datetime,timedelta
from playwright.sync_api import sync_playwright, expect
import json
from pathlib import Path
site=json.loads(Path('data/site.json').read_bytes());game=next(g for g in site['games'] if g['id']=='2026_01_SF_LA');kick=datetime.fromisoformat(game['kickoff']);start=kick-timedelta(seconds=32)
results=[]
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  b=getattr(p,engine).launch()
  for kind in ['detail','slate']:
   page=b.new_page(viewport={'width':320,'height':950});errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.clock.install(time=start);page.clock.pause_at(start+timedelta(seconds=1))
   path='/games/'+game['id'] if kind=='detail' else '/?week=1&q=Rams'
   assert page.goto('http://localhost:3000'+path,wait_until='networkidle').status==200
   if kind=='detail':
    panel=page.locator('.market-panel').filter(has=page.get_by_role('heading',name='Model versus market',exact=True))
    assert panel.get_by_label('Compare sportsbook').count()==1,'Test requires available pregame quotes'
   else:
    panel=page.locator('.game-card[href^="/games/2026_01_SF_LA"]')
    assert panel.count()==1 and 'As of' in panel.inner_text(),'Test requires one filtered card with eligible quotes'
   page.clock.run_for(30900)
   assert 'Pregame closed' not in panel.inner_text() and 'Pregame comparisons close' not in panel.inner_text()
   page.clock.run_for(200)
   if kind=='detail':
    expect(panel).to_contain_text('Pregame comparisons close at kickoff')
    assert panel.get_by_label('Compare sportsbook').count()==0
    assert panel.locator('.book-snapshot').count()==0
   else:
    expect(panel).to_contain_text('Pregame closed')
   assert not errors
   results.append({'engine':engine,'surface':kind,'viewport':320,'pregameVisible100msBefore':True,'closedAfterRenderWhileClockHeld100msAfter':True,'pageErrors':errors})
   page.close()
  b.close()
Path('reviews/kickoff-boundary-browser.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
