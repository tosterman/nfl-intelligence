import type { BookQuote } from "@/lib/odds";
import { date, time, signed } from "@/lib/teams";

const stamp = (at: string) => `${date(at)}, ${time(at)} ET`;
const range = (values: number[], spread = false) => {
  if (!values.length) return "No eligible quote";
  const format = (n: number) => (spread ? signed(n) : n.toFixed(1));
  const low = Math.min(...values),
    high = Math.max(...values);
  return `${format(low)}${low === high ? "" : ` to ${format(high)}`} · ${values.length} ${values.length === 1 ? "book" : "books"}`;
};

/** Receives only quotes admitted by assessGameOdds at the current page clock. */
export function BookSnapshot({
  books,
  home,
  away,
}: {
  books: BookQuote[];
  home: string;
  away: string;
}) {
  if (!books.length) return null;
  return (
    <details className="book-snapshot">
      <summary>
        Across sportsbooks · {books.length}{" "}
        {books.length === 1 ? "book" : "books"}
      </summary>
      <p className="fine">
        These snapshot ranges describe the eligible quotes below. Observation
        times differ; this is not a simultaneous consensus or a guaranteed
        available price.
      </p>
      <dl className="revision-deltas">
        <div>
          <dt>{home} spread range</dt>
          <dd>
            {range(
              books.flatMap((b) => (b.spread ? [b.spread.homePoint] : [])),
              true,
            )}
          </dd>
        </div>
        <div>
          <dt>Total range</dt>
          <dd>
            {range(books.flatMap((b) => (b.total ? [b.total.point] : [])))}
          </dd>
        </div>
      </dl>
      <p className="fine">
        Scroll the table horizontally on narrow screens. Prices use American
        odds. Check each sportsbook’s current prices and settlement rules.
      </p>
      <div
        className="table-scroll"
        tabIndex={0}
        role="region"
        aria-label="Sportsbook snapshot quotes"
      >
        <table className="comparison">
          <thead>
            <tr>
              <th scope="col">Sportsbook</th>
              <th scope="col">
                Spread · {home} / {away}
              </th>
              <th scope="col">Total · Over / Under</th>
              <th scope="col">
                Moneyline · {home} / {away}
              </th>
            </tr>
          </thead>
          <tbody>
            {books.map((b) => (
              <tr key={b.book}>
                <th scope="row">{b.name}</th>
                <td>
                  {b.spread ? (
                    <>
                      {home} {signed(b.spread.homePoint)} (
                      {signed(b.spread.homePrice, 0)})
                      <small className="quote-time">
                        {away} {signed(-b.spread.homePoint)} (
                        {signed(b.spread.awayPrice, 0)})
                      </small>
                      <small className="quote-time">
                        {stamp(b.spread.observedAt)}
                      </small>
                    </>
                  ) : (
                    "No eligible quote"
                  )}
                </td>
                <td>
                  {b.total ? (
                    <>
                      {b.total.point.toFixed(1)}
                      <small className="quote-time">
                        Over {signed(b.total.overPrice, 0)} / Under{" "}
                        {signed(b.total.underPrice, 0)}
                      </small>
                      <small className="quote-time">
                        {stamp(b.total.observedAt)}
                      </small>
                    </>
                  ) : (
                    "No eligible quote"
                  )}
                </td>
                <td>
                  {b.moneyline ? (
                    <>
                      {home} {signed(b.moneyline.homePrice, 0)}
                      <small className="quote-time">
                        {away} {signed(b.moneyline.awayPrice, 0)}
                      </small>
                      <small className="quote-time">
                        {stamp(b.moneyline.observedAt)}
                      </small>
                    </>
                  ) : (
                    "No eligible quote"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

