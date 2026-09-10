import type { CSSProperties } from "react";
import { teams } from "@/lib/teams";
export function BrandMark() {
  return (
    <svg viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <path d="M6 25V7h5l10 18h5V7" stroke="currentColor" strokeWidth="3" />
      <path d="M4 16h24M16 4v24" stroke="currentColor" strokeOpacity=".3" />
    </svg>
  );
}
export function TeamMark({
  code,
  large = false,
}: {
  code: string;
  large?: boolean;
}) {
  const t = teams[code];
  return (
    <span
      className={`team-mark ${large ? "large" : ""}`}
      style={{ "--team": t.color } as CSSProperties}
      aria-hidden="true"
    >
      <svg viewBox="0 0 60 60">
        <path
          d="M9 9h42v28L30 52 9 37Z"
          fill="currentColor"
          fillOpacity=".1"
          stroke="currentColor"
          strokeOpacity=".45"
        />
        <path
          d="M15 16h30M15 20h30"
          stroke="currentColor"
          strokeOpacity=".35"
        />
      </svg>
      <b>{t.short}</b>
    </span>
  );
}
