import Link from 'next/link';

export function LiveRecordSummary({ record }: {
  record: { games: number; wins: number; ties: number; missed: number };
}) {
  return <section className="live-record-summary" aria-label="Live model record">
    <div>
      <p className="eyebrow">Live model record · All tracked games</p>
      <h2>{record.games > 0
        ? `${record.wins} of ${record.games} decisive games correct`
        : 'No eligible decisive results yet'}</h2>
      <p>Only forecasts with verified pregame publication and matching game context count.</p>
      <p className="fine">{record.missed} completed {record.missed === 1 ? 'game' : 'games'} excluded for missing eligible evidence.
        {' '}{record.ties} eligible {record.ties === 1 ? 'tie' : 'ties'} excluded from winner accuracy.</p>
    </div>
    <Link href="/performance">Results, coverage &amp; methodology <span aria-hidden="true">↗</span></Link>
  </section>;
}
