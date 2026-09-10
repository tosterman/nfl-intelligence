import { test } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { LiveCalibration } from "../src/components/live-calibration";
test("live calibration distinguishes empty evidence from observed zero wins", () => {
  const empty = renderToStaticMarkup(
    createElement(LiveCalibration, { bins: [] }),
  );
  assert.match(empty, /Awaiting eligible decisive results/);
  assert.doesNotMatch(empty, /<table/);
  const observed = renderToStaticMarkup(
    createElement(LiveCalibration, {
      bins: [
        {
          lower: 0.6,
          upper: 0.7,
          count: 1,
          predicted: 0.6,
          observed: 0,
          observedLow95: 0,
          observedHigh95: 0.7934567,
        },
      ],
    }),
  );
  assert.match(observed, /<td>0.0%<\/td>/);
  assert.match(observed, /0.0%–79.3%/);
  assert.match(observed, /scope="col"/);
  assert.match(observed, /tabindex="0"/);
  assert.doesNotMatch(observed, /Awaiting eligible decisive results/);
});
