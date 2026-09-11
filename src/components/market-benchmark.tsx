import {date,time} from '@/lib/teams';
import {parseMarketBenchmark} from '@/lib/market-benchmark';
const reasonLabels:Record<string,string>={
  'stale-capture':'Capture outside the required time window', 'stale-quote':'Bookmaker update too old',
  'excluded-before-protocol':'Checkpoint before protocol activation','missing-forecast':'No eligible published entry forecast',
  'pending-result':'Final result not yet available','missing-market':'Market absent','missing-book':'Book absent',
  'missing-capture':'No eligible capture','invalid-numeric-pair':'Invalid numerical comparison'};
const checkpointLabels:Record<string,string>={evaluated:'Closing checkpoints evaluated',pending:'Not yet due at this audit',
  'excluded-before-protocol':'Before protocol activation','missing-kickoff':'Kickoff unavailable',
  'missing-book-coverage':'No bookmaker coverage at the checkpoint','export-too-early':'Capture archive does not reach the checkpoint'};
export function MarketBenchmarkPanel({data,now}:{data:unknown;now:number}){
  const report=parseMarketBenchmark(data,now);
  if(!report)return <section className="panel"><h2>Matched market comparison</h2><p>The retained benchmark report is unavailable. Missing evidence is not a zero error score.</p></section>;
  const paired=report.books.filter(row=>row.pairedGames>0);
  return <section className="panel market-benchmark" aria-labelledby="market-benchmark-title">
    <p className="eyebrow">Same games · Each sportsbook separately</p>
    <h2 id="market-benchmark-title">Matched market comparison</h2>
    <p className="lead">{report.pairedGameCount?`${report.pairedGameCount} completed games with at least one eligible comparison`:'No eligible completed comparisons yet'}</p>
    <p>This comparison uses forecasts published by 24 hours before kickoff and market lines captured in the final 15 minutes. It differs from the latest-pregame record above. Lower average error is better; tied scores count.</p>
    <p className="fine">Audit: {date(report.checkedAt)} {time(report.checkedAt)} ET. Captures covered through {date(report.coverageThrough)} {time(report.coverageThrough)} ET. Later captures and results are not included automatically.</p>
    {paired.length>0&&<div className="ratings-table-wrap" tabIndex={0} role="region" aria-label="Paired model and market errors">
      <table className="ratings-table"><caption>Average absolute error in points on identical games within each row</caption><thead><tr><th scope="col">Book / market</th><th scope="col">Games</th><th scope="col">Model</th><th scope="col">Market</th></tr></thead>
        <tbody>{paired.map(row=><tr key={`${row.book}-${row.market}`}><th scope="row">{row.book} / {row.market}</th><td>{row.pairedGames}</td><td>{row.modelMae!.toFixed(2)}</td><td>{row.marketMae!.toFixed(2)}</td></tr>)}</tbody></table>
    </div>}
    <p>{Object.entries(report.closingCheckpointCounts).map(([status,n])=>`${checkpointLabels[status]??status}: ${n}`).join(' · ')}.</p>
    {report.excludedBookMarketCount>0&&<p>{report.excludedBookMarketCount} sportsbook-and-market entries excluded across {report.excludedGameCount} {report.excludedGameCount===1?'game':'games'}. Multiple entries can refer to the same game.</p>}
    <details><summary>Coverage and exclusions by sportsbook</summary>
      <p className="fine">Counts refer to games within each book and market. Reasons may overlap. Books share games, so their counts must not be added as unique games.</p>
      {!report.books.length&&<p>No due bookmaker comparisons in this audit.</p>}
      <ul className="weekly-change-list">{report.books.map(row=><li key={`${row.book}-${row.market}`}>
        <strong>{row.book} · {row.market==='spread'?'Spread':'Total'}</strong>
        <p>{row.pairedGames} paired · {row.excludedGames} excluded</p>
        {Object.entries(row.exclusionReasons).map(([reason,n])=><p className="fine" key={reason}>{reasonLabels[reason]??reason}: {n}</p>)}
      </li>)}</ul>
    </details>
    <p className="fine">Near-kickoff samples do not establish a bookmaker’s exact closing price. These errors do not measure betting returns or prove an edge.</p>
    <details><summary>Audit identity and method</summary><p className="fine">Report fingerprint: <code style={{overflowWrap:'anywhere'}}>{report.reportHash}</code>. The report retains private source traces; no sportsbook quote archive is exposed here.</p><a href="https://github.com/tosterman/nfl-intelligence/blob/internal-development/docs/market-benchmark.md">Read the calculation and limits →</a></details>
  </section>;
}
