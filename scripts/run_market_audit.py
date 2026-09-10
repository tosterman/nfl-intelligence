"""Run and package an audit using allowlisted inputs; never acquire provider odds."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def package_report(root, export, summary):
    digest = summary['reportHash']
    if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Invalid report identity')
    report_bytes = (root / 'release-recovery/market-pairing' / (digest + '.json')).read_bytes()
    if hashlib.sha256(report_bytes).hexdigest() != digest:
        raise ValueError('Report identity mismatch')
    report = json.loads(report_bytes)
    files = {'report.json': report_bytes}
    def retain(name, body, expected):
        if hashlib.sha256(body).hexdigest() != expected:
            raise ValueError('Report dependency changed: ' + name)
        files[name] = body
    for name, expected in report['inputHashes'].items():
        if name not in ('site.json', 'ledger.json', 'publications.json'):
            raise ValueError('Unknown report input')
        retain('data/' + name, (root / 'data' / name).read_bytes(), expected)
    for name, expected in report['codeHashes'].items():
        if name not in ('report_market_pairing.py', 'market_capture.py', 'market_pairing.py', 'publication.py', 'calibration.py'):
            raise ValueError('Unknown report code')
        retain('scripts/' + name, (root / 'scripts' / name).read_bytes().replace(b'\r\n', b'\n'), expected)
    retain('export/manifest.json', (export / 'manifest.json').read_bytes(), report['exportManifestHash'])
    retain('reviews/market-pairing-protocol.md', (root / 'reviews/market-pairing-protocol.md').read_bytes().replace(b'\r\n', b'\n'), report['protocolHash'])
    payload = {'schemaVersion': 1, 'reportHash': digest,
               'archivePolicy': 'Capture files remain at original private Blob paths in export/manifest.json; verify their hashes before replay.',
               'files': {name: {'sha256': hashlib.sha256(body).hexdigest(), 'base64': base64.b64encode(body).decode()} for name, body in files.items()}}
    return gzip.compress(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode(), mtime=0)


def main():
    (ROOT / 'release-recovery/market-audit-retention.json').unlink(missing_ok=True)
    result = subprocess.run(['node', '--import', 'tsx', 'scripts/export_odds_evidence.ts'], cwd=ROOT, check=True, capture_output=True, text=True)
    export = ROOT / json.loads(result.stdout)['folder']
    subprocess.run([sys.executable, 'scripts/report_market_pairing.py', '--export', str(export)], cwd=ROOT, check=True, capture_output=True)
    summary = json.loads((ROOT / 'reviews/market-pairing-report-summary.json').read_text())
    body = package_report(ROOT, export, summary)
    digest = hashlib.sha256(body).hexdigest()
    destination = ROOT / 'release-recovery/market-pairing' / (digest + '.bundle.json.gz')
    destination.write_bytes(body)
    subprocess.run(['node', '--import', 'tsx', 'scripts/retain_market_report.ts', str(destination)], cwd=ROOT, check=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('Market audit failed; no successful retention receipt accepted.', file=sys.stderr)
        sys.exit(1)
