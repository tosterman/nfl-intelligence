import type { MetadataRoute } from "next";
import { site } from "@/lib/data";
export default function sitemap(): MetadataRoute.Sitemap {
  const base =
    process.env.NEXT_PUBLIC_SITE_URL ||
    "https://nfl-intelligence-one.vercel.app";
  return [
    "",
    "/ratings",
    "/performance",
    "/methodology",
    "/about",
    "/privacy",
    "/responsible-use",
    "/contact",
    ...site.games.filter((g) => g.snapshot).map((g) => `/games/${g.id}`),
  ].map((path) => ({
    url: base + path,
    lastModified: new Date(site.generatedAt),
    changeFrequency: path.startsWith("/games") ? "daily" : "weekly",
    priority: path === "" ? 1 : 0.7,
  }));
}
