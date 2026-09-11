# Mobile matchup hierarchy

At widths up to 600px, the scoreboard uses tighter spacing and smaller decorative
team marks while retaining team names, expected points, probabilities and their
limitations. Section links occupy one horizontally scrollable row with a visible
swipe/tab hint. Links retain a minimum 44px height. KPI card padding is reduced;
desktop layout rules are unchanged.

Independent live Chromium review at 390px measured the ATL/PIT model explanation
at 978px from the top, compared with the measured baseline of 1,339px: 361px, or
27%, earlier. The reviewer found the score summary readable, the clipped next
link and hint understandable, and no document-wide horizontal overflow. The
current screenshot was visually inspected by the main agent as well.

TypeScript checking passed. This is a bounded layout improvement, not a claim
that the entire long matchup page is optimized. No forecast values, source
evidence or historical sections were removed.

The completed browser matrix covers ATL/PIT and SF/LA in Chromium and WebKit at
320, 390 and 1280px: all 12 cases passed. The model explanation appears 329px
earlier at 320px and 361px earlier at 390px; its desktop position is unchanged.
All 120 section-link keyboard activations passed, with link heights at least
44px and no document overflow. Separate axe scans at 390px in both engines
reported no tested WCAG violations; this does not prove full accessibility.

An initial run stalled in browser.close(), confirmed by its traceback after
stopping its owned Playwright driver. That run is not counted as completed.
Progress logging was added; the subsequent full run completed successfully,
including shutdown of both browser engines. No application workaround was
introduced for the test-process shutdown issue.
