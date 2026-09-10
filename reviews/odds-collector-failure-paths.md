# Odds collector failure-path verification

The production collector now delegates to an explicitly supplied dependency boundary so the complete acquisition, retry and readback path can be exercised without network requests, environment-secret mutation or production Blob writes. The production wrapper retains the same environment key, private-store functions, fetch implementation and system clock. API authentication and schedule are unchanged.

Five collector tests pass, including three new multi-stage checks:

- Two failed writes followed by successful publication make exactly one provider acquisition, then verify the archive hash on readback. A second call within the reuse window performs no further acquisition.
- Persistent storage failure stops after three publication attempts and still makes only one provider request. An HTTP 429 stops before publication without retrying acquisition.
- Failure to read existing storage prevents provider acquisition. A fresh but different readback snapshot fails rather than reporting capture success.

The existing bearer-secret and thirty-minute reuse boundary checks remain. These are deterministic isolated failure drills, not proof of recovery from a real provider outage. No odds credits were consumed by the tests. Provider credit counts are currently returned from the acquisition response; there is no durable account-wide budget ledger or atomic distributed collection lock. Separate concurrent invocations could still acquire independently, so the existing serialized GitHub workflow remains important. No hard monthly spending cap or guaranteed quota sufficiency is claimed.
