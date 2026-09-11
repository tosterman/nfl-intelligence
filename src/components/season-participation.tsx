import artifact from '../../data/season-participation.json';
import { seasonParticipation } from '../lib/season-participation';
import type { PersonnelSnapshot, PlayerReport } from '../lib/personnel';
import { date, pct } from '../lib/teams';

export function SeasonParticipation({snapshot, player}: {snapshot: PersonnelSnapshot; player: PlayerReport}) {
  const evidence = seasonParticipation(artifact, snapshot, player);
  return <div className="season-participation">
    <h4>{player.season} season · Earlier weeks</h4>
    {!evidence ? <p className="fine">Current-season participation is not verified for this report.</p> : <>
      {evidence.shares ? <>
        <p className="fine">{evidence.appearances} recorded appearances · Last appearance {date(evidence.lastAppearance!)}.</p>
        <dl className="revision-deltas">
          <div><dt>Offensive snap share</dt><dd>{pct(evidence.shares.offense)}</dd></div>
          <div><dt>Defensive snap share</dt><dd>{pct(evidence.shares.defense)}</dd></div>
          <div><dt>Special-teams snap share</dt><dd>{pct(evidence.shares.specialTeams)}</dd></div>
        </dl>
        <p className="fine">Recency-weighted averages across up to eight recorded appearances, with a 90-day half-life. These are not full-season totals; missing games are not counted as zero.</p>
        <p className="fine">Current reported team: {evidence.currentTeamAppearances} appearances. Former teams: {evidence.formerTeamAppearances}. Both counts use the same sample.</p>
      </> : <p className="fine">No verified earlier-week appearances in this season’s source. Missing records do not mean zero participation or an absence.</p>}
      <p className="fine">{evidence.retained ? 'Retained source collected' : 'Source collected'} {date(evidence.sourceRetrievedAt)}. Same-week games are excluded; completed games also require a 24-hour buffer.</p>
    </>}
    <p className="fine">Observed participation, not expected snaps, availability or player value. No forecast adjustment.</p>
  </div>;
}
