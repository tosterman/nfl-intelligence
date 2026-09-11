"use client";
import { assessFreshness, type FreshnessInput } from "@/lib/freshness";
import { track } from "@vercel/analytics";
import { useEffect, useState } from "react";
import { assessGameOdds, type OddsFeed, type BookQuote } from "@/lib/odds";
import { fairMoneyline, noVig } from "@/lib/math";
import { teams, signed, pct, time, date } from "@/lib/teams";
import type { Prediction } from "@/lib/types";
import { BookSnapshot } from "@/components/book-snapshot";
import { marketDeadlines } from "@/lib/market-deadlines";
type Match = {
  home: string;
  away: string;
  kickoff: string | null;
  status: string;
};
function useClock(initial: number, deadlines: number[]) {
  const [now, setNow] = useState(initial);
  const deadline = Math.min(...deadlines.filter((at) => at > now));
  useEffect(() => {
    const update = () => setNow(Date.now());
    update();
    const timer = setInterval(update, 15000);
    document.addEventListener("visibilitychange", update);
    return () => {
      clearInterval(timer);
      document.removeEventListener("visibilitychange", update);
    };
  }, []);
  useEffect(() => {
    if (!Number.isFinite(deadline)) return;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const checkDeadline = () => {
      const current = Date.now();
      const remaining = deadline - current;
      if (remaining <= 0) {
        setNow(current);
        return;
      }
      // Long-lived tabs may initially be farther out than the browser timer limit.
      timer = setTimeout(checkDeadline, Math.min(remaining, 2_147_483_647));
    };
    checkDeadline();
    return () => clearTimeout(timer);
  }, [deadline]);
  return now;
}
const stamp = (value: string) => `${date(value)}, ${time(value)} ET`;
const defaultBook = (books: BookQuote[]) =>
  books.find((b) => b.book === "fanduel" && b.spread) ??
  books.find((b) => b.spread) ??
  books[0];
