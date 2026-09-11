import { site, teams, signed } from "@/lib/data";
import { TeamMark } from "@/components/brand";
import Link from "next/link";
import { orderRatings, ratingMetric } from "@/lib/ratings-order";
import { editorialMetadata } from "@/lib/editorial-metadata";
export const metadata = editorialMetadata(
  "NFL power ratings",
  "Compare all 32 NFL teams using opponent-adjusted scoring ratings, with separate offense, defense and combined views.",
  "/ratings",
);
export default async function Ratings({ searchParams }: { searchParams: Promise<{ sort?: string | string[] }> }) {
  const params = await searchParams;
  const metric = ratingMetric(typeof params.sort === "string" ? params.sort : undefined);
  const label = metric === "rating" ? "Combined" : metric === "offense" ? "Offense" : "Defense";
  const ratings = orderRatings(site.ratings, metric);
  return (
    <div className="subpage">
      <div className="page-heading">
        <div className="eyebrow">All 32 teams · Opponent-adjusted</div>
        <h1>
          Strength, without
          <br />
          the storyline.
        </h1>
        <p>
          How much does each team’s scoring profile move an average matchup?
          Separate offense, defense, and the combined picture.
        </p>
      </div>
      <div className="notice">
        Ratings are points relative to the model’s league baseline on a neutral
        field. They use prior scoring results, adjusted for opponents and
        recency. Personnel changes and play-level efficiency are not yet
        included.
      </div>
      <nav className="ratings-order" aria-label="Rank teams by">
        {([['rating', 'Combined'], ['offense', 'Offense'], ['defense', 'Defense']] as const).map(([key, name]) => (
          <Link key={key} href={`/ratings?sort=${key}`} aria-current={metric === key ? "page" : undefined}>{name}</Link>
        ))}
      </nav>
      <p className="fine">{label} order · Strongest first. Positions follow the selected metric; exact ties use team code order. Values are rounded for display.</p>
      <div
        className="ratings-table-wrap"
        role="region"
        aria-label="All team power ratings; scroll horizontally for all columns"
        tabIndex={0}
      >
        <table className="ratings-table">
          <thead>
            <tr>
              <th scope="col">Position</th>
              <th scope="col">Team</th>
              <th scope="col" aria-sort={metric === "rating" ? "descending" : undefined}>Combined</th>
              <th scope="col" aria-sort={metric === "offense" ? "descending" : undefined}>Offense</th>
              <th scope="col" aria-sort={metric === "defense" ? "descending" : undefined}>Defense</th>
            </tr>
          </thead>
          <tbody>
            {ratings.map((r, i) => (
              <tr key={r.team}>
                <td className="muted">{String(i + 1).padStart(2, "0")}</td>
                <td>
                  <div className="ratings-team">
                    <TeamMark code={r.team} />
                    <Link href={`/teams/${r.team.toLowerCase()}`}>
                      <small>{teams[r.team].city}</small>
                      {teams[r.team].name}
                    </Link>
                  </div>
                </td>
                <td>
                  <div className="rating-visual">
                    <span>{signed(r.rating)}</span>
                    <i style={{ width: Math.abs(r.rating) * 13 }} />
                  </div>
                </td>
                <td>{signed(r.offense)}</td>
                <td>{signed(r.defense)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="source-stamp">
        Positive is better for both offense and defense. Training through{" "}
        {site.model.trainingThrough}. These are model ratings, not a claim about
        actual roster strength.
      </p>
    </div>
  );
}
