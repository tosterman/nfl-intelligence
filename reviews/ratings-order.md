# Explore offense and defense ratings

The ratings page supports combined, offense and defense ordering through URL links. Each view orders strongest first, retains all 32 teams and exposes the active sort to assistive technology. Exact ties use team code order; displayed positions explicitly follow the selected metric. The model output is copied before sorting and remains unchanged.

The helper test checks metric selection, deterministic tie order, invalid-query fallback and nonmutation. Chromium and WebKit at 320px verified all three orders against displayed values, keyboard link activation, active-column semantics, reload preservation and absence of document overflow. Type checking passed. Browser evidence is in `ratings-order-browser.json`.

This is local development work; no deployment was requested or made.
