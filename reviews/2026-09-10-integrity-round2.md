# Integrity review, round 2 — 2026-09-10

Independent review of the newly introduced refresh, publication, recording and efficiency-blend paths. No production code/data modified. Added ten isolated Python regressions in tests/test_refresh_integrity.py and one TypeScript market-domain regression. These intentionally fail until the underlying findings are fixed; they are not expected-failure decorations.

## Initial test results before parent remediation

- New Python suite: 10 tests, 5 pass, 5 fail (2.94 seconds).
- TypeScript suite: existing 5 pass; new probability-domain test fails.
- Blend mutation test changes every result and both teams' efficiency statistics on or after 2024-09-05, including the target. Both predicted margin and total remain exactly unchanged. This independently supports the newly aligned weekly freeze and future-input exclusion.
- Receipt tests confirm exact-kickoff publication is excluded, an unpublished newer revision cannot supersede a public earlier forecast, and ties remain separate from decisive results.
- Offline schedule digest mismatch correctly fails closed.

## P1 findings requiring correction

1. **Receipt creation trusts fabricated evidence.** scripts/record_publication.py's inspected version accepts any HTTPS URL, a deployment ID beginning dpl_, and a local artifact containing known hash strings. The isolated regression successfully records a ready receipt for https://example.invalid, deployment dpl_fake and an artifact containing only a hash. No actual deployment exists. This is a trusted-operator tooling flaw rather than an anonymous public exploit. Fetch/verify deployment readiness, deployment identity and the exact published artifact; verify full canonical snapshots, not supplied hash labels. Parent has acknowledged and is replacing this path with verified Vercel evidence. The regression catches ValueError/SystemExit, so removing the old unsupported CLI path fails closed without writing a receipt.

2. **A valid receipt authenticates the hash label, not current snapshot bytes.** scripts/publication.py eligible_snapshot accepts a snapshot whose probability was changed from .60 to .99 while keeping its original hash, then grade_prospective grades the forged .99. Recompute canonical snapshot hashes before selection/grading. verify_append_only comparing an in-memory loaded ledger with its shallow copy is insufficient to detect already changed on-disk content. Production generation should validate every existing snapshot, and receipt recording should bind deployed bytes to the same canonical hash. Test: test_receipt_does_not_authorize_tampered_snapshot_content.

## P2 correctness findings

3. **Neutral-site explanation wrongly assigns home-field points.** The efficiency regression centers its Home venue indicator and exports centered z*beta as the term. refresh.evidence labels that centered effect Home field. Changing 2024_01_BAL_KC to Neutral produces -0.310 displayed Home field points, even though the scoring component is zero and the UI says neutral home field is zero. This is a decomposition problem: move the venue centering constant into the efficiency baseline and expose raw venue*coefficient as home field. Preserve the exact total margin rather than zeroing the term and silently changing the forecast. Test: test_neutral_game_has_zero_home_field_contribution.

4. **Projection guard checks only the smaller expected score.** canonical_prediction(100,102,(14,14),[]) returns home 101 and away 1 because the guard uses (total-abs(margin))/2 only. Validate both expected scores. Separately, canonical_prediction(20,40,(1,14),[]) emits homeWinProbability=1 after CDF/rounding. fairMoneyline rejects 1 and crashes a game route. Reject unsupported degenerate outputs or use a documented representation that remains valid through rendering; do not silently imply certainty. Both have explicit regressions.

5. **Market comparison accepts impossible probabilities.** compareMarket only checks finiteness. Passing -.1 or 1.1 yields a numeric probabilityDifference instead of null. The feature is presently disconnected, so this is a future-market safety regression rather than a currently displayed false edge. Added test in tests/math.test.ts.

6. **Source replacement remains nontransactional.** refresh.acquire writes downloaded bytes and metadata before load_rows parses them. A large CSV with a valid first token but missing required fields replaces the good cache and then fails. Efficiency acquisition similarly writes before full field validation. Validate parsed input in a temporary buffer/file, then atomically replace each cache; write ledger/site via atomic replacement as well. The statement 'write only after every model and ledger validation succeeds' protects model computation failures, but not process interruption or two concurrent refreshes. The upcoming workflow should enforce concurrency and guard protected ledger history.

## Conceptual model issue, separate from launch correctness

The efficiency regression uses sum features and a free intercept in the margin model, and difference features in the total model. These do not enforce team-exchange symmetry at a neutral venue. A concrete neutral BAL/KC probe gives -1.0630566 home margin; swapping home/away gives +1.1819103 rather than its exact negative. Expected total also changes from 42.8131280 to 42.8152347. This is small in this example, but structurally allows an arbitrary designated-home label to change a neutral prediction. Consider a future model version with antisymmetric margin features and symmetric total features, while retaining an explicit nonneutral home-field term. That changes forecasts and requires a new evaluated version; do not disguise it as a display-only fix. Centering the contribution correctly addresses finding 3 without pretending to solve this larger modeling issue.

## Improvements confirmed from round 1

- Source digest is checked offline and retrievedAt is persisted separately.
- The production path now uses weekly cutoff and records model code/source/configuration identity per snapshot.
- Prospective grading exists and requires a pre-kickoff receipt.
- Analytics callbacks consult current consent; local withdrawal reloads and storage changes are observed. This addresses the missing code-level revocation mechanism, pending real network verification.
- Slate imports team helpers/types instead of the full data module, removing the full retrospective import from its JavaScript dependency graph. The whole season's game histories still travel as props, which can grow; measure the final build.
- Unknown kickoff time is represented as null and withheld from publication.
- Postseason labels and dynamic upper bounds have replaced the original fixed regular-season assumption.
- Development evaluation labeling acknowledges the inspected historical experiments.

## Remaining operational evidence

No workflow existed at this review instant; parent is implementing release operations. Re-run these regressions after changes and report actual counts. A receipt proves only what its verifier checked; it should record the verified deployment identity and exact content. It does not retroactively turn earlier local generation into public publication.
