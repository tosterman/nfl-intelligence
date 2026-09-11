# Open-tab personnel and weather expiry

The personnel wrapper checked time once per second; the weather wrapper checked once per minute. A page left open could therefore retain context beyond the validity limit used by the server. A fixed-clock browser regression reproduced personnel remaining visible at its exact expiry before the next polling tick.

Both wrappers now use a shared deadline timer while retaining their existing polling and visibility checks for suspended tabs and clock changes. Personnel expires at its deadline; weather remains valid through the deadline and expires on the following millisecond, preserving the existing source-validity rules. Timers are capped at the browser's supported maximum, rescheduled when needed and cleaned up on unmount or changed props. Invalid deadlines withhold context after the effect runs.

The existing isolated browser fixture now includes the actual personnel and weather wrappers. At a deadline deliberately placed between polling ticks, it checks personnel closure, weather's inclusive boundary, and weather closure one millisecond later. Chromium and WebKit passed with no page errors. The browser holds virtual time while React renders: this is evidence of correct boundary scheduling, not a real-world rendering-latency guarantee. Background tab throttling still depends on the browser; visibility checks reconcile on return.

Validation: 117 application tests, TypeScript checking and the production build passed. Independent code review found no actionable issue. Deadline prop changes and unmount cleanup were reviewed but not separately browser-tested. The enhanced browser regression runs through the existing hosted verification step and writes `reviews/market-clock-fixture-browser.json`.

Personnel source investigation found no individual report timestamps in the retained weekly CSV. The existing UI already discloses that limitation. No player status, source timestamp, forecast, or numerical adjustment was invented or changed.
