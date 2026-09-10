"""Read-only owner report. Requires an authenticated Vercel CLI; no stored token.

Outputs only aggregated metrics into ignored release-recovery/. QA visits are
included. Pageview shares are content-consumption measures, not user funnels.
"""
import json, os, shutil, subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

PROJECT='prj_Dnr1nBK1cG7xk2TDgX0tNBMZZafZ'
TEAM='team_DVSLGSRzoGr2qhT7xB8TCmAB'
ROOT=Path(__file__).resolve().parents[1]

def summarize(metrics):
    for result in metrics.values():
        if result.get('status')!='ok': continue
        data=result.get('data',{})
        if not data or any(type(value) is not int or value<0 for value in data.values()):
            raise ValueError('Invalid analytics count')
    total=metrics.get('all',{}).get('data',{}).get('pageviews') if metrics.get('all',{}).get('status')=='ok' else None
    def share(key):
        result=metrics.get(key,{})
        value=result.get('data',{}).get('pageviews') if result.get('status')=='ok' else None
        return value/total if value is not None and total and value<=total else None
    return {'metrics':metrics,'gamePageviewShare':share('games'),'recordPageviewShare':share('record'),
            'methodologyPageviewShare':share('methodology'),
            'interpretation':'Consented production pageviews; includes QA. Shares are not visitor conversion or retention.'}

def query(cli, dataset, window, filter_value=None):
    params={'projectId':PROJECT,'teamId':TEAM,**window}
    if filter_value:params['filter']=filter_value
    endpoint=f'/v1/query/web-analytics/{dataset}/count?'+urlencode(params)
    # On Windows the npm .cmd shim would interpret ampersands in a bare query.
    # Pass the endpoint as data through PowerShell's environment, never shell code.
    if os.name=='nt':
        command=['powershell','-NoProfile','-Command','& vercel api $env:NFL_ANALYTICS_ENDPOINT --scope khnum --raw']
    else:command=[cli,'api',endpoint,'--scope','khnum','--raw']
    run=subprocess.run(command,env={**os.environ,'NFL_ANALYTICS_ENDPOINT':endpoint},capture_output=True,text=True,timeout=30)
    if run.returncode:
        restricted='requires an Enterprise or Pro plan' in run.stderr
        return {'status':'plan-restricted' if restricted else 'unavailable'}
    payload=json.loads(run.stdout)
    # Preserve effective source windows; never silently combine differing windows.
    actual=payload.get('query',{})
    def stamp(value):return datetime.fromisoformat(value.replace('Z','+00:00'))
    if any(stamp(actual[key])!=stamp(window[key]) for key in ['since','until']):
        return {'status':'window-mismatch'}
    fields=['visitors','pageviews'] if dataset=='visits' else ['visitors','count']
    data={field:payload['data'][field] for field in fields}
    return {'status':'ok','data':data}

def main():
    cli=shutil.which('vercel')
    if not cli:raise RuntimeError('Install and authenticate the Vercel CLI first')
    now=datetime.now(timezone.utc).replace(microsecond=0)
    today=now.replace(hour=0,minute=0,second=0)
    # Count endpoints align to UTC days. Include six prior days and partial today.
    window={'since':(today-timedelta(days=6)).isoformat(),'until':(today+timedelta(days=1)).isoformat()}
    filters={'all':None,'games':"startswith(requestPath, '/games/')",'record':"requestPath eq '/performance'",'methodology':"requestPath eq '/methodology'"}
    results={}
    for name,filter_value in filters.items():
        try:results[name]=query(cli,'visits',window,filter_value)
        except (OSError,ValueError,KeyError,subprocess.TimeoutExpired):results[name]={'status':'unavailable'}
    try:results['events']=query(cli,'events',window)
    except (OSError,ValueError,KeyError,subprocess.TimeoutExpired):results['events']={'status':'unavailable'}
    report={'generatedAt':now.isoformat(),'window':window,**summarize(results)}
    output=ROOT/'release-recovery'/'analytics-report.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