export function MarketCard({
  game,
  feed,
  initialNow,
}: {
  game: Match;
  feed: OddsFeed;
  initialNow: number;
}) {
  const now = useClock(initialNow, marketDeadlines(feed, game)),
    assessment = assessGameOdds(feed, game, now),
    books = assessment.books;
  const book = defaultBook(books);
  return (
    <div>
      <small>Market snapshot</small>
      <span>
        {book?.spread
          ? `${teams[game.home].short} ${signed(book.spread.homePoint)} (${signed(book.spread.homePrice, 0)})`
          : book
            ? "Spread not quoted"
            : assessment.label}
      </span>
      {book && <small>{book.name}</small>}
      {book?.spread && <small>As of {stamp(book.spread.observedAt)}</small>}
    </div>
  );
}
export function MarketPanel({
  freshness,
  game,
  prediction,
  feed,
  initialNow,
}: {
  game: Match;
  freshness: FreshnessInput[];
  prediction: Prediction;
  feed: OddsFeed;
  initialNow: number;
}) {
  const now = useClock(initialNow, marketDeadlines(feed, game, freshness)),
    assessment = assessGameOdds(feed, game, now),
    books = assessment.books;
  const [selected, setSelected] = useState<string | null>(null);
  const book = books.find((b) => b.book === selected) ?? defaultBook(books);
  const modelFresh = assessFreshness(freshness, now).status === "ok";
  const home = teams[game.home].short,
    away = teams[game.away].short;
  return (
    <section className="panel market-panel">
      <h2 id="market-prices" tabIndex={-1}>
        Model versus market
      </h2>
      <div
        className="sr-only"
        role="status"
        aria-label="Current market availability"
        aria-live="polite"
        aria-atomic="true"
      >
        {book
          ? `${book.name}: spread ${book.spread ? "available" : "unavailable"}, total ${book.total ? "available" : "unavailable"}, moneyline ${book.moneyline ? "available" : "unavailable"}.${modelFresh ? "" : " Model comparisons withheld because the model inputs are stale."}`
          : assessment.reason}
      </div>
      <p className="fine">
        Timestamped pregame snapshots via The Odds API. Collection is scheduled
        five times daily, but runs can be delayed or missed. Quotes older than
        six hours are withheld; prices can change between collections.
      </p>
      {!book ? (
        <p>{assessment.reason}</p>
      ) : (
        <>
          <label className="market-selector">
            Compare sportsbook{" "}
            <select
              value={book.book}
              onChange={(e) => {
                setSelected(e.target.value);
                try {
                  if (localStorage.getItem("nfl-analytics-consent") === "yes")
                    track("market_book_selected");
                } catch {}
              }}
            >
              {books.map((b) => (
                <option key={b.book} value={b.book}>
                  {b.name}
                </option>
              ))}
            </select>
          </label>
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label="Model and sportsbook comparison"
          >
            <table className="comparison">
              <thead>
                <tr>
                  <th scope="col">Market</th>
                  <th scope="col">Our model</th>
                  <th scope="col">{book.name}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{home} spread</td>
                  <td>{signed(-prediction.homeMargin)}</td>
                  <td>
                    {book.spread ? (
                      <>
                        {signed(book.spread.homePoint)}{" "}
                        <small>({signed(book.spread.homePrice, 0)})</small>
                        <small className="quote-time">
                          {stamp(book.spread.observedAt)}
                        </small>
                      </>
                    ) : (
                      "Not quoted"
                    )}
                  </td>
                </tr>
                <tr>
                  <td>Total</td>
                  <td>{prediction.total.toFixed(1)}</td>
                  <td>
                    {book.total ? (
                      <>
                        {book.total.point.toFixed(1)}
                        <small className="quote-time">
                          Over {signed(book.total.overPrice, 0)} / Under{" "}
                          {signed(book.total.underPrice, 0)}
                        </small>
                        <small className="quote-time">
                          {stamp(book.total.observedAt)}
                        </small>
                      </>
                    ) : (
                      "Not quoted"
                    )}
                  </td>
                </tr>
                <tr>
                  <td>{home} moneyline</td>
                  <td>
                    {signed(fairMoneyline(prediction.homeWinProbability), 0)}
                    <small className="quote-time">
                      Fair estimate · conditional on no tie
                    </small>
                  </td>
                  <td>
                    {book.moneyline ? (
                      <>
                        {signed(book.moneyline.homePrice, 0)}
                        <small className="quote-time">
                          {away} {signed(book.moneyline.awayPrice, 0)}
                        </small>
                        <small className="quote-time">
                          {stamp(book.moneyline.observedAt)}
                        </small>
                      </>
                    ) : (
                      "Not quoted"
                    )}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          {!modelFresh && (
            <p>
              The model inputs are stale. Model-versus-market differences are
              withheld until the forecast refreshes.
            </p>
          )}
          {modelFresh && (
            <div className="market-differences">
              <h3>Where the estimates differ</h3>
              {book.spread && (
                <p>
                  The model has {home}{" "}
                  {Math.abs(
                    prediction.homeMargin + book.spread.homePoint,
                  ).toFixed(1)}{" "}
                  points{" "}
                  {prediction.homeMargin + book.spread.homePoint >= 0
                    ? "stronger"
                    : "weaker"}{" "}
                  than this spread implies.
                </p>
              )}
              {book.total && (
                <p>
                  The model total is{" "}
                  {Math.abs(prediction.total - book.total.point).toFixed(1)}{" "}
                  points{" "}
                  {prediction.total >= book.total.point ? "higher" : "lower"}.
                </p>
              )}
              {book.moneyline && (
                <p>
                  {home} win probability: model{" "}
                  {pct(prediction.homeWinProbability)}; market{" "}
                  {pct(
                    noVig(book.moneyline.homePrice, book.moneyline.awayPrice)
                      .home,
                  )}{" "}
                  after proportionally removing the two-sided bookmaker margin.
                  The market figure normalizes the two quoted sides; verify the
                  bookmaker’s tie and overtime settlement rules.
                </p>
              )}
            </div>
          )}
          <p className="fine">
            Retrieved {stamp(feed.fetchedAt)}. Showing {books.length}{" "}
            sportsbooks with eligible quotes. Check the sportsbook for its
            current price and settlement rules.
          </p>
          <BookSnapshot books={books} home={home} away={away} />
        </>
      )}
      <p className="fine">
        Differences are not validated betting edges. Player availability is not
        included in this model, and spread/total cover probabilities and push
        risk are not yet validated. No expected return or stake recommendation
        is implied.
      </p>
    </section>
  );
}
