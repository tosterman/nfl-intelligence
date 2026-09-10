"""Cross-feed identity audit; absence is not proof of an invalid injury report."""
import csv,gzip,hashlib,io,json,re
from collections import Counter
from datetime import datetime,timezone,timedelta
from pathlib import Path
from depth_chart import instant
ROOT=Path(__file__).resolve().parents[1]

def report_scope(players):
    scopes={(p['season'],p['type'],p['week']) for p in players}
    if len(scopes)!=1:raise ValueError('Audit requires one report week; historical weeks need their own depth-chart cutoffs')
    season,kind,week=next(iter(scopes))
    return {'season':season,'type':kind,'week':week}

def reconcile_reports(players,rows,cutoff):
    latest={};selected={}
    for row in rows:
        at=instant(row['dt']);team=row['team']
        if at>=cutoff:continue
        if team not in latest or at>latest[team]:latest[team]=at;selected[team]=[]
        if at==latest[team]:selected[team].append(row)
    fresh={team for team,at in latest.items() if cutoff-at<timedelta(hours=30)}
    by_id={}
    for team in fresh:
        for row in selected[team]:
            if row['gsis_id']:by_id.setdefault(row['gsis_id'],[]).append(row)
    result=[]
    for player in players:
        team=player['team'];matches=by_id.get(player['playerId'],[])
        teams=sorted({r['team'] for r in matches})
        names=sorted({r['player_name'].strip() for r in matches if r['team']==team})
        candidates=sorted({(r['gsis_id'],r['player_name'].strip()) for r in selected.get(team,[]) if r['player_name'].strip().casefold()==player['name'].strip().casefold()}) if team in fresh and not matches else []
        if team not in fresh:status='source-unavailable'
        elif not player['playerId']:status='unidentified'
        elif not matches:status='identifier-mismatch' if candidates else 'not-listed'
        elif len(teams)>1:status='ambiguous-teams'
        elif team not in teams:status='team-conflict'
        elif len({n.casefold() for n in names})>1:status='ambiguous-names'
        elif player['name'].strip().casefold() not in {n.casefold() for n in names}:status='name-variant'
        else:status='matched'
        result.append({'playerId':player['playerId'],'name':player['name'],'reportTeam':team,'status':status,
            'season':player.get('season'),'type':player.get('type'),'week':player.get('week'),
            'depthTeams':teams,'depthNamesOnReportTeam':names,'sameNameCandidates':[{'playerId':identifier,'name':name} for identifier,name in candidates],'teamDepthRecordedAt':latest[team].isoformat() if team in latest else None})
    return result

def reconstruct(folder,source_hash):
    if not re.fullmatch('[a-f0-9]{64}',source_hash):raise ValueError('Invalid source hash')
    manifest=json.loads((folder/(source_hash+'.manifest.json')).read_text())
    blocks=[]
    for digest in manifest['chunks']:
        if not re.fullmatch('[a-f0-9]{64}',digest):raise ValueError('Invalid chunk identity')
        raw=gzip.decompress((folder/'raw-chunks'/(digest+'.gz')).read_bytes())
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Corrupt source chunk')
        blocks.append(raw)
    source=b''.join(blocks)
    if manifest['sourceHash']!=source_hash or manifest['bytes']!=len(source) or hashlib.sha256(source).hexdigest()!=source_hash:raise ValueError('Source reconstruction mismatch')
    return source

def main():
    paths={name:ROOT/'data'/file for name,file in [('personnel','personnel.json'),('quarterbacks','quarterbacks.json')]}
    p=json.loads(paths['personnel'].read_text());q=json.loads(paths['quarterbacks'].read_text())
    scope=report_scope(p['players'])
    cutoff=min(instant(p['retrievedAt']),instant(q['retrievedAt']))
    if any(not timedelta(0)<=cutoff-instant(s['assetUpdatedAt'])<timedelta(hours=30) for s in [p,q]):raise ValueError('Sources unavailable at common cutoff')
    if any(r['season']!=q['season'] for r in p['players']):raise ValueError('Source seasons disagree')
    raw=reconstruct(ROOT/'data/quarterback-sources',q['sourceHash'])
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    required={'team','dt','gsis_id','player_name'}
    if not required.issubset(reader.fieldnames or []):raise ValueError('Missing source fields')
    rows=list(reader)
    if any(None in r or any(r.get(k) is None for k in required) for r in rows):raise ValueError('Malformed source row')
    records=reconcile_reports(p['players'],rows,cutoff)
    report={'generatedAt':datetime.now(timezone.utc).isoformat(),'cutoff':cutoff.isoformat(),'season':q['season'],
        'reportScope':scope,
        'meaning':'Identity agreement between two feeds from the same publisher; not independent confirmation of a roster, injury or starter. Not-listed entries are unresolved, not disproved.',
        'counts':dict(Counter(r['status'] for r in records)),'reports':len(records),'depthSourceHash':q['sourceHash'],'personnelSourceHash':p['sourceHash'],
        'inputHashes':{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in paths.items()},
        'codeHash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':records}
    (ROOT/'reviews/personnel-identity-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))

if __name__=='__main__':main()
