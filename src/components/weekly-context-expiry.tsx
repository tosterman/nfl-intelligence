"use client";
import React, { type ReactNode } from 'react';
import { useContextExpiry } from './use-context-expiry';
export function WeeklyContextExpiry({ expiresAt, children }: { expiresAt: number; children: ReactNode }) {
  const expired = useContextExpiry(expiresAt, 1000);
  return expired ? <p role="status">Current-season evidence has expired. Refresh to check for an updated sample.</p> : children;
}
