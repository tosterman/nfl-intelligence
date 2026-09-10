"""Validate an authenticated Blob export before market checkpoint selection."""
import gzip
import hashlib
import io
import json
import math
import re
from datetime import timezone
from market_pairing import instant


def load_export(folder):
    manifest = json.loads((folder / 'manifest.json').read_text())
    if manifest.get('schemaVersion') != 1 or manifest.get('complete') is not True or manifest.get('source') != 'Authenticated private Vercel Blob':
        raise ValueError('Incomplete or unknown export')
    started, exported = instant(manifest['startedAt']), instant(manifest['exportedAt'])
    if started > exported:
        raise ValueError('Invalid export chronology')
    captures, paths = [], set()
    for metadata in manifest['captures']:
        name = metadata['filename']
        if not re.fullmatch(r'[a-f0-9]{64}\.json\.gz', name) or name != metadata['compressedHash'] + '.json.gz' or metadata['pathname'] in paths:
            raise ValueError('Invalid or duplicate export file')
        if instant(metadata['uploadedAt']) > started:
            raise ValueError('Capture uploaded after export cutoff')
        paths.add(metadata['pathname'])
        captures.append(decode_capture((folder / name).read_bytes(), metadata, exported))
    return captures


def decode_capture(compressed, metadata, exported_at):
    if len(compressed) > 2_000_000 or hashlib.sha256(compressed).hexdigest() != metadata['compressedHash']:
        raise ValueError('Compressed archive identity mismatch')
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        content = stream.read(10_000_001)
    if len(content) > 10_000_000:
        raise ValueError('Archive too large')
    digest = hashlib.sha256(content).hexdigest()
    path = metadata['pathname']
    if not re.fullmatch(r'odds/\d{4}-\d{2}-\d{2}/[A-Za-z0-9T.-]+-[a-f0-9]{64}\.json\.gz', path) or not path.endswith('-' + digest + '.json.gz'):
        raise ValueError('Archive pathname mismatch')
    def reject_constant(value):
        raise ValueError('Nonfinite JSON number')
    envelope = json.loads(content, parse_constant=reject_constant)
    feed = envelope.get('feed')
    if envelope.get('schemaVersion') != 1 or envelope.get('provider') != 'The Odds API' or not isinstance(feed, dict) or feed.get('state') != 'ready' or not isinstance(feed.get('events'), list):
        raise ValueError('Invalid odds envelope')
    acquired, uploaded = instant(feed['fetchedAt']), instant(metadata['uploadedAt'])
    if not acquired <= uploaded <= exported_at:
        raise ValueError('Invalid storage chronology')
    canonical = acquired.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    if path != 'odds/' + canonical[:10] + '/' + canonical.replace(':', '-') + '-' + digest + '.json.gz':
        raise ValueError('Archive time/path mismatch')
    events = set()
    def price(value):
        return type(value) in (int, float) and math.isfinite(value) and 100 <= abs(value) <= 100000
    def point(value):
        return type(value) in (int, float) and math.isfinite(value) and abs(value) <= 150 and value * 2 == int(value * 2)
    for event in feed['events']:
        key = (event['home'], event['away'], instant(event['kickoff']))
        if key in events or event['home'] == event['away'] or not isinstance(event.get('id'), str) or not event['id']:
            raise ValueError('Invalid or duplicate event')
        events.add(key)
        books = set()
        for book in event['books']:
            if not isinstance(book.get('book'), str) or not book['book'] or book['book'] in books:
                raise ValueError('Invalid or duplicate bookmaker')
            books.add(book['book'])
            for market in ('spread', 'moneyline', 'total'):
                quote = book.get(market)
                if quote is None:
                    continue
                if instant(quote['observedAt']) > acquired:
                    raise ValueError('Quote postdates acquisition')
                prices = ('overPrice', 'underPrice') if market == 'total' else ('homePrice', 'awayPrice')
                if not all(price(quote.get(k)) for k in prices):
                    raise ValueError('Invalid price')
                if market != 'moneyline' and not point(quote.get('point' if market == 'total' else 'homePoint')):
                    raise ValueError('Invalid line')
    return {'sha256':digest, 'uploadedAt':metadata['uploadedAt'], 'feed':feed}
