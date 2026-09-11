# Visible weather scope

As verified coverage expanded to covered venues, the outdoor-area limitation was still hidden in a collapsed source section. Readers could see temperature, wind and precipitation without seeing that those values do not establish conditions indoors or on the field.

The available-weather panel now states, above its values: “Outdoor forecast for the stadium area. Indoor and on-field conditions are unknown.” The source section retains acquisition time, roof-state limitations, attribution and source links. No numerical forecast or roof assumption changed.

Browser verification covered all thirteen currently available game records in Chromium and WebKit at 320px (26 checks). Each showed the disclosure above the values with the source details closed, displayed the actual forecast temperature, and had no document overflow or page errors. Evidence is in `weather-area-disclosure-browser.json`. This is a rendered-visibility check, not a human comprehension study.

TypeScript checking passed. Independent audience review found no material issue with fan/bettor clarity; it was a source review, not a browser or user study. The public deployment remains pending.
