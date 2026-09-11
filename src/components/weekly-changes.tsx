import Link from "next/link";
import { weeklyBriefing, type WeeklyBriefing } from "@/lib/weekly-changes";
import { date, time, teams } from "@/lib/teams";
import { type Game } from "@/lib/types";
import type { ContextBrief } from '@/lib/context-briefing';
import { useClock } from './market-panel';
const deltaText = (value: number) => `${value > 0 ? "+" : ""}${value.toFixed(3)}`;

export function WeeklyChanges({ games, week, asOf, returnTo, briefing, contextBriefs=[] }: { games: Game[]; week: number; asOf: number; returnTo?: string; briefing?: WeeklyBriefing; contextBriefs?: ContextBrief[] }) {
  const now=useClock(asOf,contextBriefs.map(row=>row.expiresAt));
  const context=contextBriefs.filter(row=>row.expiresAt>now && games.some(game=>game.id===row.gameId));
  const prepared = briefing ?? weeklyBriefing(games, asOf);
  const changes = prepared.changes;
  const comparable = changes.filter((row) => row.kind === "revision").length;
  const weatherCount=context.filter(row=>row.kind==='weather').length;
  const personnelCount=context.filter(row=>row.kind==='personnel').length;
  const available = changes.filter((row) => row.kind !== "unavailable");
  const unavailable = games.filter(game => prepared.unavailableIds.includes(game.id));
  const historyLink = (id: string) => `/games/${id}?from=${encodeURIComponent(returnTo ?? `/?week=${week}`)}#forecast-changes`;
  return (
    <details className="panel weekly-changes">
      <summary>What changed this week? <span>Week {week} · {weatherCount} weather {weatherCount===1?'update':'updates'} · {personnelCount} player-report {personnelCount===1?'update':'updates'} · {comparable} comparable model {comparable === 1 ? "revision" : "revisions"}</span></summary>
      <h3>Reported personnel & weather changes</h3>
      <p className="fine">Latest retained comparisons for upcoming games. These observations do not adjust the model. Unchanged or expired comparisons are omitted; no listed update does not establish that conditions are unchanged.</p>
      {!context.length && <p>No fresh, verified personnel or weather changes to summarize.</p>}
      {context.length>0 && <ul className="weekly-change-list">{context.map(row=>{
        const game=games.find(game=>game.id===row.gameId)!;
        const anchor=row.kind==='personnel'?'personnel-reports':'weather-history';
        return <li key={`${row.kind}-${row.gameId}`}>
          <Link href={`/games/${game.id}?from=${encodeURIComponent(returnTo??`/?week=${week}`)}#${anchor}`}>
            {teams[game.away].name} {game.neutral?'vs.':'at'} {teams[game.home].name} · {row.kind==='personnel'?'Player reports':'Weather'} →
          </Link>
          <p>{row.text}</p>
          <p className="fine">{row.kind==='personnel'?'Collected':'Forecast issued'} {date(row.previousAt)} {time(row.previousAt)} ET → {date(row.currentAt)} {time(row.currentAt)} ET{row.kind==='personnel'?'. Underlying report times are unknown.':''}</p>
        </li>;
      })}</ul>}
      <h3>Model changes</h3>
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
              <Link href={historyLink(game.id)}>
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
                Generated {previous ? `${date(previous.generatedAt)} ${time(previous.generatedAt)} ET → ` : ""}
                {date(current.generatedAt)} {time(current.generatedAt)} ET
              </p>}
            </li>
          ))}
        </ul>
      )}
      {unavailable.length > 0 && <details>
        <summary>{unavailable.length} matchup {unavailable.length === 1 ? "history" : "histories"} cannot be compared here</summary>
        <p>Current matchup context, timing or model/source identity is missing or incompatible. The retained histories remain available:</p>
        <ul className="weekly-change-list">
          {unavailable.map((game) => <li key={game.id}><Link href={historyLink(game.id)}>
            {teams[game.away].name} {game.neutral ? "vs." : "at"} {teams[game.home].name} →
          </Link></li>)}
        </ul>
      </details>}
    </details>
  );
}
