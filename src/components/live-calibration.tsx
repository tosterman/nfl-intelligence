type Bin = {
  lower: number;
  upper: number;
  count: number;
  predicted: number;
  observed: number;
  observedLow95: number;
  observedHigh95: number;
};
const percent = (value: number) => `${(value * 100).toFixed(1)}%`;
export function LiveCalibration({ bins }: { bins: Bin[] }) {
  return (
    <section
      aria-labelledby="live-calibration-heading"
      className="live-calibration"
    >
      <h3 id="live-calibration-heading">Live probability calibration</h3>
      <p>
        When we forecast a 60% home win chance, do home teams win about 60% of
        those games? Only verified pregame forecasts and decisive final results
        enter this comparison.
      </p>
      {bins.length ? (
        <>
          <div
            className="ratings-table-wrap"
            tabIndex={0}
            role="region"
            aria-label="Live calibration values; scroll horizontally if needed"
          >
            <table className="comparison">
              <thead>
                <tr>
                  <th scope="col">Forecast band</th>
                  <th scope="col">Average forecast</th>
                  <th scope="col">Home wins</th>
                  <th scope="col">95% interval</th>
                  <th scope="col">Games</th>
                </tr>
              </thead>
              <tbody>
                {bins.map((b) => (
                  <tr key={b.lower}>
                    <th scope="row">
                      {Math.round(b.lower * 100)}–{Math.round(b.upper * 100)}%
                    </th>
                    <td>{percent(b.predicted)}</td>
                    <td>{percent(b.observed)}</td>
                    <td>
                      {percent(b.observedLow95)}–{percent(b.observedHigh95)}
                    </td>
                    <td>{b.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="fine">
            Intervals describe uncertainty in the observed home win rate using
            the Wilson method. They assume independent outcomes; shared teams
            and weekly conditions can create dependence. Small groups are
            especially uncertain. This is a descriptive check, not a guarantee
            of future accuracy.
          </p>
        </>
      ) : (
        <p className="fine">
          Awaiting eligible decisive results. Empty groups are not shown as 0%
          accuracy.
        </p>
      )}
      <p className="fine">
        Bands are fixed in advance: 0–40%, 40–50%, 50–60%, 60–70%, and 70–100%.
        Boundary values enter the higher band; 100% remains in the final band.
        Ties are excluded because these probabilities are conditional on a
        decisive result.
      </p>
    </section>
  );
}
