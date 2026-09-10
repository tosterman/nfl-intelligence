import { site } from "@/lib/data";
import { Slate } from "@/components/slate";
import { assessFreshness, freshnessInputs } from "@/lib/freshness";
export default async function Home({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
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
      initial={initial}
      freshness={freshnessInputs(site)}
      initialStale={assessFreshness(freshnessInputs(site)).status !== "ok"}
      games={site.games}
      site={{
        week: site.week,
        season: site.season,
        generatedAt: site.generatedAt,
        modelVersion: site.modelVersion,
      }}
    />
  );
}
