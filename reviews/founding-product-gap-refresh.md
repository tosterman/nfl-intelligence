# Founding product gap review

Follow-up: the three implementation priorities below and slate weather are now
implemented on `internal-development`. Evidence: `reviews/slate-market-comparisons.md`,
`reviews/model-brief.md`, `reviews/total-explanation-ui.md`,
`reviews/total-explanation-browser.json`, and `reviews/slate-weather.md`.
This preserves the original gap analysis; it is not a claim of complete founding
coverage or verified human comprehension. Public deployment remains outstanding.

Re-read the founding DOCX and compared the current implementation with sections
1–31. An independent read-only founding reviewer identified the following
locally actionable priorities. This is a source review, not timed human testing.

1. Slate market comparisons. `src/components/market-panel.tsx` MarketCard gives
   a sportsbook spread, while `src/components/slate.tsx` gives model spread and
   total. Readers must subtract themselves and open details for market totals.
   Show compact selected-book spread and total differences using the same quote
   identity, expiry and kickoff guards as the detail page. Preserve unavailable
   states; label descriptive differences without claiming validated betting
   value. Verify both spread signs, total direction, missing markets and expiry,
   then check mobile density. Defer sorting until the comparisons are clear.
2. Total explanation. Game detail explains margin contributions but does not
   explain the expected total through a reconciled decomposition. This needs
   model-output schema and provenance work. Frozen experimental model files must
   remain unchanged; define a separate versioned path before implementing new
   snapshot fields. Preserve older snapshots and explicitly mark absent fields.
3. Short opening brief. Assemble the leading model factor, opposing factor when
   present, market difference and verified changes into a concise reading path.
   Link each assertion to evidence and separate descriptive context from actual
   model contributions. No invented weather/personnel adjustments.

Homepage weather context is also missing relative to the founding card example,
but market comparisons address a core question more directly and take priority.
Timed fan/editorial usability sessions are still needed to establish the actual
30-second slate and two-minute game-understanding promise. Model improvements
remain subject to independent prospective validation.

Updated launch acceptance to reflect completed season-aware matchup acquisition
and UI, completed settlement evaluation, current hosted CI evidence, and the
remaining generative-explanation gap. The public edition is still older than
development. The overall founding objective remains incomplete.

## Post-runtime review — September 11, 19:20 UTC

The independent founding reviewer identified one remaining local product
priority: include verified personnel and weather updates in the weekly briefing.
`WeeklyChanges` currently compares numerical forecast runs only, while runtime
personnel and weather changes are available on matchup pages. A returning reader
can miss those changes when the numerical forecast is unchanged.

Produce compact server-selected summaries with distinct model, reported-player
and weather timestamps and links to the detailed evidence. Pass summaries to
the slate rather than complete source histories. Repeated acquisitions without
changed values must not produce change items. Stale data and mismatched game
contexts must stay unavailable; missing reports must never imply recovery.
Preserve selected-week navigation and expiry, and do not imply that descriptive
personnel or weather observations changed the numerical model.

This is the next implementation task, not a completed feature or human usability
finding. The larger numerical requirements still need additional evidence.
