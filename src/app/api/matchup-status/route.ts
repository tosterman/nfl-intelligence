import snapshot from '../../../../data/weekly-matchup-context.json';
import site from '../../../../data/site.json';
import { matchupHealth } from '@/lib/matchup-health';
export const dynamic = 'force-dynamic';
export function GET() {
  const phases = new Set(site.games.filter(g => g.season === site.season && g.week === site.week)
    .map(g => ['WC', 'DIV', 'CON', 'SB'].includes(g.type) ? 'POST' : g.type));
  const result = matchupHealth(snapshot, {...site, gameType: phases.size === 1 ? [...phases][0] : 'unknown'});
  return Response.json(result, {status: result.status === 'ok' ? 200 : 503,
    headers: {'Cache-Control': 'no-store'}});
}
