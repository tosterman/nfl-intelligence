type Rating = { team: string; rating: number; offense: number; defense: number };
export function ratingMetric(value: string | undefined) {
  return value === "offense" || value === "defense" ? value : "rating";
}
export function orderRatings<T extends Rating>(rows: T[], requested?: string): T[] {
  const metric = ratingMetric(requested);
  return [...rows].sort((a, b) => b[metric] - a[metric] || a.team.localeCompare(b.team));
}
