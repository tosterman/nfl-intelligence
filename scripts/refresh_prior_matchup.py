"""Refresh prior-season context without discarding the last verified sample."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone
from scripts.refresh_weekly_matchup import ROOT, acquire, encode, fetch, immutable
from scripts.weekly_matchup_context import from_retained


def save(root, filename, value):
    raw = encode(value)
    immutable(root / f'data/weekly-matchup-sources/{hashlib.sha256(raw).hexdigest()}.snapshot.json', raw)
    with tempfile.NamedTemporaryFile(dir=root / 'data', delete=False) as stream:
        stream.write(raw)
        name = stream.name
    try:
        os.replace(name, root / 'data' / filename)
    finally:
        Path(name).unlink(missing_ok=True)


def run(root=ROOT, read=fetch, now=lambda: datetime.now(timezone.utc)):
    season = json.loads((root / 'data/site.json').read_text())['season']
    checked = now().isoformat()
    base = {'schemaVersion': 1, 'forecastSeason': season, 'checkedAt': checked}
    updated_hash = None
    try:
        manifest, identity = acquire(root, season - 1, checked, read, now, historical=True)
        corrections = json.loads((root / 'data/red-zone-adjudications.json').read_text())
        if corrections['sourceSha256'] != manifest['plays']['sha256']:
            corrections = {'sourceSha256': manifest['plays']['sha256'], 'decisions': []}
        result = from_retained(root, manifest, corrections, forecast_season=season)
        if result['cutoff'] > checked[:10]:
            raise ValueError('Following-season boundary has not occurred')
        # Archive and atomically replace only after every source and sample check.
        save(root, 'prior-matchup-context.json', result)
        updated_hash = hashlib.sha256(encode(result)).hexdigest()
        save(root, 'prior-matchup-collection.json', {**base, 'status': 'ok', 'manifestHash': identity,
             'artifactSha256': updated_hash})
        return 0
    except Exception:
        failure = {**base, 'status': 'unavailable', 'reason':
             'Validated sample updated but collection receipt failed' if updated_hash else
             'Prior-season acquisition or validation failed; last verified sample retained'}
        if updated_hash:
            failure['updatedArtifactSha256'] = updated_hash
        save(root, 'prior-matchup-collection.json', failure)
        return 1


if __name__ == '__main__':
    code = run()
    print('Prior-season context retained' if code == 0 else 'Prior-season refresh incomplete; inspect collection record')
    raise SystemExit(code)
