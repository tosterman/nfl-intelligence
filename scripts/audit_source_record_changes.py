"""Offline source comparison between the fixed retained edition and current inputs."""
import hashlib
import gzip
import csv
import io
import json
import tempfile
from pathlib import Path
from replay_retained_fixture import restore
from source_record_changes import compare_csv
from verify_forecast_inputs import verify

ROOT = Path(__file__).resolve().parents[1]


def audit(root=ROOT):
    current = verify(root)
    if not current['inputsMatch']:
        raise ValueError('Current input bytes do not match the edition')
    with tempfile.TemporaryDirectory() as directory:
        previous = Path(directory)
        manifest = restore(root / 'reviews/forecast-replay-inputs', previous)
        prior = verify(previous)
        if not prior['inputsMatch']:
            raise ValueError('Prior input bytes do not match the retained edition')
        old = {entry['path']: entry for entry in prior['files']}
        new = {entry['path']: entry for entry in current['files']}
        if old.keys() != new.keys():
            raise ValueError('Source set changed; explicit migration required')
        files = []
        for name in sorted(new):
            compared = compare_csv((previous / name).read_bytes(), (root / name).read_bytes(),
                                   old[name]['expectedSha256'], new[name]['expectedSha256'],
                                   ('game_id',) if name == 'data/games.csv' else ('game_id', 'team'))
            files.append({'path': name, **compared})
    historical_folder = root / 'reviews/joint-replay-inputs'
    historical_manifest = json.loads((historical_folder / 'manifest.json').read_text())
    entry = historical_manifest['files']['games.csv']
    compressed = (historical_folder / 'games.csv.gz').read_bytes()
    if hashlib.sha256(compressed).hexdigest() != entry['compressedSha256']:
        raise ValueError('Historical compressed schedule mismatch')
    historical = gzip.decompress(compressed)
    if len(historical) != entry['bytes']:
        raise ValueError('Historical schedule length mismatch')
    schedule_change = compare_csv(historical, (root / 'data/games.csv').read_bytes(),
                                  entry['sha256'], new['data/games.csv']['expectedSha256'], ('game_id',))
    known = {row['game_id'] for row in csv.DictReader(io.StringIO(historical.decode('utf-8-sig')))}
    known &= {row['game_id'] for row in csv.DictReader(io.StringIO((root / 'data/games.csv').read_bytes().decode('utf-8-sig')))}
    site = json.loads((root / 'data/site.json').read_text())
    schedule_change['comparedSiteGames'] = sorted(game['id'] for game in site['games'] if game['id'] in known)
    return {'retainedEdition': manifest['editionGeneratedAt'], 'currentEdition': current['editionGeneratedAt'],
            'currentSiteSha256': hashlib.sha256((root / 'data/site.json').read_bytes()).hexdigest(),
            'filesCompared': len(files), 'changedFiles': sum(file['recordsChanged'] for file in files),
            'addedRecords': sum(len(file['added']) for file in files),
            'removedRecords': sum(len(file['removed']) for file in files),
            'revisedRecords': sum(len(file['revised']) for file in files), 'files': files,
            'historicalScheduleComparison': {'originalAcquisitionTimeKnown': False, **schedule_change},
            'scope': 'Verified retained and current input bytes only. No attribution of numerical forecast changes; no source acquisition or model modification.'}


if __name__ == '__main__':
    report = audit()
    (ROOT / 'reviews/source-record-changes.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key not in ('files', 'historicalScheduleComparison')}, indent=2))
    change = report['historicalScheduleComparison']
    public = {key: change[key] for key in ('beforeSha256', 'afterSha256', 'comparedSiteGames')}
    public['changedRecords'] = len(change['revised'])
    public['revisions'] = [{'gameId': row['key'][0], 'fields': sorted(row['fields'])} for row in change['revised']]
    (ROOT / 'data/source-record-changes.json').write_text(json.dumps(public, indent=2) + '\n')
    print(json.dumps({'historicalScheduleAdded': len(change['added']), 'historicalScheduleRemoved': len(change['removed']),
                      'historicalScheduleRevised': len(change['revised'])}))
