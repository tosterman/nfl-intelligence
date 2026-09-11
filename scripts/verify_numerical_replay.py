"""Manual integration drill for the retained 15-forecast September 10 edition.

Run from the repository root with matching cached inputs. Never acquires data.
Writes only the review report; altered editions live in temporary directories.
"""
import copy,csv,hashlib,json,shutil,socket,sys,tempfile,urllib.request
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path('scripts').resolve()))
import replay_forecast as replay
from refresh import digest
root=Path.cwd()
paths=[root/'data/site.json',root/'data/ledger.json',root/'scripts/refresh.py',root/'scripts/build_data.py',root/'scripts/experiment_model.py',root/'data/games.csv',*list((root/'data/raw').glob('stats_team_week_*.csv'))]
hashes=lambda:{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes()
with patch.object(urllib.request,'urlopen',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')):
 report=replay.replay(root)
 assert report['matched']==15 and report['mismatches']==0
 assert hashes()==before
 with tempfile.TemporaryDirectory() as folder:
  target=Path(folder);(target/'data/raw').mkdir(parents=True)
  shutil.copy2(root/'data/games.csv',target/'data/games.csv')
  original=json.loads((root/'data/site.json').read_bytes())
  for source in original['efficiencySources']:
   name=f"stats_team_week_{source['season']}.csv"
   shutil.copy2(root/'data/raw'/name,target/'data/raw'/name)
  def save(site): (target/'data/site.json').write_text(json.dumps(site))
  def reject(site):
   save(site)
   try: replay.replay(target)
   except ValueError:return
   raise AssertionError('Expected rejection')
  altered=copy.deepcopy(original)
  snap=next(g['snapshot'] for g in altered['games'] if g['snapshot'])
  snap['prediction']['homeScore']+=1
  snap['hash']=digest({k:v for k,v in snap.items() if k!='hash'})
  save(altered)
  assert replay.replay(target)['mismatches']==1
  altered=copy.deepcopy(original);altered['model']['configuration']['scoreRidge']=99;reject(altered)
  altered=copy.deepcopy(original)
  snap=next(g['snapshot'] for g in altered['games'] if g['snapshot']);snap['gameContext']['neutral']=not snap['gameContext']['neutral']
  snap['hash']=digest({k:v for k,v in snap.items() if k!='hash'});reject(altered)
  # Results from this week's future games must not influence the frozen forecasts.
  schedule=target/'data/games.csv'
  with schedule.open(newline='',encoding='utf-8') as f:
   reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
  for row in rows:
   if row['season']=='2026' and row['week']=='1' and row['gameday']>=original['model']['weeklyCutoff']:
    row['home_score']='70';row['away_score']='0'
  with schedule.open('w',newline='',encoding='utf-8') as f:
   writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
  altered=copy.deepcopy(original);newhash=hashlib.sha256(schedule.read_bytes()).hexdigest();altered['source']['sha256']=newhash
  for game in altered['games']:
   if game['snapshot']:
    snap=game['snapshot'];snap['sourceHash']=newhash;snap['hash']=digest({k:v for k,v in snap.items() if k!='hash'})
  save(altered)
  leak=replay.replay(target);assert leak['matched']==15 and leak['mismatches']==0
  schedule.unlink();reject(altered)
assert hashes()==before
report['verification']={'networkBlocked':True,'originalFilesUnchanged':True,'validHashNumericalTamperingDetected':True,'configurationMismatchRejected':True,'contextMismatchRejected':True,'missingScheduleRejected':True,'sameWeekFutureResultPerturbationUnchanged':True}
Path('reviews/numerical-replay.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
