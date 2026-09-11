import { createHash } from "node:crypto";
import { put } from "@vercel/blob";
import { readBlob } from "./odds-store";

type Stage = "reserved" | "requested" | "captured" | "failed";
type Reason = "provider-error" | "storage-error" | "readback-error" | "unknown-error";
type Event = { attemptStartedAt: number; eventAt: number; stage: Stage; archiveSha256?: string; reason?: Reason };
type IO = { read: (path: string) => Promise<Buffer | null>; write: (path: string, body: Buffer) => Promise<void> };
const defaultIO: IO = {
  read: readBlob,
  write: async (path, body) => {
    await put(path, body, { access: "private", allowOverwrite: false, addRandomSuffix: false,
      contentType: "application/json", abortSignal: AbortSignal.timeout(5000) });
  },
};
const pathFor = (at: number, slot: string) => `odds/attempt-journal/${at}/${slot}.json`;

function encode(event: Event) {
  if (!Number.isSafeInteger(event.attemptStartedAt) || event.attemptStartedAt < 0 ||
      !Number.isSafeInteger(event.eventAt) || event.eventAt < event.attemptStartedAt ||
      (event.stage === "reserved" && event.eventAt !== event.attemptStartedAt))
    throw new Error("Invalid attempt event time");
  if (!["reserved", "requested", "captured", "failed"].includes(event.stage))
    throw new Error("Invalid attempt event stage");
  if (event.stage === "captured" && !/^[a-f0-9]{64}$/.test(event.archiveSha256 ?? ""))
    throw new Error("Invalid captured archive digest");
  if (event.stage === "failed" && !["provider-error", "storage-error", "readback-error", "unknown-error"].includes(event.reason ?? ""))
    throw new Error("Invalid attempt failure reason");
  // Construct an allowlisted record; never serialize a provider Error or URL.
  return Buffer.from(JSON.stringify({ schemaVersion: 1, attemptStartedAt: event.attemptStartedAt,
    eventAt: event.eventAt, stage: event.stage,
    ...(event.stage === "captured" ? { archiveSha256: event.archiveSha256 } : {}),
    ...(event.stage === "failed" ? { reason: event.reason } : {}),
  }));
}

/** Immutable event evidence, not proof that historical coverage is complete.
 * Reservation and provider access remain separate operations. An interrupted
 * producer may leave a reserved/requested event with no known final outcome.
 */
export async function recordAttemptEvent(event: Event, io: IO = defaultIO) {
  const body = encode(event);
  const terminal = event.stage === "captured" || event.stage === "failed";
  const path = pathFor(event.attemptStartedAt, terminal ? "outcome" : event.stage);
  const receipt = { path, sha256: createHash("sha256").update(body).digest("hex") };
  const existing = await io.read(path);
  if (existing) {
    if (!existing.equals(body)) throw new Error("Attempt journal conflict");
  }
  let previousAt = event.attemptStartedAt;
  for (const predecessor of terminal ? ["reserved", "requested"] : event.stage === "requested" ? ["reserved"] : []) {
    const raw = await io.read(pathFor(event.attemptStartedAt, predecessor));
    if (!raw) throw new Error("Attempt journal predecessor missing");
    let prior;
    try { prior = JSON.parse(raw.toString()); } catch { throw new Error("Invalid attempt journal predecessor"); }
    if (!prior || typeof prior !== "object" || Array.isArray(prior) ||
        prior.schemaVersion !== 1 || prior.stage !== predecessor ||
        prior.attemptStartedAt !== event.attemptStartedAt || !encode(prior).equals(raw) ||
        prior.eventAt < previousAt || prior.eventAt > event.eventAt)
      throw new Error("Invalid attempt journal predecessor");
    previousAt = prior.eventAt;
  }
  if (existing) return receipt;
  try { await io.write(path, body); } catch {
    // A write response may be lost after successful persistence. Readback is
    // authoritative; a conflicting concurrent outcome is never overwritten.
  }
  const saved = await io.read(path);
  if (!saved?.equals(body)) throw new Error("Attempt journal readback failed or conflicted");
  return receipt;
}
