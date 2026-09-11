"use client";
import { type ReactNode } from "react";
import { useContextExpiry } from "./use-context-expiry";
export function PersonnelExpiry({
  expiresAt,
  children,
}: {
  expiresAt: number;
  children: ReactNode;
}) {
  const expired = useContextExpiry(expiresAt, 1000);
  return expired ? (
    <p role="status">
      Pregame personnel context has expired. Refresh for the latest available
      snapshot.
    </p>
  ) : (
    children
  );
}
