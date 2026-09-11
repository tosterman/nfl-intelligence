import type { PlayerReport } from './personnel';

export function groupPersonnel(players: PlayerReport[]) {
  const labels = ['Reported out', 'Reported doubtful', 'Reported questionable', 'Other game designations', 'No game designation'];
  const groups = labels.map(label => ({label, players: [] as PlayerReport[]}));
  for (const player of players) {
    const index = player.reportStatus === 'Out' ? 0 : player.reportStatus === 'Doubtful' ? 1 : player.reportStatus === 'Questionable' ? 2 : player.reportStatus ? 3 : 4;
    groups[index].players.push(player);
  }
  return groups.filter(group => group.players.length);
}
