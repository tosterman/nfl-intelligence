import { site } from "@/lib/data";
export const dynamic = "force-static";
export function GET() {
  return Response.json({
    generatedAt: site.generatedAt,
    modelVersion: site.modelVersion,
    games: site.games.filter((g) => g.snapshot),
  });
}
