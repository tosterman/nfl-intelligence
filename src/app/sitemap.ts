import type { MetadataRoute } from "next";
import { site } from "@/lib/data";
import { teams } from "@/lib/teams";
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
    ...Object.keys(teams).map((code) => `/teams/${code.toLowerCase()}`),
    ...site.games.filter((g) => g.snapshot).map((g) => `/games/${g.id}`),
  ].map((path) => ({
    url: base + path,
    ...(["", "/ratings", "/performance"].includes(path) ||
    path.startsWith("/games/") ||
    path.startsWith("/teams/")
      ? { lastModified: new Date(site.generatedAt) }
      : {}),
    changeFrequency: path.startsWith("/games") ? "daily" : "weekly",
    priority: path === "" ? 1 : 0.7,
  }));
}
