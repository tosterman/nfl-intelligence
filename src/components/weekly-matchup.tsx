import React from 'react';
import snapshot from '../../data/weekly-matchup-context.json';
import { selectWeeklyContext, type WeeklyGame, type WeeklySnapshot } from '../lib/weekly-matchup';
import { WeeklyContextExpiry } from './weekly-context-expiry';

export function WeeklyMatchup({ game, kind, evidence = snapshot as WeeklySnapshot }: {
  game: WeeklyGame; kind: 'big-play' | 'inside20'; evidence?: WeeklySnapshot;
}) {
  const selected = selectWeeklyContext(evidence, game);
  const content = selected.reason ? <p className="fine">{selected.reason}</p> : <>
    <p className="fine">Completed earlier-week games before {selected.data!.cutoff}. Collected {new Date(selected.data!.sourceObservedAt).toISOString().replace('T', ' ').slice(0, 16)} UTC. Samples are pooled and are not adjusted for opponents or roster changes.</p>
    {[[game.away, game.home], [game.home, game.away]].map(([offense, defense]) => {
      const produced = selected.data!.teams[offense].offense, allowed = selected.data!.teams[defense].defense;
      const rows = kind === 'big-play' ? [
        ['Pass · 20+ yards', produced.passing.explosive, produced.passing.plays, allowed.passing.explosive, allowed.passing.plays],
        ['Run · 10+ yards', produced.rushing.explosive, produced.rushing.plays, allowed.rushing.explosive, allowed.rushing.plays],
      ] as const : [['Inside-20 TD', produced.inside20.touchdowns, produced.inside20.possessions, allowed.inside20.touchdowns, allowed.inside20.possessions]] as const;
      const rate = (n: number, d: number) => <span className="explosive-rate"><strong>{d ? `${(100 * n / d).toFixed(1)}%` : <><span aria-hidden="true">—</span><span className="sr-only">Unavailable</span></>}</strong><small>{n} / {d} {kind === 'big-play' ? 'plays' : 'possessions'}</small></span>;
      return <div className="explosive-pair" key={offense}>
        <h4>{offense} offense vs {defense} defense</h4>
        <p className="fine">Offense sample: {produced.gameIds.length} {produced.gameIds.length === 1 ? 'game' : 'games'} · Defense sample: {allowed.gameIds.length} {allowed.gameIds.length === 1 ? 'game' : 'games'}</p>
        <table className="comparison"><caption className="sr-only">Current-season {offense} produced versus {defense} allowed</caption>
          <thead><tr><th scope="col">Play</th><th scope="col">Produced</th><th scope="col">Allowed</th></tr></thead>
          <tbody>{rows.map(([label, n, d, an, ad]) => <tr key={label}><th scope="row">{label}</th><td>{rate(n, d)}</td><td>{rate(an, ad)}</td></tr>)}</tbody>
        </table>
      </div>;
    })}
    <p className="fine">Descriptive evidence only. These samples do not change the forecast.</p>
  </>;
  return <div className="weekly-matchup"><h3>This season · {game.season}</h3>
    {selected.expiresAt ? <WeeklyContextExpiry expiresAt={selected.expiresAt}>{content}</WeeklyContextExpiry> : content}
  </div>;
}
