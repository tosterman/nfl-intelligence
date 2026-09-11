import React from 'react';
import historical from '../../data/player-usage.json';
import current from '../../data/season-participation.json';
import { groupPersonnel } from '../lib/personnel-briefing';
import { usageForPlayer, hasUsageIdentityConflict } from '../lib/player-usage';
import { seasonParticipation } from '../lib/season-participation';
import type { PersonnelSnapshot, PlayerReport } from '../lib/personnel';
import { pct, date } from '../lib/teams';

function ParticipationFact({snapshot, player, sharedEmpty}: {snapshot: PersonnelSnapshot; player: PlayerReport; sharedEmpty: boolean}) {
  if (hasUsageIdentityConflict(historical, snapshot, player)) return <p className="fine">Identity unresolved · participation withheld.</p>;
  const season = seasonParticipation(current, snapshot, player);
  const prior = usageForPlayer(historical, snapshot, player);
  const leading = prior ? Object.entries({offense:prior.shares.offense_pct, defense:prior.shares.defense_pct, 'special teams':prior.shares.st_pct}).sort((a,b)=>b[1]-a[1])[0] : null;
  return <>
    {!sharedEmpty && <p className="fine">{season?.shares
      ? `${player.season} earlier weeks: offense ${pct(season.shares.offense)}, defense ${pct(season.shares.defense)}, special teams ${pct(season.shares.specialTeams)} · ${season.appearances} appearances (${season.currentTeamAppearances} current team, ${season.formerTeamAppearances} former teams).`
      : `${player.season} earlier-week participation ${season ? 'has no verified sample' : 'is not verified'}.`}</p>}
    {season?.shares && <p className="fine">{season.retained ? 'Retained source collected' : 'Source collected'} {date(season.sourceRetrievedAt)}.</p>}
    {!season?.shares && prior && leading && <p className="fine">{prior.season} highest snap share: {leading[0]} {pct(leading[1])} · {prior.appearances} appearances · Teams: {prior.historicalTeams.join(', ')}.</p>}
    {!season?.shares && !prior && <p className="fine">No verified prior-season participation. Missing history does not mean zero.</p>}
  </>;
}

export function PersonnelBriefing({snapshot, players}: {snapshot: PersonnelSnapshot; players: PlayerReport[]}) {
  const sharedEmpty = players.length > 0 && players.every(player => {
    const evidence = seasonParticipation(current, snapshot, player);
    return evidence !== null && evidence.shares === null;
  });
  return <div className="personnel-briefing">
    {sharedEmpty && <p className="fine">No verified {players[0].season} earlier-week sample for these players. Prior-season history is shown separately; missing games do not mean zero participation.</p>}
    {groupPersonnel(players).map(group => <section key={group.label}>
      <h4>{group.label} <span className="muted">· {group.players.length}</span></h4>
      {group.label === 'No game designation' && <p className="fine">Game availability is unreported. Practice information is separate.</p>}
      <ul className="personnel-list">{group.players.map(player => <li key={player.playerId}>
        <strong>{player.name}</strong> <span className="fine">{player.position}</span>
        {group.label === 'Other game designations' && <p className="fine">Game designation: {player.reportStatus}</p>}
        {group.label === 'No game designation' && <p className="fine">Practice: {player.practiceStatus ?? 'Unreported'}</p>}
        <ParticipationFact snapshot={snapshot} player={player} sharedEmpty={sharedEmpty} />
      </li>)}</ul>
    </section>)}
    <p className="fine">Snap shares are recency-weighted across up to eight appearances, with a 90-day half-life. Observed history is not expected snaps, availability or player value. See full reports for source dates and details.</p>
  </div>;
}
