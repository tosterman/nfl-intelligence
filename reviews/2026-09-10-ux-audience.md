# NFL Intelligence: audience and UX review

Reviewed 2026-09-10 against the running local app at http://localhost:3000. This is an independent sub-review for the broader review, with simulated audience lenses, not actual interviews or endorsements by ESPN, the NFL, or their employees. No production code was changed.

## Verdict and first actions

The app is unusually candid about its research limitations and visually coherent. It succeeds as a compact, transparent scoring-model exhibit. It is not yet a compelling daily destination for a football fan or a ready-made media intelligence product: the forecasts explain aggregate scoring strengths, while the personnel, matchup, news, and change context that drives fan interest is mostly absent. That is a product gap, not a reason to invent narrative.

1. Fix team search aliases and preserve the selected week/search on return from details.
2. Rebalance the first viewport toward a useful football takeaway, uncertainty, and current input coverage; increase small explanatory text.
3. Make every metric understandable where it appears, and make filtered result counts explicit.

No critical user harm or data-loss defect was identified in this bounded UX review. These findings do not certify model correctness, source rights, production readiness, full accessibility, or commercial suitability.

## Evidence and coverage

Actual CUA navigation covered the slate, current 49ers/Rams detail, future Eagles/Titans detail, filters/search, ratings, performance, methodology, and contact. Desktop screenshots were inspected at the session's approximately 1265-by-712 viewport. Screenshots showed coherent rendering without overlap at that width. Screenshot observations are retained in the tool transcript; no screenshot files were saved. Source inspection covered AGENTS.md, slate.tsx, globals.css, game detail, ratings, performance, and contact rendering. Mobile findings below are CSS inspection, not a physical-device or mobile-browser pass. No global viewport change was made to avoid interfering with the parent review.

## Must-change: reproducible defects

### UX-01 — P2 / medium: returning from a later week silently resets context

**Evidence:** On the slate, press Next week to select Week 2, search Eagles, open Eagles at Titans, then press `Back to the slate / Week 2`. The result is Week 1, with an empty search and all games shown. The breadcrumb suggests a week-specific return but links to `/`. Source: `src/components/slate.tsx:9`, `src/app/games/[id]/page.tsx:9`.

**Fix:** Put week, search, filter, and sort into URL search parameters and link back to the appropriate slate view. At minimum, the breadcrumb must restore the game's week. Verify a Week 2 detail round trip and a copied filtered URL.

**Fan advocate:** A fan comparing several games needs to keep their place.

**Karen:** “You literally said back to Week 2. Why am I looking at Week 1 again?”

### UX-02 — P2 / medium: displayed Rams abbreviation does not work in search

**Evidence:** Week 1 visibly labels Rams as `LAR` in hero probabilities and card spread. Typing `LAR` into Search teams produces `No games match this view.` Search concatenates internal keys (`LA`) and city/name, but omits the displayed short code. Source: `src/components/slate.tsx:10`.

**Fix:** Search normalized display names, short codes, source codes, and approved familiar aliases; trim/collapse whitespace. Verify `LAR`, `LA`, `Rams`, and `Los Angeles`.

**Fan advocate:** Support the exact identifiers the interface teaches users.

**Karen:** “I copied the letters off your own card. Your search says that team doesn't exist.”

### UX-03 — P2 / medium: filter results have no updated count or assistive announcement

**Evidence:** Close matchups yields 11 cards, but `Week 1 matchups 16` remains unchanged. A team search can yield one or zero while the same 16 badge remains. There is no live result-count region in slate source. Source: `src/components/slate.tsx:15`.

**Fix:** Keep the season total if useful, but explicitly say `11 of 16 games shown` and update a polite status region. Define close matchups where the filter is used, e.g. favorites below 58%, consistent with the implemented threshold.

**Accessibility advocate:** Filtering should announce the result without requiring exploration of the entire card grid.

