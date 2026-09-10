import { freshnessInputs } from "@/lib/freshness";
import { getOdds } from "@/lib/odds-server";
import { MarketPanel } from "@/components/market-panel";
import { MarketHistoryPanel } from "@/components/market-history";
import { getMarketHistory } from "@/lib/odds-history-server";
import { snapshotTime } from "@/lib/types";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowUpRight } from "lucide-react";
import { site, teams, pct, signed, time, date } from "@/lib/data";
import { fairMoneyline } from "@/lib/math";
import { TeamMark } from "@/components/brand";
import { RevisionHistory } from "@/components/revision-history";
import { WeatherContext } from "@/components/weather-context";
import { ScheduleContext } from "@/components/schedule-context";
import { PersonnelPanel } from "@/components/personnel-panel";
import {
  ScheduledContext,
  ForecastPendingNotice,
} from "@/components/scheduled-context";
export function generateStaticParams() {
  return site.games.map((g) => ({ id: g.id }));
}
export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const g = site.games.find((g) => g.id === id);
  return {
    title: g
      ? `${teams[g.away].name} ${g.neutral ? "vs" : "at"} ${teams[g.home].name} — Week ${g.week}`
      : "Game not found",
  };
}
export default async function GamePage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ from?: string }>;
}) {
  const { id } = await params;
  const g = site.games.find((g) => g.id === id);
  if (!g) notFound();
  const { from } = await searchParams;
  const returnTo =
    from?.startsWith("/?week=") && !from.includes("\\")
      ? from
      : `/?week=${g.week}`;
  const p = g.snapshot?.prediction;
  const marketData = p
    ? await Promise.all([getOdds(), getMarketHistory(g)])
    : null;
  const favorite = p ? (p.homeWinProbability >= 0.5 ? g.home : g.away) : null;
  const probability = p
    ? Math.max(p.homeWinProbability, 1 - p.homeWinProbability)
    : 0;
  return (
    <div className="subpage">
      <h1 className="sr-only">
        {teams[g.away].city} {teams[g.away].name} {g.neutral ? "vs" : "at"}{" "}
        {teams[g.home].city} {teams[g.home].name} · Week {g.week}
      </h1>
      <Link className="breadcrumb" href={returnTo}>
        <ArrowLeft size={14} /> Back to the slate <span>/</span> Week {g.week}
      </Link>
      <section className="detail-hero">
        <div className="detail-hero-meta">
          <span>
            {date(g.kickoff)} · {time(g.kickoff)} ET
          </span>
          <span>
            {g.venue}
            {g.neutral ? " · Neutral venue" : ""}
          </span>
        </div>
        <div className="detail-scoreboard">
          {[g.away, g.home].map((code, i) => (
            <div className="detail-team" key={code}>
              <TeamMark code={code} large />
              <small>
                {teams[code].city} ·{" "}
                {g.neutral
                  ? i
                    ? "Designated home"
                    : "Designated away"
                  : i
                    ? "Home"
                    : "Away"}
              </small>
              <h2>{teams[code].name}</h2>
              <strong>
                {g.status === "final"
                  ? i
                    ? g.actualHome
                    : g.actualAway
                  : p
                    ? (i ? p.homeScore : p.awayScore).toFixed(1)
                    : "—"}
              </strong>
              <span>
                {p
                  ? `${pct(i ? p.homeWinProbability : 1 - p.homeWinProbability)} pregame win probability`
                  : g.history.length
                    ? "No forecast verified for this matchup context"
                    : "No pregame forecast"}
              </span>
              {g.status === "final" && p && (
                <span>
                  Pregame estimate: {(i ? p.homeScore : p.awayScore).toFixed(1)}{" "}
                  points
                </span>
              )}
            </div>
          ))}
        </div>
        <div className="detail-prob">
          {p && (
            <div className="prob-track">
              <i
                style={{
                  width: pct(1 - p.homeWinProbability),
                  background: teams[g.away].color,
                }}
              />
              <i style={{ flex: 1, background: teams[g.home].color }} />
            </div>
          )}
          <p>
            {g.status === "final"
              ? "Final score"
              : p
                ? "Expected points · Not an exact-score prediction"
                : "No model forecast available"}
            {p ? " · Probability conditional on a decisive result" : ""}
          </p>
        </div>
      </section>
      {!p ? (
        <>
          <ForecastPendingNotice game={g} />
          <ScheduledContext game={g} />
        </>
      ) : (
        <>
          <nav className="matchup-nav" aria-label="Matchup sections">
            <span className="eyebrow">Explore this game</span>
            <div>
              <a href="#model-read">Model outlook</a>
              {!!p.profiles?.length && (
                <a href="#team-profiles">Team profiles</a>
              )}
              <a href="#forecast-changes">Forecast changes</a>
              <a href="#kickoff-weather">Weather</a>
              <a href="#market-prices">Sportsbook comparison</a>
              <a href="#personnel-reports">Personnel</a>
              <a href="#market-history">Price history</a>
              <a href="#schedule-context">Schedule</a>
            </div>
          </nav>
          <div className="kpi-grid">
            <div className="kpi">
              <small>Model spread · Home team</small>
              <strong>
                {teams[g.home].short} {signed(-p.homeMargin)}
              </strong>
              <span>Independent of sportsbook lines</span>
            </div>
            <div className="kpi">
              <small>Expected total</small>
              <strong>{p.total.toFixed(1)}</strong>
              <span>Combined points</span>
            </div>
            <div className="kpi">
              <small>{teams[favorite!].name} fair moneyline</small>
              <strong>{signed(fairMoneyline(probability), 0)}</strong>
              <span>Conditional on no tie</span>
            </div>
            <div className="kpi">
              <small>Model confidence</small>
              <strong>Limited</strong>
              <span>Personnel & weather not in model</span>
            </div>
          </div>
          <div className="detail-grid">
            <div className="detail-stack">
              <section className="panel">
                <h2 id="model-read" tabIndex={-1}>
                  The model’s read
                </h2>
                <p className="lead">
                  {teams[favorite!].city}{" "}
                  {g.status === "final"
                    ? "had the stronger pregame scoring profile"
                    : "has the stronger pregame scoring profile"}
                  , with a {pct(probability)} chance of winning a decisive game.
                  The pregame expected margin{" "}
                  {g.status === "final" ? "was" : "is"}{" "}
                  {Math.abs(p.homeMargin).toFixed(1)} points.
                </p>
                <p>
                  {p.contributions
                    .filter((c) => Math.abs(c.points) > 0.05)
                    .sort((a, b) => Math.abs(b.points) - Math.abs(a.points))
                    .slice(0, 3)
                    .map(
                      (c) =>
                        `${c.name} contributes ${Math.abs(c.points).toFixed(1)} points toward ${teams[c.points > 0 ? g.home : g.away].name}.`,
                    )
                    .join(" ")}{" "}
                  These are model contributions from prior scoring and
                  efficiency, not player-specific matchup findings.
                </p>
                <div className="notice">
                  <strong>Room for a different result</strong>
                  <p>The middle 80% of modeled margins span {marginRange(p.marginInterval80, teams[g.home].name, teams[g.away].name) ?? "an unavailable range"}.</p>
                  <p>The middle 80% of modeled combined scores span {p.totalInterval80[0].toFixed(1)} to {p.totalInterval80[1].toFixed(1)} total points.</p>
                  <p className="fine">Each range leaves about 20% of its modeled outcomes outside it. These are separate ranges, not an 80% guarantee that both will hold. They describe possible game results, not confidence in the average prediction. Football scores are whole numbers; these continuous-model boundaries are approximate.</p>
                </div>
                <p className="fine">
                  Explanation generated deterministically from the structured
                  model output. No unsupported injury, weather, or lineup
                  narrative.
                </p>
              </section>
              <WeatherContext game={g} />
              <section className="panel">
                <h2>What moves the projection</h2>
                <p className="fine">
                  Points toward {teams[g.away].name} ← → Points toward{" "}
                  {teams[g.home].name}
                </p>
                {p.contributions.map((c) => (
                  <div key={c.name}>
                    <div className="chart-row">
                      <span>{c.name}</span>
                      <div className="bar-axis">
                        <div
                          className="bar-fill"
                          style={{
                            left:
                              c.points >= 0
                                ? "50%"
                                : `${50 - Math.min(48, Math.abs(c.points) * 8)}%`,
                            width: `${Math.min(48, Math.abs(c.points) * 8)}%`,
                            background:
                              teams[c.points > 0 ? g.home : g.away].color,
                          }}
                        />
                      </div>
                      <strong>{signed(c.points)}</strong>
                    </div>
                  </div>
                ))}
                <p className="fine">
                  Contributions sum to the {signed(p.homeMargin)} home margin.
                  The offense and defense terms account for opponent strength
                  and recency.
                </p>
              </section>
              {!!p.profiles?.length && (
                <section className="panel">
                  <h2 id="team-profiles" tabIndex={-1}>
                    The matchup, beneath the score
                  </h2>
                  <p>
                    Recent passing and rushing profiles, weighted over time.
                    Each offense is shown alongside what the opponent has
                    allowed.
                  </p>
                  <table className="comparison">
                    <thead>
                      <tr>
                        <th scope="col">Historical profile</th>
                        {p.profiles.map((t) => (
                          <th scope="col" key={t.team}>
                            {teams[t.team].short}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Passing EPA / dropback</td>
                        {p.profiles.map((t) => (
                          <td key={t.team}>{signed(t.passEpa, 3)}</td>
                        ))}
                      </tr>
                      <tr>
                        <td>Pass EPA allowed</td>
                        {p.profiles.map((t) => (
                          <td key={t.team}>{signed(t.passEpaAllowed, 3)}</td>
                        ))}
                      </tr>
                      <tr>
                        <td>Rushing EPA / carry</td>
                        {p.profiles.map((t) => (
                          <td key={t.team}>{signed(t.rushEpa, 3)}</td>
                        ))}
                      </tr>
                      <tr>
                        <td>Rush EPA allowed</td>
                        {p.profiles.map((t) => (
                          <td key={t.team}>{signed(t.rushEpaAllowed, 3)}</td>
                        ))}
                      </tr>
                      <tr>
                        <td>Sacks / dropback</td>
                        {p.profiles.map((t) => (
                          <td key={t.team}>{(t.sackRate * 100).toFixed(1)}%</td>
                        ))}
                      </tr>
                      <tr>
                        <td>Completion over expected</td>
                        {p.profiles.map((t) => (
                          <td key={t.team}>{signed(t.cpoe)} pp</td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                  <details>
                    <summary>What do these numbers mean?</summary>
                    <p>
                      EPA means expected points added: how much a play changes
                      the scoring outlook. Positive is better for offense;
                      negative is better for defense. CPOE compares completion
                      rate with expected completion difficulty. These are
                      historical team profiles, not today’s player or scheme
                      scouting.
                    </p>
                  </details>
                  <p className="fine">
                    90-day half-life ·{" "}
                    {p.profiles
                      .map(
                        (t) =>
                          `${teams[t.team].short}: ${t.games} prior games through ${t.through}`,
                      )
                      .join(" · ")}
                    . Displayed profiles are unshrunk summaries; regression
                    features also include shrinkage and standardization.
                  </p>
                </section>
              )}
              <MarketPanel
                freshness={freshnessInputs(site)}
                game={{
                  home: g.home,
                  away: g.away,
                  kickoff: g.kickoff,
                  status: g.status,
                }}
                prediction={p}
                feed={marketData![0]}
                initialNow={Date.now()}
              />
            </div>
            <div className="detail-stack">
              <section className="panel">
                <h2>Evidence coverage</h2>
                <div className="availability">
                  <span>Scoring offense & defense</span>
                  <span>Included</span>
                </div>
                <div className="availability">
                  <span>Opponent strength</span>
                  <span>Adjusted</span>
                </div>
                <div className="availability">
                  <span>Passing & rushing efficiency</span>
                  <span>
                    {p.profiles?.length ? "Included" : "Not in this version"}
                  </span>
                </div>
                <div className="availability">
                  <span>Home field</span>
                  <span>{g.neutral ? "Neutral · 0 points" : "Included"}</span>
                </div>
                <div className="availability">
                  <span>Player availability</span>
                  <span>Not in model</span>
                </div>
                <div className="availability">
                  <span>Trench & scheme matchup</span>
                  <span>Not modeled</span>
                </div>
                <div className="availability">
                  <span>Kickoff weather</span>
                  <span>Not in model</span>
                </div>
                <div className="availability">
                  <span>Market prices</span>
                  <span>Timestamped snapshots</span>
                </div>
                <p className="fine">
                  Missing features receive no adjustment. They are not evidence
                  of full health, calm weather, or market agreement.
                </p>
              </section>
              <section className="panel">
                <h2>Under the hood</h2>
                <p className="fine">
                  Version {g.snapshot!.modelVersion}
                  <br />
                  {g.snapshot!.trainingGames.toLocaleString()} prior games ·
                  Training through {g.snapshot!.trainingThrough}
                </p>
                <details>
                  <summary>Prediction interval & assumptions</summary>
                  <p>
                    Margin standard deviation: {p.sigmaMargin.toFixed(2)}{" "}
                    points. Total standard deviation: {p.sigmaTotal.toFixed(2)}{" "}
                    points. Both are estimated from 2023 out-of-sample
                    residuals.
                  </p>
                  <p>
                    The normal approximation smooths over football’s discrete
                    scoring and does not estimate ties. Moneyline probabilities
                    are conditional on a decisive result.
                  </p>
                </details>
                <details>
                  <summary>Snapshot fingerprint</summary>
                  <p className="hash">{g.snapshot!.hash}</p>
                  <p className="fine">
                    SHA-256 of the canonical snapshot. The data repository
                    preserves the history.
                  </p>
                </details>
                <Link className="text-link" href="/methodology">
                  Full methodology <ArrowUpRight size={14} />
                </Link>
              </section>
            </div>
          </div>
          <PersonnelPanel game={g} />
          <MarketHistoryPanel
            history={marketData![1]}
            home={g.home}
            away={g.away}
          />
        </>
      )}
      {g.history.length > 0 && <RevisionHistory history={g.history} />}
      <ScheduleContext game={g} games={site.games} />
    </div>
  );
}
import { marginRange } from "@/lib/outcome-range";
