# Source evidence in forecast history

The history panel can now expand a verified schedule-file comparison. It requires
the exact ordered source hashes and a game present in both compared schedules.
Unknown or reversed source pairs show no record explanation. The compact artifact
contains changed field names and counts, not old betting prices.

This matchup's changed fields are grouped as betting lines/prices, quarterback
identity, or other schedule fields. The separate count covers other existing
records revised; it does not claim to count additions or removals. The release
file allowlist includes the new server-side data artifact.

Prediction comparison still requires matching retained matchup context. Browser
testing initially found the source explanation hidden for all older snapshots
because they lack that context. Source-file comparison is independently supported
by exact retained hashes, so it now appears separately while prediction deltas
remain unavailable. The text explicitly disclaims forecast causality, discloses
the unknown older acquisition time, and distinguishes source lines from verified
closing odds.

All 154 application tests and TypeScript checking passed. The release-file
coverage test and three CSV comparison tests passed. The offline builder was
rerun against current verified bytes. Independent AI review confirmed the current
hash matching and attribution; it identified the future-facing count wording,
which was corrected to refer explicitly to existing records revised.

The final browser run passed all 60 combinations: 15 current forecast pages,
Chromium and WebKit, widths 320 and 1280. It opened each source explanation,
checked revision counts and the evidence limitations, and found no page errors
or horizontal overflow. The final mobile screenshot was visually inspected.
Results: `source-revision-browser.json`; screenshot: `source-revision-mobile.png`.

The evidence artifact currently covers one retained source pair. A later refresh
with different hashes suppresses this explanation until its own verified comparison
is produced. Automatic retention and comparison during refresh remains unfinished.
