import { usageForPlayer, hasUsageIdentityConflict } from "@/lib/player-usage";
import type { PersonnelSnapshot, PlayerReport } from "@/lib/personnel";
import { date, pct } from "@/lib/teams";
import { SeasonParticipation } from './season-participation';

export function PlayerUsage({
  snapshot,
  player,
  historical: artifact,
  current,
}: {
  snapshot: PersonnelSnapshot;
  player: PlayerReport;
  historical: unknown;
  current: unknown;
}) {
  const usage = usageForPlayer(artifact, snapshot, player);
  return (
    <>
      {hasUsageIdentityConflict(artifact, snapshot, player) && (
        <p className="fine">
          Prior-season identity unresolved: historical participation is withheld.
          The reported identifier differs from the same-name depth-chart entry.
        </p>
      )}
      <details className="player-usage">
        <summary>Historical participation</summary>
        <SeasonParticipation snapshot={snapshot} player={player} artifact={current} />
        <h4>Prior-season history</h4>
        {usage ? (
          <>
            <p className="fine">
              {usage.season} season · {usage.appearances} recorded appearances ·
              Last appearance {date(usage.lastAppearance)},{" "}
              {new Date(usage.lastAppearance).getUTCFullYear()}.
            </p>
            <dl className="revision-deltas">
              <div>
                <dt>Offensive snap share</dt>
                <dd>{pct(usage.shares.offense_pct)}</dd>
              </div>
              <div>
                <dt>Defensive snap share</dt>
                <dd>{pct(usage.shares.defense_pct)}</dd>
              </div>
              <div>
                <dt>Special-teams snap share</dt>
                <dd>{pct(usage.shares.st_pct)}</dd>
              </div>
            </dl>
            <p className="fine">
              Historical teams: {usage.historicalTeams.join(", ")}.
              {!usage.historicalTeams.includes(player.team)
                ? " The current reported team is not represented in these appearances."
                : ""}
            </p>
            <p className="fine">
              Recency-weighted averages across up to eight recorded appearances,
              with a 90-day half-life. Missing games are not counted as zero.
              These are historical shares, not expected snaps, availability or
              player value.
            </p>
          </>
        ) : (
          <p className="fine">
            No verified historical usage for this report. Missing or unresolved
            history does not mean zero participation.
          </p>
        )}
      </details>
    </>
  );
}
