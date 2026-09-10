import snapshot from "../../data/quarterbacks.json";
import collection from "../../data/quarterback-collection.json";
import { quarterbackForGame } from "@/lib/quarterbacks";
import type { Game } from "@/lib/types";
import { teams, date, time } from "@/lib/teams";
import { PersonnelExpiry } from "./personnel-expiry";
export function QuarterbackContext({ game }: { game: Game }) {
  return (
    <div className="quarterback-context">
      <h3>Listed first at quarterback</h3>
      <p className="fine">
        Depth-chart order, not a confirmed starter. Provider record times are
        not announcement times. These roles do not adjust the model.
      </p>
      {collection.status !== "ok" && (
        <p role="status">
          Latest depth-chart collection failed. Any roles below come from the
          previous verified snapshot.
        </p>
      )}
      <div className="personnel-teams">
        {[game.away, game.home].map((team) => {
          const role = quarterbackForGame(snapshot, game, team);
          return (
            <div key={team}>
              <h4>
                {teams[team].city} {teams[team].name}
              </h4>
              {role ? (
                <PersonnelExpiry expiresAt={role.expiresAt}>
                  <strong>{role.name}</strong>
                  <p className="fine">
                    Recorded {date(role.recordedAt)} at {time(role.recordedAt)}{" "}
                    ET
                  </p>
                </PersonnelExpiry>
              ) : (
                <p className="fine">
                  No eligible recent pregame role. Starter unknown.
                </p>
              )}
            </div>
          );
        })}
      </div>
      <details>
        <summary>Quarterback role source</summary>
        <p className="fine">
          nflverse depth charts · Acquired {date(snapshot.retrievedAt)} at{" "}
          {time(snapshot.retrievedAt)} ET. Roles expire after thirty hours or at
          kickoff.
        </p>
        <a className="text-link" href={snapshot.sourceUrl}>
          Source snapshot feed ↗
        </a>
        {" · "}
        <a href="https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md">
          Source license
        </a>
        <p className="hash">{snapshot.sourceHash}</p>
      </details>
    </div>
  );
}
