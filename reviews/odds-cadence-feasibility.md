# Kickoff-aware odds cadence: offline experiment

The first prospective closing audit exposed missing recent captures. Adding 29 kickoff requests to the existing 155-call baseline would exceed the budget. This experiment instead redistributes baseline requests around the retained schedule's kickoff windows.

`scripts/plan_odds_cadence.py` groups only intersecting acquisition windows from fifteen to five minutes before kickoff, selects times backwards while respecting a thirty-minute cooldown, then fills gaps with ordinary refreshes. It targets at most 5.5 hours between requests, leaving a nominal half-hour before the six-hour display limit. No provider request, scheduled job or production behavior is created by this script.

For the real retained 31-day schedule beginning September 11 at 00:40 UTC, the candidate uses 153 requests and nominally covers all 29 distinct kickoff groups. Planned consecutive gaps range from 30 to 323.75 minutes. The full request list and source hash are in `odds-cadence-feasibility.json`. Three tests check shared windows, rejection of conflicting windows and continued refresh when no games occur. The initial implementation unnecessarily required a request at the horizon endpoint; that artificial constraint was removed while preserving coverage through the horizon.

This is not ready to activate. Only two attempts remain under the 155-attempt budget in a hypothetical empty-budget start. Existing rolling usage, manual calls and retries reduce capacity. Exact thirty-minute spacing has no cooldown margin if the first request runs late. The latest planned acquisitions have only five minutes before kickoff. Actual bookmaker updates can still be stale even when acquisition is on time. No optimality or guaranteed coverage claim follows from this calculation.

Next evaluation should account for actual prior attempts, delayed execution and retries, then compare robust coverage against freshness and budget constraints. The published closing-window protocol and live collection configuration remain unchanged.
