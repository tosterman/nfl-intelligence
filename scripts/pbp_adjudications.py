"""Apply documented exceptions only to their exact retained source and row."""
import hashlib
import json


def apply_adjudications(rows, source_sha256, adjudications):
    if source_sha256 != adjudications['sourceSha256']:
        raise ValueError('Adjudication source differs')
    decisions = {}
    for decision in adjudications['decisions']:
        key = (decision['gameId'], decision['playId'])
        if key in decisions or decision['action'] != 'exclude-nullified-kickoff':
            raise ValueError('Invalid or duplicate adjudication')
        decisions[key] = decision
    applied, result = set(), []
    for row in rows:
        key = (row['game_id'], row['play_id'])
        if key not in decisions:
            result.append(row)
            continue
        digest = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        if key in applied or row['play_type'] != 'kickoff' or digest != decisions[key]['rowSha256']:
            raise ValueError('Adjudicated record changed or duplicated')
        applied.add(key)
    if applied != set(decisions):
        raise ValueError('Adjudicated record missing')
    return result
