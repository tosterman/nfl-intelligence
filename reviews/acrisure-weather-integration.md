# Acrisure weather integration

The registry now uses `confirmed-official-linked-place` for Acrisure. This is distinct from OSM address-tag reconciliation. Before collection, the validator verifies retained OSM/NWS response bytes, the reviewed official-linked-place candidate, registry-to-evidence identity, the precise derived midpoint, address and map attribution. Any address tags on this fallback feature require separate reconciliation. The nested candidate receipt records the earlier observation; its candidate-only status describes that observation, not the later registry decision.

The production weather collector was run locally after integration. The September 10, 2026 refresh produced eight available game records, including `2026_01_ATL_PIT`, and retained response bytes and ledger entries. The stadium registry now covers 19 US locations. This does not change model predictions, assert field-level conditions or relax neutral-game withholding. Freshness and kickoff-hour coverage remain separate checks.

Verification: five linked-place tests, eight venue/acquisition tests and seven weather tests passed, including source-byte reproduction after refresh; TypeScript checking passed. Independent code review found no material integration gap. Chromium and WebKit at 320px showed the real Falcons–Steelers weather panel with OSM attribution and the official-linked-place limitation, without horizontal document overflow. Browser observations are in `acrisure-weather-browser.json`.

This is development-branch evidence, not a deployment receipt. Vercel publication remains pending. Earlier reports stating 18 locations and seven available games describe their earlier snapshots.