**Karen:** “It says sixteen games and I can only find eleven. Which number am I supposed to trust?”

### UX-04 — P2 / medium: the slate's blanket score label contradicts final-result cards

**Evidence:** The section says `Scores shown are model expectations`, immediately above Patriots 10, Seahawks 13 labeled Final, where the actual result is shown. Source: `src/components/slate.tsx:15` and GameCard on the next line. Final detail correctly says Final score, so this is a local copy defect.

**Fix:** Say `Forecasts show expected points; final games show actual scores`, or place the distinction directly on each card.

**ESL advocate:** Avoid making readers infer the exception from several separate labels.

## Recommended improvements

### UX-05 — P2 / medium: analytical meaning arrives after a very large decorative scoreboard

At the tested desktop size, the home first viewport is introduction plus featured-game hero; the filter and matchup grid are below the fold. The game-detail hero extends from roughly y=197 to y=660, so the first viewport contains virtually no explanation beyond expected scores and probabilities. Users click `Explore the matchup` and receive a larger rendition of what they already saw.

Reduce hero height, move a concise evidence-based takeaway next to the score, and show `Limited inputs: personnel and weather unavailable` in the initial detail viewport. Preserve the attractive condensed typography and calm palette. Do not add fabricated matchup facts to fill this space.

**Media executive advocate:** “Give me the angle and its support in one screen.”

**Media executive skeptic:** “This is a handsome scoreboard. What exactly can my producer use from it?”

### UX-06 — P2 / medium: crucial explanatory copy is disproportionately small

CSS sets many card and evidence labels to 9–11px, including home/away, model spread/total labels, limitations, source stamps, and mobile spotlight limitation copy. The desktop screenshot confirms these are visually subordinate to very large numbers. This is a legibility finding, not an asserted WCAG contrast failure. Mobile CSS sets week-arrow buttons to 26px (24px below 380px), which is a usability concern on a phone but not by itself proof of WCAG failure.

Raise material labels to 12–14px and body copy toward 16px where appropriate, give navigation controls comfortable touch areas, and test 200% zoom and a real 360–390px layout. Keep uncertainty information readable beside the prediction.

### UX-07 — P2 / medium: glossary and ratings interpretation are too far from use

The detail exposes `LAR -1.6`, fair moneyline `-121`, decisive result, and home-team margin interval `-16.0 to +19.2`. Performance exposes Brier score, log loss, MAE, pushes, and calibration. Some are explained in long methodology prose, but there is no short in-place definition. On ratings, `Positive is better for both offense and defense` and the training cutoff appear only after all 32 rows.

Add short expandable definitions with examples: `LAR -1.6 means the model expects the Rams to win by about 1.6 points`; `a +1 defense rating means about one fewer point allowed than average`. Put ratings direction and cutoff above the table. Keep deeper statistical detail available in methodology.

**ESL skeptic:** “Minus is good on this page and plus is good on the next one. Just tell me who is better and why.”

### UX-08 — P2 / medium product gap: almost no return-visit or team-specific journey

Ratings rows are static, unsortable, and do not link to team games. The slate offers a text search but no persistent team preference, game-day grouping, or jump to a specific week. Later weeks require repeated arrow taps. There is no surfaced freshness/change summary per team, and the current detail shows only an initial snapshot.

Start small: team links from ratings, direct week selection, and a visible `what changed since the last publication` indicator when real new data exists. A shareable snapshot URL would help media/editorial users cite the exact version. These are proposed capabilities, not broken promised features.

### UX-09 — P3 / low: developer-oriented explanations interrupt fan-facing prose

The model-read panel says `Explanation generated deterministically from the structured model output. No unsupported injury, weather, or lineup narrative.` It is truthful, but speaks about implementation rather than helping a fan interpret the game. Replace the primary copy with `Based on past scoring results. Injuries, lineups, and weather are not included`; leave generation mechanics under methodology.

