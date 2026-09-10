export function marginRange(interval: number[], home: string, away: string) {
  if (interval.length !== 2 || !interval.every(Number.isFinite) || interval[0] > interval[1]) return null;
  const endpoint = (value: number) => value === 0 ? "an even score" : `${value > 0 ? home : away} by ${Math.abs(value).toFixed(1)}`;
  return `${endpoint(interval[0])} to ${endpoint(interval[1])}`;
}
