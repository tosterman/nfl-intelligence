import {
  personnelChangesForGame,
  type PersonnelChanges,
} from "@/lib/personnel-changes";
import type { PersonnelSnapshot } from "@/lib/personnel";
import type { Game } from "@/lib/types";
import { date, time } from "@/lib/teams";
const labels: Record<string, string> = {
  name: "Listed name",
  position: "Position",
  reportStatus: "Game designation",
  practiceStatus: "Practice",
  reportInjury: "Game report",
  practiceInjury: "Practice report",
  practiceSecondaryInjury: "Secondary practice report",
};
export function PersonnelChangesPanel({
  game,
  snapshot,
  history,
}: {
  game: Game;
  snapshot: PersonnelSnapshot;
  history: PersonnelChanges;
}) {
  const selected = personnelChangesForGame(
    history as PersonnelChanges,
    snapshot,
    game,
  );
  if (!selected)
    return (
      <p className="fine">
        A verified comparison with the previous personnel collection is
        unavailable.
      </p>
    );
  return (
    <details className="personnel-changes">
      <summary>
        Since the previous collection ·{" "}
        {selected.changes.length
          ? `${selected.changes.length} player entries changed`
          : "No changes observed"}
      </summary>
      <p className="fine">
        Compared {date(selected.start)} at {time(selected.start)} ET with{" "}
        {date(selected.end)} at {time(selected.end)} ET. These are collection
        times; the time of each underlying report is unknown.
      </p>
      {selected.changes.length ? (
        <ul className="personnel-list">
          {selected.changes.map((c) => (
            <li key={`${c.team}-${c.playerId}`}>
              <strong>{c.playerName}</strong>{" "}
              <span className="fine">
                {c.team} · {c.position}
              </span>
              {c.kind === "no-longer-present" ? (
                <p>
                  No longer present in this weekly file. This does not establish
                  that the player is cleared or available.
                </p>
              ) : c.kind === "first-observed" ? (
                <p>
                  First observed in this weekly file. This does not establish
                  when the report began.
                </p>
              ) : null}
              {c.kind !== "no-longer-present" && (
                <ul>
                  {Object.entries(c.fields)
                    .filter(
                      ([key]) =>
                        c.kind === "changed" ||
                        !["name", "position"].includes(key),
                    )
                    .map(([key, value]) => (
                      <li key={key}>
                        {labels[key] ?? key}:{" "}
                        {c.kind === "changed" && (
                          <>{value.before ?? "Unreported"} → </>
                        )}
                        <strong>{value.after ?? "Unreported"}</strong>
                      </li>
                    ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="fine">
          No differences in the two teams’ matching weekly entries. This does
          not confirm unchanged health or lineups.
        </p>
      )}
    </details>
  );
}