### UX-10 — P3 / low: correction channel requires repository familiarity

Contact has a real issue-tracker link and useful instructions. This is not a dead-link finding. However, ordinary fans must understand a repository, typically use GitHub, and supply a game ID that is more obvious in the URL than in the page. Add a `Report this game's data` link that prepopulates a GitHub issue template, or provide an owner-approved simple channel before broad consumer distribution. Do not invent an operator contact.

## Audience conclusions and counterarguments

| Simulated audience | Constructive conclusion | Adversarial conclusion | Reconciliation |
|---|---|---|---|
| Diehard fan | Useful quick view of all games and independent baseline strength | No QB, roster, trenches, scheme, or current football story; many forecasts feel interchangeable | Good baseline companion, insufficient as a comprehensive game-intelligence destination |
| Skeptical casual / Karen | Clear final/forecast states and no exaggerated winning claims | Tiny caveats, unexplained decimals/negative numbers, broken displayed-code search | Fix comprehension and navigation before adding more metrics |
| Accessibility reader | Skip link, labeled search, visible focus CSS, semantic tables, reduced-motion support, calibration table alternative exist | Long whole-card link names, no filtered result announcement, very small labels | Strong foundations; full keyboard/screen-reader/zoom audit still required |
| ESL reader | Expected-points warning and unavailability explanations are candid | “Slate,” “edge,” “fair moneyline,” “Brier,” “push,” and sign conventions assume prior knowledge | Use local examples and plain labels while keeping advanced terms secondary |
| Mobile-constrained reader | CSS provides single-column cards and stacked panels | Long preamble, 16 tall cards, small navigation targets, repeated empty market fields consume attention | Test actual mobile and prioritize compact scanning and team navigation |
| ESPN-like media executive | Transparent provenance, reproducible claims, consistent visual language | Little editorial differentiation or ready-to-cite snapshot packaging | Potential supporting widget/research product; no evidence yet for a premium newsroom platform |
| League commissioner / integrity lens | Original typographic emblems, explicit non-affiliation, missing-input disclosure, no betting advantage claim | Headline brand and polished scores could still be overread as authoritative; no prospective track record yet | Preserve disclosures and transparent versioning; do not escalate marketing claims beyond evidence |

## What is working and should survive

- Performance prominently distinguishes retrospective 2024–2025 replays from pregame publication and says no completed prospective forecasts are available.
- The site admits the closing market estimates margins more accurately and no reliable betting advantage has been demonstrated.
- Missing inputs are explicitly unknown/unmodeled, not silently asserted healthy or neutral.
- Historical versus live markets and local timestamps versus publication proof are distinguished in methodology.
- Current and future detail routes rendered correctly. Future games show awaiting forecasts instead of manufactured projections.
- Team identity is communicated with names and abbreviations in addition to color. Calibration has an expandable table alternative.
- Visual spacing, typography, and the reserved palette are coherent; no need for a wholesale reskin.

## Contested preferences, not defects

- Decimal expected scores are statistically defensible and explicitly explained; removing them outright is not required. Better hierarchy and plain explanation are preferable to pretending exact integer predictions are more truthful.
- A restrained dark sports-analytics aesthetic fits the subject. It is not a defect merely because it uses panels.
- Repeating `Market edge Unavailable` is transparent, but occupies valuable space in every card. A single slate-level market-status note plus a per-game exception would be less repetitive. Preserve the absence of a verified edge.
- The lack of player/weather features is openly disclosed. Do not call the existing model deceptive for lacking them; call the scope limited, and evaluate any extension against genuine held-out evidence.

## Validation limits

This review did not measure real-user performance, throttle network speed, run a screen reader, complete a full keyboard sequence, or verify commercial data/trademark rights. No blind independent advocate/Karen pair was run inside this sub-review; paired perspectives here are a structured single-reviewer synthesis. The parent review provides separately delegated expertise.
