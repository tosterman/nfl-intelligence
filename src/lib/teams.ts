export const pct = (p: number) => `${(p * 100).toFixed(0)}%`;
export const signed = (v: number, d = 1) =>
  `${v > 0 ? "+" : ""}${v.toFixed(d)}`;
export const time = (value: string | null) =>
  value
    ? new Intl.DateTimeFormat("en-US", {
        weekday: "short",
        hour: "numeric",
        minute: "2-digit",
        timeZone: "America/New_York",
      }).format(new Date(value))
    : "Time TBD";
export const date = (value: string | null) =>
  value
    ? new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        timeZone: "America/New_York",
      }).format(new Date(value))
    : "Time TBD";
export const teams: Record<
  string,
  { name: string; city: string; color: string; short: string }
> = {
  ARI: { name: "Cardinals", city: "Arizona", color: "#da677e", short: "AZ" },
  ATL: { name: "Falcons", city: "Atlanta", color: "#d86673", short: "ATL" },
  BAL: { name: "Ravens", city: "Baltimore", color: "#ab8cf1", short: "BAL" },
  BUF: { name: "Bills", city: "Buffalo", color: "#6599f5", short: "BUF" },
  CAR: { name: "Panthers", city: "Carolina", color: "#51b8e8", short: "CAR" },
  CHI: { name: "Bears", city: "Chicago", color: "#e6a16d", short: "CHI" },
  CIN: { name: "Bengals", city: "Cincinnati", color: "#f39557", short: "CIN" },
  CLE: { name: "Browns", city: "Cleveland", color: "#e89457", short: "CLE" },
  DAL: { name: "Cowboys", city: "Dallas", color: "#9eacc6", short: "DAL" },
  DEN: { name: "Broncos", city: "Denver", color: "#efa26a", short: "DEN" },
  DET: { name: "Lions", city: "Detroit", color: "#67b5ed", short: "DET" },
  GB: { name: "Packers", city: "Green Bay", color: "#d6c065", short: "GB" },
  HOU: { name: "Texans", city: "Houston", color: "#d7828a", short: "HOU" },
  IND: { name: "Colts", city: "Indianapolis", color: "#7b9ede", short: "IND" },
  JAX: {
    name: "Jaguars",
    city: "Jacksonville",
    color: "#72c4be",
    short: "JAX",
  },
  KC: { name: "Chiefs", city: "Kansas City", color: "#ec7c89", short: "KC" },
  LA: { name: "Rams", city: "Los Angeles", color: "#91b4f4", short: "LAR" },
  LAC: {
    name: "Chargers",
    city: "Los Angeles",
    color: "#83cfe6",
    short: "LAC",
  },
  LV: { name: "Raiders", city: "Las Vegas", color: "#bec7d3", short: "LV" },
  MIA: { name: "Dolphins", city: "Miami", color: "#73cbbb", short: "MIA" },
  MIN: { name: "Vikings", city: "Minnesota", color: "#b89bec", short: "MIN" },
  NE: { name: "Patriots", city: "New England", color: "#9caecb", short: "NE" },
  NO: { name: "Saints", city: "New Orleans", color: "#d3c39b", short: "NO" },
  NYG: { name: "Giants", city: "New York", color: "#7c9ddd", short: "NYG" },
  NYJ: { name: "Jets", city: "New York", color: "#79b59c", short: "NYJ" },
  PHI: { name: "Eagles", city: "Philadelphia", color: "#6db3a8", short: "PHI" },
  PIT: { name: "Steelers", city: "Pittsburgh", color: "#e7c168", short: "PIT" },
  SEA: { name: "Seahawks", city: "Seattle", color: "#a0c17b", short: "SEA" },
  SF: { name: "49ers", city: "San Francisco", color: "#df9697", short: "SF" },
  TB: { name: "Buccaneers", city: "Tampa Bay", color: "#df8b81", short: "TB" },
  TEN: { name: "Titans", city: "Tennessee", color: "#8db8d8", short: "TEN" },
  WAS: {
    name: "Commanders",
    city: "Washington",
    color: "#d5ab74",
    short: "WAS",
  },
};
