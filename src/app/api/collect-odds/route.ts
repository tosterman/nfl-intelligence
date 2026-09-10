import { revalidateTag } from "next/cache";
import { authorizedCollector, collectOdds } from "@/lib/odds-collector";
export const dynamic = "force-dynamic";
export const maxDuration = 120;
export async function POST(request: Request) {
  const headers = { "Cache-Control": "no-store" };
  if (
    process.env.VERCEL_ENV !== "production" ||
    !authorizedCollector(
      request.headers.get("authorization"),
      process.env.ODDS_COLLECTION_SECRET,
    )
  )
    return Response.json({ status: "unauthorized" }, { status: 401, headers });
  try {
    const result = await collectOdds();
    revalidateTag("published-odds", { expire: 0 });
    return Response.json(result, { headers });
  } catch {
    console.error("Scheduled odds collection failed");
    return Response.json({ status: "unavailable" }, { status: 503, headers });
  }
}
