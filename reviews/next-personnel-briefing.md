# Next product priority: readable personnel briefing

Independent read-only founding review of 5989a3a identified section 24's
requirement to provide more than an injury dump. The current personnel panel
renders every full report; observed participation sits inside each player's
disclosure. This makes readers assemble the summary themselves.

Build a compact briefing per team grouping reported Out, Doubtful and
Questionable players, with practice-only entries clearly separate. Display a
short verified participation fact beside each name and retain full reports in
expandable detail. Do not add an impact score, projected lineup or numerical
injury adjustment.

Acceptance criteria:

- Every designated player remains represented, including missing usage and
  unresolved identities.
- Current-season and prior-season participation remain distinct, including
  sample size and former-team history.
- Practice-only reports never imply game availability.
- Existing freshness and kickoff gates also govern the briefing.
- Reported absences, unresolved availability and observed participation can be
  read without opening every player's disclosure.

Implemented locally with grouped game designations, a compact highest-share
prior-season fact, independent current-season evidence, and expandable full
reports. Shared empty-season wording appears once per team only when every
player has a verified empty sample. Missing and conflicting identities remain
visible. Full breakdowns preserve all three snap-share channels.

Independent audience review prompted shorter repeated text. Independent code
review caught a historical-conflict early return that could hide a valid newer
current-season sample; separate evidence paths and a mixed-evidence regression
correct it. Three briefing tests pass. The prior full application run passed
193 tests, and the post-correction production build passes. Four Chromium/WebKit
checks cover nested report disclosures at 320/1280px; a 390px real-page check
verifies grouping, keyboard expansion, no overflow and zero scoped axe issues.
These are bounded automated/source reviews, not human comprehension studies.

Separately, a local mobile-load diagnostic of the existing production build
measured one cold browser navigation each for slate, matchup and performance.
At 150ms simulated latency, 1.6Mbps download and 4x CPU slowdown, largest-content
paint ranged from 972 to 1576ms, with no horizontal overflow. Raw measurements
are in local-mobile-load-probe.json. These are single-run lab observations,
not field Core Web Vitals, current-head build verification or a launch verdict.
