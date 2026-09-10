# Adversarial code and model review — 2026-09-10

Scope: current working files, engine, model experiment, design, frontend, dependency injection code and tests. This is an independent simulated QA/security/privacy/statistician/professional-bettor review, not an endorsement by a real person. The implementation is actively evolving; findings describe the files inspected before remediation.

## Verdict

The score arithmetic and basic historical time isolation are sound enough for a clearly labeled research preview. The present implementation is not yet an operational auditable forecasting publication service. Its most serious gaps concern consent withdrawal, publication proof, stale-state handling and prospective grading. Missing player/market modules are honestly disclosed and should remain roadmap items rather than be filled with invented estimates.

## P1 — fix before calling the service operational

1. **Consent withdrawal does not stop already injected measurement scripts.** `src/components/privacy.tsx:5` conditionally mounts Analytics/SpeedInsights and unmounts them on reopening settings or declining. The installed SDK injection effects (`node_modules/@vercel/analytics/dist/react/index.mjs:181`, `node_modules/@vercel/speed-insights/dist/react/index.mjs:146`) have no cleanup that removes scripts/listeners or disables measurement. Custom events check localStorage, but already loaded performance collection is not governed by that check. Add a beforeSend gate that consults current consent for both SDKs, and implement a hard reload after withdrawal if needed. Acceptance: allow, generate events, decline, navigate/hide page, verify no further analytics/vitals transmissions; also exercise withdrawal in another tab. This is a code-proven missing revocation mechanism; post-withdrawal network behavior still needs browser evidence.

2. **Local generation is still represented as publication.** `scripts/build_data.py:107-110,134-142` assigns `publishedAt=now` before any deployment, selects `pre[-1]` by that timestamp and exposes it as a pregame snapshot. No publication receipt exists. An artifact generated before kickoff but first deployed after kickoff will claim a pregame history. Methodology correctly acknowledges receipt requirements, but the code does not enforce them. Separate createdAt from successful public publication, append a deployment receipt, and score only a fixed eligible pre-kickoff receipt. Also preserve source hash, code revision, actual parameter values and model identity per snapshot; current snapshot keys contain none of those except a manually assigned version. Source metadata on the latest site artifact cannot reproduce older revisions after inputs change.

3. **Prospective results can never appear.** `src/app/performance/page.tsx:4` permanently states no completed prospective forecasts exist; `scripts/build_data.py:157` exports only 2024–2025 retrospective metrics. After any of the 15 existing forecasts finishes, the promised public record still remains empty. Add a separate prospective ledger join/grade using eligible publication receipts, account for missed forecasts and revisions, and derive the notice from actual counts. Keep retrospective and prospective universes separate.

4. **There is no scheduled refresh, failure monitoring or stale state in inspected files.** `.github/workflows` is absent; all rendered data/status values are baked into JSON. `src/components/slate.tsx:16` prints a refresh timestamp but never calculates freshness or indicates service degradation. `scripts/build_data.py:149` can leave an incomplete old game marked in-progress indefinitely. A successful deployment does not make the promised weekly service operate. Add refresh + deployment scheduling and failure visibility, an explicit data-age state, and unknown/delayed-result handling; do not imply a live score. A browser left open over kickoff should not continue presenting a scheduled state without a stale qualifier.

5. **Offline rebuilds fabricate a fresh source retrieval time.** `scripts/build_data.py:115-120,154` skips fetching under NFL_OFFLINE but always writes source.retrievedAt=now. Both methodology and footer then make unchanged old bytes look freshly retrieved. Persist retrieval metadata alongside raw bytes and reuse it offline; distinguish builtAt and retrievedAt. Validate a downloaded CSV before replacing the last good file: the current comment says parse first, but it only checks prefix/size and overwrites before load_rows validates.

6. **Production and reported evaluation use different update policies.** `scripts/build_data.py:74-79` freezes replay at each week's first game, while `:130` fits production at today's date. Existing Week 1 forecasts have trainingThrough=2026-09-09 and include the completed same-week NE–SEA opener. The methodology's blanket statement that same-week outcomes never enter football predictions is false for production. Choose and document the intended production cutoff and evaluate that same policy; either freeze live weekly or describe/evaluate rolling pregame updates. This is a policy mismatch, not target-game result leakage.

## P2 — bounded correctness and product fixes

