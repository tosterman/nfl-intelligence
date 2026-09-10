# Personnel source chronology

On September 10, the live five-feed probe passed at 19:20:26 UTC. Inspection nevertheless found a defensive validation gap: the personnel API, game display, Python game helper and external health monitor accepted a source timestamp later than its acquisition, provided both timestamps were independently fresh. The collector already rejects this chronology during acquisition; downstream consumers now enforce the same invariant if supplied inconsistent data.

Regression fixtures first reproduced false health and exposed rows, then passed after adding `assetUpdatedAt <= retrievedAt` to each consumer. The Python helper also now expires exactly at thirty hours, matching the public display and health checks. Equal source/acquisition times remain allowed. Collection `checkedAt` records the start of acquisition, so it is intentionally not required to follow retrieval.

Validation: five TypeScript personnel tests, ten Python personnel tests and seven external health tests passed. The production build passed. This fixes a reproducible validation gap; it is not evidence that the current live snapshot was corrupt.

The GitHub health workflow is active, but the inspected run history contains only manual dispatches. Successful manual probes do not establish that scheduled execution or notification delivery is reliable.
