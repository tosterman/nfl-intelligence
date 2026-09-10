"""Reproduce the identified cross-feed conflict from pinned registry bytes."""
import csv,gzip,hashlib,io,json
from pathlib import Path
from player_identity import compare_registry_ids
ROOT=Path(__file__).resolve().parents[1]

def main():
    source=json.loads((ROOT/'reviews/player-registry-source.json').read_text())
    raw=gzip.decompress((ROOT/'reviews/player-identity-source.csv.gz').read_bytes())
    if len(raw)!=source['bytes'] or hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('Registry source mismatch')
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    audit_path=ROOT/'reviews/personnel-identity-audit.json';audit=json.loads(audit_path.read_text())
    findings=[]
    for r in audit['records']:
        for candidate in r.get('sameNameCandidates',[]):
            findings.append({'reportId':r['playerId'],'depthChartId':candidate['playerId'],'reportScope':{k:r[k] for k in ['season','type','week','reportTeam']},
                'comparison':compare_registry_ids(rows,r['playerId'],candidate['playerId'])})
    report={'source':source,'auditHash':hashlib.sha256(audit_path.read_bytes()).hexdigest(),
        'codeHashes':{name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in ['player_identity.py','investigate_personnel_id.py']},'findings':findings}
    (ROOT/'reviews/player-identity-investigation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(findings,indent=2))

if __name__=='__main__':main()
