import { getOdds } from "@/lib/odds-server";
import { site } from "@/lib/data";
import { Slate } from "@/components/slate";
import { LiveRecordSummary } from "@/components/live-record-summary";
import { weeklyBriefing } from "@/lib/weekly-changes";
import { assessFreshness, freshnessInputs } from "@/lib/freshness";
import { getWeather } from '@/lib/weather-server';
import { slateWeather } from "@/lib/slate-weather";
import { getPersonnelPublication } from '@/lib/personnel-server';
import { personnelEvidenceForGame } from '@/lib/personnel-presentation';
import { personnelBrief, type ContextBrief } from '@/lib/context-briefing';
export default async function Home({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const now = Date.now();
  const [{snapshot:weather,briefs:weatherBriefs}, personnel] = await Promise.all([getWeather(undefined, now),getPersonnelPublication()]);
  const contextBriefs:ContextBrief[] = [...weatherBriefs];
  if(personnel) for(const game of site.games){
    const brief=personnelBrief(personnelEvidenceForGame(personnel.presentation,game),game,now);
    if(brief)contextBriefs.push(brief);
  }
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
      liveRecord={<LiveRecordSummary record={site.livePerformance} />}
      weather={Object.fromEntries(site.games.map(game => [game.id, slateWeather(weather.games[game.id], game, now)]))}
      odds={await getOdds()}
      initialNow={now}
      briefings={briefings}
      contextBriefs={contextBriefs}
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
