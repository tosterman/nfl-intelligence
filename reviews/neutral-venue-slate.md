# Neutral venue clarity — 2026-09-10

Live browser review found that the Melbourne 49ers–Rams game used “at” and unqualified home/away labels on the slate. The detail page already identified the neutral venue and the model already assigned zero home-field points. The slate concealed that distinction until users opened the matchup.

The featured matchup now uses “vs,” names the neutral venue, and explicitly states that the model assigns no home-field points. The compact mobile focus also names the venue. Neutral game cards show the venue above the teams and use designated home/away labels. Ordinary home games retain their existing wording.

Verification: successful production build; fresh local browser accessibility tree confirmed all three neutral labels and ordinary home-game labels; desktop screenshot reviewed for hierarchy and wrapping. Independent source review from fan/editorial-integrity perspectives found no actionable issue. That review was simulated and source-only; this change did not receive a new physical-device mobile check.

Commit `d134267` received a successful [Vercel production deployment](https://vercel.com/khnum/nfl-intelligence/7sRuXrS5GVuQjo3xKwNvYvoYn2gA). Public slate HTTP 200 includes the Melbourne venue, no-home-field explanation, and both designated-team labels. Numerical forecasts are unchanged.
