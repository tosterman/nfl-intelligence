"""Measure text contrast against rendered backgrounds at changed glyph pixels."""
import io,json,re
from pathlib import Path
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def luminance(rgb):
    c=[v/255 for v in rgb]
    c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
    return .2126*c[0]+.7152*c[1]+.0722*c[2]
def ratio(a,b):
    a,b=sorted((luminance(a),luminance(b)))
    return (b+.05)/(a+.05)
def measure(node):
    node.evaluate("e=>e.scrollIntoView({block:'center',inline:'center',behavior:'instant'})")
    style=node.evaluate('''e=>{const s=getComputedStyle(e);let opacity=1;for(let p=e;p;p=p.parentElement)opacity*=Number(getComputedStyle(p).opacity);return {color:e instanceof SVGElement?s.fill:s.color,svg:e instanceof SVGElement,opacity,text:e.textContent,style:e.getAttribute('style')}}''')
    foreground=[float(v) for v in re.findall(r'[\d.]+',style['color'])]
    if len(foreground)<3:return {'text':style['text'],'status':'unmeasured-color'}
    before=Image.open(io.BytesIO(node.screenshot(animations='disabled'))).convert('RGB')
    try:
        node.evaluate("(e,svg)=>e.style.setProperty(svg?'fill':'color','transparent','important')",style['svg'])
        after=Image.open(io.BytesIO(node.screenshot(animations='disabled'))).convert('RGB')
    finally:
        node.evaluate("(e,s)=>s===null?e.removeAttribute('style'):e.setAttribute('style',s)",style['style'])
    if before.size!=after.size:return {'text':style['text'],'status':'geometry-changed'}
    alpha=(foreground[3] if len(foreground)==4 else 1)*style['opacity']
    ratios=[]
    for a,b in zip(before.getdata(),after.getdata()):
        if max(abs(a[i]-b[i]) for i in range(3))>2:
            fg=[foreground[i]*alpha+b[i]*(1-alpha) for i in range(3)]
            ratios.append(ratio(fg,b))
    return {'text':style['text'],'color':style['color'],'opacity':style['opacity'],'glyphPixels':len(ratios),'minimumRatio':round(min(ratios),3) if ratios else None,'status':'measured' if ratios else 'no-visible-glyphs'}
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch();page=browser.new_page(viewport={'width':390,'height':900},device_scale_factor=1)
    for route,selector in [('/ratings','.team-mark b'),('/performance','.calibration-svg text'),('/games/2026_01_SF_LA','.detail-hero-meta > span')]:
        page.goto('http://localhost:3000'+route,wait_until='networkidle')
        decline=page.get_by_role('button',name='Decline',exact=True)
        if decline.count():decline.click()
        page.evaluate('document.fonts.ready')
        for node in page.locator(selector).all():results.append({'route':route,'selector':selector,**measure(node)})
    browser.close()
report={'method':'Chromium at 390 CSS pixels; original vs text-transparent screenshots identify visible glyph positions; contrast uses computed foreground and underlying rendered RGB at those pixels. Small-text threshold 4.5. No broad WCAG certification.','results':results}
(ROOT/'reviews/rendered-text-contrast.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'records':len(results),'measured':sum(r['status']=='measured' for r in results),'unmeasured':sum(r['status']!='measured' for r in results),'minimum':min(r['minimumRatio'] for r in results if r.get('minimumRatio')),'below4.5':[r for r in results if r.get('minimumRatio',99) is not None and r.get('minimumRatio',99)<4.5]}))
