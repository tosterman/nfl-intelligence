# Personnel runtime readability review

Scope: simulated NFL fan and analytical reader perspectives, with source review
and local rendering checks. This is not a review by actual professional bettors
or evidence of general user comprehension.

Two ambiguities were corrected:

- When both participation calculations are withheld, matching player reports
  now receive one section-level explanation. It does not invent a collection
  outage and leaves the original source dates visible.
- The full disclosure now scopes an identity mismatch to prior-season history,
  matching the compact briefing. It no longer broadly labels the current report
  as unresolved merely because historical participation could not be joined.

The reviewer confirmed both revised wordings. Seven injected-view regressions
passed, including a case with successful collection but withheld calculations.
Type checking passed. Populated live localhost panels passed keyboard disclosure,
season separation, horizontal overflow and scoped axe checks at 320 and 1280px
in Chromium and WebKit. Those browser checks exercise the available-data view;
the new withheld-calculation notice is covered by the injected rendering test.

No numerical forecasts, personnel statuses or source timestamps were changed.
