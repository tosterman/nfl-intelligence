import { snapshotTime, type Snapshot } from "@/lib/types";
import { compareRevisions, sameRevisionContext } from "@/lib/revisions";
import { date, time, signed, pct } from "@/lib/teams";

export function RevisionHistory({ history }: { history: Snapshot[] }) {
  return (
    <section className="panel">
      <h2 id="forecast-changes" tabIndex={-1}>
        What changed
      </h2>
      <p className="fine">
        Compare each run with its predecessor. Source changes identify revised
        data files; they do not establish a player, injury or weather
        explanation.
      </p>
      {[...history].reverse().map((snapshot, reverseIndex) => {
        const index = history.length - 1 - reverseIndex;
        const previous = history[index - 1];
        const diff =
          previous && sameRevisionContext(previous, snapshot)
            ? compareRevisions(previous, snapshot)
            : null;
        const home = snapshot.gameContext?.home ?? "Recorded home side";
        const away = snapshot.gameContext?.away ?? "Recorded away side";
        return (
          <details
            className="revision"
            key={snapshot.hash}
            open={reverseIndex === 0}
          >
            <summary>
              {reverseIndex === 0 ? "Latest" : `Revision ${index + 1}`} ·{" "}
              {date(snapshotTime(snapshot))} · {time(snapshotTime(snapshot))} ET
            </summary>
            <p className="fine">
              {snapshot.gameContext
                ? `${away} at ${home} · ${snapshot.gameContext.venue} · ${date(snapshot.gameContext.kickoff!)} ${time(snapshot.gameContext.kickoff!)} ET · ${snapshot.gameContext.neutral ? "Neutral venue" : "Home venue"}`
                : "Legacy archive: original matchup context was not recorded. Excluded from the verified record."}
            </p>
            <p>
              {home} {pct(snapshot.prediction.homeWinProbability)} · Expected
              margin {signed(snapshot.prediction.homeMargin)}
            </p>
            {diff ? (
              <>
                <dl className="revision-deltas">
                  <div>
                    <dt>{home} win chance</dt>
                    <dd>{signed(diff.probabilityPoints)} percentage points</dd>
                  </div>
                  <div>
                    <dt>{home} expected points</dt>
                    <dd>{signed(diff.homePoints)}</dd>
                  </div>
                  <div>
                    <dt>{away} expected points</dt>
                    <dd>{signed(diff.awayPoints)}</dd>
                  </div>
                  <div>
                    <dt>{home} margin change</dt>
                    <dd>{signed(diff.margin)} points</dd>
                  </div>
                  <div>
                    <dt>Expected total</dt>
                    <dd>{signed(diff.total)}</dd>
                  </div>
                </dl>
                {diff.changes.length > 0 ? (
                  <ul className="revision-reasons">
                    {diff.changes.map((change) => (
                      <li key={change}>{change}.</li>
                    ))}
                  </ul>
                ) : (
                  <p className="fine">
                    {diff.completeProvenance
                      ? "No change in recorded model or input identities."
                      : "Provenance is incomplete for one or both snapshots; we cannot identify all input or model changes."}
                  </p>
                )}
                {!diff.completeProvenance && diff.changes.length > 0 && (
                  <p className="fine">
                    Provenance is incomplete for one or both snapshots. The
                    changes above may not explain the entire difference.
                  </p>
                )}
              </>
            ) : (
              <p className="fine">
                {previous
                  ? "Not compared: original matchup context is missing or changed."
                  : "Initial model snapshot. No earlier prediction is available."}
              </p>
            )}
            <p className="fine">
              {snapshot.modelVersion} · Training through{" "}
              {snapshot.trainingThrough}
            </p>
          </details>
        );
      })}
      <p className="fine">
        Every earlier snapshot is retained. These are generation times; verified
        public availability is recorded separately.
      </p>
    </section>
  );
}
