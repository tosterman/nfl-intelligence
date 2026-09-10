# Optional historical-usage failure drill

The exact multi-command block from the refresh workflow was executed with Bash's fail-fast behavior in four isolated fixture directories. Identity audit, usage audit, and export were each made to fail in turn with exit code 23. In every failure case, later commands were not executed and the previous artifact's bytes were unchanged. The successful control executed all three stages and replaced the fixture artifact. The workflow's `continue-on-error: true` setting was verified from its parsed definition.

This tests shell orchestration with simulated stages, not the production calculations or GitHub's hosted continuation semantics. Calculation validation and atomic replacement have separate unit tests. No provider requests or production files were changed by the drill.

The actual `PlayerUsage` component was also rendered against the retained artifact and current personnel report, then with a changed source hash and changed retrieval time. Only the matching input displayed snap shares. Both mismatched variants displayed the unknown-history state, without inherited shares. This is a rendered-component fixture check, not browser or hosted schedule evidence.

Results are retained in `usage-failure-drill.json` and `usage-retention-render.json`. Together they support the intended local failure behavior: an older artifact can remain on disk while incompatible public context is withheld. Hosted optional-failure continuation and sustained scheduled refresh remain open acceptance requirements.
