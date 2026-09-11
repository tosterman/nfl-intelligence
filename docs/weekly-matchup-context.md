# Weekly matchup context

Goal: evolve the current static 2025 big-play and inside-20 panels into a weekly
product. Keep prior-season history and current-season samples distinct. Preserve
the existing football definitions, exact source evidence and sample denominators.
Do not change forecast numbers or imply a validated predictive effect.

## Implemented foundation

`scripts/weekly_matchup_context.py` builds the current-season component at an
exact season, phase and week. Its boundary is the earliest scheduled game date
in that scope. Only earlier weeks with completed games strictly before that
boundary are eligible. Postseason scopes include preceding regular-season games.
This is a descriptive weekly cutoff, not a claim about historical data arrival.

Retained-source loading checks the exact play and schedule hashes and applies
only hash-bound adjudications. Each eligible game must contain both offenses,
one terminal END GAME record last in source row order, and matching final scores.
That detects missing endings and score disagreements, but cannot prove that no
intermediate play was omitted. Unknown source formats fail instead of being
silently treated as complete. A week without eligible games has an explicit
`no-eligible-games` state and no invented zero rates.

Outputs retain game IDs for team sample sizes, passing/rushing numerators and
denominators, inside-20 possession/TD counts, cutoff, source hashes, adjudication
identity and observation time. They aggregate plays and possessions, not averages
of team/game percentages. Late source corrections require a new retained vintage;
older snapshot artifacts must not be silently overwritten.

## Remaining integration

1. Current-season acquisition and immutable snapshots are implemented in
   `refresh_weekly_matchup.py`. Provider asset URL, size, SHA-256 and update time
   are checked; files older than 30 hours fail. Collection completion time is
   retained separately from its start. A local real 2026 capture succeeded with
   a Week 1 `no-eligible-games` result. Prior-season rotation remains to be built;
   the existing dated 2025 panels still use their pinned archive.
2. Content-addressed weekly artifacts and manifests are retained. First public
   publication identities remain separate work; local retention proves no public
   pregame availability.
3. The shared refresh, recovery artifact paths, Git publication paths and runtime
   allowlist are wired in the development branch. The production refresh remains
   disabled pending the existing release recovery; no hosted weekly run is claimed.
4. Both panels now show separated prior/current-season samples, game counts,
   cutoffs and source observation times. Missing or expired current data leaves
   dated historical evidence visible. See `reviews/weekly-matchup-ui.md` for the
   tested empty state and limitations of fixture-only positive samples.
5. Exercise refresh failure/recovery and mobile/desktop browser behavior before
   publishing. Model integration remains a separate evaluation decision.

## Evidence

Eight targeted tests cover week boundaries, same/later-week changes, anomalously
dated later weeks, missing coverage, unfinished games, postseason transition,
partial terminal records, score disagreement and nonchronological play IDs. A
real replay caught inserted timeout IDs exceeding END GAME in KC/JAX and NE/BAL;
the check uses retained row order, not ID magnitude. Historical offline builds at
2025 Weeks 2, 10, 18 and postseason Week 22 are recorded in `reviews/weekly-matchup-replay.json`.
The pre-terminal-check and corrected post-terminal-check results share the same
artifact digests at all three boundaries (16, 135 and 256 eligible games). The
independent review is scoped to the builder, not the
unimplemented refresh or UI integration.

Postseason source review found that schedule rows use WC/DIV/CON/SB rather than
POST. The builder now normalizes those round codes for weekly phase matching and
earlier-round eligibility. The real Week 22 replay includes 284 prior games and
excludes the Super Bowl at the February 8 boundary. All three regular-season
artifact hashes remain unchanged. Earlier synthetic POST-only tests had missed
this source vocabulary mismatch; a regression now uses the actual round codes.

Prior-season rotation remains open. The provider's 2025 compressed source still
matches the retained hash, but its asset update is August 13, 2026. A historical
archive's age must be treated separately from the 30-hour current-feed freshness
rule; immutable source identity and complete-season validation remain required.

The shared builder now also creates `data/prior-matchup-context.json` for a
forecast season's preceding season. It requires a scheduled following-season
opener, completed prior-season rows, one Super Bowl, regular-season coverage,
matching terminal scores and both offensive samples for every supplied game.
This validates completeness against the supplied schedule; it cannot establish
that the schedule itself omits no games. Prior-season and weekly samples remain
separate, and neither changes numerical forecasts.

`python -O -m scripts.replay_prior_matchup_context` reconciles every team's
offensive and defensive passing, rushing and inside-20 counts, and all game
sets, against the retained historical panels: 285 games, 32 teams. The result is
recorded in `reviews/prior-matchup-replay.json`. Validation uses explicit errors
so Python optimization cannot skip comparisons. Three targeted tests cover prior
scope and deliberate reconciliation failures; all eight weekly builder tests
also pass. The shared aggregation refactor preserves the four recorded weekly
replay hashes. Automatic historical acquisition and UI consumption of this new
artifact were initially separate integration steps. Both historical matchup
panels now consume this artifact through `selectPriorContext`, which validates
the forecast/prior-season relationship, teams, source hashes, and dates. It does
not apply current-feed expiry to historical evidence. The runtime release copy
includes the artifact. Two additional TypeScript tests cover selection, a
synthetic following-season transition, and every historical count. Automatic
historical acquisition still remains pending; UI consumption alone is not a
complete season-rollover implementation.

Acquisition has four additional tests: immutable repeat capture/corrupt existing
object rejection; bad digest/stale/future metadata rejection; and failed refresh
preserving earlier archives while replacing current state with unavailable; and
reproducing the current artifact from its retained manifest and source bytes.
An independent acquisition review found no material defect. UI integration now
validates scope and source freshness before display; positive live samples remain
unavailable at the current Week 1 cutoff.
The full Python suite passed 295 tests before the final artifact-replay test was
added; all four targeted acquisition tests then passed.
