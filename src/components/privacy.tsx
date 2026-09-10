"use client";
import { useEffect, useState, useRef } from "react";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
function consented() {
  try {
    return localStorage.getItem("nfl-analytics-consent") === "yes";
  } catch {
    return false;
  }
}
export function Privacy() {
  const [choice, setChoice] = useState<string | null>("loading");
  const declineRef = useRef<HTMLButtonElement>(null);
  const openedByUser = useRef(false);
  useEffect(() => {
    if (choice === null && openedByUser.current) declineRef.current?.focus();
  }, [choice]);
  useEffect(() => {
    try {
      setChoice(localStorage.getItem("nfl-analytics-consent"));
    } catch {
      setChoice(null);
    }
    const sync = () => setChoice(consented() ? "yes" : null);
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);
  const save = (v: string) => {
    const wasAllowed = consented();
    try {
      localStorage.setItem("nfl-analytics-consent", v);
    } catch {}
    setChoice(v);
    if (wasAllowed && v === "no") window.location.reload();
  };
  return (
    <>
      {choice === "yes" && (
        <>
          <Analytics beforeSend={(event) => (consented() ? event : null)} />
          <SpeedInsights beforeSend={(event) => (consented() ? event : null)} />
        </>
      )}
      {choice === null && (
        <aside className="consent" aria-label="Analytics privacy choice">
          <div>
            <strong>A little insight helps us improve.</strong>
            <p>
              Allow anonymous usage analytics? Your choice won’t affect the
              football analysis.
            </p>
          </div>
          <button
            ref={declineRef}
            onClick={() => save("no")}
            className="button quiet"
          >
            Decline
          </button>
          <button onClick={() => save("yes")} className="button">
            Allow analytics
          </button>
        </aside>
      )}
      <button
        className="privacy-settings"
        onClick={() => {
          openedByUser.current = true;
          setChoice(null);
        }}
      >
        Privacy settings
      </button>
    </>
  );
}
