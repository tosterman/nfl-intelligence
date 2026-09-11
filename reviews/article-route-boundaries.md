# Unknown article routes return 404

Local HTTP probing reproduced server errors for `/constructor`, `/toString` and `/__proto__`. Article lookup used a normal JavaScript object and a truthiness check, so inherited properties were treated as page definitions. Rendering then failed because those values had no article sections. This was a lookup error; no object mutation or prototype pollution was demonstrated.

Both metadata and rendering now use one lookup that requires an own property of the article registry. Five invalid names return HTTP 404 and all four defined articles return HTTP 200 (`article-route-boundaries.json`). Two automated tests cover the not-found exception, no-index metadata and valid canonical URLs, so a generic server exception does not satisfy the regression.

Chromium and WebKit at 320px verified the friendly not-found page and its return-to-slate link, with no page errors (`article-route-browser.json`). The first browser assertion incorrectly required an empty query string after returning; the slate legitimately adds its filter defaults, so the check was corrected to allow those parameters. The production build passed.

The team route uppercases identifiers before its lookup and the game route uses an array search; the reproduced inherited-name path applies to the article registry. This bounded fix is staged for publication, not yet a production deployment.
