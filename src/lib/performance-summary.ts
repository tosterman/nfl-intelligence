type MarginComparison = {
  marketGames: number;
  matchedModelMarginMae: number | null;
  marketMarginMae: number | null;
};

export function marginComparisonSummary(metrics: MarginComparison): string {
  const { marketGames, matchedModelMarginMae: model, marketMarginMae: market } = metrics;
  if (!Number.isInteger(marketGames) || marketGames <= 0 ||
      typeof model !== "number" || !Number.isFinite(model) || model < 0 ||
      typeof market !== "number" || !Number.isFinite(market) || market < 0) {
    return "A matched-game margin comparison is unavailable for this edition.";
  }
  const modelDisplayed = Number(model.toFixed(2));
  const marketDisplayed = Number(market.toFixed(2));
  const sample = `Across ${marketGames} historical games with closing spread lines`;
  if (modelDisplayed === marketDisplayed) {
    return `${sample}, model and market margin errors are equal at the displayed precision.`;
  }
  const better = modelDisplayed < marketDisplayed ? "the model" : "the closing market";
  return `${sample}, ${better} has the lower average margin error in this retrospective sample.`;
}
