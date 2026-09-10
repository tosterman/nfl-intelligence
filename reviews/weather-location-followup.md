# Weather location follow-up — September 10, 2026

Five additional official venue addresses were checked against the US Census geocoder. No new coordinate was accepted. Exact requests, returned matches, and acquisition timestamps are retained in `weather-location-followup.json`.

| Venue | Primary address source | Result |
| --- | --- | --- |
| Gillette Stadium | [Operator guide](https://www.gillettestadium.com/a-to-z-guide/) | One fuzzy match: requested Patriot Place, returned Patriot Circle. Rejected. |
| Paycor Stadium | [Bengals fan guide](https://www.bengals.com/fans/fanguide) | No matches. |
| Hard Rock Stadium | [Dolphins contact information in terms](https://www.miamidolphins.com/legal/terms-conditions) | No matches. |
| Huntington Bank Field | [Operator contact page](https://huntingtonbankfield.com/contact/) | No matches. |
| Northwest Stadium | [Commanders stadium guide](https://www.commanders.com/stadium/stadium-guide) | No matches. |

A single returned match does not establish a correct location. Added a collector preflight that checks every confirmed Census point against its recorded street, city, state, and exact returned coordinates. Common street/direction abbreviations are normalized, but Place and Circle remain distinct. Postal-code equality is deliberately not asserted for these vicinity points; the existing Lumen street/locality match returns 98104 while the operator address uses 98134. These remain area-forecast lookup points, not surveyed field centers.

All nine existing points pass. Three evidence-validation tests and seven weather tests pass, including the real Gillette mismatch, coordinate drift, duplicate matches, and reproduction of previously captured NWS source bytes. Coverage remains nine venues and was not inflated with rejected matches.

Alternative-source exploration found an operator-provided Gillette Google Maps link, but the accessible link contains a place-name query rather than a verifiable point. The [federal Major Sport Venues catalog](https://catalog.data.gov/dataset/major-sport-venues) describes a public historical dataset last updated in 2022, without a directly exposed download on the viewed catalog page. Neither was treated as verified current coordinates. Next work requires a traceable venue map point or public GIS geometry reconciled to the current physical stadium; a historic stadium name alone is insufficient for relocations.
