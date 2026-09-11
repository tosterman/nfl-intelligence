"""Deterministic paired forecast/closing-line errors; caller verifies archived captures.

Uses the unchanged v1 entry forecast and sampled closing quote conventions.
This module makes no acquisition, publication, trading or profitability claim.
"""
from collections import Counter
import csv
import hashlib
import io
import json
import math
from market_pairing import checkpoint, forecast_at, instant
from report_market_pairing import build_report
from personnel_schedule import verify_schedule


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def verified_results(site, raw, now):
    """Final scores must agree with the exact, context-verified schedule artifact."""
    verify_schedule(site, raw)
    acquired = instant(site['source']['retrievedAt'])
    if acquired > now or acquired > instant(site['generatedAt']) or instant(site['generatedAt']) > now:
        raise ValueError('Result source chronology invalid')
    rows = {row['game_id']: row for row in csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
            if int(row['season']) == site['season']}
    results = {}
    for game in site['games']:
        row = rows[game['id']]
        present = [row.get(key) not in (None, '') for key in ('home_score', 'away_score')]
        if any(present) != all(present):
            raise ValueError('Partial result source')
        if game['status'] != 'final':
            if all(present):
                raise ValueError('Unsettled edition disagrees with result source')
            continue
        if not all(present) or not game.get('kickoff') or acquired <= instant(game['kickoff']):
            raise ValueError('Final result lacks post-kickoff source')
        home, away = float(row['home_score']), float(row['away_score'])
        if any(not number(v) or v < 0 or v != int(v) for v in (home, away)):
            raise ValueError('Invalid final score')
        if game.get('actualHome') != home or game.get('actualAway') != away:
            raise ValueError('Final result differs from retained source')
        results[game['id']] = {'margin': home-away, 'total': home+away,
            'sourceHash': site['source']['sha256'], 'retrievedAt': site['source']['retrievedAt']}
    return results


def grade_benchmark(site, ledger, receipts, captures, now, coverage_through, result_bytes):
    results = verified_results(site, result_bytes, now)
    audit = build_report(site['games'], ledger, receipts, captures, now, coverage_through)
    games = {game['id']: game for game in site['games']}
    rows = []
    for close in audit['checkpoints']:
        if close['phase'] != 'closing':
            continue
        game = games[close['gameId']]
        base = {'gameId': game['id'], 'checkpointStatus': close['status'],
                'resultStatus': 'final' if game['id'] in results else 'pending-result'}
        if close['status'] != 'evaluated':
            rows.append(base | {'status': close['status'], 'book': None, 'market': None})
            continue
        window = checkpoint(game, 'entry', now)
        forecast = forecast_at(game, ledger, receipts, window['cutoff']) if window['status']=='due' else {'status':window['status']}
        for market in close['markets']:
            if market['market'] not in ('spread', 'total'):
                continue
            row = base | {'book': market['book'], 'market': market['market'],
                'checkpointStatus': market['status'], 'forecastStatus': forecast['status']}
            failures = []
            if market['status'] != 'matched': failures.append(market['status'])
            if forecast['status'] != 'matched': failures.append(forecast['status'])
            if game['id'] not in results: failures.append('pending-result')
            if failures:
                rows.append(row | {'status':'excluded', 'reasons':failures})
                continue
            snapshot = forecast['snapshot']
            metric = 'homeMargin' if market['market']=='spread' else 'total'
            predicted = snapshot.get('prediction', {}).get(metric)
            quote = market['quote']
            line = quote['quote'].get('homePoint' if metric=='homeMargin' else 'point')
            if not number(predicted) or not number(line):
                rows.append(row | {'status':'excluded', 'reasons':['invalid-numeric-pair']})
                continue
            selected_receipts = [r for r in receipts if r.get('status')=='ready' and
                snapshot['hash'] in r.get('snapshotHashes',[]) and r.get('deploymentUrl','').startswith('https://') and
                instant(r['publishedAt'])==instant(forecast['publishedAt'])]
            if not selected_receipts:
                raise ValueError('Selected forecast receipt missing')
            result = results[game['id']]
            actual = result['margin' if metric=='homeMargin' else 'total']
            market_prediction = -line if metric=='homeMargin' else line
            rows.append(row | {'status':'paired', 'modelError':abs(predicted-actual),
                'marketError':abs(market_prediction-actual), 'snapshotHash':snapshot['hash'],
                'receiptHash':min(digest(r) for r in selected_receipts),
                'forecastPublishedAt':forecast['publishedAt'], 'captureHash':quote['sha256'],
                'quoteObservedAt':quote['quote']['observedAt'], 'captureUploadedAt':quote['uploadedAt'],
                'resultSourceHash':result['sourceHash'], 'resultRetrievedAt':result['retrievedAt']})
    summaries=[]
    for book, market in sorted({(r['book'],r['market']) for r in rows if r['book'] is not None}):
        selected=[r for r in rows if r['book']==book and r['market']==market]
        paired=[r for r in selected if r['status']=='paired']
        count=len(paired)
        summaries.append({'book':book,'market':market,'pairedGames':count,
            'modelMae':sum(r['modelError'] for r in paired)/count if count else None,
            'marketMae':sum(r['marketError'] for r in paired)/count if count else None,
            'excludedGames':len(selected)-count,
            'exclusionReasons':dict(Counter(reason for r in selected for reason in r.get('reasons',[])))})
    return {'schemaVersion':1,'checkedAt':now.isoformat(),'coverageThrough':coverage_through.isoformat(),
        'scopeGames':len(games),'closingCheckpointCounts':dict(Counter(r['status'] for r in audit['checkpoints'] if r['phase']=='closing')),
        'pairedGameCount':len({r['gameId'] for r in rows if r['status']=='paired'}),
        'books':summaries,'records':rows,
        'inputHashes':{'site':digest(site),'ledger':digest(ledger),'receipts':digest(receipts),'resultSource':hashlib.sha256(result_bytes).hexdigest()},
        'interpretation':'24-hour entry forecasts versus sampled final-15-minute market lines. Same games per book and market; ties included in score errors. No betting returns or CLV.'}


def public_summary(report):
    """Only aggregate accounting crosses the public boundary; private traces stay retained."""
    keys=('schemaVersion','checkedAt','coverageThrough','scopeGames','closingCheckpointCounts','pairedGameCount','books','interpretation')
    excluded=[row for row in report['records'] if row['status']=='excluded' and row['book'] is not None]
    return {key:report[key] for key in keys} | {'reportHash':digest(report),
        'excludedBookMarketCount':len(excluded),'excludedGameCount':len({row['gameId'] for row in excluded})}
