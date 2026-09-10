import snapshot from "../../../../data/quarterbacks.json";
import collection from "../../../../data/quarterback-collection.json";
import site from "../../../../data/site.json";
import { quarterbackHealth } from "@/lib/quarterback-health";
export const dynamic = "force-dynamic";
export async function GET() {
  const result = quarterbackHealth(
    snapshot,
    collection,
    site.season,
    site.games.flatMap((g) => [g.home, g.away]),
  );
  return Response.json(result, {
    status: result.status === "ok" ? 200 : 503,
    headers: { "Cache-Control": "no-store" },
  });
}
