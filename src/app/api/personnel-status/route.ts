import {getPersonnelPublication} from '@/lib/personnel-server';
import site from "../../../../data/site.json";
import { personnelHealth } from "@/lib/personnel-health";
export const dynamic = "force-dynamic";
export async function GET() {
  const stored=await getPersonnelPublication();
  const evidence=stored?.presentation.evidence;
  const result = evidence?personnelHealth(evidence.snapshot as Parameters<typeof personnelHealth>[0],
    {...evidence.collection,checkedAt:evidence.collection.checkedAt??''},site.season):{status:'unavailable'};
  return Response.json({...result,publicationHash:stored?.publication.sha256??null}, {
    status: result.status === "ok" ? 200 : 503,
    headers: { "Cache-Control": "no-store" },
  });
}
