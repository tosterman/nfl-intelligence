# Weekly context briefing — local verification

Implemented founding §21 personnel and weather comparisons in the existing weekly briefing. The client receives compact summaries, timestamps and expiry deadlines, not personnel or weather histories. Personnel changes use the exact game-bound publication and require successful collection; removed entries explicitly do not establish recovery. Weather comparisons use distinct retained issues from a single selected publication. Unchanged, mismatched, future, expired and closed-game comparisons are omitted.

Independent code review identified repeated private storage reads. Fixed with one cached index and immutable-root/ref-keyed history caches, with freshness evaluated outside the cache on every render. Reads are limited to upcoming seven-day games and four concurrent requests.

Validation: TypeScript passed. Full application suite passed 252 tests before adding the final render/navigation test; the context suite then passed all three tests. Real Chromium at 390px rendered ten current weather comparisons, followed the first link to its actual weather-history anchor with slate return parameters, and reported no page errors or horizontal overflow. See weekly-context-browser.json. Player source comparisons were unchanged in the current publication, so no synthetic personnel update was introduced.

Scope: local implementation and verification only. Public deployment, scheduled worker acceptance and commercial launch gates remain outstanding. Broader browser/assistive-technology coverage is not established by this check.

## Reader review follow-up

The independent fan/analyst source review found that the collapsed summary hid ten weather changes behind a zero-model-revision label, and generic field names required another click to understand magnitude. Fixed with separate weather/player/model counts and retained before/after measurements, preserving unknowns and raw wind ranges. Forecast-description changes link onward rather than shipping long forecast prose. Source timestamps remain distinct from model generation.

Chromium and WebKit at 320px verified keyboard opening, count visibility, real measurement text, no page errors and no document overflow. The first actual row showed wind 6 mph to 7 mph and precipitation chance 8% to 5%. Evidence: weekly-context-ux-browser.json. Targeted tests passed after the wording changes. This was a simulated audience lens, not an actual reader interview.

Screenshot review then exposed excessive mobile height when all ten context rows opened with the main briefing. They now have a separate native disclosure with the update count; model information remains reachable without traversing every context row. Weather summaries explicitly describe outside-stadium conditions and preserve unknown field/roof conditions. Chromium verified keyboard opening of the nested disclosure and axe returned zero violations and zero incomplete checks for the expanded briefing at 320px (eight applicable checks). Evidence: weekly-context-accessibility.json. Eleven focused context/model briefing tests passed. This bounded automated check does not establish comprehensive accessibility compliance.

Open-page deadline verification now mounts the actual WeeklyChanges component in the existing isolated browser fixture. Chromium and WebKit remove the personnel row at its exact deadline, keep the independent weather row until its later deadline, then update both counts and the empty state without navigation or reload. The fixture uses invented summaries and a controlled clock; it is not publication evidence. Existing market, weather and personnel deadline assertions also passed, as did TypeScript. The existing CI browser step invokes this checker; its updated hosted execution remains to be observed.

Release preparation on September 11 also confirmed no commits on origin/main missing from development and 157 release files matching Git's staged contents. This is a file-integrity check, not a fresh-edition or public-deployment acceptance.
