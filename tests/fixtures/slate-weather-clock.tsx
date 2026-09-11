import React from "react";
import { createRoot } from "react-dom/client";
import { SlateWeatherContext } from "../../src/components/slate-weather";
const now = Date.parse("2026-09-11T12:00:00Z");
createRoot(document.getElementById("root")!).render(<SlateWeatherContext
  initialNow={now} kickoff="2026-09-11T12:00:20Z"
  weather={{ text: "72°F · Wind 10 mph · 20% precipitation", expiresAt: now + 10001 }} />);
