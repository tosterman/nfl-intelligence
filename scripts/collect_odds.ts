import { mkdir, writeFile } from "node:fs/promises";
import { collectionResult } from "../src/lib/collection-evidence";

async function main() {
  const startedAt = new Date().toISOString();
  let stage = "configuration";
  let httpStatus: number | null = null;
  let result: ReturnType<typeof collectionResult> | null = null;
  let success = false;
  try {
    const secret = process.env.ODDS_COLLECTION_SECRET;
    if (!secret) throw new Error("Missing collection configuration");
    stage = "request";
    const response = await fetch(
      "https://nfl-intelligence-one.vercel.app/api/collect-odds",
      {
        method: "POST",
        redirect: "error",
        headers: { Authorization: `Bearer ${secret}` },
        signal: AbortSignal.timeout(120000),
      },
    );
    httpStatus = response.status;
    if (!response.ok) {
      await response.body?.cancel();
      throw new Error("Collection failed");
    }
    stage = "validate-response";
    result = collectionResult(await response.json());
    success = true;
    stage = "complete";
    console.log(JSON.stringify(result));
  } catch {
    // Never persist exception strings, raw response bodies or authenticated URLs.
    console.error(
      "Scheduled odds collection failed; inspect retained collection report.",
    );
    process.exitCode = 1;
  } finally {
    await mkdir("release-recovery", { recursive: true });
    await writeFile(
      "release-recovery/odds-collection-report.json",
      JSON.stringify(
        {
          schemaVersion: 1,
          startedAt,
          completedAt: new Date().toISOString(),
          success,
          stage,
          httpStatus,
          result,
        },
        null,
        2,
      ) + "\n",
    );
  }
}
main().catch(() => {
  console.error("Unable to retain collection evidence.");
  process.exitCode = 1;
});
