import { intervalCoverage, type IntervalRecord } from "@/lib/interval-coverage";

export function IntervalCoverage({ records }: { records: IntervalRecord[] }) {
  const audit = intervalCoverage(records);
  return (
    <section
      className="panel"
      style={{ marginTop: 24 }}
      aria-labelledby="interval-coverage-heading"
    >
      <h2 id="interval-coverage-heading">Did the ranges leave enough room?</h2>
      <p>
        These ranges target 80% of final outcomes. The table shows how often the
        final margin and combined score landed inside them, alongside their
        average width in points. Wider ranges are easier to hit.
      </p>
      <p>
        Groups use the absolute difference between the model’s expected home
        margin and the historical closing market. A larger disagreement does not
        establish a stronger betting opportunity.
      </p>
      <div
        className="ratings-table-wrap"
        tabIndex={0}
        role="region"
        aria-label="Historical outcome range coverage by market disagreement"
      >
        <table className="comparison" style={{ minWidth: 680 }}>
          <thead>
            <tr>
              <th scope="col">Model–market difference</th>
              <th scope="col">Margin covered</th>
              <th scope="col">Margin range width</th>
              <th scope="col">Total covered</th>
              <th scope="col">Total range width</th>
            </tr>
          </thead>
          <tbody>
            {[audit.all, ...audit.disagreement].map((row) => (
              <tr key={row.label}>
                <th scope="row">{row.label}</th>
                <td>
                  {row.games
                    ? `${row.margin.covered}/${row.games} · ${((100 * row.margin.covered) / row.games).toFixed(1)}%`
                    : "No games"}
                </td>
                <td>
                  {row.margin.meanWidth == null
                    ? "—"
                    : `${row.margin.meanWidth.toFixed(1)} points`}
                </td>
                <td>
                  {row.games
                    ? `${row.total.covered}/${row.games} · ${((100 * row.total.covered) / row.games).toFixed(1)}%`
                    : "No games"}
                </td>
                <td>
                  {row.total.meanWidth == null
                    ? "—"
                    : `${row.total.meanWidth.toFixed(1)} points`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="fine">
        Historical development analysis, not forecasts published before kickoff.
        Small groups can vary substantially by chance; these comparisons do not
        establish a persistent defect or prove calibration. Margin and total are
        evaluated separately, not as a joint 80% guarantee.{" "}
        {audit.missingMarket} games without a closing spread are included in all
        games but excluded from the disagreement groups. Individual game records
        follow below.
      </p>
    </section>
  );
}
