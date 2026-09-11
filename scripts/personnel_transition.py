"""Replay one explicit personnel transition without scanning older captures."""
import re
from personnel_changes import load_capture, changes


def build_transition(folder, current_capture, previous_capture):
    def read(identity):
        if not isinstance(identity, str) or not re.fullmatch('[a-f0-9]{64}', identity):
            raise ValueError('Invalid personnel capture reference')
        return load_capture(folder / (identity + '.snapshot.json.gz'), folder)
    after = read(current_capture)
    before = read(previous_capture) if previous_capture is not None else None
    if before and before['season'] != after['season']:
        raise ValueError('Personnel transition season changed; explicit baseline required')
    differences = changes(before, after) if before else []
    return {'schemaVersion': 1, 'beforeCapture': previous_capture,
            'afterCapture': current_capture,
            'presentation': {
                'schemaVersion': 1, 'sourceHash': after['sourceHash'],
                'retrievedAt': after['retrievedAt'],
                'previousRetrievedAt': before['retrievedAt'] if before else None,
                'changes': differences,
            }}
