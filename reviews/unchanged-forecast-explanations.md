# Real refresh and retained explanations — September 11, 2026

The 16:17 UTC real-data refresh picked up SF–LA's final result. It added no
forecast snapshots: unchanged predictions preserve their original identity.
The ledger remains at 120 snapshots, and the strict prospective record has zero
eligible games and two missed games. See first-result-eligibility.md.

This exposed a product regression: the current explanation artifact contained
only newly generated forecasts, so an unchanged refresh erased the displayed
total breakdown. The artifact now keeps native records separate from 15
retained records. Each retained entry contains its original artifact and input
manifest identities, original model/explanation provenance, and exact record.
The original native artifact must match its digest and replay from its restored
input bundle. References to other retained records are never followed.

Publication verification recomputes selected coverage and origin provenance.
Missing or unsupported historical evidence stays unavailable. Conflicting
displayed terms fail; raw-only differences use the existing 1e-9 replay tolerance.
Independent code review identified that tolerance requirement and it was fixed.

Validation: 185 application tests and ten focused Python tests passed; production
build generated 319 pages. Twelve Chromium/WebKit checks at 320, 390 and 1280px
verified upcoming PIT and completed SF–LA breakdowns, keyboard disclosure,
displayed arithmetic, overflow and scoped axe checks. The source-comparison test
now locates the retained unchanged pair rather than assuming the latest pair is
unchanged. The missing-new-forecast test uses an explicit new-forecast fixture.

The final site bytes use Git's LF line endings before archive retention, so the
edition identity survives checkout. These are local/development results, not a
public deployment or prospective predictive-success claim.

Follow-up: an isolated `git archive HEAD` checkout also passed the current
explanation verifier. CI now runs that verifier before preparing test fixtures,
so it checks the committed current edition in addition to historical replay.

A 390px Chromium readback of the refreshed SF–LA page showed the final 27–7
score separately from the saved pregame estimates and probabilities. The
performance page showed two excluded completed games, zero eligible results,
and the missing-context/publication explanation. No retrospective result was
silently added to the verified pregame record.
