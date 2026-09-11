import type { Game } from "@/lib/types";
import { WeatherContext } from "./weather-context";
import { PersonnelPanel } from "./personnel-panel";
import Link from "next/link";
import type {WeatherRecord} from '@/lib/weather';
import type {WeatherHistory} from '@/lib/weather-history';
import type {PersonnelEvidence} from '@/lib/personnel-evidence';

export function ForecastPendingNotice({
  game,
  now = Date.now(),
}: {
  game: Game;
  now?: number;
}) {
  const kickoff = Date.parse(game.kickoff ?? "");
  const closed = game.status === "final" || kickoff <= now;
  return (
    <section className="panel" style={{ marginTop: 24 }}>
      <h2>
        {closed
          ? "No rewritten pregame prediction."
          : Number.isFinite(kickoff)
            ? "The forecast is still ahead."
            : "Kickoff timing needs verification."}
      </h2>
      <p>
        {game.status === "final"
          ? "No forecast was recorded before this game. We show the final score and exclude this game from the prospective record."
          : closed
            ? "Kickoff has passed without a recorded pregame forecast. We will show the result when it is verified; this game will not receive a backfilled prediction."
            : Number.isFinite(kickoff)
              ? "This game is on the schedule. A versioned projection will appear during game week, before kickoff."
              : "A verified kickoff time is required before a pregame forecast can be published."}
      </p>
      <Link href="/methodology" className="text-link">
        Read our forecasting policy →
      </Link>
    </section>
  );
}

export function ScheduledContext({
  game,
  weather,
  personnel = null,
  now = Date.now(),
}: {
  game: Game;
  weather?:{record?:WeatherRecord;history:WeatherHistory};
  personnel?:PersonnelEvidence|null;
  now?: number;
}) {
  const kickoff = Date.parse(game.kickoff ?? "");
  if (game.status === "final" || !Number.isFinite(kickoff) || kickoff <= now)
    return null;
  return (
    <>
      <nav className="matchup-nav" aria-label="Available game context">
        <span className="eyebrow">While the forecast is pending</span>
        <div>
          <a href="#kickoff-weather">Weather</a>
          <a href="#personnel-reports">Personnel</a>
          <a href="#schedule-context">Schedule</a>
          <a href="#explosive-heading">Big-play history</a>
          <a href="#red-zone-heading">Inside the 20</a>
        </div>
        <p className="fine">
          These feeds are checked separately from the model. Missing reports do
          not imply healthy players or clear weather. Listed quarterback roles
          describe the recent source snapshot, not a promised starter for this
          future game.
        </p>
      </nav>
      <div className="scheduled-context">
        <WeatherContext game={game} record={weather?.record} history={weather?.history} />
        <PersonnelPanel game={game} evidence={personnel} />
      </div>
    </>
  );
}
