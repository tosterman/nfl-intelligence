import Link from "next/link";
import { site } from "@/lib/data";
export const metadata = {
  title: "Inside the model — Methodology & limitations",
};
export default function Methodology() {
  return (
    <div className="subpage">
      <div className="page-heading">
        <div className="eyebrow">The model constitution</div>
        <h1>
          Show the work.
          <br />
          Earn the confidence.
        </h1>
        <p>
          The numbers come from a statistical system. The explanation follows
          the evidence. Neither gets to invent what is missing.
        </p>
      </div>
      <article className="prose">
        <h2>What this model actually knows</h2>
        <p>
          The scoring component estimates scoring offense, scoring defense, and
          home-field advantage from prior NFL results. Each team plays different
          opponents; regularized regression separates those effects instead of
          taking raw points per game at face value.
        </p>
        <p>
          Recent results carry more weight. The selected half-life is{" "}
          {site.model.parameters.halfLifeDays} days: a result that old carries
          half the weight of a fresh result. Ridge regularization shrinks
          uncertain team ratings toward the league average. A maximum four-year
          history supplies {site.model.trainingGames.toLocaleString()} games for
          the current fit.
        </p>
        <p>
          The published model blends 75% of that scoring model with 25% of a
          separate efficiency regression. The second model uses passing EPA per
          dropback, rushing EPA per carry, completion percentage over expected,
          sacks, interceptions, lost fumbles and pass frequency, paired with the
          opposing defense’s historical allowed rates. Its features use a 90-day
          half-life and ridge regularization of 10. These are additive
          historical profiles, not player-specific or causal scheme
          interactions.
        </p>
        <h2>From ratings to a forecast</h2>
        <p>
          Expected home points equal the league scoring baseline, plus the home
          team’s offensive rating, plus the visiting defense’s points-allowed
          effect, plus half the estimated home advantage. Expected away points
          use the reverse matchup and subtract half the home advantage. Neutral
          games receive no home advantage.
        </p>
        <p>
          The difference gives the expected margin; the sum gives the expected
          total. A normal residual approximation translates the margin into a
          win probability. Its variance is estimated from out-of-sample 2023
          games. It is an approximation, not a 10,000-game simulation or a
          football drive simulator.
        </p>
        <p>
          Scores are expectations and can contain decimals. They are not
          predictions that a team will literally score 24.6 points. The 80%
          interval describes possible game outcomes, not uncertainty in the
          average projection. Ties and exact-score key numbers are not
          separately modeled; displayed win probabilities and fair moneylines
          are conditional on a decisive result.
        </p>
        <h2>How we test without reading the future</h2>
        <ol>
          <li>
            Candidate recency and regularization settings are selected using
            2021 and 2022 historical replays.
          </li>
          <li>The 2023 replay supplies margin and total residual scales.</li>
          <li>
            The initial model is evaluated on all 2024 and 2025 games. At every
            replay week, the model fits only games dated before that week’s
            first kickoff date.
          </li>
          <li>
            Same-week outcomes, target-game scores, target injuries, observed
            game weather, and betting lines never enter the football prediction.
          </li>
        </ol>
        <p>
          There is a limitation: these are current downloads of historical
          results, not preserved versions of the data as they existed then.
          Later source corrections may be included. EPA and completion models
          may themselves use revised upstream estimates. The 2024–2025 results
          have been inspected during development and are no longer an untouched
          holdout. This supports a retrospective development test, not an exact
          reconstruction of what an analyst knew on a particular Friday.
        </p>
        <h2>Missing evidence is visible</h2>
        <p>
          Player availability, quarterback changes, snap-weighted personnel
          value, trench matchups, nonlinear scheme interactions, travel, rest
          and kickoff weather are not in the current model. Missing inputs get
          no adjustment; that does not mean their real effect is zero. This is
          why a favorite can have a high win probability while the model’s
          evidence coverage is still limited.
        </p>
        <h2>Market disagreement is a separate question</h2>
        <p>
          Live comparisons require a timestamped, matched two-sided quote. We
          remove the overround from American moneyline prices before comparing
          implied probabilities. Stale, incomplete and future-dated markets
          cannot produce a displayed edge. Without a verified market feed, the
          status is “unavailable,” not “no edge.”
        </p>
        <p>
          The public historical evaluation compares the model against closing
          lines. An exploratory two-point difference selects sides for that
          diagnostic only. It does not establish a viable betting strategy, an
          available entry price, or an expected return. The initial model’s
          margin error is worse than the closing market’s.
        </p>
        <h2>A record that cannot quietly improve itself</h2>
        <p>
          Pregame snapshot files are append-only within the publishing workflow.
          Each records its creation timestamp, model version, training cutoff
          and content fingerprint. Once kickoff passes, the pipeline refuses to
          create the first forecast for that game. Final scores are stored
          separately from forecast objects.
        </p>
        <p>
          A local creation timestamp alone is not proof of public publication.
          Only snapshots with an accompanying successful publication receipt
          should enter prospective performance. Missed games stay missed.
          Historical replays stay in the retrospective section. Repository
          owners can alter Git history, so this is an auditable operating policy
          rather than an absolute cryptographic guarantee.
        </p>
        <h2>Data provenance & attribution</h2>
        <p>
          Schedule and game results:{" "}
          <a href="https://github.com/nflverse/nflverse-data">
            nflverse data releases, with schedules maintained by Lee Sharpe and
            contributors
          </a>
          . Data was retrieved {site.source.retrievedAt}. See{" "}
          <a href="https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html">
            the upstream update schedule
          </a>
          . The downloaded schedule and weekly team-stat releases are
          distributed under{" "}
          <a href="https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md">
            CC BY 4.0
          </a>
          . We transform and model these datasets. This does not grant rights to
          official logos, photographs, or third-party feeds.
        </p>
        <p className="hash">Source SHA-256: {site.source.sha256}</p>
        <p>
          Team emblems on this site are original typographic identifiers, not
          official team logos. Barlow and Barlow Condensed are distributed under
          the SIL Open Font License and served locally.
        </p>
        <h2>What earns a model upgrade</h2>
        <p>
          Better inputs must show repeatable out-of-sample improvement, survive
          leakage checks, and improve calibration or decision usefulness. We
          retain failed experiments. If a model changes after reviewing a test
          set, that set becomes development evidence; a new untouched evaluation
          period is required before a fresh validation claim.
        </p>
        <h2>Experiments we did not rush into production</h2>
        <p>
          Extra rest sounds like an obvious advantage. In our bounded test, six
          rest adjustments failed to improve the selection result, so the model
          kept its existing forecast.{" "}
          <a href="https://github.com/tosterman/nfl-intelligence/blob/main/reviews/rest-experiment.md">
            Read the rest experiment
          </a>
          .
        </p>
        <p>
          A discrete margin model improved some probability scores, but its
          first version predicted too many ties. A constrained version fixed
          that problem while exposing other gaps in intervals and expected-score
          consistency. It remains research, not a hidden change to your
          forecast.{" "}
          <a href="https://github.com/tosterman/nfl-intelligence/blob/main/reviews/distribution-experiment-v2.md">
            Read the distribution experiment
          </a>
          .
        </p>
        <p>
          <Link href="/performance">Inspect the full track record</Link> or{" "}
          <Link href="/contact">report a correction</Link>.
        </p>
      </article>
    </div>
  );
}
