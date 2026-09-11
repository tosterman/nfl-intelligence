import React from 'react';
import { weeklyChanges } from '../lib/weekly-changes';
import { snapshotTime, type Game } from '../lib/types';
import { date, time, signed } from '../lib/teams';

export function RevisionBrief({game, asOf}: {game: Game; asOf: number}) {
  const change = weeklyChanges([game], asOf)[0];
  if (!change) return null;
  const changed = change.kind === 'revision' && change.delta &&
    (change.delta.margin !== 0 || change.delta.total !== 0 || change.delta.probabilityPoints !== 0);
  return <div className="revision-brief">
    <p><strong>Latest recorded change. </strong>{changed ? <>
      {game.home} win chance {signed(change.delta!.probabilityPoints, 3)} percentage points;
      {' '}expected home margin {signed(change.delta!.margin, 3)} points;
      {' '}total {signed(change.delta!.total, 3)} points.
    </> : change.note}</p>
    {changed && change.previous && <p className="fine">Compared with {date(snapshotTime(change.previous))}, {time(snapshotTime(change.previous))} ET. These are model-run changes, not proof of a football cause or when the forecasts became public.</p>}
    <p className="fine"><a href="#forecast-changes">Inspect the recorded revisions</a></p>
  </div>;
}
