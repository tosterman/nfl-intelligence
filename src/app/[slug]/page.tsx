import Link from "next/link";
import { notFound } from "next/navigation";
import { editorialMetadata } from "@/lib/editorial-metadata";
const pages: Record<
  string,
  {
    title: string;
    intro: string;
    description?: string;
    sections: { heading: string; text: string }[];
  }
> = {
  about: {
    title: "A clearer way to follow football.",
    intro:
      "NFL Intelligence is an independent football analytics project built around four questions: who is likely to win, by how much, why, and what might we be missing?",
    sections: [
      {
        heading: "Analysis with a visible standard",
        text: "The statistical model determines the numbers. Explanations describe those numbers and their inputs. Every result belongs in the record, including the misses. No team, league, sportsbook or advertiser determines a forecast.",
      },
      {
        heading: "A research edition, in public",
        text: "The present model combines opponent-adjusted scoring and historical efficiency profiles. Personnel and scheme interactions remain outside its current coverage. The product publishes its limitations alongside its projections. It has not demonstrated a profitable betting edge.",
      },
      {
        heading: "Independent identity",
        text: "NFL Intelligence is not affiliated with or endorsed by the National Football League, any franchise, ESPN, or any sportsbook. Team names identify the subjects of analysis. Team emblems are original text-based illustrations.",
      },
      {
        heading: "Editorial and advertising policy",
        text: "Any future paid placement must be clearly labeled as advertising. Advertising must not change rankings, predictions, explanations, or the reported track record. There are currently no paid placements or sportsbook affiliate links.",
      },
    ],
  },
  privacy: {
    title: "Your football. Your privacy.",
    description: "How NFL Intelligence handles analytics consent, browser storage, hosting data and privacy choices in the current research edition.",
    intro:
      "This page describes the current research edition. Last updated September 10, 2026.",
    sections: [
      {
        heading: "Your choice comes first",
        text: "Optional anonymous usage analytics and performance measurements load only after you choose Allow analytics. Declining leaves the analysis fully available. You can reopen Privacy settings at the bottom of every page to change your choice.",
      },
      {
        heading: "What we store",
        text: "The site stores your analytics preference in browser local storage under nfl-analytics-consent. It has no account registration, payment collection, email list or personalized advertising. Team search and filters appear in the page URL, which can be retained in browser history and ordinary hosting request logs. Optional analytics strip URL queries and fragments before sending events.",
      },
      {
        heading: "Hosting and analytics",
        text: "Vercel hosts the site and processes ordinary request information necessary to deliver and protect the service. When enabled by your choice, Vercel Analytics and Speed Insights measure page views, bounded interaction events and site performance. We do not send search text, names, email addresses or betting behavior as custom analytics properties.",
      },
      {
        heading: "Future advertising",
        text: "Google advertising is not enabled. Before introducing ads, the operator must update this notice, configure applicable consent requirements and review the publisher program rules. This site does not currently claim that a local preference banner is a Google-certified consent management platform.",
      },
      {
        heading: "Corrections and requests",
        text: "Use the contact page to report a privacy concern or an inaccurate statement about data use. Avoid including sensitive personal information in public repository issues.",
      },
    ],
  },
  "responsible-use": {
    title: "Keep the game in perspective.",
    intro:
      "NFL Intelligence provides statistical information and entertainment. It does not accept bets, hold funds, or offer guaranteed outcomes.",
    sections: [
      {
        heading: "A probability is not a promise",
        text: "A 70% favorite still loses about three times in ten if the probability is calibrated. Models can also be wrong about the probability itself. Injuries, weather, lineup changes and randomness can change the outcome.",
      },
      {
        heading: "No stake recommendations",
        text: "The research model has not established a reliable profitable edge. Do not treat a projected score, model disagreement, historical record or fair moneyline as a recommendation to risk money.",
      },
      {
        heading: "If gambling stops being fun",
        text: "Do not chase losses or wager money needed for essentials. If gambling is causing stress or financial harm, seek help from a qualified local support service. In the United States, the National Council on Problem Gambling provides resources and a current helpline through ncpgambling.org.",
      },
      {
        heading: "Adults and local rules",
        text: "If you choose to wager elsewhere, follow the minimum age and laws where you are physically located. This site does not provide access to gambling operators.",
      },
    ],
  },
  contact: {
    title: "Make the analysis better.",
    intro:
      "Found a data issue, a confusing prediction, or something that does not match the evidence? We want it documented.",
    sections: [
      {
        heading: "Report an issue",
        text: "The project repository is the current public correction channel. Include the game ID, the page address, what you expected, and the source that supports the correction. Never post personal information, account credentials or betting account details.",
      },
      {
        heading: "Correction policy",
        text: "Factual display errors can be corrected and documented. Pregame prediction records must remain intact. A revised model produces a new version and an explanation; it does not rewrite a past forecast.",
      },
      {
        heading: "Business inquiries",
        text: "Publisher and sponsorship setup is not open in this research edition. A verified operator contact and commercial terms must be established before any paid placement is accepted.",
      },
    ],
  },
};
function pageForSlug(slug: string) {
  return Object.hasOwn(pages, slug) ? pages[slug] : undefined;
}
export function generateStaticParams() {
  return Object.keys(pages).map((slug) => ({ slug }));
}
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const page = pageForSlug(slug);
  if (!page) return { title: "Not found", robots: { index: false } };
  return editorialMetadata(page.title, page.description ?? page.intro, `/${slug}`);
}
export default async function Article({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const p = pageForSlug(slug);
  if (!p) notFound();
  return (
    <div className="subpage">
      <div className="page-heading">
        <div className="eyebrow">NFL Intelligence</div>
        <h1>{p.title}</h1>
        <p>{p.intro}</p>
      </div>
      <article className="prose">
        {p.sections.map((s) => (
          <section key={s.heading}>
            <h2>{s.heading}</h2>
            <p>{s.text}</p>
          </section>
        ))}
        {slug === "contact" && (
          <p>
            <a href="https://github.com/tosterman/nfl-intelligence/issues">
              Open the project’s issue tracker →
            </a>
          </p>
        )}
        {slug === "responsible-use" && (
          <p>
            <a href="https://www.ncpgambling.org/">
              National Council on Problem Gambling resources →
            </a>
          </p>
        )}
        <p>
          <Link href="/methodology">Read our methodology</Link> ·{" "}
          <Link href="/performance">See the complete model record</Link>
        </p>
      </article>
    </div>
  );
}
