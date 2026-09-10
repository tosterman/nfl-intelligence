async function main() {
  const secret = process.env.ODDS_COLLECTION_SECRET;
  if (!secret) throw new Error("Missing collection configuration");
  const response = await fetch(
    "https://nfl-intelligence-one.vercel.app/api/collect-odds",
    {
      method: "POST",
      redirect: "error",
      headers: { Authorization: `Bearer ${secret}` },
      signal: AbortSignal.timeout(120000),
    },
  );
  if (!response.ok) throw new Error("Collection failed");
  const result = await response.json();
  if (!["captured", "already-current"].includes(result.status))
    throw new Error("Invalid collection result");
  console.log(
    JSON.stringify({
      status: result.status,
      fetchedAt: result.fetchedAt,
      sha256: result.sha256,
      events: result.events,
      creditsRemaining: result.creditsRemaining,
    }),
  );
}
main().catch(() => {
  console.error(
    "Scheduled odds collection failed; inspect production collection health.",
  );
  process.exitCode = 1;
});
