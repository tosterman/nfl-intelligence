# Forecast publication preflight

The native Git publisher now validates the intended edition before staging, committing, or pushing. This closes a release-sequencing gap: verifying that the public response equals a local file does not establish that the local file contains forecasts eligible under the new game-context rules.

The gate requires every displayed forecast to have a valid hash, matching game ID and context, exact canonical-ledger retention, and membership in its game's history. Generation must precede kickoff and must not exceed the edition's generation time. Current-week games whose kickoff follows edition generation require a forecast using the edition's model version. Duplicate game IDs and ledger hashes are rejected. Edition generation cannot be in the future relative to the publication process clock; no future-clock tolerance is allowed.

Historical ledger entries remain intact. Final games without an eligible forecast and later-week games without forecasts are allowed. The check does not claim source freshness, forecast accuracy, verified public availability, or complete current coverage simply because an old edition is internally consistent. Existing source-health checks and the post-deployment exact-artifact capture remain necessary.

## Verified behavior

- The existing checked-in edition was rejected for displayed forecasts lacking matching game context. This is the expected migration condition, not a successful release.
- The retained, unmodified first output from the isolated context-aware generator passed with 15 displayed forecasts. That diagnostic directory's later synthetic output remains unsuitable for deployment.
- Five preflight tests and ten native publication tests passed. The integration test proves invalid editions reach neither Git mutation commands nor public capture.
- The full Python suite passed 213 tests before the final future-clock regression was added. The affected tests were rerun after that correction and passed.
- Independent review found a future-edition clock bypass; it was fixed with a failing-then-passing regression before release. The reviewer then verified closure and found no remaining material issue within this bounded review.

## Production sequence still required

1. After deployment capacity is available, regenerate the consolidated release from real current source inputs, run its checks, and pass this preflight. Do not deploy diagnostic or synthetic files.
2. Publish the tested commit and verify the native Vercel status plus exact public forecast artifact. Retain the receipt separately from generated forecasts. A successful application deployment alone does not complete this step.
3. Confirm the public collector is the new implementation and old collector executions have drained before validating collection behavior. Verify a collection outcome and the downstream private market audit, including unsuccessful collection outcomes. Do not infer cutover from a successful build or consume provider credits merely to retry a blocked deployment.
4. Recheck production edition parity, source health, public desktop/mobile flows, and receipt eligibility. Retain failures without inventing backdated publication evidence.

No deployment or paid provider request was made for this change. Hosting capacity, live cutover verification, and the remaining commercial/product gates are still outstanding.
