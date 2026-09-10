import { test } from "node:test";
import assert from "node:assert/strict";
import { renderToStaticMarkup } from "react-dom/server";
import Performance from "../src/app/performance/page";
import { site } from "../src/lib/data";

test("ties-only live record exposes score errors without claiming there are no completed forecasts", () => {
  const original = site.livePerformance;
  try {
    site.livePerformance = {
      ...original,
      games: 0,
      wins: 0,
      ties: 1,
      missed: 0,
      brier: null,
      logLoss: null,
      scoreGames: 1,
      marginMae: 3,
      totalMae: 5,
      marginIntervalCoverage: 1,
      totalIntervalCoverage: null,
      marginIntervalGames: 1,
      totalIntervalGames: 0,
      records: [],
      scoreRecords: [
        {
          gameId: "2026_01_A_B",
          snapshotHash: "a".repeat(64),
          generatedAt: "2026-09-10T10:00:00Z",
          homeMargin: 3,
          total: 45,
          actualMargin: 0,
          actualTotal: 40,
          marginError: 3,
          totalError: 5,
          marginCovered80: true,
          totalCovered80: null,
        },
      ],
    };
    const html = renderToStaticMarkup(Performance());
    assert.match(html, /No decisive results yet/);
    assert.doesNotMatch(html, /No completed forecasts with verified/);
    assert.match(html, /3.00 points/);
    assert.match(html, /5.00 points/);
    assert.match(html, new RegExp("a".repeat(64)));
    assert.match(html, /href="\/games\/2026_01_A_B"/);
    site.livePerformance = {
      ...site.livePerformance,
      scoreGames: 0,
      ties: 0,
      scoreRecords: [],
    };
    assert.match(
      renderToStaticMarkup(Performance()),
      /No completed forecasts with verified/,
    );
  } finally {
    site.livePerformance = original;
  }
});
