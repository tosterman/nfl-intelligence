"use client";
import { MarketCard, useClock } from "./market-panel";
import { SlateWeatherContext } from "./slate-weather";
import type { SlateWeather } from "@/lib/slate-weather";
import { featuredGame, slateGameStatus } from "@/lib/slate-timing";
import { WeeklyChanges } from "./weekly-changes";
import type { WeeklyBriefing } from "@/lib/weekly-changes";
import type { ContextBrief } from '@/lib/context-briefing';
import type { OddsFeed } from "@/lib/odds";
import { useState, useEffect, type ReactNode } from "react";
import Link from "next/link";
import {
  ArrowRight,
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  Search,
  SlidersHorizontal,
  ShieldCheck,
} from "lucide-react";
import { teams, pct, signed, time, date } from "@/lib/teams";
import type { Game } from "@/lib/types";
import { TeamMark } from "./brand";
import { track } from "@vercel/analytics";
import { assessFreshness, type FreshnessInput } from "@/lib/freshness";
function event(name: string) {
  try {
    if (localStorage.getItem("nfl-analytics-consent") === "yes") track(name);
  } catch {}
}
export function Slate({
  games,
  site,
  initial,
  freshness,
  initialStale,
  odds,
  initialNow,
  briefings,
  contextBriefs = [],
  weather = {},
  liveRecord,
}: {
  liveRecord?: ReactNode;
  weather?: Record<string, SlateWeather>;
  games: Game[];
  briefings: Record<number, WeeklyBriefing>;
  contextBriefs?: ContextBrief[];
  odds: OddsFeed;
  initialNow: number;
  freshness: FreshnessInput[];
  initialStale: boolean;
  initial: { week: number; query: string; filter: string; sort: string };
  site: {
    week: number;
    season: number;
    generatedAt: string;
    modelVersion: string;
  };
}) {
  const [week, setWeek] = useState(initial.week),
    [filter, setFilter] = useState(initial.filter),
    [query, setQuery] = useState(initial.query),
    [sort, setSort] = useState(initial.sort);
  const returnTo = `/?${new URLSearchParams({ week: String(week), q: query, filter, sort })}`;
  useEffect(() => {
    window.history.replaceState(null, "", returnTo);
  }, [returnTo]);
  const [stale, setStale] = useState(initialStale);
  useEffect(() => {
    const check = () => setStale(assessFreshness(freshness).status !== "ok");
    check();
    const timer = setInterval(check, 60000);
    return () => clearInterval(timer);
  }, [freshness]);
  const weekGames = games.filter((g) => g.week === week);
  const now = useClock(initialNow, weekGames.map(game => Date.parse(game.kickoff ?? "")));
  const filtered = weekGames
    .filter(
      (g) =>
        (filter !== "upcoming" ||
          (g.status === "scheduled" && Date.parse(g.kickoff ?? "") > now)) &&
        (filter !== "forecast" || !!g.snapshot) &&
        (filter !== "close" ||
          (g.snapshot &&
            Math.abs(g.snapshot.prediction.homeWinProbability - 0.5) < 0.08)) &&
        `${teams[g.home].city} ${teams[g.home].name} ${teams[g.away].city} ${teams[g.away].name} ${g.home} ${g.away} ${teams[g.home].short} ${teams[g.away].short}`
          .toLowerCase()
          .includes(query.toLowerCase()),
    )
    .sort((a, b) =>
      sort === "confidence"
        ? Math.abs((b.snapshot?.prediction.homeWinProbability ?? 0.5) - 0.5) -
          Math.abs((a.snapshot?.prediction.homeWinProbability ?? 0.5) - 0.5)
        : (a.kickoff ?? "z").localeCompare(b.kickoff ?? "z"),
    );
  const featured = featuredGame(weekGames, now);
  const featuredPrediction = featured?.snapshot?.prediction;
  const featuredFavorite = featured && featuredPrediction
    ? teams[featuredPrediction.homeMargin >= 0 ? featured.home : featured.away].name
    : null;
  const forecasts = weekGames.filter((g) => g.snapshot);
  const close = forecasts.filter(
    (g) => Math.abs(g.snapshot!.prediction.homeWinProbability - 0.5) < 0.08,
  ).length;
  return (
    <>
      <section className="page-intro">
        <div className="eyebrow">
          <span className="status-dot" />
          {site.season}{" "}
          {weekGames[0]?.type === "REG" ? "regular season" : "postseason"}
          <span className="slash">/</span>Week {week}
        </div>
        <div className="intro-row">
          <div>
            <h1>
              The whole slate.
              <br />
              <span>A clearer picture.</span>
            </h1>
            <p>
              Independent projections. The evidence behind them.
              <br className="desktop-break" /> A little less noise before
              kickoff.
            </p>
          </div>
          <div className="week-picker">
            <button
              aria-label="Previous week"
              disabled={week === 1}
              onClick={() => setWeek(week - 1)}
            >
              <ChevronLeft size={18} />
            </button>
            <div>
              <small>
                {weekGames[0]?.type === "REG" ? "Regular season" : "Postseason"}
              </small>
              <strong>Week {String(week).padStart(2, "0")}</strong>
              <span>
                {weekGames[0]
                  ? date(weekGames[0].kickoff)
                  : "Schedule unavailable"}
                {weekGames.length > 1
                  ? ` – ${date(weekGames.at(-1)!.kickoff)}`
                  : ""}
              </span>
            </div>
            <button
              aria-label="Next week"
              disabled={week === Math.max(...games.map((g) => g.week))}
              onClick={() => setWeek(week + 1)}
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </section>
      {stale && (
        <div className="notice" role="status">
          This edition or a required input is older than 30 hours, or its
          timestamp cannot be verified. Treat schedules, game status and
          forecasts as potentially outdated.
        </div>
      )}
      {featured && (
        <section className="spotlight">
          <div className="spotlight-copy">
            <div className="eyebrow">
              Next up <span className="slash">/</span> {time(featured.kickoff)}{" "}
              ET
            </div>
            <h2>{Math.abs(featuredPrediction!.homeMargin) < 0.05
              ? "Too close to separate."
              : `${featuredFavorite} by ${Math.abs(featuredPrediction!.homeMargin).toFixed(1)}.`}</h2>
            <p>
              {teams[featured.away].name} {featured.neutral ? "vs" : "at"}{" "}
              {teams[featured.home].name}. The next scheduled matchup with a
              forecast. Explore the projected margin, the strongest counterargument,
              and the range of possible outcomes.
            </p>
            {featured.neutral && (
              <p className="neutral-venue">
                Neutral venue · {featured.venue}. No home-field points in the
                model.
              </p>
            )}
            <Link
              className="text-link"
              href={`/games/${featured.id}?from=${encodeURIComponent(returnTo)}`}
              onClick={() => event("spotlight_open")}
            >
              Explore the matchup <ArrowUpRight size={17} />
            </Link>
            <span className="spotlight-note">
              Research model · Personnel and weather not included
            </span>
          </div>
          <div className="field-art" aria-hidden="true">
            <div className="field-line line1" />
            <div className="field-line line2" />
            <div className="field-line line3" />
            <div className="field-circle" />
            <span className="field-number left">40</span>
            <span className="field-number right">40</span>
          </div>
          <div className="spotlight-matchup">
            <div className="featured-teams">
              <div>
                <TeamMark code={featured.away} large />
                <span>{teams[featured.away].name}</span>
                <strong>
                  {featured.snapshot!.prediction.awayScore.toFixed(1)}
                </strong>
              </div>
              <span className="versus">{featured.neutral ? "vs" : "at"}</span>
              <div>
                <TeamMark code={featured.home} large />
                <span>{teams[featured.home].name}</span>
                <strong>
                  {featured.snapshot!.prediction.homeScore.toFixed(1)}
                </strong>
              </div>
            </div>
            <div className="featured-prob">
              <span>
                {teams[featured.away].short}{" "}
                {pct(1 - featured.snapshot!.prediction.homeWinProbability)}
              </span>
              <span>Win probability</span>
              <span>
                {teams[featured.home].short}{" "}
                {pct(featured.snapshot!.prediction.homeWinProbability)}
              </span>
            </div>
            <div className="prob-track">
              <i
                style={{
                  width: pct(
                    1 - featured.snapshot!.prediction.homeWinProbability,
                  ),
                  background: teams[featured.away].color,
                }}
              />
              <i style={{ flex: 1, background: teams[featured.home].color }} />
            </div>
            <small>Expected points, not an exact-score prediction</small>
          </div>
        </section>
      )}
      {featured && (
        <Link
          className="mobile-focus"
          href={`/games/${featured.id}?from=${encodeURIComponent(returnTo)}`}
        >
          <span>
            <small>In focus · {time(featured.kickoff)} ET</small>
            <strong>
              {teams[featured.away].name} {featured.neutral ? "vs" : "at"}{" "}
              {teams[featured.home].name}
            </strong>
            {featured.neutral && (
              <small>Neutral venue · {featured.venue}</small>
            )}
          </span>
          <ArrowUpRight size={19} />
        </Link>
      )}
      <section className="slate-summary" aria-label="Week overview">
        <div>
          <strong>{weekGames.length}</strong>
          <span>Games this week</span>
        </div>
        <div>
          <strong>
            {forecasts.length}
            <small> / {weekGames.length}</small>
          </strong>
          <span>Pregame snapshots</span>
        </div>
        <div>
          <strong>{close}</strong>
          <span>Closely matched</span>
        </div>
        <Link href="/performance">
          <ShieldCheck size={20} />
          <span>
            Every result counts.<small>See the full model record</small>
          </span>
          <ArrowUpRight size={17} />
        </Link>
      </section>
      {liveRecord}
      <section className="games-section">
        <WeeklyChanges games={weekGames} week={week} asOf={initialNow} returnTo={returnTo} briefing={briefings[week]} contextBriefs={contextBriefs} />
        <div className="section-heading">
          <div>
            <h2>
              Week {week} matchups <span>{filtered.length}</span>
            </h2>
            <p>
              All times Eastern · Forecasts show expected points; final games
              show results
            </p>
          </div>
          <Link className="small-link" href="/methodology">
            How to read the slate <ArrowUpRight size={14} />
          </Link>
        </div>
        <p className="market-context">
          <strong>Model and market, side by side.</strong> Open a matchup for
          timestamped sportsbook snapshots. Prices refresh on a limited
          schedule; model differences are not validated betting edges.
        </p>
        <div className="toolbar">
          <div className="filters" role="group" aria-label="Filter games">
            {[
              ["all", "All games"],
              ["upcoming", "Upcoming"],
              ["forecast", "With forecasts"],
              ["close", "Close matchups"],
            ].map(([v, l]) => (
              <button
                key={v}
                aria-pressed={filter === v}
                onClick={() => {
                  setFilter(v);
                  event("slate_filter");
                }}
              >
                {l}
              </button>
            ))}
          </div>
          <div className="tools">
            <label className="search">
              <Search size={15} />
              <input
                aria-label="Search teams"
                placeholder="Find a team"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </label>
            <label className="sort">
              <SlidersHorizontal size={15} />
              <select
                aria-label="Sort games"
                value={sort}
                onChange={(e) => setSort(e.target.value)}
              >
                <option value="kickoff">Kickoff</option>
                <option value="confidence">Win probability</option>
              </select>
            </label>
          </div>
        </div>
        <p className="result-count" role="status" aria-live="polite">
          Showing {filtered.length} of {weekGames.length} games
        </p>
        <div className="game-grid">
          {filtered.map((g) => (
            <GameCard
              key={g.id}
              game={g}
              weather={weather[g.id]}
              returnTo={returnTo}
              odds={odds}
              initialNow={now} freshness={freshness}
            />
          ))}
        </div>
        {!filtered.length && (
          <div className="empty">
            <h3>No games match this view.</h3>
            <p>
              {filter === "forecast"
                ? "Forecasts are published for the current week before kickoff."
                : "Try a different team or show all games."}
            </p>
            <button
              className="button"
              onClick={() => {
                setFilter("all");
                setQuery("");
              }}
            >
              Show all games
            </button>
          </div>
        )}
      </section>
      <section className="trust-banner">
        <ShieldCheck size={26} />
        <div>
          <h3>Confidence should come with receipts.</h3>
          <p>
            Our model has limits. We publish those alongside the predictions,
            the methodology, and the misses.
          </p>
        </div>
        <Link className="text-link" href="/methodology">
          Inside the model <ArrowRight size={17} />
        </Link>
      </section>
      <p className="source-stamp">
        Model generated {date(site.generatedAt)}, {time(site.generatedAt)} ET ·
        nflverse schedule and results · {site.modelVersion}
      </p>
    </>
  );
}
function GameCard({
  game: g,
  returnTo,
  odds,
  initialNow, freshness,
  weather,
}: {
  weather?: SlateWeather;
  game: Game;
  returnTo: string;
  odds: OddsFeed;
  initialNow: number; freshness: FreshnessInput[];
}) {
  const p = g.snapshot?.prediction;
  const fav = p ? (p.homeWinProbability >= 0.5 ? g.home : g.away) : null;
  return (
    <Link
      className="game-card"
      href={`/games/${g.id}?from=${encodeURIComponent(returnTo)}`}
      onClick={() => event("game_open")}
    >
      <div className="card-top">
        <span>{time(g.kickoff)} ET</span>
        <span className={g.status === "final" ? "final-label" : "muted"}>
          {slateGameStatus(g, initialNow)}
        </span>
      </div>
      {g.neutral && <p className="card-venue">Neutral venue · {g.venue}</p>}
      <div className="card-teams">
        {[g.away, g.home].map((code, i) => (
          <div className="team-row" key={code}>
            <TeamMark code={code} />
            <div>
              <small>{teams[code].city}</small>
              <h3>
                {teams[code].name}
                <span>
                  {g.neutral
                    ? i === 1
                      ? "Designated home"
                      : "Designated away"
                    : i === 1
                      ? "Home"
                      : "Away"}
                </span>
              </h3>
            </div>
            <strong>
              {g.status === "final"
                ? i
                  ? g.actualHome
                  : g.actualAway
                : p
                  ? (i ? p.homeScore : p.awayScore).toFixed(1)
                  : "—"}
            </strong>
          </div>
        ))}
      </div>
      {p ? (
        <>
          <div className="card-prob">
            <span>
              {teams[fav!].name}{" "}
              <strong>
                {pct(Math.max(p.homeWinProbability, 1 - p.homeWinProbability))}
              </strong>
            </span>
            <small>Pregame win probability</small>
          </div>
          <div className="prob-track">
            <i
              style={{
                width: pct(1 - p.homeWinProbability),
                background: teams[g.away].color,
              }}
            />
            <i style={{ flex: 1, background: teams[g.home].color }} />
          </div>
          <div className="card-stats">
            <div>
              <small>Model spread</small>
              <strong>
                {teams[g.home].short} {signed(-p.homeMargin)}
              </strong>
            </div>
            <div>
              <small>Model total</small>
              <strong>{p.total.toFixed(1)}</strong>
            </div>
            <MarketCard game={g} feed={odds} initialNow={initialNow} prediction={p} freshness={freshness} />
          </div>
        </>
      ) : (
        <div className="card-unavailable">
          <p>
            {g.status === "final"
              ? "No forecast was published before this game."
              : "Forecast publishes during game week."}
          </p>
          <small>
            {g.status === "final"
              ? "This result is excluded from the live model record."
              : "The schedule is confirmed; the projection is not yet published."}
          </small>
        </div>
      )}
      {weather && <SlateWeatherContext weather={weather} kickoff={g.kickoff} initialNow={initialNow} />}
      <div className="card-bottom">
        <span>
          {p ? "Scoring + efficiency · Limited inputs" : "Schedule & results"}
        </span>
        <span>
          Game intelligence <ArrowUpRight size={14} />
        </span>
      </div>
    </Link>
  );
}
