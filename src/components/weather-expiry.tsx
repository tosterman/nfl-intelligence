"use client";
import { type ReactNode } from "react";
import { useContextExpiry } from "./use-context-expiry";

export function WeatherExpiry({
  expiresAt,
  children,
}: {
  expiresAt: number;
  children: ReactNode;
}) {
  // Weather remains valid at the exact inclusive freshness limit.
  const expired = useContextExpiry(expiresAt + 1, 60000);
  return expired ? (
    <p role="status">Weather forecast is outdated; awaiting refresh.</p>
  ) : (
    children
  );
}
