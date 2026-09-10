import { test } from "node:test";
import assert from "node:assert/strict";
import { assessFreshness, freshnessInputs } from "../src/lib/freshness";
const now = Date.parse("2026-09-10T12:00:00Z");
test("fresh generation cannot hide stale cached source", () => {
  const result = assessFreshness(
    [
      { name: "Model edition", retrievedAt: "2026-09-10T12:00:00Z" },
      { name: "Results", retrievedAt: "2026-09-08T12:00:00Z" },
    ],
    now,
  );
  assert.equal(result.status, "stale");
  assert.equal(result.checks[1].ageHours, 48);
});
test("missing, malformed and future timestamps fail closed", () => {
  for (const retrievedAt of [undefined, "invalid", "2026-09-11T12:00:00Z"])
    assert.equal(
      assessFreshness([{ name: "Input", retrievedAt }], now).checks[0].status,
      "invalid",
    );
  assert.equal(assessFreshness([], now).status, "stale");
});
test("unrounded age controls the 30-hour boundary", () => {
  assert.equal(
    assessFreshness(
      [{ name: "Input", retrievedAt: "2026-09-09T06:00:00Z" }],
      now,
    ).status,
    "ok",
  );
  assert.equal(
    assessFreshness(
      [{ name: "Input", retrievedAt: "2026-09-09T05:59:59Z" }],
      now,
    ).status,
    "stale",
  );
});
test("both recent efficiency seasons are required; frozen older seasons are excluded", () => {
  const inputs = freshnessInputs({
    season: 2026,
    generatedAt: "2026-09-10T12:00:00Z",
    source: { retrievedAt: "2026-09-10T12:00:00Z" },
    efficiencySources: [
      { season: 2010, retrievedAt: "2020-01-01" },
      { season: 2026, retrievedAt: "2026-09-10T12:00:00Z" },
    ],
  });
  assert.equal(inputs.length, 4);
  assert.equal(assessFreshness(inputs, now).status, "stale");
  assert.equal(
    inputs.some((i) => i.name.includes("2010")),
    false,
  );
});
