"use client";
import { useEffect, useState, useRef } from "react";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
function storedChoice(): "yes" | "no" | null {
  try {
    const value = localStorage.getItem("nfl-analytics-consent");
    return value === "yes" || value === "no" ? value : null;
  } catch {
    return null;
  }
}
function consented() {
  return storedChoice() === "yes";
}
export function Privacy() {
  const [choice, setChoice] = useState<string | null>("loading");
  const declineRef = useRef<HTMLButtonElement>(null);
  const settingsRef = useRef<HTMLButtonElement>(null);
  const openedByUser = useRef(false);
  useEffect(() => {
    if (choice === null && openedByUser.current) declineRef.current?.focus();
  }, [choice]);
  useEffect(() => {
    setChoice(storedChoice());
    const sync = (event: StorageEvent) => {
      if (event.key === null || event.key === "nfl-analytics-consent")
        setChoice(storedChoice());
    };
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);
  const save = (v: string) => {
    const wasAllowed = consented();
    try {
      localStorage.setItem("nfl-analytics-consent", v);
    } catch {}
    setChoice(v);
    if (openedByUser.current) {
      settingsRef.current?.focus();
      openedByUser.current = false;
    }
    if (wasAllowed && v === "no") window.location.reload();
  };
  return (
    <>
      {choice === "yes" && (
        <>
          <Analytics
            beforeSend={(event) =>
              consented() ? { ...event, url: event.url.split(/[?#]/)[0] } : null
            }
          />
          <SpeedInsights
            beforeSend={(event) =>
              consented() ? { ...event, url: event.url.split(/[?#]/)[0] } : null
            }
          />
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
        ref={settingsRef}
        className="privacy-settings"
        onClick={() => {
          openedByUser.current = true;
          if (choice === null) declineRef.current?.focus();
          setChoice(null);
        }}
      >
        Privacy settings
      </button>
    </>
  );
}
