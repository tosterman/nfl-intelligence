"use client";
import { useState } from "react";
import type { MarketHistory } from "@/lib/odds-history";
import { teams, signed, date, time } from "@/lib/teams";
const stamp = (value: string) => `${date(value)}, ${time(value)} ET`;
export function MarketHistoryPanel({
  history,
  home,
  away,
}: {
  history: MarketHistory;
  home: string;
  away: string;
}) {
  const [selected, setSelected] = useState("fanduel");
  const books = [
    ...new Map(
      history.observations.flatMap((o) => o.books).map((b) => [b.book, b.name]),
    ).entries(),
  ].sort((a, b) => a[1].localeCompare(b[1]));
  const chosen = books.find(([key]) => key === selected) ?? books[0];
  const rows = chosen
    ? history.observations.flatMap((o) => {
        const book = o.books.find((b) => b.book === chosen[0]);
        return book ? [{ fetchedAt: o.fetchedAt, book }] : [];
      })
    : [];
  const spreads = rows.flatMap((r) =>
    r.book.spread ? [r.book.spread.homePoint] : [],
  );
  return (
    <section className="panel market-panel market-history-panel">
      <div className="eyebrow">The price over time</div>
      <h2>Recent market observations</h2>
      <p className="fine">
        Saved pregame quotes. First and latest observations are not verified
        opening or closing lines. Gaps and changes between captures are
        possible.
      </p>
      <p className="fine">
        Recent window: up to 12 captures from today and the previous two days,
        by UTC date.
      </p>
      {history.state !== "ready" && (
        <p className="fine">
          {history.state === "unavailable"
            ? "History is temporarily unavailable."
            : "Some captures could not be verified. This history is incomplete."}
        </p>
      )}
      {!rows.length ? (
        <p>
          No eligible saved observations for this matchup in the recent window.
        </p>
      ) : (
        <>
          <label className="market-selector">
            History sportsbook{" "}
            <select
              value={chosen[0]}
              onChange={(e) => setSelected(e.target.value)}
            >
              {books.map(([key, name]) => (
                <option key={key} value={key}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          {spreads.length > 1 && (
            <p>
              <strong>{teams[home].short} spread:</strong> {signed(spreads[0])}{" "}
              first shown → {signed(spreads.at(-1)!)} latest shown. Net change{" "}
              {signed(spreads.at(-1)! - spreads[0])} points.
            </p>
          )}
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label="Historical sportsbook observations"
          >
            <table className="comparison history-table">
              <caption>
                {chosen[1]} · {rows.length} saved observations · historical
                prices, not current offers
              </caption>
              <thead>
                <tr>
                  <th scope="col">Captured</th>
                  <th scope="col">{teams[home].short} spread</th>
                  <th scope="col">Total</th>
                  <th scope="col">Moneyline</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(({ fetchedAt, book }) => (
                  <tr key={fetchedAt}>
                    <th scope="row">{stamp(fetchedAt)}</th>
                    <td>
                      {book.spread ? (
                        <>
                          {signed(book.spread.homePoint)} (
                          {signed(book.spread.homePrice, 0)})
                          <small className="quote-time">
                            Book updated {stamp(book.spread.observedAt)}
                          </small>
                        </>
                      ) : (
                        "Not quoted"
                      )}
                    </td>
                    <td>
                      {book.total ? (
                        <>
                          {book.total.point.toFixed(1)}
                          <small className="quote-time">
                            Over {signed(book.total.overPrice, 0)} / Under{" "}
                            {signed(book.total.underPrice, 0)}
                          </small>
                          <small className="quote-time">
                            Book updated {stamp(book.total.observedAt)}
                          </small>
                        </>
                      ) : (
                        "Not quoted"
                      )}
                    </td>
                    <td>
                      {book.moneyline ? (
                        <>
                          {teams[home].short}{" "}
                          {signed(book.moneyline.homePrice, 0)} /{" "}
                          {teams[away].short}{" "}
                          {signed(book.moneyline.awayPrice, 0)}
                          <small className="quote-time">
                            Book updated {stamp(book.moneyline.observedAt)}
                          </small>
                        </>
                      ) : (
                        "Not quoted"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
