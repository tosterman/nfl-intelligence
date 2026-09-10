import { site } from "@/lib/data";
export const dynamic = "force-dynamic";
export function GET() {
  const ageHours = (Date.now() - Date.parse(site.generatedAt)) / 3600000;
  return Response.json(
    {
      status: ageHours > 30 ? "stale" : "ok",
      generatedAt: site.generatedAt,
      ageHours: Math.round(ageHours * 10) / 10,
      modelVersion: site.modelVersion,
      sourceHash: site.source.sha256,
    },
    {
      status: ageHours > 30 ? 503 : 200,
      headers: { "Cache-Control": "no-store" },
    },
  );
}
