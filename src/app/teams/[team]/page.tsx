import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowUpRight } from "lucide-react";
import { site, teams, signed, pct, time, date } from "@/lib/data";
import { TeamMark } from "@/components/brand";
export function generateStaticParams() {
  return Object.keys(teams).map((team) => ({ team: team.toLowerCase() }));
}
export async function generateMetadata({
  params,
}: {
  params: Promise<{ team: string }>;
}) {
  const { team } = await params;
  const t = teams[team.toUpperCase()];
  return {
    title: t ? `${t.city} ${t.name} — Team intelligence` : "Team not found",
  };
}
export default async function TeamPage({
  params,
}: {
  params: Promise<{ team: string }>;
}) {
  const { team } = await params;
  const code = team.toUpperCase();
  const t = teams[code];
  if (!t) notFound();
  const rating = site.ratings.find((r) => r.team === code)!;
  const games = site.games.filter((g) => g.home === code || g.away === code);
  const next = games.find((g) => g.snapshot && g.status === "scheduled");
  return (
    <div className="subpage">
      <Link className="breadcrumb" href="/ratings">
        <ArrowLeft size={14} /> All power ratings
      </Link>
      <div className="team-page-heading">
        <TeamMark code={code} large />
        <div className="page-heading">
          <div className="eyebrow">
            {t.city} · {site.season}
          </div>
          <h1>{t.name} intelligence.</h1>
          <p>
            Your team’s scoring strength, upcoming matchups, and the full season
            ahead.
          </p>
        </div>
      </div>
      <div className="kpi-grid">
        <div className="kpi">
          <small>Scoring power rank</small>
          <strong>#{site.ratings.findIndex((r) => r.team === code) + 1}</strong>
          <span>Of 32 teams</span>
        </div>
        <div className="kpi">
          <small>Neutral-field scoring rating</small>
          <strong>{signed(rating.rating)}</strong>
          <span>Points relative to league baseline</span>
        </div>
        <div className="kpi">
          <small>Scoring offense</small>
          <strong>{signed(rating.offense)}</strong>
          <span>Opponent-adjusted points</span>
        </div>
        <div className="kpi">
          <small>Scoring defense</small>
          <strong>{signed(rating.defense)}</strong>
          <span>Positive means fewer points allowed</span>
        </div>
      </div>
      {next && (
        <Link className="trust-banner" href={`/games/${next.id}`}>
          <TeamMark code={next.home === code ? next.away : next.home} />
          <div>
            <h3>
              Up next: {next.home === code ? "vs." : "at"}{" "}
              {teams[next.home === code ? next.away : next.home].name}
            </h3>
            <p>
              {date(next.kickoff)} · {time(next.kickoff)} ET · Model win
              probability{" "}
              {pct(
                next.home === code
                  ? next.snapshot!.prediction.homeWinProbability
                  : 1 - next.snapshot!.prediction.homeWinProbability,
              )}
            </p>
          </div>
          <ArrowUpRight size={20} />
        </Link>
      )}
      <section className="panel">
        <h2>The full season</h2>
        <p className="fine">
          Bye weeks have no game row. Forecasts appear during game week.
          Historical scoring ratings do not include current roster changes.
        </p>
        <div
          className="ratings-table-wrap"
          tabIndex={0}
          role="region"
          aria-label={`${t.name} schedule; scroll horizontally`}
        >
          <table className="comparison">
            <thead>
              <tr>
                <th scope="col">Week</th>
                <th scope="col">Opponent</th>
                <th scope="col">Kickoff · ET</th>
                <th scope="col">Status</th>
                <th scope="col">Details</th>
              </tr>
            </thead>
            <tbody>
              {games.map((g) => (
                <tr key={g.id}>
                  <th scope="row">{g.week}</th>
                  <td>
                    {g.home === code ? "vs." : "at"}{" "}
                    {teams[g.home === code ? g.away : g.home].name}
                  </td>
                  <td>
                    {date(g.kickoff)} · {time(g.kickoff)}
                  </td>
                  <td>
                    {g.status === "final"
                      ? `${g.home === code ? g.actualHome : g.actualAway}–${g.home === code ? g.actualAway : g.actualHome} final`
                      : g.snapshot
                        ? "Forecast available"
                        : "Awaiting forecast"}
                  </td>
                  <td>
                    <Link className="small-link" href={`/games/${g.id}`}>
                      View game <ArrowUpRight size={13} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
