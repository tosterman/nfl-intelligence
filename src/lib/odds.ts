import { teams } from "./teams";
export const ODDS_MAX_AGE_MS = 6 * 60 * 60 * 1000;
type Pair = { observedAt: string; homePrice: number; awayPrice: number };
export type BookQuote = {
  book: string;
  name: string;
  spread: (Pair & { homePoint: number }) | null;
  moneyline: Pair | null;
  total: {
    observedAt: string;
    point: number;
    overPrice: number;
    underPrice: number;
  } | null;
};
export type OddsEvent = {
  id: string;
  home: string;
  away: string;
  kickoff: string;
  books: BookQuote[];
};
export type OddsFeed = {
  fetchedAt: string;
  events: OddsEvent[];
  state: "ready" | "unavailable" | "not-configured";
};
type Obj = Record<string, unknown>;
const obj = (v: unknown): Obj =>
  v !== null && typeof v === "object" && !Array.isArray(v) ? (v as Obj) : {};
const list = (v: unknown): unknown[] => (Array.isArray(v) ? v : []);
const validPrice = (v: unknown): v is number =>
  typeof v === "number" &&
  Number.isFinite(v) &&
  Math.abs(v) >= 100 &&
  Math.abs(v) <= 100000;
const validPoint = (v: unknown): v is number =>
  typeof v === "number" &&
  Number.isFinite(v) &&
  Math.abs(v) <= 150 &&
  Number.isInteger(v * 2);
const teamCode = (name: unknown) =>
  Object.entries(teams).find(([, t]) => `${t.city} ${t.name}` === name)?.[0];
export function normalizeOdds(raw: unknown, fetchedAt: string): OddsFeed {
  if (!Array.isArray(raw) || !Number.isFinite(Date.parse(fetchedAt)))
    throw new Error("Invalid odds response");
  const events: OddsEvent[] = [];
  const identities = new Set<string>();
  for (const value of raw) {
    const e = obj(value),
      home = teamCode(e.home_team),
      away = teamCode(e.away_team);
    if (
      e.sport_key !== "americanfootball_nfl" ||
      !home ||
      !away ||
      home === away ||
      typeof e.id !== "string" ||
      typeof e.commence_time !== "string" ||
      !Number.isFinite(Date.parse(e.commence_time))
    )
      continue;
    const identity = `${home}/${away}/${e.commence_time}`;
    if (identities.has(identity))
      throw new Error("Ambiguous duplicate odds event");
    identities.add(identity);
    const books: BookQuote[] = [];
    const bookKeys = new Set<string>();
    for (const item of list(e.bookmakers)) {
      const b = obj(item);
      if (
        typeof b.key !== "string" ||
        typeof b.title !== "string" ||
        bookKeys.has(b.key) ||
        list(e.bookmakers).filter((value) => obj(value).key === b.key)
          .length !== 1
      )
        continue;
      bookKeys.add(b.key);
      const quote: BookQuote = {
        book: b.key,
        name: b.title.slice(0, 80),
        spread: null,
        moneyline: null,
        total: null,
      };
      const markets = list(b.markets).map(obj);
      for (const m of markets) {
        if (markets.filter((other) => other.key === m.key).length !== 1)
          continue;
        const at =
          typeof m.last_update === "string" ? m.last_update : b.last_update;
        if (
          typeof at !== "string" ||
          !Number.isFinite(Date.parse(at)) ||
          Date.parse(at) > Date.parse(fetchedAt)
        )
          continue;
        const outcomes = list(m.outcomes).map(obj);
        if (
          outcomes.length !== 2 ||
          !outcomes.every((o) => validPrice(o.price))
        )
          continue;
        const h = outcomes.find((o) => o.name === e.home_team),
          a = outcomes.find((o) => o.name === e.away_team);
        if (m.key === "h2h" && h && a)
          quote.moneyline = {
            observedAt: at,
            homePrice: h.price as number,
            awayPrice: a.price as number,
          };
        if (
          m.key === "spreads" &&
          h &&
          a &&
          validPoint(h.point) &&
          validPoint(a.point) &&
          h.point === -a.point
        )
          quote.spread = {
            observedAt: at,
            homePrice: h.price as number,
            awayPrice: a.price as number,
            homePoint: h.point,
          };
        const over = outcomes.find((o) => o.name === "Over"),
          under = outcomes.find((o) => o.name === "Under");
        if (
          m.key === "totals" &&
          over &&
          under &&
          validPoint(over.point) &&
          over.point > 0 &&
          over.point === under.point
        )
          quote.total = {
            observedAt: at,
            point: over.point,
            overPrice: over.price as number,
            underPrice: under.price as number,
          };
      }
      if (quote.spread || quote.moneyline || quote.total) books.push(quote);
    }
    books.sort((a, b) => a.name.localeCompare(b.name));
    events.push({ id: e.id, home, away, kickoff: e.commence_time, books });
  }
  return { state: "ready", fetchedAt, events };
}
export function quotesForGame(
  feed: OddsFeed,
  game: { home: string; away: string; kickoff: string | null; status: string },
  now: number,
): BookQuote[] {
  if (
    feed.state !== "ready" ||
    game.status === "final" ||
    !game.kickoff ||
    !Number.isFinite(now)
  )
    return [];
  const kickoff = Date.parse(game.kickoff),
    age = now - Date.parse(feed.fetchedAt);
  if (
    !Number.isFinite(kickoff) ||
    now >= kickoff ||
    !Number.isFinite(age) ||
    age < 0 ||
    age > ODDS_MAX_AGE_MS
  )
    return [];
  const matches = feed.events.filter(
    (e) =>
      e.home === game.home &&
      e.away === game.away &&
      Date.parse(e.kickoff) === kickoff,
  );
  if (matches.length !== 1) return [];
  const fresh = <T extends { observedAt: string }>(
    market: T | null,
  ): T | null =>
    market &&
    now - Date.parse(market.observedAt) >= 0 &&
    now - Date.parse(market.observedAt) <= ODDS_MAX_AGE_MS
      ? market
      : null;
  return matches[0].books
    .map((b) => ({
      ...b,
      spread: fresh(b.spread),
      total: fresh(b.total),
      moneyline: fresh(b.moneyline),
    }))
    .filter((b) => b.spread || b.total || b.moneyline);
}
