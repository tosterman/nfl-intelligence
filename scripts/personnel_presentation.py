"""Assemble compatible replayed personnel artifacts; not a raw-source verifier.

The publisher must replay source normalization and derived calculations before
calling this consistency boundary, and retain their exact immutable evidence.
"""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from personnel_schedule import verify_schedule

FILES = ('site.json', 'personnel.json', 'personnel-collection.json', 'quarterbacks.json',
         'quarterback-collection.json', 'participation-source.json', 'participation-collection.json',
         'personnel-changes.json', 'player-usage.json', 'season-participation.json')


def assemble(files, now=None):
    now = now or datetime.now(timezone.utc)
    data = {name: json.loads(files[name]) for name in FILES}
    contexts = verify_schedule(data['site.json'], files['games.csv'])
    personnel, quarterback = data['personnel.json'], data['quarterbacks.json']
    history, historical, current = (data[name] for name in
                                   ('personnel-changes.json', 'player-usage.json', 'season-participation.json'))

    def instant(value):
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None or parsed > now:
            raise ValueError('Invalid personnel chronology')
        return parsed

    for source in (personnel, quarterback):
        if source['season'] != data['site.json']['season']:
            raise ValueError('Personnel season binding differs')
        if instant(source['assetUpdatedAt']) > instant(source['retrievedAt']):
            raise ValueError('Invalid personnel chronology')
    for name, statuses in [('personnel-collection.json', {'ok', 'unavailable'}),
                           ('quarterback-collection.json', {'ok', 'unavailable'}),
                           ('participation-collection.json', {'collected', 'failed'})]:
        state = data[name]
        if state.get('status') not in statuses:
            raise ValueError('Invalid personnel collection state')
        for key in ('checkedAt', 'attemptedAt', 'retrievedAt'):
            if key in state:
                instant(state[key])
    if history['sourceHash'] != personnel['sourceHash'] or history['retrievedAt'] != personnel['retrievedAt']:
        raise ValueError('Personnel history binding differs')
    cutoff = min(instant(personnel['retrievedAt']), instant(quarterback['retrievedAt']))
    compatible = all(timedelta(0) <= cutoff - instant(source['assetUpdatedAt']) < timedelta(hours=30)
                     for source in (personnel, quarterback))
    if compatible:
        audit_raw = files['identityAudit']
        audit = json.loads(audit_raw)
        if any(audit['inputHashes'][name] != hashlib.sha256(files[name+'.json']).hexdigest()
               for name in ('personnel', 'quarterbacks')):
            raise ValueError('Personnel identity audit binding differs')
        if (historical['auditHashes']['identity'] != hashlib.sha256(audit_raw).hexdigest() or
                current['inputHashes']['identity'] != hashlib.sha256(audit_raw.replace(b'\r\n', b'\n')).hexdigest()):
            raise ValueError('Participation identity audit binding differs')
        for artifact in (historical, current):
            if (artifact['personnelSourceHash'] != personnel['sourceHash'] or
                    artifact['personnelRetrievedAt'] != personnel['retrievedAt'] or
                    instant(artifact['calculatedAt']) < instant(personnel['retrievedAt'])):
                raise ValueError('Personnel participation binding differs')
        if historical['personnelArtifactHash'] != hashlib.sha256(files['personnel.json']).hexdigest():
            raise ValueError('Historical participation binding differs')
        source = data['participation-source.json']
        if (current['sourceHash'] != source['sourceHash'] or
                current['sourceRetrievedAt'] != source['retrievedAt'] or
                current['sourceSeason'] != source['season'] or source['season'] != personnel['season'] or
                current['inputHashes']['schedule'] != hashlib.sha256(files['games.csv']).hexdigest() or
                instant(current['calculatedAt']) < instant(source['retrievedAt'])):
            raise ValueError('Current participation binding differs')
        collection = data['participation-collection.json']
        if collection['status'] == 'collected' and any(collection.get(key) != source[key] for key in ('sourceHash', 'retrievedAt', 'season')):
            raise ValueError('Participation collection binding differs')
        current = {**current, 'collectionStatus': 'current' if collection['status'] == 'collected' else 'retained'}
    else:
        historical, current = None, None
    result = {'schemaVersion': 1, 'kind': 'personnel-presentation', 'generatedAt': now.isoformat(),
              'contexts': contexts, 'scheduleHash': data['site.json']['source']['sha256'],
              'derivation': {'status': 'compatible' if compatible else 'unavailable',
                             'cutoff': cutoff.isoformat(),
                             'reason': None if compatible else 'Injury and depth-chart sources lack a compatible identity cutoff'},
              'evidence': {'snapshot': personnel, 'quarterback': quarterback,
                           'collection': data['personnel-collection.json'],
                           'quarterbackCollection': data['quarterback-collection.json'],
                           'participationCollection': data['participation-collection.json'],
                           'history': history, 'historical': historical, 'current': current}}
    if len(json.dumps(result, separators=(',', ':')).encode()) > 2_000_000:
        raise ValueError('Personnel presentation exceeds size bound')
    return result
