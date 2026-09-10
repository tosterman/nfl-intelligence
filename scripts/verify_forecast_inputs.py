"""Verify retained model inputs against an edition without acquiring new data."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(root):
    site = json.loads((root / 'data/site.json').read_text())
    sources = site.get('efficiencySources')
    if not isinstance(sources, list) or not sources:
        raise ValueError('Edition efficiency source manifest is missing')
    entries = [('data/games.csv', site['source'])]
    seasons = set()
    for source in sources:
        season = source.get('season')
        if type(season) is not int or not 1900 <= season <= 2200 or season in seasons:
            raise ValueError('Invalid or duplicate efficiency season')
        seasons.add(season)
        entries.append((f'data/raw/stats_team_week_{season}.csv', source))
    results = []
    for name, source in entries:
        expected = source.get('sha256')
        if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
            raise ValueError('Invalid input digest: ' + name)
        path = root / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        results.append({'path': name, 'expectedSha256': expected,
                        'actualSha256': actual, 'matches': actual == expected})
    return {'editionGeneratedAt': site['generatedAt'], 'inputsMatch': all(r['matches'] for r in results),
            'files': results, 'scope': 'Input bytes only; not a numerical replay or publication receipt.'}


if __name__ == '__main__':
    report = verify(ROOT)
    folder = ROOT / 'release-recovery'
    folder.mkdir(exist_ok=True)
    (folder / 'forecast-inputs.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if not report['inputsMatch']:
        raise SystemExit('Edition input bytes are missing or mismatched; publication withheld')
