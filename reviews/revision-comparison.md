# Forecast revision comparison — 2026-09-10

Founding section 21 previously displayed a generic "Input refresh" for any unchanged version label. That could misidentify a code-only rerun as new football evidence.

The game page now shows the latest revision first and lets readers expand older ones. Each comparison reports home and away expected-point changes, home margin, total, and home win chance in percentage points. Source hashes, code hashes, configuration and training sample are compared separately. Legacy missing provenance is explicitly incomplete. Source-file changes do not imply a particular injury, player or weather adjustment.

Six regression cases cover source changes without changed numbers, code changes without a version bump, configuration key ordering, missing provenance, arithmetic direction/percentage-point units and cross-game rejection. Independent code review found no blocking defect; its two improvements (display margin change and identify incomplete provenance in either snapshot) were adopted.

Actual local browser evidence: latest SF/LAR revision reports unchanged projections and changed model code. Expanding revision 2 shows +4.9 percentage points home win probability, +1.4 home expected points, -0.3 away points, +1.1 total, model-version and training-sample changes, and incomplete legacy provenance. At viewport320, document width305 and revision width229 showed no document overflow. This is generation-history analysis; it does not establish public pregame publication.
