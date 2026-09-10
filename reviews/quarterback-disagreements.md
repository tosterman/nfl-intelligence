# What the quarterback disagreements mean

The retained 2025 sample points to uncertainty about which listed quarterback will play, rather than missing player IDs in comparable charts. This is a source-quality diagnosis, not evidence for a better forecast.

| Cutoff | Matching first-listed QB | Game QB listed lower | Missing/stale chart | Total team-games |
| --- | ---: | ---: | ---: | ---: |
| 24 hours before kickoff | 495 | 47 | 28 | 570 |
| Immediately before kickoff | 517 | 49 | 4 | 570 |

All 47 disagreements at 24 hours had the schedule's recorded game QB in the same selected depth chart: 46 at rank two and one at rank three. At kickoff, all 49 disagreements likewise had that ID listed: 47 at rank two and two at rank three. None of the comparable disagreements involved an ID absent from the chart. This does not resolve the separate personnel-registry identity conflict documented elsewhere.

Of the original 47 disagreements, 46 persisted and one became a match at kickoff. Of 28 unavailable charts at 24 hours, 25 became matches and three became disagreements. Four previously matching charts expired. These paired transitions explain why later observations increased coverage without materially changing agreement among comparable charts. They do not establish that a particular polling frequency causes better predictions.

## Consequence for development

Keep the production model unchanged. The existing quarterback residual experiment improved development-sample margin MAE by only 0.0588 points, with an uncertainty interval crossing zero. This additional look at the same season is not a new evaluation set.

The next useful acquisition is a timestamped, attributable starter-confirmation signal with retained original evidence and player-ID reconciliation. Capture when the project first observed it as well as any source publication time. Explicitly retain conflicting reports and unknown status. A depth-chart rank by itself cannot supply calibrated probabilities for the alternatives.

Before testing a numerical adjustment, freeze its feature definition, fallback, cutoff, and evaluation criteria. Evaluate on separately declared future observations or broader chronological seasons. Do not substitute the eventual recorded game QB into a pregame prediction. If scenarios are displayed before calibrated probabilities exist, describe them as conditional alternatives and do not combine them into a purported expected advantage.

## Reproduction and limits

Run `python scripts/audit_quarterback_disagreements.py` with the retained depth-chart source. The script checks the source against the original role audit, reconstructs every selected snapshot using the existing freshness and rank-validation logic, and reproduces all 1,140 role classifications before reporting rank membership. It rejects duplicate observations and unpaired cutoffs. The JSON retains all observations, selected QB lists, paired transitions, input hashes, and code hashes.

The original role audit supplies the latest-snapshot selection and retrospective schedule labels. This downstream analysis independently reconstructs the selected chart, but does not reselect the latest chart from the entire timeline. The original audit and its source-quality limitations remain part of the evidence chain.

The schedule's game QB field is not a snap-share ledger or proof of an official starter announcement. Historical provider files acquired now can include corrections. A lower-listed recorded game QB therefore does not, by itself, identify injury, benching, rest, or in-game replacement as the cause. No such causes are inferred here. No source requests, provider credits, or production forecast changes were required for this analysis.

An independent automated code review reproduced all 1,140 observations, summaries, transitions, and hashes without rewriting the output, and found no material issue. The consolidated branch also passed 208 Python tests and 87 application tests. These checks establish internal consistency, not independent expert endorsement or predictive performance.
