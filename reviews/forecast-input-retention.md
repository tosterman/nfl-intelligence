# Reusable forecast input retention

The archive stores exact edition JSON and its verified CSV inputs as compressed
objects addressed by the uncompressed content hash. An immutable manifest binds
paths, raw and compressed hashes, byte lengths, edition generation time and site
hash. Retention validates all source identities before writing a completion
manifest. Existing objects are reused only after their decompressed bytes match;
valid alternative compression is preserved. Corrupt or conflicting content fails.

Restore validates the manifest digest, allowed unique paths, object integrity and
complete correspondence to the edition's required source files before writing.
Existing destination files cannot be silently overwritten. Generation time is
not a storage or public-availability timestamp. This archive does not preserve
an engine executable; numerical replay depends on matching retained model code.

The current real edition is retained in 19 objects totaling 1,695,797 compressed
bytes. Manifest:
`b662fbbc53d786bb1994a1a51838943a2a6426226654363f46356acd10cb27ff`.
All 15 current forecasts reproduced exactly after restoring this bundle into a
temporary directory with network access forbidden. See `input-archive-replay.json`.

The staged refresh workflow retains a bundle after input verification, includes
the archive in recovery artifacts, and stages it in the publication Git commit.
The staged CI workflow restores and numerically replays the initial bundle.
The refresh workflow remains disabled; these changes do not demonstrate a
successful hosted refresh or deployment.

Five targeted tests cover exact roundtrip and reuse, mismatched source rejection,
corrupt stored objects, unsafe manifest identities and reuse of alternate valid
gzip encoding. Independent review found the compression portability defect;
a failing regression reproduced it before the fix. The full Python suite passed
278 tests before that final regression; the final targeted suite has five passes.
The independent reviewer reran those five tests, confirmed the portability fix,
and found no additional material issue.

Automatic source-record comparisons between newly retained bundles remain to be
connected. Existing source-history UI still requires its known exact hash pair.
