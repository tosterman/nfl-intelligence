import { site } from "@/lib/data";
import { assessFreshness, freshnessInputs } from "@/lib/freshness";
export const dynamic = "force-dynamic";
export function GET() {
  const health = assessFreshness(freshnessInputs(site));
  return Response.json(
    {
      ...health,
      generatedAt: site.generatedAt,
      ageHours: health.checks[0].ageHours,
      modelVersion: site.modelVersion,
      sourceHash: site.source.sha256,
    },
    {
      status: health.status === "ok" ? 200 : 503,
      headers: { "Cache-Control": "no-store" },
    },
  );
}
