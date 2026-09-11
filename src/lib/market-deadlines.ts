import { ODDS_MAX_AGE_MS, type OddsFeed } from "./odds";
import { MAX_AGE_HOURS, type FreshnessInput } from "./freshness";

export function marketDeadlines(
  feed: OddsFeed,
  game: { home: string; away: string; kickoff: string | null },
  freshness: FreshnessInput[] = [],
) {
  const kickoff = Date.parse(game.kickoff ?? "");
  const collected = Date.parse(feed.fetchedAt);
  const times = [kickoff, collected, collected + ODDS_MAX_AGE_MS + 1];
  for (const event of feed.events) {
    if (
      event.home !== game.home ||
      event.away !== game.away ||
      Date.parse(event.kickoff) !== kickoff
    )
      continue;
    for (const book of event.books) {
      for (const quote of [book.spread, book.total, book.moneyline]) {
        if (!quote) continue;
        const observed = Date.parse(quote.observedAt);
        // Eligibility includes exactly six hours; the next millisecond expires it.
        times.push(observed, observed + ODDS_MAX_AGE_MS + 1);
      }
    }
  }
  for (const input of freshness) {
    const collected = Date.parse(input.retrievedAt ?? "");
    times.push(collected - 5 * 60000, collected + MAX_AGE_HOURS * 3600000 + 1);
  }
  return [...new Set(times.filter(Number.isFinite))];
}
