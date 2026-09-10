# Historical participation in personnel panels

Each reported player now has an expandable historical-participation section. Available entries show source season, appearance count, last appearance date, offense/defense/special-teams weighted shares, and historical teams. A team-change statement appears when the reported team is absent from those appearances. Unknown identities and missing history show no numeric shares.

The runtime selector binds the export to the displayed personnel source hash and exact retrieval time, requires a unique player ID/team/season/type/week match and exact name, and accepts only corroborated identity status. It rejects invalid/future calculation times, invalid appearance dates or counts, unknown teams, and nonfinite/out-of-range shares. Conflicting duplicate names within one player scope are rejected. The panel sits inside the existing personnel expiry boundary.

Copy describes appearance-conditioned, recency-weighted historical shares, including the eight-appearance limit and 90-day half-life. It explicitly rejects current availability, expected snaps and player-value interpretations. The source section links the 2025 snap-count CSV and labels it revised historical data rather than a preserved pregame vintage.

The refresh workflow now rebuilds identity audit, usage audit and public export after collecting personnel. The optional step preserves the previous artifact on failure; mismatched retrieval/source bindings withhold it in the UI. Both native Git staging and REST runtime packaging include the artifact. Recovery uploads include the two audit outputs. This workflow change has not yet been exercised in production.

Validation: 96 application tests passed before the final conflicting-duplicate guard; three affected tests and TypeScript checking passed afterward. Runtime packaging and all ten native publication tests passed. Chromium/WebKit at 320 and 1440 rendered 18 personnel entries in the SF/LA matchup, expanded the history with keyboard input and showed no document overflow. The mobile view was visually inspected, including unavailable identity history. Exact browser results are in `player-usage-browser.json`.

Independent automated review caught tests that depended on mutable production files and a fixed future clock, which would have blocked later refreshes. Those tests now use isolated fixtures and cover safe withholding when the artifact binding is stale. No numeric forecast, player value, or production availability claim changed. Public rollout and hosted optional-failure behavior remain to be verified.
