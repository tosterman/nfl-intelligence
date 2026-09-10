import {
  performanceBands,
  type DiagnosticRecord,
} from "@/lib/performance-bands";

export function PerformanceBands({ records }: { records: DiagnosticRecord[] }) {
  const groups = performanceBands(records);
  return (
    <section className="panel" style={{ marginTop: 24 }}>
      <h2>Where confidence meets the result</h2>
      <p>
        Retrospective development diagnostics, not the published-before-kickoff
        record. These fixed bands describe this sample; they were not selected
        to maximize returns. Small groups are especially uncertain.
      </p>
      <p className="fine">
        Confidence is the larger of the home and away win probabilities. At
        exactly 50%, the home side is used for winner accuracy. Ties are
        separate. Disagreement is the absolute difference between model home
        margin and the recorded closing-market home margin, not a validated
        edge.
      </p>
      {[
        { title: "By forecast confidence", bands: groups.confidence },
        { title: "By closing-market disagreement", bands: groups.disagreement },
      ].map((group) => (
        <div key={group.title}>
          <h3>{group.title}</h3>
          {group.bands.map((b) => (
            <details key={b.label} className="diagnostic-band">
              <summary>
                {b.label} · {b.records.length} games · {b.correct}/{b.decisive}{" "}
                decisive winners correct
              </summary>
              <p className="fine">
                {b.ties} tied games. Margin MAE{" "}
                {b.marginMae?.toFixed(2) ?? "Unavailable"}; total MAE{" "}
                {b.totalMae?.toFixed(2) ?? "Unavailable"}. Against the closing
                spread: {b.wins} wins, {b.losses} losses, {b.pushes} pushes;{" "}
                {b.noDirection} with no model direction.
              </p>
              <div
                className="ratings-table-wrap"
                role="region"
                tabIndex={0}
                aria-label={`${group.title}: ${b.label} constituent games`}
              >
                <table className="comparison">
                  <thead>
                    <tr>
                      <th scope="col">Game</th>
                      <th scope="col">Home win</th>
                      <th scope="col">Model margin</th>
                      <th scope="col">Final margin</th>
                      <th scope="col">Market margin</th>
                      <th scope="col">Margin error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {b.records.map((r) => (
                      <tr key={r.id}>
                        <th scope="row">{r.id.replaceAll("_", " · ")}</th>
                        <td>{(r.homeWinProbability * 100).toFixed(1)}%</td>
                        <td>{r.homeMargin.toFixed(2)}</td>
                        <td>{r.actualMargin}</td>
                        <td>{r.marketMargin?.toFixed(2) ?? "Missing"}</td>
                        <td>
                          {Math.abs(r.homeMargin - r.actualMargin).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          ))}
        </div>
      ))}
      <p className="fine">
        {groups.missingMarket} records lack a closing margin and are excluded
        from disagreement bands and spread settlement. Spread direction uses
        every nonzero model–market difference, with no selection threshold. A
        positive difference selects the home side; a negative difference selects
        away. Pushes land exactly on the market margin. These diagnostics are
        distinct from the thresholded selections above and contain no price,
        vig, stake or profit calculation.
      </p>
    </section>
  );
}
