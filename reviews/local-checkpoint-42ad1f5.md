# Integrated local verification

Source 42ad1f5 passed all 113 application tests and 229 Python tests against the refreshed real-data edition. The latest local production build also passed after query-driven ratings were introduced. Expected acquisition-failure fixture messages in the Python output are exercised failure paths; the suite finished OK.

Independent source review found no material issue in the new uncertainty explanations or ratings sorting. It checked endpoint direction, separate versus joint interval coverage, strongest-first defense ordering, source nonmutation, repeated/invalid query fallback, selected-link and column-sort semantics, and awaited search parameters.

Follow-up metadata gives ratings sort variants the same canonical `/ratings` URL. A rendered Chromium check verified the base page, offense view and defense view; see `ratings-canonical.json`. This is metadata consistency evidence, not proof of search indexing or ranking.

The refreshed local forecasts, uncertainty copy and ratings interactions have not been deployed. Vercel rollout and commercial acceptance remain separate unfinished work.
