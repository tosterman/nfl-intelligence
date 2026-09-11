# Additional venue coverage

On September 11, 2026 UTC, four official stadium addresses were checked against the Census geocoder. Official sources and full returned records are in `additional-venue-geocodes.json`; each response is retained by raw-byte SHA-256 in `data/weather-location-sources`.

Lucas Oil Stadium's official guest-services address, 500 South Capitol Avenue, Indianapolis, IN 46225, produced one exact normalized street/locality/state match. The existing venue validator accepted it; NWS confirmed Indiana grid IND/58,69. The real collector produced kickoff-hour context for Ravens–Colts (`2026_01_BAL_IND`).

SoFi Stadium, Allegiant Stadium and U.S. Bank Stadium returned no Census matches for their cited official addresses. Their registry records remain unavailable without coordinates. This establishes the next needed step: independently reconciled map geometry or other authoritative location evidence. No fuzzy match or guessed point was accepted.

The refreshed local edition has ten available weather games and 21 verified US venue locations. Weather remains outdoor area context, with no numerical forecast adjustment or inference about roof state or conditions on the field. Previous weather ledger entries and numerical forecast artifacts were preserved.

Validation: seven venue-evidence and seven weather tests passed, including a new check binding every retained Census response to its hash, requested address and recorded match list. Chromium and WebKit at 320px showed the Colts game's actual forecast, correct NWS link and expanded outdoor-area limitation with no page errors or overflow; see `lucas-oil-weather-browser.json`.

The prior expiry commit passed hosted run 34546562368. The Ford Field commit's hosted run 34546708946 was still running at this checkpoint. These new changes are development work, not a public deployment receipt.
