import React from "react";
import retainedEvidence from "../../data/prior-matchup-context.json";
import { selectPriorContext, type PriorMatchup } from '../lib/prior-matchup';
import { WeeklyMatchup } from './weekly-matchup';

type Props = { away: string; home: string; season: number; kickoff: string | null; week?: number; type?: string; evidence?: PriorMatchup };
function Rate({ counts }: { counts: { possessions: number; touchdowns: number } }) {
  return <span className="explosive-rate">
    <strong>{counts.possessions ? `${(100 * counts.touchdowns / counts.possessions).toFixed(1)}%` : "Unavailable"}</strong>
    <small>{counts.touchdowns} touchdowns from {counts.possessions} possessions</small>
  </span>;
}

export function RedZoneMatchup({ away, home, season, kickoff, week, type, evidence = retainedEvidence }: Props) {
  const valid = selectPriorContext(evidence, { away, home, season, kickoff });
  if (!valid) return <section className="panel"><h2 id="red-zone-heading" tabIndex={-1}>Inside-20 history unavailable</h2>
    <WeeklyMatchup game={{ away, home, season, kickoff, week, type }} kind="inside20" />
    <p>Compatible prior-season possession evidence is not available for this matchup.</p></section>;
  const rows = evidence.teams;
  return <section className="panel red-zone-panel" aria-labelledby="red-zone-heading">
    <div className="eyebrow">INSIDE THE 20 · MATCHUP</div>
    <h2 id="red-zone-heading" tabIndex={-1}>Who finished the drive?</h2>
    <WeeklyMatchup game={{ away, home, season, kickoff, week, type }} kind="inside20" />
    <h3>Last season · {evidence.season}</h3>
    <p>{evidence.season} regular season and playoffs. Offensive touchdowns from possessions with a snap or pre-snap situation strictly inside the opponent’s 20-yard line.</p>
    <div className="explosive-matchups">
      {[[away, home], [home, away]].map(([offense, defense]) => <div className="explosive-pair" key={offense}>
        <h3>{offense} offense <span>vs</span> {defense} defense</h3>
        <table className="comparison">
          <caption className="sr-only">Historical inside-20 touchdown rates: {offense} scored and {defense} allowed</caption>
          <thead><tr><th scope="col">Scored</th><th scope="col">Allowed</th></tr></thead>
          <tbody><tr><td><Rate counts={rows[offense].offense.inside20} /></td><td><Rate counts={rows[defense].defense.inside20} /></td></tr></tbody>
        </table>
      </div>)}
    </div>
    <p className="fine-print">Each possession counts once. Historical rates do not change the forecast and are not adjusted for opponents or roster changes.</p>
    <details><summary>Possession definition &amp; source</summary>
      <p>A possession qualifies when its pre-snap field position is less than 20 yards from the opponent’s goal line. The 20-yard line itself is excluded. Penalty situations can qualify; a long touchdown without an inside-20 situation cannot. Leaving and re-entering counts as one possession.</p>
      <p>Conversion attempts are excluded. Defensive and return touchdowns are not offensive conversions. Drives end at the touchdown, before the extra-point sequence. These are our reproducible historical counts, not a claim of official league statistics.</p>
      <p>Source: <a href="https://nflreadr.nflverse.com/reference/load_pbp.html">nflverse play-by-play</a>, CC BY 4.0. Completed games before {evidence.cutoff}. Source corrections are bound to the exact retained data used for these counts. Uses historical data collected after those games.</p>
    </details>
  </section>;
}
