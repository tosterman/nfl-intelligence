import { getOdds } from "@/lib/odds-server";
import { oddsHealth } from "@/lib/odds-store";
export const dynamic = "force-dynamic";
export async function GET() {
  const health = oddsHealth(await getOdds());
  return Response.json(
    { ...health, maximumAgeHours: 6 },
    {
      status: health.status === "ok" ? 200 : 503,
      headers: { "Cache-Control": "no-store" },
    },
  );
}
