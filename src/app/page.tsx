import { getOdds } from "@/lib/odds-server";
import { site } from "@/lib/data";
import { Slate } from "@/components/slate";
import { weeklyBriefing } from "@/lib/weekly-changes";
import { assessFreshness, freshnessInputs } from "@/lib/freshness";
export default async function Home({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const now = Date.now();
  const briefings = Object.fromEntries([...new Set(site.games.map(game => game.week))].map(week => [week, weeklyBriefing(site.games.filter(game => game.week === week), now)]));
  const requested = Number(params.week);
  const initial = {
    week: site.games.some((g) => g.week === requested) ? requested : site.week,
    query: typeof params.q === "string" ? params.q.slice(0, 60) : "",
    filter:
      typeof params.filter === "string" &&
      ["all", "forecast", "close"].includes(params.filter)
        ? params.filter
        : "all",
    sort: params.sort === "confidence" ? "confidence" : "kickoff",
  };
  return (
    <Slate
      odds={await getOdds()}
      initialNow={now}
      briefings={briefings}
      initial={initial}
      freshness={freshnessInputs(site)}
      initialStale={assessFreshness(freshnessInputs(site)).status !== "ok"}
      games={site.games.map(game => ({ ...game, history: [] }))}
      site={{
        week: site.week,
        season: site.season,
        generatedAt: site.generatedAt,
        modelVersion: site.modelVersion,
      }}
    />
  );
}
