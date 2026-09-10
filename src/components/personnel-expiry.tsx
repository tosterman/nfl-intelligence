"use client";
import { useEffect, useState, type ReactNode } from "react";
export function PersonnelExpiry({
  expiresAt,
  children,
}: {
  expiresAt: number;
  children: ReactNode;
}) {
  const [expired, setExpired] = useState(false);
  useEffect(() => {
    const check = () => setExpired(Date.now() >= expiresAt);
    check();
    const timer = window.setInterval(check, 1000);
    document.addEventListener("visibilitychange", check);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", check);
    };
  }, [expiresAt]);
  return expired ? (
    <p role="status">
      Pregame personnel context has expired. Refresh for the latest available
      snapshot.
    </p>
  ) : (
    children
  );
}
