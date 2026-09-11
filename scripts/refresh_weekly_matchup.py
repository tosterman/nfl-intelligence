"""Acquire current-season matchup context independently of numerical forecasts."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from scripts.weekly_matchup_context import from_retained

ROOT = Path(__file__).resolve().parents[1]


def immutable(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        pass
    if path.read_bytes() != raw:
        raise ValueError('Immutable matchup source conflict')


def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'NFLIntelligence-matchup-context'}), timeout=40) as response:
        body = response.read(50_000_001)
    if len(body) > 50_000_000:
        raise ValueError('Source exceeds collection limit')
    return body


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def acquire(root, season, observed_at, read=fetch, now=lambda: datetime.now(timezone.utc)):
    parsed = datetime.fromisoformat(observed_at.replace('Z', '+00:00'))
    if parsed.tzinfo is None or type(season) is not int:
        raise ValueError('Invalid acquisition scope')
    sources = {}
    for key, tag, name in [('plays', 'pbp', f'play_by_play_{season}.csv.gz'),
                           ('schedule', 'schedules', 'games.csv')]:
        metadata = json.loads(read(f'https://api.github.com/repos/nflverse/nflverse-data/releases/tags/{tag}'))
        assets = [a for a in metadata['assets'] if a['name'] == name]
        if len(assets) != 1:
            raise ValueError('Expected source asset missing')
        asset = assets[0]
        url = f'https://github.com/nflverse/nflverse-data/releases/download/{tag}/{name}'
        if asset['browser_download_url'] != url:
            raise ValueError('Unexpected source identity')
        updated = datetime.fromisoformat(asset['updated_at'].replace('Z', '+00:00'))
        if updated.tzinfo is None or updated > parsed or (parsed - updated).total_seconds() > 30 * 3600:
            raise ValueError('Invalid source update time')
        raw = read(url)
        digest = hashlib.sha256(raw).hexdigest()
        if asset.get('digest') != 'sha256:' + digest or asset['size'] != len(raw):
            raise ValueError('Source bytes disagree with metadata')
        compressed = raw if name.endswith('.gz') else gzip.compress(raw, mtime=0)
        compressed_sha = hashlib.sha256(compressed).hexdigest()
        path = f'data/weekly-matchup-sources/{compressed_sha}.csv.gz'
        immutable(root / path, compressed)
        sources[key] = {'path': path, 'sha256': compressed_sha, 'originalSha256': digest,
                        'url': url, 'assetUpdatedAt': asset['updated_at']}
    finished = now()
    if finished.tzinfo is None or finished < parsed:
        raise ValueError('Invalid completion time')
    manifest = {'season': season, 'retainedAt': finished.isoformat(), **sources,
                'license': 'CC BY 4.0', 'licenseUrl': 'https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md'}
    raw = encode(manifest)
    identity = hashlib.sha256(raw).hexdigest()
    immutable(root / f'data/weekly-matchup-sources/{identity}.manifest.json', raw)
    return manifest, identity


def save_current(root, value):
    raw = encode(value)
    identity = hashlib.sha256(raw).hexdigest()
    immutable(root / f'data/weekly-matchup-sources/{identity}.snapshot.json', raw)
    with tempfile.NamedTemporaryFile(dir=root / 'data', delete=False) as stream:
        stream.write(raw)
        name = stream.name
    try:
        os.replace(name, root / 'data/weekly-matchup-context.json')
    finally:
        Path(name).unlink(missing_ok=True)


def run(root=ROOT, read=fetch, now=lambda: datetime.now(timezone.utc)):
    site = json.loads((root / 'data/site.json').read_text())
    checked = now().isoformat()
    scope = {'season': site['season'], 'week': site['week']}
    base = {'schemaVersion': 1, 'checkedAt': checked, **scope}
    try:
        phases = {'POST' if g['type'] in ('WC', 'DIV', 'CON', 'SB') else g['type']
                  for g in site['games'] if g['season'] == scope['season'] and g['week'] == scope['week']}
        if len(phases) != 1 or not phases.issubset({'REG', 'POST'}):
            raise ValueError('Ambiguous current phase')
        manifest, identity = acquire(root, scope['season'], checked, read, now)
        # Existing corrections are usable only if their entire source identity matches.
        corrections = json.loads((root / 'data/red-zone-adjudications.json').read_text())
        if corrections['sourceSha256'] != manifest['plays']['sha256']:
            corrections = {'sourceSha256': manifest['plays']['sha256'], 'decisions': []}
        result = from_retained(root, manifest, corrections, scope['week'], phases.pop())
        if result['cutoff'] > checked[:10]:
            raise ValueError('Weekly boundary has not occurred')
        save_current(root, {**base, 'status': 'ok', 'manifestHash': identity, 'currentSeason': result})
        return 0
    except Exception:
        # Prior immutable snapshots remain retained. Current failure cannot masquerade
        # as a fresh successful sample; historical panels remain independent.
        save_current(root, {**base, 'status': 'unavailable', 'reason': 'Current-season acquisition or validation failed'})
        return 1


if __name__ == '__main__':
    code = run()
    print('Weekly matchup context retained' if code == 0 else 'Weekly matchup context unavailable; prior archives preserved')
    raise SystemExit(code)
