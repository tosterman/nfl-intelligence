# Preserve the briefing reader's slate view

The briefing's new history links initially omitted the `from` parameter used by existing slate cards. Returning from a history would therefore retain the game's week but lose the reader's team search, filter and sorting.

Both comparable and unavailable-history links now receive the slate's existing return URL, encode it as one query parameter, and retain the `forecast-changes` anchor. The game page's existing return handling remains unchanged. Direct component use defaults to the selected week.

All six briefing tests and TypeScript validation pass. The regression checks both link categories. A real local Chromium/WebKit round trip opened the Rams history from Week 1 with `q=Rams`, `filter=forecast`, and `sort=confidence`, verified the history anchor, then used the breadcrumb to return with all four state fields intact. Results are in `weekly-changes-navigation.json`. No comparable later-week production history exists yet, so this browser evidence is limited to the real Week 1 path.
