import React from "react";
import evidence from "../../data/explosive-plays.json";
import { WeeklyMatchup } from './weekly-matchup';

type Props = { away: string; home: string; season: number; kickoff: string | null; week?: number; type?: string };
type Counts = { plays: number; explosive: number };

function Rate({ counts }: { counts: Counts }) {
  return <span className="explosive-rate">
    <strong>{counts.plays ? `${(100 * counts.explosive / counts.plays).toFixed(1)}%` : "Unavailable"}</strong>
    <small>{counts.explosive} / {counts.plays} credited plays</small>
  </span>;
}

export function ExplosiveMatchup({ away, home, season, kickoff, week, type }: Props) {
  const valid = season === evidence.season + 1 && away !== home &&
    Object.hasOwn(evidence.teams, away) && Object.hasOwn(evidence.teams, home) &&
    kickoff !== null && Number.isFinite(Date.parse(kickoff)) &&
    Date.parse(kickoff) >= Date.parse(`${evidence.cutoff}T00:00:00Z`);
  if (!valid) return <section className="panel"><h2 id="explosive-heading" tabIndex={-1}>Historical comparison unavailable</h2>
    <p>Compatible prior-season big-play evidence is not available for this matchup.</p></section>;
  const rows = evidence.teams as Record<string, typeof evidence.teams.BUF>;
  return <section className="panel explosive-panel" aria-labelledby="explosive-heading">
    <div className="eyebrow">BIG-PLAY MATCHUP</div>
    <h2 id="explosive-heading" tabIndex={-1}>Who created the big plays?</h2>
    <WeeklyMatchup game={{ away, home, season, kickoff, week, type }} kind="big-play" />
    <h3>Last season · {evidence.season}</h3>
    <p>{evidence.season} regular season and playoffs. Compare what each offense produced with what the opposing defense allowed.</p>
    <div className="explosive-matchups">
      {[[away, home], [home, away]].map(([offense, defense]) => <div key={offense} className="explosive-pair">
        <h3>{offense} offense <span>vs</span> {defense} defense</h3>
        <table className="comparison">
          <caption className="sr-only">{offense} produced versus {defense} allowed, historical explosive-play rates</caption>
          <thead><tr><th scope="col">Play</th><th scope="col">Produced</th><th scope="col">Allowed</th></tr></thead>
          <tbody>{([['passing', 'Pass · 20+ yards'], ['rushing', 'Run · 10+ yards']] as const).map(([kind, label]) =>
            <tr key={kind}><th scope="row">{label}</th><td><Rate counts={rows[offense].offense[kind]} /></td><td><Rate counts={rows[defense].defense[kind]} /></td></tr>
          )}</tbody>
        </table>
      </div>)}
    </div>
    <p className="fine-print">Historical rates, not a prediction of this game. Each eligible play counts equally; opponents and roster changes are not adjusted. These rates do not change the forecast.</p>
    <details><summary>Definitions &amp; source</summary>
      <p>Passing plays include sacks; rushing plays include scrambles. Two-point attempts, kneels, spikes, nullified plays and special teams are excluded. Valid penalized plays retain the source’s credited yardage. Thresholds are 20 passing yards and 10 rushing yards.</p>
      <p>Source: <a href="https://nflreadr.nflverse.com/reference/load_pbp.html">nflverse play-by-play</a>, CC BY 4.0. Prior games only, before {evidence.cutoff}. This is a historical data vintage, not a pregame publication record.</p>
    </details>
  </section>;
}
