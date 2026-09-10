# A same-name collision, not a safe alias

The pinned [nflverse player registry](https://github.com/nflverse/nflverse-data/releases/download/players/players.csv) contains two distinct records for the identifiers uncovered by the personnel audit:

| Field | Personnel identifier | Depth-chart identifier |
|---|---|---|
| GSIS field | 00-0041363 | THO581952 |
| Display name | James Thompson Jr. | James Thompson |
| Position | DT | WR |
| Rookie / last season | 2026 / 2026 | 1978 / 1978 |
| Latest listed team | SF | NYG |
| PFR identifier | ThomJa06 | ThomJa01 |
| ESB identifier | THO743352 | THO581952 |

This contradicts treating the two strings as interchangeable identifiers for the current player. The depth-chart row's name/team and its identifier point to inconsistent registry identities. The prior official-team check corroborates the named current player's team presence, but does not make the incorrect identifier safe. Neither feed is rewritten, and no name-based alias is inserted into the model.

The exact registry CSV was acquired and its byte length (7,287,825) and SHA-256 (`c2402e02d39c7ca1adbd9ca5c894bb11f693ab01da0721bff44db2a8bd1ea53d`) matched GitHub release asset metadata. The compressed source is retained beside this report under the upstream CC BY 4.0 data license; see `player-registry-source.json` for attribution and archive time. `investigate_personnel_id.py` checks those bytes and links its output to the prior audit and executable code hashes.

The comparison helper joins only the declared GSIS namespace. Equal names never merge different registry IDs; missing IDs, identifiers from other namespaces, and duplicated registry rows remain unresolved or ambiguous. Tests cover those cases and reproduce this real collision from the pinned source. This investigation establishes a registry conflict, not independent confirmation of an injury or a ready canonical repair. The source ambiguity must stay visible in future cross-feed player-value work.
