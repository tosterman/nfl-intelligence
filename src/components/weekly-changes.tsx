import Link from "next/link";
import { weeklyChanges } from "@/lib/weekly-changes";
import { date, time, teams } from "@/lib/teams";
import { snapshotTime, type Game } from "@/lib/types";
const deltaText = (value: number) => `${value > 0 ? "+" : ""}${value.toFixed(3)}`;

export function WeeklyChanges({ games, week, asOf }: { games: Game[]; week: number; asOf: number }) {
  const changes = weeklyChanges(games, asOf);
  const comparable = changes.filter((row) => row.kind === "revision").length;
  const available = changes.filter((row) => row.kind !== "unavailable");
  const unavailable = games.filter((game) =>
    changes.some((row) => row.game.id === game.id && row.kind === "unavailable") ||
    (!game.snapshot && game.history.length > 0));
  return (
    <details className="panel weekly-changes">
      <summary>What changed this week? <span>Week {week} · {comparable} comparable {comparable === 1 ? "revision" : "revisions"}</span></summary>
      <p>
        Each matchup’s latest retained forecast versus its preceding run,
        ordered by largest absolute margin change, then win-chance change.
        This is not a comparison with your last visit. Times describe generation,
        not verified publication; see each game’s evidence before drawing conclusions.
      </p>
      {!available.length && <p>No comparable revisions or first current-context forecasts to summarize for this week.</p>}
      {available.length > 0 && (
        <ul className="weekly-change-list">
          {available.map(({ game, current, previous, kind, note, delta, contribution }) => (
            <li key={game.id}>
              <Link href={`/games/${game.id}#forecast-changes`}>
                {teams[game.away].name} {game.neutral ? "vs." : "at"} {teams[game.home].name} →
              </Link>
              <p>{note}</p>
              {delta && <p>
                {teams[game.home].short} margin {deltaText(delta.margin)} points · Win chance {deltaText(delta.probabilityPoints)} percentage points · Total {deltaText(delta.total)} points
              </p>}
              {contribution && <p className="fine">
                Largest reconciled term: {contribution.name}, {contribution.change > 0 ? "+" : ""}{contribution.change.toFixed(3)} points in the home margin.
                Statistical accounting, not a causal football explanation.
              </p>}
              {kind !== "unavailable" && <p className="fine">
                Generated {previous ? `${date(snapshotTime(previous))} ${time(snapshotTime(previous))} ET → ` : ""}
                {date(snapshotTime(current))} {time(snapshotTime(current))} ET
              </p>}
            </li>
          ))}
        </ul>
      )}
      {unavailable.length > 0 && <details>
        <summary>{unavailable.length} matchup {unavailable.length === 1 ? "history" : "histories"} cannot be compared here</summary>
        <p>Current matchup context, timing or model/source identity is missing or incompatible. The retained histories remain available:</p>
        <ul className="weekly-change-list">
          {unavailable.map((game) => <li key={game.id}><Link href={`/games/${game.id}#forecast-changes`}>
            {teams[game.away].name} {game.neutral ? "vs." : "at"} {teams[game.home].name} →
          </Link></li>)}
        </ul>
      </details>}
    </details>
  );
}
