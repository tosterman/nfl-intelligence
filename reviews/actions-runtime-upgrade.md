# GitHub Actions runtime upgrade

All five workflows now pin official actions to immutable release commits: checkout v7.0.1 (`3d3c42e5aac5ba805825da76410c181273ba90b1`), setup-node v7.0.0 (`820762786026740c76f36085b0efc47a31fe5020`), setup-python v7.0.0 (`5fda3b95a4ea91299a34e894583c3862153e4b97`) and upload-artifact v7.0.1 (`043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`). Release metadata and each exact action.yml were inspected through GitHub's API; all declare node24. The application remains Node 22 / Python 3.13. Permissions, schedules and publication behavior are unchanged. Future action upgrades require deliberately changing the pins.

Verified successful hosted runs:

- [CI 34524577630](https://github.com/tosterman/nfl-intelligence/actions/runs/34524577630): application and model tests, build and dependency audit.
- [Refresh 34524578110](https://github.com/tosterman/nfl-intelligence/actions/runs/34524578110): acquisition, tests, build, authenticated Git push, native Vercel publication verification, recovery upload and receipt commit.
- [Health 34524580501](https://github.com/tosterman/nfl-intelligence/actions/runs/34524580501): monitoring and downloadable health artifact.
- [Odds 34524595814](https://github.com/tosterman/nfl-intelligence/actions/runs/34524595814): authenticated production collection path, returning already-current without another paid acquisition.
- [Research 34524769278](https://github.com/tosterman/nfl-intelligence/actions/runs/34524769278): automatically triggered by the successful refresh, graded 0 / pending 15 / excluded 0.

All five runs had zero check annotations, eliminating the prior Node 20 deprecation warnings. The downloaded research input exactly matched the refresh recovery artifact and its report hash `91497ce97cbf78b7e3b2cdc1f3992ed07d1a1132e22987a8e9fba92b82e2bd46`. These executions verify compatibility, including the changed checkout credential storage and artifact implementation; they do not prove sustained clock-triggered reliability or prospective predictive performance.
