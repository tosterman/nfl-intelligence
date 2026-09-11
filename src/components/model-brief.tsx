import React from 'react';
import type { Prediction } from '../lib/types';

export function ModelBrief({ prediction, home, away }: { prediction: Prediction; home: string; away: string }) {
  const factors = prediction.contributions;
  const sum = factors.reduce((value, factor) => value + factor.points, 0);
  const valid = Number.isFinite(prediction.homeMargin) && factors.every(f => Number.isFinite(f.points)) &&
    Math.abs(sum - prediction.homeMargin) <= (factors.length + 1) * 0.0005 + 1e-9;
  if (!valid) return <p>The contribution breakdown could not be reconciled to this forecast.</p>;
  const direction = Math.sign(prediction.homeMargin);
  const ranked = [...factors].filter(f => Math.abs(f.points) >= 0.05).sort((a, b) => Math.abs(b.points) - Math.abs(a.points));
  const lead = ranked.find(f => Math.sign(f.points) === direction);
  const counter = ranked.find(f => Math.sign(f.points) === -direction);
  const describe = (factor: typeof factors[number]) => `${factor.name} adds ${Math.abs(factor.points).toFixed(1)} points toward ${factor.points > 0 ? home : away}.`;
  return <div className="model-brief">
    {lead ? <p><strong>Leading advantage. </strong>{describe(lead)}</p> : <p>No single directional advantage stands out at the displayed precision.</p>}
    {counter && <p><strong>Strongest counterweight. </strong>{describe(counter)}</p>}
    <p className="fine">These are model contributions to the expected margin, not player-specific findings. <a href="#model-contributions">See every contribution</a>.</p>
  </div>;
}
