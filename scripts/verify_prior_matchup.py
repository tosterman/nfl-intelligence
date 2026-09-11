"""Verify the accepted historical sample before publication, including fallback."""
import hashlib
import json
from scripts.refresh_weekly_matchup import ROOT, encode
from scripts.weekly_matchup_context import from_retained


def verify(root=ROOT):
    sample = json.loads((root / 'data/prior-matchup-context.json').read_text())
    collection = json.loads((root / 'data/prior-matchup-collection.json').read_text())
    digest = hashlib.sha256(encode(sample)).hexdigest()
    archive = root / 'data/weekly-matchup-sources'
    if (archive / f'{digest}.snapshot.json').read_bytes() != encode(sample):
        raise ValueError('Historical sample differs from archived bytes')
    if collection['status'] == 'ok':
        receipt = collection
    elif collection['status'] == 'unavailable':
        # A failed refresh can preserve an older sample, but it cannot waive
        # evidence verification. Locate its original successful receipt.
        receipts = []
        for path in archive.glob('*.snapshot.json'):
            raw = path.read_bytes()
            item = json.loads(raw)
            if item.get('status') == 'ok' and item.get('artifactSha256') == digest:
                if path.stem != hashlib.sha256(raw).hexdigest() + '.snapshot':
                    raise ValueError('Historical receipt archive identity mismatch')
                receipts.append(item)
        if not receipts:
            raise ValueError('No successful receipt for preserved historical sample')
        receipt = receipts[0]
    else:
        raise ValueError('Unknown historical collection state')
    if receipt.get('artifactSha256') != digest or receipt.get('forecastSeason') != sample['forecastSeason']:
        raise ValueError('Historical sample and receipt disagree')
    identity = receipt['manifestHash']
    if not isinstance(identity, str) or len(identity) != 64 or any(c not in '0123456789abcdef' for c in identity):
        raise ValueError('Invalid historical manifest identity')
    raw = (archive / f'{identity}.manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != identity:
        raise ValueError('Historical manifest digest mismatch')
    manifest = json.loads(raw)
    corrections = json.loads((root / 'data/red-zone-adjudications.json').read_text())
    if corrections['sourceSha256'] != manifest['plays']['sha256']:
        corrections = {'sourceSha256': manifest['plays']['sha256'], 'decisions': []}
    replay = from_retained(root, manifest, corrections, forecast_season=sample['forecastSeason'])
    if replay != sample:
        raise ValueError('Historical sample does not replay from retained sources')
    return digest


if __name__ == '__main__':
    print('Verified historical matchup artifact: ' + verify())
