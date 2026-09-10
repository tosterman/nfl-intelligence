"""Retain a complete current-season checkpoint audit; does not acquire odds."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from market_capture import load_export
from market_pairing import START, checkpoint, forecast_at, instant, pair_checkpoint

ROOT = Path(__file__).resolve().parents[1]


def verify_protocol(body, receipt, now):
    commit = receipt.get('commit', '')
    expected = f'https://raw.githubusercontent.com/tosterman/nfl-intelligence/{commit}/reviews/market-pairing-protocol.md'
    if not re.fullmatch('[a-f0-9]{40}', commit) or receipt.get('url') != expected or receipt.get('status') != 'verified-before-activation':
        raise ValueError('Unverified protocol publication')
    if hashlib.sha256(body.replace(b'\r\n', b'\n')).hexdigest() != receipt.get('sha256'):
        raise ValueError('Protocol changed after publication')
    observed = instant(receipt['observedAt'])
    if not instant(receipt['githubHttpDate']) <= observed < START or observed > now or instant(receipt['effectiveAfter']) != START:
        raise ValueError('Protocol publication chronology invalid')


def build_report(games, ledger, receipts, captures, now, coverage_through):
    if coverage_through > now:
        raise ValueError('Export coverage is from the future')
    if len({g['id'] for g in games}) != len(games):
        raise ValueError('Duplicate game scope')
    records = []
    for game in games:
        for phase in ('entry', 'closing'):
            row = {'gameId':game['id'], 'phase':phase, 'markets':[]}
            if not game.get('kickoff'):
                records.append(row | {'status':'missing-kickoff'}); continue
            window = checkpoint(game, phase, now)
            row |= {'cutoff':window['cutoff'].isoformat(), 'status':window['status'],
                    'home':game['home'], 'away':game['away'], 'kickoff':game['kickoff']}
            if window['status'] != 'due':
                records.append(row); continue
            if window['cutoff'] > coverage_through:
                records.append(row | {'status':'export-too-early'}); continue
            # Book coverage comes only from evidence available by this checkpoint.
            # Retain formerly observed books even if the latest event omits them.
            books = set()
            for capture in captures:
                acquired, uploaded = instant(capture['feed']['fetchedAt']), instant(capture['uploadedAt'])
                if acquired > window['cutoff'] or uploaded > window['cutoff'] or phase == 'closing' and (acquired == window['cutoff'] or uploaded == window['cutoff']):
                    continue
                for event in capture['feed']['events']:
                    if event['home'] == game['home'] and event['away'] == game['away'] and instant(event['kickoff']) == instant(game['kickoff']):
                        books.update(b['book'] for b in event['books'])
            if not books:
                row['status'] = 'missing-book-coverage'
                if phase == 'entry': row['forecast'] = forecast_at(game, ledger, receipts, window['cutoff'])
            else:
                row['markets'] = [pair_checkpoint(game, phase, now, ledger, receipts, captures, book, market)
                                  for book in sorted(books) for market in ('spread','total','moneyline')]
                row['status'] = 'evaluated'
            records.append(row)
    return {'checkedAt':now.isoformat(), 'coverageThrough':coverage_through.isoformat(), 'games':len(games), 'checkpoints':records,
            'checkpointCounts':dict(Counter(r['status'] for r in records)),
            'marketCounts':dict(Counter(m['status'] for r in records for m in r['markets']))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', required=True, type=Path)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    receipt_path = ROOT / 'reviews/market-pairing-protocol-publication.json'
    receipt = json.loads(receipt_path.read_text())
    verify_protocol((ROOT / 'reviews/market-pairing-protocol.md').read_bytes(), receipt, now)
    captures = load_export(args.export)
    manifest = json.loads((args.export / 'manifest.json').read_text())
    if instant(manifest['exportedAt']) > now:
        raise ValueError('Export is from the future')
    inputs = {n:(ROOT / 'data' / n).read_bytes() for n in ['site.json','ledger.json','publications.json']}
    site = json.loads(inputs['site.json'])
    report = build_report(site['games'],json.loads(inputs['ledger.json']),json.loads(inputs['publications.json']),captures,now,instant(manifest['startedAt']))
    report |= {'schemaVersion':1, 'protocolHash':receipt['sha256'], 'protocolPublication':receipt,
               'inputHashes':{n:hashlib.sha256(raw).hexdigest() for n,raw in inputs.items()},
               'exportManifestHash':hashlib.sha256((args.export / 'manifest.json').read_bytes()).hexdigest(),
               'captureHashes':[c['sha256'] for c in captures],
               'codeHashes':{n:hashlib.sha256((ROOT / 'scripts' / n).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for n in ['report_market_pairing.py','market_capture.py','market_pairing.py','publication.py']},
               'interpretation':'Checkpoint evidence audit only; closing means sampled near kickoff. No betting return or CLV calculation.'}
    payload = (json.dumps(report,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    digest = hashlib.sha256(payload).hexdigest()
    folder = ROOT / 'release-recovery/market-pairing'
    folder.mkdir(parents=True,exist_ok=True)
    destination = folder / (digest + '.json')
    with destination.open('xb') as stream: stream.write(payload)
    summary = {k:report[k] for k in ['checkedAt','coverageThrough','games','checkpointCounts','marketCounts','captureHashes','protocolHash']}
    summary |= {'reportHash':digest, 'reportPath':str(destination), 'productionWorkflow':False}
    (ROOT / 'reviews/market-pairing-report-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
