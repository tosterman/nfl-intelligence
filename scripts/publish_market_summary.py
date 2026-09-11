"""Replay-gated, atomic local benchmark replacement; does not deploy the site."""
import json
import os
import re
from pathlib import Path
import tempfile
from market_benchmark import digest, public_summary
from market_pairing import instant
from replay_market_benchmark import replay


def atomic_json(path, value):
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,
                prefix='.market-benchmark-',suffix='.tmp',delete=False) as output:
            temporary=Path(output.name)
            json.dump(value,output,indent=2,allow_nan=False);output.write('\n')
            output.flush();os.fsync(output.fileno())
        os.replace(temporary,path)
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)


def publish_summary(root,identity):
    if not re.fullmatch('[a-f0-9]{64}',identity):raise ValueError('Invalid benchmark identity')
    lock=root/'release-recovery/market-benchmark-publish.lock'
    with lock.open('x') as handle:
        handle.write(identity)
    try:
        return _publish_summary(root,identity)
    finally:
        lock.unlink()


def _publish_summary(root,identity):
    folder=root/'release-recovery/market-benchmark'
    report=json.loads((folder/(identity+'.json')).read_text())
    if digest(report)!=identity:raise ValueError('Benchmark identity differs')
    proof=replay(identity,folder)
    if proof.get('matched') is not True or proof.get('networkBlocked') is not True or proof.get('reportHash')!=identity:
        raise ValueError('Benchmark replay was not verified')
    summary=public_summary(report)|{'publicationStatus':report['publicationStatus']}
    target=root/'data/market-benchmark.json'
    if target.exists():
        previous=json.loads(target.read_text())
        if instant(summary['checkedAt'])<instant(previous['checkedAt']) or instant(summary['coverageThrough'])<instant(previous['coverageThrough']):
            raise ValueError('Benchmark publication would move backward')
        for field in ('resultSourceRetrievedAt','editionGeneratedAt'):
            if field in previous and instant(summary[field])<instant(previous[field]):
                raise ValueError('Benchmark source would move backward')
    # Diagnostic write first. A failure before the final atomic replace leaves
    # the reader's previous report and its original timestamps intact.
    atomic_json(root/'reviews/market-benchmark-summary.json',summary)
    atomic_json(root/'reviews/market-benchmark-replay.json',proof)
    atomic_json(target,summary)
    return summary