7. **Unknown kickoff times are converted into invented 23:59 kickoffs.** `scripts/build_data.py:21` uses 23:59 when source gametime is blank. That can authorize a forecast after a real game has started and presents an invented time to readers. Refuse publication when kickoff is unknown, display TBD, and retain schedule revisions so postponements cannot retroactively recategorize a snapshot as pregame.

8. **Postseason navigation breaks.** `src/components/slate.tsx:9-11` fixes labels to regular season and only disables Next at week 18. Engine selects upcoming week regardless of game_type. When the engine chooses a postseason week above 18, the UI labels it regular season and allows endless nonexistent future weeks. Use actual available week/type keys, safe bounds and postseason labels. Current source season may not yet include postseason, so this is a lifecycle reproduction to add.

9. **Every slate visitor receives the full retrospective record as JavaScript.** `src/components/slate.tsx:5` imports site through `src/lib/data.ts:1`, which imports all site.json. Inspected data/site.json is 506,788 bytes; generated `.next/static/chunks/3y32g-g3zrf6f.js` is 511,564 bytes and contains actualMargin records. Split server-only evaluation data from a compact slate payload and pass week/season metadata explicitly. Recheck bundle after remediation; compression does not remove parse/execute cost or payload growth.

10. **The model's fixed identity is not coupled to its parameters or evaluation artifact.** `scripts/build_data.py:15,123-127` reselects parameters each refresh from mutable historical source while VERSION remains constant. A corrected old score could silently alter selection under the same displayed version. Pin the released training/tuning dataset and parameter selection, or version changes explicitly with a full model manifest. The experiment also evaluates multiple families on 2024–2025 (`scripts/experiment_model.py` and `reviews/model-experiment-results.json`); future decisions informed by these comparisons must call those seasons development evidence. Retaining the unchanged baseline can retain its originally declared evaluation, but do not call a subsequent selected winner freshly untouched.

11. **Numerical tests are too narrow to support publication claims.** The current six Python and five TypeScript tests all pass. However, ledger testing only recomputes hashes and compares timestamps against kickoff; it does not verify append-only preservation, failed-deploy exclusion, source identity, final-result separation, postponed games or actual prospective grading. Add boundary tests for those concrete failure modes. Test main with injected clock/paths, avoiding production artifact rewrites. The existing tests do establish future-score invariance for fit(), market independence and basic reconciliation; do not discount that evidence.

12. **Documented history length differs from implementation.** Methodology says maximum four-year history, but fit() retains from January 1 of cutoff-year minus four. A September 2026 fit includes January 2022 onward, about 4.7 years. Use a true rolling timedelta cutoff or document four prior calendar years plus the current year. This is a small model-description defect, not evidence of leakage.

## Research and roadmap, not launch blockers for a limited preview

- Personnel, QB/OL/DL, scheme, EPA, travel/rest, forecast weather and timestamped live markets are absent but visibly disclosed. The full founding vision remains incomplete; a scoring baseline can still be useful.
- Normal probabilities omit ties/key-number mass and are described as decisive-result approximations. Avoid implying precise settlement probabilities or expected profit. Current ATS/totals records are exploratory and correctly avoid ROI claims.
- Calibration has severe local underconfidence in the exported high-probability bin (24 games at mean 72.32%, observed 91.67%); counts are visible, but uncertainty bands and a broader empirical baseline would help. This alone is not license to recalibrate on the holdout.
- Margin MAE is 10.472 versus closing market 9.687 on 570 matched games. Product copy acknowledges this. No demonstrated betting advantage.
- No accounts, payments, user text ingestion or live ad scripts currently creates a comparatively small security surface. CSP permits unsafe-inline; treat nonce/hardening as defense in depth, not a demonstrated XSS vulnerability.

## Checks performed

- Read AGENTS.md, CLAUDE.md, docs/design.md, docs/implementation-plan.md, engine/experiment, src files, tests, next.config.ts and generated artifacts.
- npm test: 5/5 pass.
- python -m unittest discover -s tests -p test_engine.py: 6/6 pass.
- Confirmed 15 snapshots, generatedAt 2026-09-10T14:01:18.585353+00:00; all current forecast training cutoffs 2026-09-09 in inspected artifact.
- Confirmed full retrospective payload in a 511,564-byte client JavaScript chunk.
- At review time git status reported no repository initialized, and .github/workflows was absent. These may change during the parent's release work.
- Did not mutate production code or data. Did not run another production generation, deploy, or claim browser/network privacy verification.
