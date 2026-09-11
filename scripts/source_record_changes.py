"""Compare verified CSV vintages without attributing forecast causality."""
import csv
import hashlib
import io
import re


def read_records(raw, expected, keys):
    if not isinstance(expected, str) or not re.fullmatch('[a-f0-9]{64}', expected):
        raise ValueError('Invalid source digest')
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Source digest mismatch')
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), strict=True)
    columns = reader.fieldnames
    if not columns or any(not column for column in columns) or len(set(columns)) != len(columns):
        raise ValueError('Invalid source columns')
    if not keys or len(set(keys)) != len(keys) or any(key not in columns for key in keys):
        raise ValueError('Invalid record identity columns')
    records = {}
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError('Malformed source row')
        identity = tuple(row[key] for key in keys)
        if any(not value.strip() for value in identity) or identity in records:
            raise ValueError('Missing or duplicate source identity')
        records[identity] = row
    if not records:
        raise ValueError('Empty source records')
    return set(columns), records


def compare_csv(before, after, before_sha256, after_sha256, keys):
    old_columns, old = read_records(before, before_sha256, keys)
    new_columns, new = read_records(after, after_sha256, keys)
    if old_columns != new_columns:
        raise ValueError('Source schema changed; explicit migration required')
    added = [{'key': list(key), 'record': new[key]} for key in sorted(new.keys() - old.keys())]
    removed = [{'key': list(key), 'record': old[key]} for key in sorted(old.keys() - new.keys())]
    revised = []
    for key in sorted(old.keys() & new.keys()):
        fields = {field: {'before': old[key][field], 'after': new[key][field]}
                  for field in sorted(old_columns) if old[key][field] != new[key][field]}
        if fields:
            revised.append({'key': list(key), 'fields': fields})
    return {'beforeSha256': before_sha256, 'afterSha256': after_sha256,
            'identityColumns': list(keys), 'beforeRows': len(old), 'afterRows': len(new),
            'bytesChanged': before_sha256 != after_sha256,
            'recordsChanged': bool(added or removed or revised),
            'added': added, 'removed': removed, 'revised': revised,
            'interpretation': 'Exact string field differences between verified source bytes. Not proof of correction intent, model influence, or historical availability.'}
