export function collectionResult(value: unknown, now = Date.now()) {
  if (!value || typeof value !== "object")
    throw new Error("Invalid collection result");
  const r = value as Record<string, unknown>;
  if (r.status !== "captured" && r.status !== "already-current")
    throw new Error("Invalid collection status");
  if (
    typeof r.fetchedAt !== "string" ||
    !Number.isFinite(Date.parse(r.fetchedAt))
  )
    throw new Error("Missing collection time");
  const age = now - Date.parse(r.fetchedAt);
  if (age < 0 || age > (r.status === "captured" ? 120000 : 30 * 60000))
    throw new Error("Invalid collection age");
  if (r.status === "already-current")
    return { status: r.status, fetchedAt: r.fetchedAt };
  if (
    typeof r.sha256 !== "string" ||
    !/^[a-f0-9]{64}$/.test(r.sha256) ||
    !Number.isSafeInteger(r.events) ||
    (r.events as number) < 0
  )
    throw new Error("Invalid collection evidence");
  if (
    r.creditsRemaining !== null &&
    (typeof r.creditsRemaining !== "string" ||
      !/^\d+$/.test(r.creditsRemaining) ||
      !Number.isSafeInteger(Number(r.creditsRemaining)))
  )
    throw new Error("Invalid quota evidence");
  return {
    status: r.status,
    fetchedAt: r.fetchedAt,
    sha256: r.sha256,
    events: r.events as number,
    creditsRemaining: r.creditsRemaining,
  };
}
