# Avoid duplicate development verification runs

The development branch was starting the entire verification job for both `push` and `pull_request` on each update. GitHub runs 34533700105 and 34533705176 confirmed the two event types for the same head commit, `2db4582cb85bcf74a824dfd91b5e27b9c1936058`.

Push verification is now limited to main. Pull-request verification remains enabled, and manual dispatch supports explicit checks on a branch without an open pull request. A concurrency group separates event types and pull requests; only superseded pull-request runs are canceled. Main and manual checks are not canceled by newer runs. No data-collection or publication workflow was changed.

The complete verification job is unchanged: dependency installation, test-data preparation, application tests, Python tests, production build, and high-severity production dependency audit. A YAML parse and structural comparison verified identical job definitions and retained read-only repository permissions. Hosted behavior must still be checked after pushing the change. This reduces duplicated GitHub work; it does not remove the Vercel deployment rate limit or prove a hosting-cost saving amount.
