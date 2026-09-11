"""Local-only geometry experiment; no ad tags, publisher requests or product edits.

Requires localhost:3000 and Python Playwright with Chromium/WebKit installed.
Browser contexts are disposable. Outputs a review report and ignored screenshots.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
results=[]
with sync_playwright() as p:
 for engine in ['chromium','webkit']:
  browser=getattr(p,engine).launch()
  for width in [320,390,1440]:
   for reserve in [True,False]:
    page=browser.new_page(viewport={'width':width,'height':900})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    assert page.goto('http://localhost:3000/?week=1',wait_until='networkidle').status==200
    assert page.locator('.games-section').count()==1
    assert page.locator('.trust-banner').count()==1
    setup=page.evaluate('''(reserve)=>{
      const slate=document.querySelector('.games-section');
      const slot=document.createElement('aside');slot.id='ad-layout-test';slot.setAttribute('aria-label','Advertisement layout test');
      const available=slate.getBoundingClientRect().width;
      const w=available>=728?728:available>=300?300:250;const h=w===728?90:250;
      slot.style.cssText='margin:32px 0;text-align:center;overflow:hidden;';
      if(reserve)slot.style.minHeight=(h+28)+'px';
      slot.innerHTML='<div style="font-size:11px;line-height:20px;color:#aab5c4">Advertisement · local layout test</div>';
      slate.after(slot);return {creativeWidth:w,creativeHeight:h,available};
    }''',reserve)
    page.locator('#ad-layout-test').scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    before=page.locator('.trust-banner').bounding_box()['y']+page.evaluate('scrollY')
    page.evaluate('''({creativeWidth:w,creativeHeight:h})=>{
      const creative=document.createElement('div');creative.id='test-creative';
      creative.style.cssText=`width:${w}px;height:${h}px;margin:0 auto;background:#26364a;color:#e8eef7;display:grid;place-items:center;font:14px sans-serif;`;
      creative.textContent='Test creative — no ad request';
      document.querySelector('#ad-layout-test').append(creative);
    }''',setup)
    page.wait_for_timeout(100)
    after=page.locator('.trust-banner').bounding_box()['y']+page.evaluate('scrollY')
    filled_shift=round(after-before,3)
    overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
    if reserve:
     assert filled_shift==0,filled_shift
     page.locator('#ad-layout-test').screenshot(path=f'release-recovery/ad-layout-{engine}-{width}.png')
    else: assert filled_shift==setup['creativeHeight'],filled_shift
    page.locator('#test-creative').evaluate('(el)=>el.remove()')
    empty=page.locator('.trust-banner').bounding_box()['y']+page.evaluate('scrollY')
    empty_shift=round(empty-after,3)
    if reserve:assert empty_shift==0,empty_shift
    assert not overflow and not errors
    results.append({'engine':engine,'viewport':width,'reserved':reserve,**setup,'fillDownstreamMovementPx':filled_shift,'emptyDownstreamMovementPx':empty_shift,'documentOverflow':overflow,'pageErrors':errors})
    page.close()
  browser.close()
Path('reviews/ad-layout-feasibility.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
