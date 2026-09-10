import Link from "next/link";
import { site, pct } from "@/lib/data";
export const metadata = { title: "Track record — Every result counts" };
export default function Performance() {
  const m = site.performance.aggregate;
  return (
    <div className="subpage">
      <div className="page-heading">
        <div className="eyebrow">Model accountability</div>
        <h1>
          The record.
          <br />
          Including the misses.
        </h1>
        <p>
          A model should be judged by what it gets right, how it gets things
          wrong, and whether its confidence is deserved.
        </p>
      </div>
      <div className="notice">
        <strong>
          Retrospective development evaluation · 2024–2025 seasons
        </strong>
        <br />
        These are historical replays, generated after the games. They are not
        predictions published before kickoff, and not evidence of profitable
        wagering. This period has been inspected during development and is no
        longer an untouched holdout.
      </div>
      <section className="panel">
        <h2>Published-before-kickoff record</h2>
        {site.livePerformance.games ? (
          <p className="lead">
            {site.livePerformance.wins} / {site.livePerformance.games} decisive
            games correct · Brier {site.livePerformance.brier?.toFixed(4)}
          </p>
        ) : (
          <p>
            No completed forecasts with verified pregame publication receipts
            yet. The record starts here, without backfilled results.
          </p>
        )}
        <p className="fine">
          {site.livePerformance.missed} completed games excluded because no
          eligible publication receipt exists. {site.livePerformance.ties} tied
          games excluded from win-probability scoring.
        </p>
      </section>
      <div className="kpi-grid">
        <div className="kpi">
          <small>Straight-up accuracy</small>
          <strong>{pct(m.accuracy)}</strong>
          <span>
            {m.wins} / {m.decisiveGames} decisive games · {m.ties} tie excluded
          </span>
        </div>
        <div className="kpi">
          <small>Brier score · Lower is better</small>
          <strong>{m.brier.toFixed(3)}</strong>
          <span>Coin-flip baseline: 0.250</span>
        </div>
        <div className="kpi">
          <small>Margin error · Points</small>
          <strong>{m.marginMae.toFixed(2)}</strong>
          <span>Closing market: {m.marketMarginMae?.toFixed(2)}</span>
        </div>
        <div className="kpi">
          <small>80% interval coverage</small>
          <strong>{pct(m.intervalCoverage)}</strong>
          <span>{m.games} games · Target: 80%</span>
        </div>
      </div>
      <div className="two-column">
        <section className="panel">
          <h2>Does confidence match reality?</h2>
          <p>
            Each dot compares the model’s average home win probability with
            actual home wins. A calibrated model follows the diagonal.
          </p>
          <svg
            className="calibration-svg"
            viewBox="0 0 390 300"
            role="img"
            aria-label="Calibration plot; tabulated values follow"
          >
            <path d="M45 20V250H365" stroke="#536071" fill="none" />
            {[0, 0.25, 0.5, 0.75, 1].map((v) => (
              <g key={v}>
                <path d={`M45 ${250 - v * 220}H365`} stroke="#2e3743" />
                <text x="33" y={254 - v * 220} textAnchor="end">
                  {pct(v)}
                </text>
                <text x={45 + v * 320} y="271" textAnchor="middle">
                  {pct(v)}
                </text>
              </g>
            ))}
            <path d="M45 250L365 30" stroke="#7f8ea2" strokeDasharray="5 6" />
            {m.calibration.map((b, i) => (
              <path
                key={`interval-${i}`}
                d={`M${45 + b.predicted * 320} ${250 - b.observedLow95 * 220}V${250 - b.observedHigh95 * 220}`}
                stroke="#acc8e8"
                strokeWidth="2"
                strokeOpacity=".5"
              />
            ))}
            {m.calibration.map((b, i) => (
              <circle
                key={i}
                cx={45 + b.predicted * 320}
                cy={250 - b.observed * 220}
                r={Math.max(5, Math.sqrt(b.count) * 0.6)}
                fill="#acc8e8"
                fillOpacity=".75"
              >
                <title>
                  {`${pct(b.predicted)} predicted; ${pct(b.observed)} observed; ${b.count} games`}
                </title>
              </circle>
            ))}
            <text className="axis-label" x="205" y="295" textAnchor="middle">
              Predicted home win probability
            </text>
          </svg>
          <details>
            <summary>Read the calibration values</summary>
            <table className="comparison">
              <thead>
                <tr>
                  <th>Predicted</th>
                  <th>Observed</th>
                  <th>Games</th>
                </tr>
              </thead>
              <tbody>
                {m.calibration.map((b, i) => (
                  <tr key={i}>
                    <td>{pct(b.predicted)}</td>
                    <td>
                      {pct(b.observed)}{" "}
                      <small>
                        ({pct(b.observedLow95)}–{pct(b.observedHigh95)})
                      </small>
                    </td>
                    <td>{b.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
          <p className="fine">
            Vertical lines and parenthesized ranges show 95% Wilson intervals
            for observed win rates. Small bins are noisy. Ties are excluded.
            This retrospective diagnostic did not tune the probability mapping.
          </p>
        </section>
        <section className="panel">
          <h2>The comparison that matters</h2>
          <table className="comparison">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Model</th>
                <th>Baseline</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Winner accuracy</td>
                <td>{pct(m.accuracy)}</td>
                <td>{pct(m.homeBaselineAccuracy)} · Home team</td>
              </tr>
              <tr>
                <td>Brier score</td>
                <td>{m.brier.toFixed(4)}</td>
                <td>0.2500 · Coin flip</td>
              </tr>
              <tr>
                <td>Mean margin error</td>
                <td>{m.marginMae.toFixed(2)}</td>
                <td>{m.marketMarginMae?.toFixed(2)} · Closing line</td>
              </tr>
              <tr>
                <td>Mean total error</td>
                <td>{m.totalMae.toFixed(2)}</td>
                <td>No comparison</td>
              </tr>
              <tr>
                <td>Log loss</td>
                <td>{m.logLoss.toFixed(4)}</td>
                <td>0.6931 · Coin flip</td>
              </tr>
            </tbody>
          </table>
          <p>
            The model improves on simple winner baselines. The closing market
            still estimates margins more accurately. We have not demonstrated a
            reliable betting advantage.
          </p>
          <p className="fine">
            The market comparison uses {m.marketGames} games with historical
            closing lines. Their intraday availability is not known.
          </p>
        </section>
      </div>
      <section className="panel">
        <h2>Against historical closing lines</h2>
        <p>
          A fixed, exploratory 2-point difference selects sides in this
          diagnostic. The threshold has not been established as profitable. No
          stakes, returns, or entry-price assumptions are implied.
        </p>
        <div className="two-column">
          {[
            ["Spreads", m.ats],
            ["Totals", m.totals],
          ].map(([name, value]) => {
            const v = value as typeof m.ats;
            return (
              <div key={name as string}>
                <h3>{name as string}</h3>
                <p className="lead">
                  {v.wins} wins · {v.losses} losses · {v.pushes} pushes
                </p>
                <p className="fine">
                  {v.noPick} games without a selected side. All {m.games} games
                  are accounted for.
                </p>
              </div>
            );
          })}
        </div>
        <div className="availability">
          <span>Closing line value</span>
          <span>Not measurable without timestamped entry prices</span>
        </div>
      </section>
      <section className="panel" style={{ marginTop: 24 }}>
        <h2>Season by season</h2>
        <div className="ratings-table-wrap">
          <table className="comparison">
            <thead>
              <tr>
                <th>Season</th>
                <th>Games</th>
                <th>Accuracy</th>
                <th>Brier</th>
                <th>Margin MAE</th>
              </tr>
            </thead>
            <tbody>
              {site.performance.bySeason.map((s) => (
                <tr key={s.season}>
                  <td>{s.season}</td>
                  <td>{s.games}</td>
                  <td>{pct(s.accuracy)}</td>
                  <td>{s.brier.toFixed(4)}</td>
                  <td>{s.marginMae.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="fine">
          Parameters selected on 2021–2022. Residual distributions estimated on
          2023. All forecasts use earlier weeks’ games. Final historical results
          are not vintage snapshots and can contain later corrections.
        </p>
        <Link className="text-link" href="/methodology">
          Read the assumptions and limitations →
        </Link>
      </section>
    </div>
  );
}
