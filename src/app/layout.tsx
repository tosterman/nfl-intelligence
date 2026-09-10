import type { Metadata } from "next";
import { Header, Footer } from "@/components/shell";
import { Privacy } from "@/components/privacy";
import "./globals.css";
export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ||
      "https://nfl-intelligence-one.vercel.app",
  ),
  title: {
    default: "NFL Intelligence — Know the game",
    template: "%s | NFL Intelligence",
  },
  description:
    "Independent NFL predictions, transparent probabilities, opponent-adjusted power ratings, and an honest public model record.",
  robots: { index: true, follow: true },
  openGraph: {
    type: "website",
    siteName: "NFL Intelligence",
    title: "Know the game. Respect the uncertainty.",
    description: "A clearer view of every NFL matchup.",
  },
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        <div className="site-wrap">
          <Header />
          <main id="main" tabIndex={-1}>
            {children}
          </main>
          <Footer />
        </div>
        <Privacy />
      </body>
    </html>
  );
}
