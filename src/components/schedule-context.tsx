import Link from "next/link";
import type { Game } from "@/lib/types";
import { scheduleSpacing } from "@/lib/schedule-spacing";
import { teams, date, time } from "@/lib/teams";

export function ScheduleContext({
  game,
  games,
  now = Date.now(),
}: {
  game: Game;
  games: Game[];
  now?: number;
}) {
  const rows = scheduleSpacing(game, games, now);
  return (
    <section className="panel" style={{ marginTop: 24 }}>
      <div className="eyebrow">Schedule · Context only</div>
      <h2 id="schedule-context" tabIndex={-1}>
        Between games
      </h2>
      <p className="fine">
        Elapsed time between kickoffs, not days off or a measure of recovery.
        This does not adjust the model.
      </p>
      <dl className="revision-deltas">
        {rows.map((r) => (
          <div key={r.team}>
            <dt>{teams[r.team].name}</dt>
            <dd>
              {r.previous ? (
                <>
                  <strong>{r.days!.toFixed(1)} days</strong>
                  <br />
                  <Link href={`/games/${r.previous.id}`}>
                    Previous game:{" "}
                    {
                      teams[
                        r.previous.home === r.team
                          ? r.previous.away
                          : r.previous.home
                      ].short
                    }
                  </Link>
                  <br />
                  <small>
                    {date(r.previous.kickoff!)} · {time(r.previous.kickoff!)} ET
                  </small>
                </>
              ) : (
                r.reason
              )}
            </dd>
          </div>
        ))}
      </dl>
      <p className="fine">
        Based on the current schedule and recorded final results in this season.
        Later schedule corrections can change this context; it is not a
        preserved pregame input.
      </p>
    </section>
  );
}
