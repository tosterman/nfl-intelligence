import snapshot from "../../data/personnel.json";
import collection from "../../data/personnel-collection.json";
import { personnelForGame } from "@/lib/personnel";
import type { Game } from "@/lib/types";
import { teams, date, time } from "@/lib/teams";
import { PersonnelExpiry } from "./personnel-expiry";

export function PersonnelPanel({ game }: { game: Game }) {
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
          <div className="personnel-teams">
            {[game.away, game.home].map((team) => {
              const players = selected.players.filter((r) => r.team === team);
              return (
                <div key={team}>
                  <h3>
                    {teams[team].city} {teams[team].name}
                  </h3>
                  {!players.length ? (
                    <p>
                      No matching reports in this snapshot. Availability is
                      unknown.
                    </p>
                  ) : (
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
                        </li>
                      ))}
                    </ul>
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
