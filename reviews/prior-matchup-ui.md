# Prior-season matchup integration

Both historical panels now read the reconciled prior-season artifact rather
than separate fixed-season files. The selector requires the requested season to
follow the artifact season and match its forecast season. It checks both teams,
cutoff and observation dates, and source hashes. Historical data does not use
the current-feed expiration timer. Current-season context remains independent.

Validation: six targeted TypeScript tests passed; the following-season selection
case was then added and both prior-context tests passed again. TypeScript
checking passed. Every historical passing, rushing and inside-20 count matches
the previous panel inputs. Twelve local browser cases passed: Chromium and
WebKit, widths 320/390/1280, with and without a numerical forecast. They checked
season headings, empty current sample, expiration behavior, no horizontal
overflow and no page errors. The 390px screenshot was visually inspected.

The runtime release copy includes the new JSON. Automatic prior-season source
acquisition, publication and hosted verification remain pending. This change
does not alter the model or demonstrate predictive profitability.
