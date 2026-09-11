"""Build the prior-season artifact and reconcile every count to retained history."""
import hashlib
import json
from pathlib import Path
from scripts.weekly_matchup_context import from_retained


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reconcile(result, big, red):
    """Reject differing coverage or counts, including under optimized Python."""
    require(result['season'] == big['season'] == red['season'], 'Season mismatch')
    require(set(result['gameIds']) == {r['gameId'] for r in big['games']} == {r['gameId'] for r in red['drives']}, 'Game coverage mismatch')
    require(set(result['teams']) == set(big['teams']) == set(red['teams']), 'Team coverage mismatch')
    for team, sample in result['teams'].items():
        for side in ('offense', 'defense'):
            for kind in ('passing', 'rushing'):
                require(sample[side][kind] == big['teams'][team][side][kind], 'Big-play counts differ')
            require(sample[side]['inside20'] == red['teams'][team][side], 'Inside-20 counts differ')
            require(set(sample[side]['gameIds']) == {r['gameId'] for r in big['games'] if r[side] == team}, 'Team game sample differs')


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'data/explosive-source.json').read_text())
    corrections = json.loads((root / 'data/red-zone-adjudications.json').read_text())
    result = from_retained(root, manifest, corrections, forecast_season=manifest['season'] + 1)
    big = json.loads((root / 'data/explosive-plays.json').read_text())
    red = json.loads((root / 'data/red-zone.json').read_text())
    reconcile(result, big, red)
    raw = (json.dumps(result, indent=2) + '\n').encode()
    # Replay is an audit, not an acquisition. Never replace the live artifact
    # independently of its collection receipt.
    (root / 'reviews/prior-matchup-retained-replay.json').write_bytes(raw)
    report = {'season': result['season'], 'forecastSeason': result['forecastSeason'], 'cutoff': result['cutoff'],
              'games': len(result['gameIds']), 'teams': len(result['teams']), 'artifactSha256': hashlib.sha256(raw).hexdigest(),
              'sourceSha256': result['sourceSha256'], 'scheduleSha256': result['scheduleSha256'],
              'allPriorCountsMatch': True, 'limitations': 'Retained historical vintage. Acquisition rollover and UI consumption remain separate integration steps.'}
    (root / 'reviews/prior-matchup-replay.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
