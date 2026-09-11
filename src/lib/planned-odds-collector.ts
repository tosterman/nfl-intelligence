import { decideCollection } from "./odds-collection-decision";
import { runOddsCollection } from "./odds-collector";

type DecisionInput = Parameters<typeof decideCollection>[0];
type Decision = ReturnType<typeof decideCollection>;
type Collector = Parameters<typeof runOddsCollection>[0];

class NoLongerDue extends Error {
  constructor(readonly decision: Decision) {
    super("Collection is no longer due");
  }
}

/** Experimental executor; no route or scheduler invokes this adapter.
 * History completeness must be established by the caller. reserve remains the
 * authoritative atomic budget/cooldown check, including concurrent callers.
 */
export async function runPlannedOddsCollection({
  collector,
  readHistory,
  games,
}: {
  collector: Omit<Collector, "reuse">;
  readHistory: () => Promise<DecisionInput["history"]>;
  games: DecisionInput["games"];
}) {
  const check = async () => {
    const [history, feed] = await Promise.all([
      readHistory(),
      collector.read(),
    ]);
    const input = {
      now: collector.now(),
      history: history ? { ...history, attempts: [...history.attempts] } : null,
      feed,
      games,
    };
    return { input, decision: decideCollection(input) };
  };
  const { decision } = await check();
  if (decision.action !== "collect")
    return { status: "deferred" as const, decision };
  let reservedInput: DecisionInput | undefined;
  try {
    return await runOddsCollection({
      ...collector,
      // The policy checks exact-event reuse. General thirty-minute feed reuse
      // must not override a due decision for a different event.
      reuse: () => false,
      reserve: async (at) => {
        const latest = await check();
        if (latest.decision.action !== "collect")
          throw new NoLongerDue(latest.decision);
        const expiry = await collector.reserve(at);
        reservedInput = latest.input;
        // Reassess time after the durable write. Use the pre-reservation
        // history so this request does not block itself on its own attempt.
        // A closed window keeps its consumed reservation; it is never refunded.
        const after = decideCollection({
          ...latest.input,
          now: collector.now(),
        });
        if (after.action !== "collect") throw new NoLongerDue(after);
        return expiry;
      },
      beforeRequest: async () => {
        await collector.beforeRequest?.();
        if (!reservedInput)
          throw new Error("Planned reservation context missing");
        const after = decideCollection({
          ...reservedInput,
          now: collector.now(),
        });
        if (after.action !== "collect") throw new NoLongerDue(after);
      },
    });
  } catch (error) {
    if (error instanceof NoLongerDue)
      return { status: "deferred" as const, decision: error.decision };
    throw error;
  }
}
