import raw from "../../data/weather.json";
import { weatherStatus, type WeatherRecord } from "@/lib/weather";
import { date, time } from "@/lib/teams";
import { WeatherExpiry } from "./weather-expiry";
import { VenueConditions } from "./venue-conditions";
import { WeatherHistory } from "./weather-history";

export function WeatherContext({
  game,
}: {
  game: { id: string; venue: string; kickoff: string | null };
}) {
  const record = (raw.games as Record<string, WeatherRecord>)[game.id];
  const status = weatherStatus(record, game);
  return (
    <section className="panel">
      <div className="eyebrow">Conditions · Context only</div>
      <h2 id="kickoff-weather" tabIndex={-1}>
        At kickoff, around the venue
      </h2>
      {status === "available" ? (
        <WeatherExpiry
          expiresAt={
            Math.min(
              Date.parse(record.issuedAt!),
              Date.parse(record.retrievedAt!),
            ) +
            30 * 3600000
          }
        >
          <p className="fine">
            Outdoor forecast for the stadium area. Indoor and on-field conditions
            are unknown.
          </p>
          <p>{record.summary || "Forecast description unavailable"}</p>
          <dl className="revision-deltas weather-values">
            <div>
              <dt>Temperature</dt>
              <dd>
                {record.temperature == null
                  ? "Unavailable"
                  : `${record.temperature}°${record.temperatureUnit}`}
              </dd>
            </div>
            <div>
              <dt>Wind</dt>
              <dd>
                {record.windSpeed
                  ? `${record.windSpeed} ${record.windDirection ?? ""}`
                  : "Unavailable"}
              </dd>
            </div>
            <div>
              <dt>Precipitation chance</dt>
              <dd>
                {record.precipitationProbability == null
                  ? "Unavailable"
                  : `${record.precipitationProbability}%`}
              </dd>
            </div>
          </dl>
          <p className="fine">
            NWS forecast issued {date(record.issuedAt!)} at{" "}
            {time(record.issuedAt!)} ET. Hour containing scheduled kickoff:{" "}
            {time(record.periodStart!)}–{time(record.periodEnd!)} ET.
          </p>
          <details>
            <summary>Weather source & limitations</summary>
            <p className="fine">
              Roof status and actual game conditions are not inferred.
              Captured {date(record.retrievedAt!)} at{" "}
              {time(record.retrievedAt!)} ET.
            </p>
            <a
              className="text-link"
              href={record.sourceUrl}
              target="_blank"
              rel="noreferrer"
            >
              National Weather Service source ↗
            </a>
            {["confirmed-osm-stadium", "confirmed-official-linked-place", "confirmed-official-map-entrance"].includes(record.locationEvidence?.status ?? "") && (
              <p className="fine">
                Stadium map location:{" "}
                <a
                  href={record.locationEvidence?.mapSource}
                  target="_blank"
                  rel="noreferrer"
                >
                  OpenStreetMap contributors
                </a>{" "}
                (
                <a
                  href="https://www.openstreetmap.org/copyright"
                  target="_blank"
                  rel="noreferrer"
                >
                  ODbL
                </a>
                ). The lookup uses the mapped stadium bounds, not a field
                sensor.
              </p>
            )}
            {record.locationEvidence?.status === "confirmed-official-linked-place" && (
              <p className="fine">
                Venue identity was reconciled using the stadium website’s link
                to a named map place at its official address. The place falls
                within the stadium’s mapped bounds; this does not establish
                field-level accuracy.
              </p>
            )}
            {record.locationEvidence?.status === "confirmed-official-map-entrance" && (
              <p className="fine">
                The 2026 stadium bounds were reconciled using Entry 1 on the{" "}
                <a href="https://map.concept3d.com/?id=2167" target="_blank" rel="noreferrer">Bills’ officially linked stadium map</a>.
                The postal house number remains unresolved. The lookup is a stadium-area midpoint, not a field sensor or roof-status report.
              </p>
            )}
            <p className="hash">{record.sourceHash}</p>
            <p className="fine">
              The linked source updates over time; the fingerprint identifies
              the captured response. Government data attribution does not imply
              endorsement.
            </p>
          </details>
        </WeatherExpiry>
      ) : (
        <p>{status}.</p>
      )}
      <VenueConditions venue={game.venue} />
      <WeatherHistory current={record} game={game} />
      <p className="fine">
        Weather has no numerical adjustment in this model. This context cannot
        establish a betting edge.
      </p>
    </section>
  );
}
