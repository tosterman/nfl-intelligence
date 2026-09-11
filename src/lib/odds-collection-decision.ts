import type { OddsFeed } from "./odds";
import {
  ACQUISITION_COOLDOWN_MS,
  ACQUISITION_MAX_ATTEMPTS,
  ACQUISITION_WINDOW_MS,
} from "./odds-store";

type History = { complete: boolean; observedAt: number; attempts: number[] };
type Game = { home: string; away: string; kickoff: string | null };
type Decision = {
  action: "collect" | "wait" | "blocked";
  reason: string;
  retryAt?: number;
};

/** Read-only proposal. A caller must establish history completeness, then
 * recheck/reserve atomically before acting. This does not certify quote quality.
 * No route or scheduled job invokes this experimental decision layer yet. */
export function decideCollection({
  now,
  history,
  feed,
  games,
}: {
  now: number;
  history: History | null;
  feed: OddsFeed | null;
  games: Game[];
}): Decision {
  if (!Number.isSafeInteger(now) || now < 0)
    return { action: "blocked", reason: "invalid-clock" };
  if (!history?.complete)
    return { action: "blocked", reason: "history-unavailable" };
  const attempts = history.attempts;
  if (
    !Number.isSafeInteger(history.observedAt) ||
    history.observedAt > now ||
    now - history.observedAt > 60000 ||
    attempts.length > ACQUISITION_MAX_ATTEMPTS ||
    attempts.some(
      (at, i) =>
        !Number.isSafeInteger(at) ||
        at < 0 ||
        at > history.observedAt ||
        (i > 0 && at <= attempts[i - 1]),
    )
  )
    return { action: "blocked", reason: "invalid-history" };
  const fetched = feed?.state === "ready" ? Date.parse(feed.fetchedAt) : null;
  if (fetched !== null && (!Number.isFinite(fetched) || fetched > now))
    return { action: "blocked", reason: "invalid-feed-time" };
  const closingDue = games.some((game) => {
    const kickoff = Date.parse(game.kickoff ?? "");
    if (
      !Number.isFinite(kickoff) ||
      now < kickoff - 10 * 60000 ||
      now >= kickoff
    )
      return false;
    // A capture with this exact event already in the final 15 minutes should
    // be audited for quote quality, not repeatedly reacquired on each poll.
    return !(
      fetched !== null &&
      fetched >= kickoff - 15 * 60000 &&
      feed?.events.some(
        (event) =>
          event.home === game.home &&
          event.away === game.away &&
          Date.parse(event.kickoff) === kickoff,
      )
    );
  });
  const refreshDue = fetched === null || now - fetched >= 5.5 * 3600000;
  if (!closingDue && !refreshDue)
    return { action: "wait", reason: "recent-capture" };
  const last = attempts.at(-1);
  if (last !== undefined && now - last < ACQUISITION_COOLDOWN_MS)
    return {
      action: "wait",
      reason: "cooldown",
      retryAt: last + ACQUISITION_COOLDOWN_MS,
    };
  const active = attempts.filter((at) => at > now - ACQUISITION_WINDOW_MS);
  if (active.length >= ACQUISITION_MAX_ATTEMPTS)
    return {
      action: "blocked",
      reason: "budget-exhausted",
      retryAt: active[0] + ACQUISITION_WINDOW_MS,
    };
  return {
    action: "collect",
    reason: closingDue ? "closing-window" : "regular-refresh",
  };
}
