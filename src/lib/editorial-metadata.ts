import type { Metadata } from "next";

export function editorialMetadata(title: string, description: string, path: string): Metadata {
  return {
    title,
    description,
    alternates: { canonical: path },
    openGraph: {
      title,
      description,
      url: path,
      type: "website",
      siteName: "NFL Intelligence",
      images: ["/opengraph-image"],
    },
  };
}
