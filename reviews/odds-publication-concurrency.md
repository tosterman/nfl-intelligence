# Odds publication ordering

The old publisher unconditionally replaced `odds/latest.json`. A delayed older acquisition could therefore become the public latest snapshot after a newer collector finished. A regression test reproduced this before the change.

The publisher now reads the pointer and its ETag together directly from origin. Existing pointers advance only through an `ifMatch` conditional write; absent pointers use create-only writes. Older acquisitions and equal-time conflicting content are rejected. An exact retry after a committed write succeeds without rewriting the pointer. The immutable archive is still written before the pointer, preserving recovery after interrupted publication.

Verification on September 10, 2026:

- All 70 application tests and TypeScript checking pass. Storage tests cover racing initial creation, racing existing updates, older acquisition retries, equal-time conflicts and a lost response after a committed pointer write.
- An independent code review found no material defect and independently passed all 14 collector/storage tests.
- A real isolated object in the configured private Blob store verified conditional replacement, rejection of a stale ETag, rejection of duplicate create-only writes, and unchanged content after those rejections. The verification object was removed with its current ETag. No production odds pointer was changed and no paid Odds API request was made.

This change is on the development branch pending a validated production release after hosting capacity recovers. It does not deduplicate concurrent provider requests or impose a monthly credit budget. A losing writer can retain an unused immutable archive and report failure even when the winning newer snapshot is healthy. Those are explicit remaining operational considerations.

Provider contract: [Vercel Blob conditional writes](https://vercel.com/docs/vercel-blob). The installed SDK version also exposes `ifMatch` and the ETag on `get()` results.
