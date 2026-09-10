# NFL Intelligence

Independent NFL analysis with an auditable statistical engine, current-week forecasts, game breakdowns, team pages, and a public research record.

## Run

Requires Node 22 and Python 3.13.

```sh
npm ci
pip install -r requirements.txt
npm run dev
```

Checked-in artifacts let the website run without downloading source data. To rebuild forecasts, run `npm run data:refresh`. This downloads nflverse schedule/results and weekly team statistics, verifies required coverage, fits strictly earlier-week data, retains previous snapshots, and exports the site artifact.

## Verification

```sh
python scripts/prepare_test_data.py
npm test
python -m unittest discover -s tests -p 'test_*.py'
npm run build
npm audit --omit=dev --audit-level=high
```

The test suite includes score/odds arithmetic, no-vig probabilities, future-data perturbations, neutral venue behavior, publication receipt eligibility, archive tampering, malformed sources, and probability bounds. Browser and independent review evidence lives in `reviews/`.

## Model and data

The scoring component is opponent-adjusted, regularized and recency-weighted. The efficiency component uses passing/rushing EPA, CPOE, sacks, turnovers and passing share. Selection uses 2021–22, residual scales use 2023. 2024–25 is explicitly retrospective development evaluation, not an untouched holdout. Live performance admits only successful pre-kickoff publication receipts, excluding games first published after kickoff.

Sources: [nflverse data releases](https://github.com/nflverse/nflverse-data), [CC BY 4.0](https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md). Derived forecasts are transformations of upstream data. Actual file URLs, hashes and acquisition times travel in each artifact. Current player availability, lineup and scheme inputs are unavailable. Selected US games include NWS kickoff-hour weather context, separate from the numerical model. No live market edge or profitability is claimed.

Run `python scripts/refresh_weather.py` to acquire weather for upcoming games whose exact venue has a verified mapping. The initial mapping resolves four venues through official addresses and the US Census geocoder. It does not substitute home-team coordinates for neutral games. Hourly forecasts are matched to kickoff and expire after 30 hours by issue and retrieval time. Null values remain unknown. Source responses are compressed in `data/weather-sources/`; `weather-ledger.json` retains captured records. NWS data use follows its [public-domain terms](https://www.weather.gov/disclaimer/). Address coordinates represent venue vicinity, not surveyed field centers. Weather collection is included in the publishing workflow, whose account configuration remains incomplete.

## Publishing

`scripts/deploy_release.py` deploys through Vercel REST using `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` environment secrets. It verifies READY state, fetches the deployed forecast artifact, compares each snapshot with its canonical local version, then records the receipt. A failed deployment cannot enter the prospective record. The public `/api/status` endpoint returns 503 when the model edition, schedule/results input, or either of the two recent efficiency-season inputs is over 30 hours old or lacks a valid acquisition time. An offline rerun cannot make stale inputs healthy. Individual checks are returned for monitoring, and the slate uses the same assessment.

GitHub Actions verifies every push and provides a daily refresh workflow. Scheduled publishing requires the three repository secrets. Missing credentials fail explicitly before changing public data. Retain branch protection and restrict write access to ledger and publication workflows. Git administrators can rewrite history; hashes and receipts are evidence, not absolute immutability guarantees.

## Analytics and advertising

Enable Vercel Web Analytics and Speed Insights in the project dashboard. Both are opt-in, with consent gates at load and send time. Product events are bounded names, never arbitrary search strings. Revenue activation requires the owner’s publisher account, production domain, appropriate commercial hosting plan, Google eligibility review, and applicable certified consent configuration. No ad script or fake publisher ID is shipped enabled.

The source founding document is excluded from the repository. `docs/design.md`, implementation notes, and review reports describe the implementation and remaining operational requirements.
