# Matchup and team sharing metadata

Matchup titles now include season and week. Descriptions distinguish current forecasts, pending forecasts and completed results. Neutral-site matchups use “vs” rather than implying home-field advantage. Team pages identify the team and season and describe the actual schedule/rating/forecast content.

Both page families now emit canonical paths and corresponding Open Graph URLs, titles, descriptions and an explicit shared image. An initial browser check caught custom Open Graph metadata dropping the inherited image; explicit image references fixed the issue. Chromium verified a neutral forecast with a return query, a pending game, a completed game and an uppercase team URL normalized to the lowercase canonical. Type checking passed. Rendered observations are in `page-sharing-metadata.json`.

This verifies local metadata output, not how every social service caches previews, actual search indexing, ranking or audience growth. No public deployment occurred.
