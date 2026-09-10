import Link from "next/link";
import { site, pct } from "@/lib/data";
import { LiveCalibration } from "@/components/live-calibration";
import { marginComparisonSummary } from "@/lib/performance-summary";
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
      <details className="panel metric-guide">
        <summary>How to read this record</summary>
        <dl>
          <div>
            <dt>Winner accuracy</dt>
            <dd>
              How often the more likely team won. Ties are excluded. Getting
              the winner right does not mean a bet beat its price or spread.
            </dd>
          </div>
          <div>
            <dt>Margin and total error · Lower is better</dt>
            <dd>
              Mean absolute error (MAE) is the average distance from the final
              result, in points. Predicting a home win by 7 when the home team
              wins by 3 gives a margin error of 4. Total error measures the
              combined score the same way.
            </dd>
          </div>
          <div>
            <dt>Brier score and log loss · Lower is better</dt>
            <dd>
              These score the probability, not just the chosen winner. A 60%
              home win forecast has a Brier score of 0.16 if the home team wins
              and 0.36 if it loses. Log loss penalizes confident mistakes more
              sharply. Both scores are averaged across decisive games.
            </dd>
          </div>
          <div>
            <dt>Calibration</dt>
            <dd>
              Across many games forecast near 60%, roughly 60% should go that
              way. The chart checks that relationship; a small group can look
              good or bad by chance.
            </dd>
          </div>
          <div>
            <dt>80% interval coverage</dt>
            <dd>
              The share of final results inside the forecast ranges. The target
              is about 8 in 10 over many games, not 100%. Coverage also needs to
              be judged alongside range width: wider ranges are easier to hit.
            </dd>
          </div>
          <div>
            <dt>Closing line and push</dt>
            <dd>
              The closing line is the recorded market benchmark near kickoff;
              it may differ from a price available earlier. A push lands exactly
              on the spread or total and is counted separately from wins and
              losses.
            </dd>
          </div>
        </dl>
      </details>
      <section className="panel">
        <h2>Published-before-kickoff record</h2>
        {site.livePerformance.games ? (
          <p className="lead">
            {site.livePerformance.wins} / {site.livePerformance.games} decisive
            games correct · Brier {site.livePerformance.brier?.toFixed(4)}
          </p>
        ) : site.livePerformance.scoreGames ? (
          <p>
            No decisive results yet. Eligible tied games are included in score
            errors below.
          </p>
        ) : (
          <p>
            No completed forecasts with verified pregame publication and
            matching game context yet. The record starts here, without
            backfilled results.
          </p>
        )}
        <p className="fine">
          {site.livePerformance.missed} completed games excluded because no
          eligible publication with matching game context exists.{" "}
          {site.livePerformance.ties} tied games excluded from win-probability
          scoring.
        </p>
        <p>
          Score errors include every eligible completed game, including ties. We
          grade the latest generated forecast verified publicly available before
          kickoff, with the same teams, kickoff, venue and neutral-site status.
          Later revisions cannot replace it. Older archives without that context
          remain in history but do not qualify for this record.
        </p>
        {site.livePerformance.scoreGames > 0 && (
          <>
            <dl className="live-score-metrics">
              <div>
                <dt>Margin error</dt>
                <dd>{site.livePerformance.marginMae?.toFixed(2)} points</dd>
              </div>
              <div>
                <dt>Total error</dt>
                <dd>{site.livePerformance.totalMae?.toFixed(2)} points</dd>
              </div>
              <div>
                <dt>Decisive-game log loss</dt>
                <dd>
                  {site.livePerformance.logLoss?.toFixed(4) ??
                    "Awaiting a decisive result"}
                </dd>
              </div>
              <div>
                <dt>80% margin interval coverage</dt>
                <dd>
                  {site.livePerformance.marginIntervalCoverage == null
                    ? "Unavailable"
                    : pct(site.livePerformance.marginIntervalCoverage)}{" "}
                  · {site.livePerformance.marginIntervalGames} games
                </dd>
              </div>
              <div>
                <dt>80% total interval coverage</dt>
                <dd>
                  {site.livePerformance.totalIntervalCoverage == null
                    ? "Unavailable"
                    : pct(site.livePerformance.totalIntervalCoverage)}{" "}
                  · {site.livePerformance.totalIntervalGames} games
                </dd>
              </div>
            </dl>
            <p className="fine">
              Score errors use {site.livePerformance.scoreGames} games.
              Probability scores use {site.livePerformance.games} decisive
              games. A small live sample cannot establish reliability or
              profitable edge.
            </p>
            <details>
              <summary>Inspect every graded forecast</summary>
              <ul className="live-score-audit">
                {site.livePerformance.scoreRecords.map((record) => (
                  <li key={record.gameId}>
                    <Link href={`/games/${record.gameId}`}>
                      {record.gameId.replaceAll("_", " · ")}
                    </Link>
                    <p>
                      Home margin: {record.homeMargin.toFixed(2)} predicted /{" "}
                      {record.actualMargin} actual. Total:{" "}
                      {record.total.toFixed(2)} predicted / {record.actualTotal}{" "}
                      actual.
                    </p>
                    <p className="fine">
                      Forecast generated {record.generatedAt}. SHA-256:{" "}
                      <code>{record.snapshotHash}</code>
                    </p>
                  </li>
                ))}
              </ul>
            </details>
          </>
        )}
        <LiveCalibration bins={site.livePerformance.calibration} />
      </section>
      <h2 style={{ marginTop: 36 }}>Historical development record</h2>
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
            <path d="M60 20V250H365" stroke="#536071" fill="none" />
            {[0, 0.25, 0.5, 0.75, 1].map((v) => (
              <g key={v}>
                <path d={`M60 ${250 - v * 220}H365`} stroke="#2e3743" />
                <text x="48" y={254 - v * 220} textAnchor="end">
                  {pct(v)}
                </text>
                <text x={60 + v * 305} y="271" textAnchor="middle">
                  {pct(v)}
                </text>
              </g>
            ))}
            <path d="M60 250L365 30" stroke="#7f8ea2" strokeDasharray="5 6" />
            {m.calibration.map((b, i) => (
              <path
                key={`interval-${i}`}
                d={`M${60 + b.predicted * 305} ${250 - b.observedLow95 * 220}V${250 - b.observedHigh95 * 220}`}
                stroke="#acc8e8"
                strokeWidth="2"
                strokeOpacity=".5"
              />
            ))}
            {m.calibration.map((b, i) => (
              <circle
                key={i}
                cx={60 + b.predicted * 305}
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
                  <th scope="col">Predicted</th>
                  <th scope="col">Observed</th>
                  <th scope="col">Games</th>
                </tr>
              </thead>
              <tbody>
                {m.calibration.map((b, i) => (
                  <tr key={i}>
                    <th scope="row">{pct(b.predicted)}</th>
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
                <th scope="col">Metric</th>
                <th scope="col">Model</th>
                <th scope="col">Baseline</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">Winner accuracy</th>
                <td>{pct(m.accuracy)}</td>
                <td>{pct(m.homeBaselineAccuracy)} · Home team</td>
              </tr>
              <tr>
                <th scope="row">Brier score</th>
                <td>{m.brier.toFixed(4)}</td>
                <td>0.2500 · Coin flip</td>
              </tr>
              <tr>
                <th scope="row">Matched margin error</th>
                <td>{m.matchedModelMarginMae?.toFixed(2) ?? "Unavailable"}</td>
                <td>
                  {m.marketMarginMae?.toFixed(2) ?? "Unavailable"} · Closing
                  line
                </td>
              </tr>
              <tr>
                <th scope="row">Matched total error</th>
                <td>{m.matchedModelTotalMae?.toFixed(2) ?? "Unavailable"}</td>
                <td>
                  {m.marketTotalMae?.toFixed(2) ?? "Unavailable"} · Closing
                  total
                </td>
              </tr>
              <tr>
                <th scope="row">Log loss</th>
                <td>{m.logLoss.toFixed(4)}</td>
                <td>0.6931 · Coin flip</td>
              </tr>
            </tbody>
          </table>
          <p>
            {marginComparisonSummary(m)} A lower sample error alone does not
            establish a reliable betting advantage.
          </p>
          <p className="fine">
            Historical market coverage: {m.marketGames} spread lines and{" "}
            {m.marketTotalGames} totals. Model and market errors use the same
            games for each comparison. Their intraday availability is not known.
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
        <h2>Regular season and postseason</h2>
        <p>
          Playoff games are a different sample. Both groups remain in the full
          record; a small postseason sample cannot establish stronger
          reliability.
        </p>
        <div
          className="ratings-table-wrap"
          tabIndex={0}
          role="region"
          aria-label="Performance by season phase"
        >
          <table className="comparison">
            <thead>
              <tr>
                <th scope="col">Phase</th>
                <th scope="col">Games</th>
                <th scope="col">Accuracy</th>
                <th scope="col">Brier</th>
                <th scope="col">Margin MAE</th>
                <th scope="col">Total MAE</th>
              </tr>
            </thead>
            <tbody>
              {site.performance.byPhase.map((group) => (
                <tr key={group.phase}>
                  <th scope="row">{group.phase}</th>
                  <td>{group.games}</td>
                  <td>{pct(group.accuracy)}</td>
                  <td>{group.brier.toFixed(4)}</td>
                  <td>{group.marginMae.toFixed(2)}</td>
                  <td>{group.totalMae.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="fine">
          Accuracy and Brier exclude ties. Error metrics include all games.
          Postseason combines wild card, divisional, conference and championship
          games.
        </p>
      </section>
      <section className="panel" style={{ marginTop: 24 }}>
        <h2 id="season-performance-heading">Season by season</h2>
        <div
          className="ratings-table-wrap"
          tabIndex={0}
          role="region"
          aria-labelledby="season-performance-heading"
        >
          <table className="comparison">
            <thead>
              <tr>
                <th scope="col">Season</th>
                <th scope="col">Games</th>
                <th scope="col">Accuracy</th>
                <th scope="col">Brier</th>
                <th scope="col">Margin MAE</th>
              </tr>
            </thead>
            <tbody>
              {site.performance.bySeason.map((s) => (
                <tr key={s.season}>
                  <th scope="row">{s.season}</th>
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
