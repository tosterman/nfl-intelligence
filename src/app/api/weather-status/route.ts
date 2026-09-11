import {getWeather} from '@/lib/weather-server';
import venues from "../../../../data/weather-venues.json";
import osmVenues from "../../../../data/weather-osm-venues.json";
import site from "../../../../data/site.json";
import { weatherHealth } from "@/lib/weather-health";
export const dynamic = "force-dynamic";
export async function GET() {
  const {snapshot,manifestHash}=await getWeather();
  const result = weatherHealth(snapshot, site.games, {
    ...venues,
    ...osmVenues,
  });
  return Response.json({...result,manifestHash}, {
    status: result.status === "ok" ? 200 : 503,
    headers: { "Cache-Control": "no-store" },
  });
}
