import {getPersonnelPublication,getParticipationSource} from '@/lib/personnel-server';
import site from '../../../../data/site.json';
import { participationHealth } from '@/lib/participation-health';
export const dynamic = 'force-dynamic';
export async function GET() {
  const stored=await getPersonnelPublication();
  const source=stored?await getParticipationSource(stored.root):null;
  const evidence=stored?.presentation.evidence;
  const result=source&&evidence?.current?participationHealth(source,
    evidence.participationCollection as Parameters<typeof participationHealth>[1],
    evidence.current as Parameters<typeof participationHealth>[2],evidence.snapshot,site.season):{status:'unavailable'};
  return Response.json({...result,publicationHash:stored?.publication.sha256??null}, {status: result.status === 'ok' ? 200 : 503, headers: {'Cache-Control':'no-store'}});
}
