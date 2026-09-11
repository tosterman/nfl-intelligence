"""Verify that the public reader serves the exact independently published bundle."""
import json
import re
import time
from datetime import datetime, timezone
from urllib.request import Request, build_opener
from production_health import ROOT, ORIGIN, NoRedirect, validate_health


def verify(expected, status, payload, now):
    if expected.get('mode') != 'published' or not re.fullmatch('[a-f0-9]{64}', expected.get('manifestHash') or ''):
        raise ValueError('Missing successful storage publication receipt')
    validate_health('weather', status, payload, now)
    if payload.get('manifestHash') != expected['manifestHash'] or payload.get('generatedAt') != expected['generatedAt']:
        raise ValueError('Public weather does not match the published bundle')


def main():
    expected = json.loads((ROOT / 'release-recovery/weather-publication-report.json').read_text())
    attempts = []
    for attempt in range(7):
        result = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'healthy': False}
        try:
            request = Request(ORIGIN + '/api/weather-status', headers={'Cache-Control': 'no-cache'})
            with build_opener(NoRedirect()).open(request, timeout=10) as response:
                raw = response.read(100001)
                if len(raw) > 100000:
                    raise ValueError('Oversized weather response')
                verify(expected, response.status, json.loads(raw), datetime.now(timezone.utc))
            result['healthy'] = True
        except (OSError, ValueError, TypeError, KeyError) as error:
            result['failure'] = type(error).__name__
        attempts.append(result)
        if result['healthy']:
            break
        if attempt < 6:
            time.sleep(15)
    report = {'manifestHash': expected.get('manifestHash'), 'healthy': attempts[-1]['healthy'], 'attempts': attempts}
    (ROOT / 'release-recovery/weather-public-readback.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return 0 if report['healthy'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
