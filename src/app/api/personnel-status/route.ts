import snapshot from "../../../../data/personnel.json";
import collection from "../../../../data/personnel-collection.json";
import site from "../../../../data/site.json";
import { personnelHealth } from "@/lib/personnel-health";
export const dynamic = "force-dynamic";
export async function GET() {
  const result = personnelHealth(snapshot, collection, site.season);
  return Response.json(result, {
    status: result.status === "ok" ? 200 : 503,
    headers: { "Cache-Control": "no-store" },
  });
}
