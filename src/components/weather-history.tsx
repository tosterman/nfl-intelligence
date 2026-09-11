import { weatherHistoryForGame, type WeatherHistory as History } from "@/lib/weather-history";
import type { WeatherRecord } from "@/lib/weather";
import { date, time } from "@/lib/teams";

export function WeatherRevisionBrief({ game,current,history }: { current?:WeatherRecord;history:History;game: { id: string; venue: string; kickoff: string | null } }) {
  const selected = weatherHistoryForGame(history as History, current, game);
  if (!selected?.changed) return null;
  return <p className="fine">The latest retained outdoor weather forecast differs from the previous issue. <a href="#weather-history">See the weather changes</a>. Weather does not change this model’s numbers.</p>;
}

const temperature = (r: WeatherRecord) => r.temperature == null ? "Unavailable" : `${r.temperature}°${r.temperatureUnit}`;
const wind = (r: WeatherRecord) => r.windSpeed ? `${r.windSpeed}${r.windDirection ? ` ${r.windDirection}` : ""}` : "Unavailable";
const precipitation = (r: WeatherRecord) => r.precipitationProbability == null ? "Unavailable" : `${r.precipitationProbability}%`;

export function WeatherHistory({ current, game, history }: { history:History; current: WeatherRecord | undefined;
  game: { id: string; venue: string; kickoff: string | null } }) {
  const selected = weatherHistoryForGame(history as History, current, game);
  const latest = selected?.issues[0], previous = selected?.issues[1];
  return <div className="weather-history">
    <h3 id="weather-history" tabIndex={-1}>How the weather forecast changed</h3>
    {!latest ? <p className="fine">Comparable retained weather history unavailable for this kickoff and location.</p> : <>
      <p className="fine">{!previous ? "This is the first retained forecast issue for this kickoff and location." : selected.changed
        ? "The latest retained issue differs from the previous issue."
        : "The latest two retained issues show the same conditions."} These are historical outdoor forecasts, not observed game conditions or changes to the model.</p>
      {previous && selected.changed && <ul className="fine">
        {temperature(previous) !== temperature(latest) && <li>Temperature: {temperature(previous)} → {temperature(latest)}</li>}
        {wind(previous) !== wind(latest) && <li>Wind: {wind(previous)} → {wind(latest)}</li>}
        {precipitation(previous) !== precipitation(latest) && <li>Precipitation chance: {precipitation(previous)} → {precipitation(latest)}</li>}
        {previous.summary !== latest.summary && <li>Outlook: {previous.summary || "Unavailable"} → {latest.summary || "Unavailable"}</li>}
      </ul>}
      <details>
        <summary>Inspect {selected.issues.length} retained forecast {selected.issues.length === 1 ? "issue" : "issues"}</summary>
        <p className="fine">Newest issue first. Repeat captures are grouped by issue time; capture times below identify the retained observation shown. Different kickoff times and location lookups are not combined.</p>
        {selected.issues.map(row => <div className="weather-history-issue" key={row.hash}>
          <p><strong>Issued {date(row.issuedAt!)} at {time(row.issuedAt!)} ET</strong></p>
          <p>{temperature(row)} · Wind {wind(row)} · Precipitation {precipitation(row)}</p>
          <p className="fine">{row.summary || "Outlook unavailable"}. Captured {date(row.retrievedAt!)} at {time(row.retrievedAt!)} ET.</p>
          <p className="fine">Retained source fingerprint</p><p className="hash">{row.sourceHash}</p>
        </div>)}
      </details>
    </>}
  </div>;
}
