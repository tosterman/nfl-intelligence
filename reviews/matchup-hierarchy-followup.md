# Matchup hierarchy follow-up

A source-based fan/editor/analyst review identified two navigation problems after the new context sections accumulated: weather preceded the central model explanation, and team profiles/forecast revisions lacked direct shortcuts. The model read now leads the primary column, followed by weather. Conditional Team profiles and Forecast changes shortcuts target focusable headings; all source disclosures remain visible in their existing sections.

Local browser verification on TB/CIN confirmed heading order, clicked both new shortcuts and observed focus on the corresponding `team-profiles` and `forecast-changes` headings. At the inspected 1133px viewport, document width was 1118px with scrollbar allocation and no document overflow. This is a desktop navigation check, not a new physical mobile or human usability study. The production build passed. No numerical forecasts or collection behavior changed.
