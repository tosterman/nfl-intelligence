"""As-of selection primitives for market-pairing-protocol v1; no wagering advice."""
from datetime import datetime, timedelta, timezone
from publication import context_matches, snapshot_valid

START = datetime(2026, 9, 11, tzinfo=timezone.utc)


def instant(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timezone required')
    return result


def checkpoint(game, phase, now):
    if phase not in ('entry', 'closing'):
        raise ValueError('Unknown checkpoint')
    cutoff = instant(game['kickoff']) - (timedelta(hours=24) if phase == 'entry' else timedelta())
    status = 'excluded-before-protocol' if cutoff < START else 'pending' if now < cutoff else 'due'
    return {'status': status, 'cutoff': cutoff, 'maxAge': timedelta(hours=6) if phase == 'entry' else timedelta(minutes=15)}


def forecast_at(game, ledger, receipts, cutoff):
    candidates = []
    for snapshot in ledger:
        if snapshot['gameId'] != game['id'] or not snapshot_valid(snapshot) or not context_matches(snapshot, game):
            continue
        generated = instant(snapshot.get('generatedAt', snapshot.get('publishedAt')))
        if generated > cutoff:
            continue
        published = [instant(r['publishedAt']) for r in receipts if r.get('status') == 'ready'
                     and snapshot['hash'] in r.get('snapshotHashes', []) and r.get('deploymentUrl', '').startswith('https://')
                     and generated <= instant(r['publishedAt']) <= cutoff and instant(r['publishedAt']) < instant(game['kickoff'])]
        if published:
            candidates.append((generated, min(published), snapshot['hash'], snapshot))
    if not candidates:
        return {'status': 'missing-forecast'}
    _, published, _, snapshot = max(candidates, key=lambda x: x[:3])
    return {'status': 'matched', 'snapshot': snapshot, 'publishedAt': published.isoformat()}


def quote_at(game, captures, book, market, cutoff, max_age, exclusive=False):
    """Input captures must already have verified archive hashes and upload metadata."""
    if market not in ('spread', 'total', 'moneyline'):
        raise ValueError('Unknown market')
    eligible = []
    for capture in captures:
        acquired, uploaded = instant(capture['feed']['fetchedAt']), instant(capture['uploadedAt'])
        if uploaded < acquired:
            raise ValueError('Storage upload predates acquisition')
        if acquired > cutoff or uploaded > cutoff or exclusive and (acquired == cutoff or uploaded == cutoff):
            continue
        matches = [e for e in capture['feed']['events'] if e['home'] == game['home'] and e['away'] == game['away'] and instant(e['kickoff']) == instant(game['kickoff'])]
        if len(matches) > 1:
            raise ValueError('Ambiguous odds event')
        if matches:
            eligible.append((acquired, capture, matches[0]))
    if not eligible:
        return {'status': 'missing-capture'}
    latest_time = max(c[0] for c in eligible)
    latest = [c for c in eligible if c[0] == latest_time]
    if len({c[1]['sha256'] for c in latest}) > 1:
        raise ValueError('Conflicting same-time captures')
    acquired, capture, event = latest[0]
    if cutoff - acquired > max_age:
        return {'status': 'stale-capture'}
    books = [b for b in event['books'] if b['book'] == book]
    if len(books) > 1:
        raise ValueError('Ambiguous bookmaker')
    if not books:
        return {'status': 'missing-book'}
    quote = books[0].get(market)
    if quote is None:
        return {'status': 'missing-market'}
    updated = instant(quote['observedAt'])
    if updated > acquired:
        raise ValueError('Quote update postdates acquisition')
    if cutoff - updated > max_age:
        return {'status': 'stale-quote'}
    return {'status': 'matched', 'sha256': capture['sha256'], 'acquiredAt': acquired.isoformat(),
            'uploadedAt': capture['uploadedAt'], 'book': book, 'market': market, 'quote': quote}


def pair_checkpoint(game, phase, now, ledger, receipts, captures, book, market):
    window = checkpoint(game, phase, now)
    result = {'gameId':game['id'], 'phase':phase, 'cutoff':window['cutoff'].isoformat(),
              'book':book, 'market':market, 'status':window['status']}
    if window['status'] != 'due':
        return result
    quote = quote_at(game, captures, book, market, window['cutoff'], window['maxAge'], exclusive=phase == 'closing')
    result['quote'] = quote
    if phase == 'closing':
        return result | {'status':quote['status']}
    forecast = forecast_at(game, ledger, receipts, window['cutoff'])
    return result | {'forecast':forecast, 'status':'matched' if quote['status'] == forecast['status'] == 'matched' else 'incomplete'}
