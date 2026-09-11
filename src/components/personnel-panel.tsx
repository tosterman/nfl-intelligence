import type { PersonnelEvidence } from '@/lib/personnel-evidence';
import { personnelForGame, orderPersonnelReports } from "@/lib/personnel";
import type { Game } from "@/lib/types";
import { teams, date, time } from "@/lib/teams";
import { PersonnelExpiry } from "./personnel-expiry";
import { PersonnelChangesPanel } from "./personnel-changes";
import { QuarterbackContext } from "./quarterback-context";
import { PlayerUsage } from "./player-usage";
import { PersonnelBriefing } from './personnel-briefing';

export function PersonnelPanel({ game, evidence }: { game: Game; evidence: PersonnelEvidence | null }) {
  if(!evidence)return <section className="panel personnel-panel">
    <div className="eyebrow">Personnel · Reported context</div>
    <h2 id="personnel-reports" tabIndex={-1}>Practice & game designations</h2>
    <p>Verified player reports are unavailable for this matchup. Availability is unknown.</p>
    <p className="fine">Personnel does not adjust this model’s forecast.</p>
  </section>;
  const { snapshot, collection, quarterback, quarterbackCollection, history, current, historical } = evidence;
  const selected = personnelForGame(snapshot, game);
  return (
    <section className="panel personnel-panel">
      <div className="eyebrow">Personnel · Reported context</div>
      <h2 id="personnel-reports" tabIndex={-1}>
        Practice & game designations
      </h2>
      <p className="fine">
        Individual report dates are unavailable. These are entries in the
        acquired weekly file, not confirmed lineups. Personnel does not adjust
        this model’s forecast.
      </p>
      <QuarterbackContext game={game} snapshot={quarterback} collection={quarterbackCollection} />
      {evidence.participationCollection.status !== 'collected' && (
        <p role="status">
          Latest participation collection failed. Any participation shown uses
          an earlier source with its original collection date.
        </p>
      )}
      {collection.status !== "ok" && (
        <p role="status">
          Latest collection failed. Any entries below come from the previous
          verified snapshot.
        </p>
      )}
      {selected.reason ? (
        <p>{selected.reason}</p>
      ) : (
        <PersonnelExpiry expiresAt={selected.expiresAt}>
          <p className="fine">
            File updated {date(snapshot.assetUpdatedAt)} at{" "}
            {time(snapshot.assetUpdatedAt)} ET · Acquired{" "}
            {date(snapshot.retrievedAt)} at {time(snapshot.retrievedAt)} ET
          </p>
          <PersonnelChangesPanel game={game} snapshot={snapshot} history={history} />
          <div className="personnel-teams">
            {[game.away, game.home].map((team) => {
              const players = orderPersonnelReports(
                selected.players.filter((r) => r.team === team),
              );
              return (
                <div key={team}>
                  <h3>
                    {teams[team].city} {teams[team].name}
                  </h3>
                  {players.length > 0 && (
                    <p className="fine">
                      {players.filter((p) => p.reportStatus !== null).length}{" "}
                      with a reported game designation ·{" "}
                      {players.filter((p) => p.reportStatus === null).length}{" "}
                      unreported. Out, doubtful and questionable entries appear
                      first. Unreported does not mean available.
                    </p>
                  )}
                  {!players.length ? (
                    <p>
                      No matching reports in this snapshot. Availability is
                      unknown.
                    </p>
                  ) : (
                    <>
                    <PersonnelBriefing snapshot={snapshot} players={players} current={current} historical={historical} />
                    <details className="personnel-full-reports">
                    <summary>Full reports & participation details · {players.length}</summary>
                    <ul className="personnel-list">
                      {players.map((player) => (
                        <li key={player.playerId}>
                          <strong>{player.name}</strong>{" "}
                          <span className="fine">{player.position}</span>
                          <div>
                            Game designation:{" "}
                            <strong>
                              {player.reportStatus ?? "Unreported"}
                            </strong>
                          </div>
                          <div className="fine">
                            Practice: {player.practiceStatus ?? "Unreported"}
                          </div>
                          {player.reportInjury && (
                            <div className="fine">
                              Game report: {player.reportInjury}
                            </div>
                          )}
                          {(player.practiceInjury ||
                            player.practiceSecondaryInjury) && (
                            <div className="fine">
                              Practice report:{" "}
                              {[
                                player.practiceInjury,
                                player.practiceSecondaryInjury,
                              ]
                                .filter(Boolean)
                                .join(" · ")}
                            </div>
                          )}
                          <PlayerUsage snapshot={snapshot} player={player} current={current} historical={historical} />
                        </li>
                      ))}
                    </ul>
                    </details>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </PersonnelExpiry>
      )}
      <details>
        <summary>Personnel source & limitations</summary>
        <p className="fine">
          Prior-season participation uses the{" "}
          <a href="https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_2025.csv">
            nflverse 2025 snap-count release
          </a>
          , joined through retained player identifiers. These revised historical
          records are not a preserved pregame data vintage.
          {' '}Current-season appearances come from the corresponding nflverse
          season release and exclude the report’s own week. They do not establish
          current availability or a player’s expected role.
        </p>
        <p className="fine">
          A blank designation or absent player does not establish health or
          availability. Practice participation is separate from game status. The
          source can revise earlier reports.
        </p>
        <a
          className="text-link"
          href="https://github.com/nflverse/nflverse-data/releases/tag/injuries"
          target="_blank"
          rel="noreferrer"
        >
          nflverse injury and practice reports ↗
        </a>
        <p className="fine">
          Normalized from nflverse data under{" "}
          <a href="https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md">
            CC BY 4.0
          </a>
          . No NFL endorsement. Empty statuses are shown as unreported.
        </p>
        <p className="hash">{snapshot.sourceHash}</p>
      </details>
    </section>
  );
}
