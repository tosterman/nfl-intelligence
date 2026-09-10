"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, ArrowUpRight } from "lucide-react";
import { BrandMark } from "./brand";
export function Header() {
  const path = usePathname();
  return (
    <header className="header">
      <Link className="brand" href="/" aria-label="NFL Intelligence home">
        <BrandMark />
        <span>
          NFL <strong>Intelligence</strong>
          <small>Independent football analysis</small>
        </span>
      </Link>
      <nav aria-label="Main navigation">
        {[
          ["/", "The slate"],
          ["/ratings", "Power ratings"],
          ["/performance", "Track record"],
          ["/methodology", "The model"],
        ].map(([href, label]) => (
          <Link
            key={href}
            href={href}
            aria-current={path === href ? "page" : undefined}
          >
            {label}
          </Link>
        ))}
      </nav>
      <Link className="header-status" href="/methodology">
        <Activity size={14} /> Research edition <ArrowUpRight size={13} />
      </Link>
    </header>
  );
}
export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-top">
        <Link href="/" className="brand">
          <BrandMark />
          <span>
            NFL <strong>Intelligence</strong>
          </span>
        </Link>
        <p>
          Know the game.
          <br />
          Respect the uncertainty.
        </p>
      </div>
      <div className="footer-bottom">
        <p>
          Independent analysis. Not affiliated with the NFL or its teams.
          <br />
          For information and entertainment. No prediction guarantees an
          outcome.
        </p>
        <nav aria-label="Footer navigation">
          <Link href="/about">About</Link>
          <Link href="/privacy">Privacy</Link>
          <Link href="/responsible-use">Responsible use</Link>
          <Link href="/contact">Contact</Link>
        </nav>
      </div>
    </footer>
  );
}
