import source from '../../../../data/participation-source.json';
import collection from '../../../../data/participation-collection.json';
import artifact from '../../../../data/season-participation.json';
import personnel from '../../../../data/personnel.json';
import site from '../../../../data/site.json';
import { participationHealth } from '@/lib/participation-health';
export const dynamic = 'force-dynamic';
export async function GET() {
  const result = participationHealth(source, collection, artifact, personnel, site.season);
  return Response.json(result, {status: result.status === 'ok' ? 200 : 503, headers: {'Cache-Control':'no-store'}});
}
