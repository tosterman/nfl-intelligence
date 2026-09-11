"use client";
import { useEffect, useState } from "react";

/** deadline is the first millisecond at which the context is unavailable. */
export function useContextExpiry(deadline: number, pollMs: number) {
  const [expired, setExpired] = useState(false);
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    const check = () => {
      clearTimeout(timer);
      const remaining = deadline - Date.now();
      const closed = !Number.isFinite(remaining) || remaining <= 0;
      setExpired(closed);
      if (!closed) {
        timer = setTimeout(check, Math.min(remaining, 2_147_483_647));
      }
    };
    check();
    // Reconcile suspended tabs and changes to the system clock as well.
    const interval = setInterval(check, pollMs);
    document.addEventListener("visibilitychange", check);
    return () => {
      clearTimeout(timer);
      clearInterval(interval);
      document.removeEventListener("visibilitychange", check);
    };
  }, [deadline, pollMs]);
  return expired;
}
