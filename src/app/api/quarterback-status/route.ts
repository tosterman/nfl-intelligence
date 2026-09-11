import {getPersonnelPublication} from '@/lib/personnel-server';
import site from "../../../../data/site.json";
import { quarterbackHealth } from "@/lib/quarterback-health";
export const dynamic = "force-dynamic";
export async function GET() {
  const stored=await getPersonnelPublication();
  const evidence=stored?.presentation.evidence;
  const result = evidence?quarterbackHealth(
    evidence.quarterback,
    {...evidence.quarterbackCollection,checkedAt:evidence.quarterbackCollection.checkedAt??''},
    site.season,
    site.games.flatMap((g) => [g.home, g.away]),
  ):{status:'unavailable'};
  return Response.json({...result,publicationHash:stored?.publication.sha256??null}, {
    status: result.status === "ok" ? 200 : 503,
    headers: { "Cache-Control": "no-store" },
  });
}
