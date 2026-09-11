# Retained comparisons in forecast history

The display registry now supports multiple exact schedule-source pairs. Each
additional entry is derived only after verifying the comparison filename digest,
recomputing the complete comparison from restored bundles, and matching its exact
canonical bytes. The compact entry contains field names, counts and game identities
present in both schedules; it does not expose historical betting prices.

The existing historical primary pair is preserved as previously verified evidence.
Additional pairs are rebuilt from all retained comparison reports. The current
additional entry is the real same-edition comparison, with zero record changes;
it is not evidence of another refresh. Fixture tests exercise distinct editions.

The UI selects the exact ordered source pair and game identity. Newer evidence
does not replace another pair's explanation. The primary pair retains its unknown
original collection-time disclosure. Additional pairs use the narrower statement
that source differences do not establish public availability. Missing matchup
context continues to withhold numerical prediction comparisons.

The staged refresh workflow rebuilds this registry after input comparison, includes
it in recovery artifacts, and stages it in the publication commit. It remains
disabled. No new source data, model change or public deployment was performed.

One Python registry test covers verified derivation and rejection of changed
comparison bytes. Four TypeScript tests cover ordered pair matching, per-game
counts, additional pair selection and rendered evidence limitations. The full
application suite passed 155 tests before the final render test was added;
all four final targeted tests passed. Independent AI review repeated those tests
and found no material defect.

Final TypeScript checking passed. The existing browser regression passed all 60
game/browser/viewport combinations with no page errors or horizontal overflow.
The additional-pair wording was exercised by the rendered component test; the
real site's current histories exercise the historical primary pair.
