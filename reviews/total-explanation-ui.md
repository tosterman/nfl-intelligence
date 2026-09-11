# Total explanation UI

Game pages now show a separate “Why this total?” section. The default text
describes the combined fitted intercepts and net team/venue adjustment. An
expandable table shows every weighted term and explicit rounding reconciliation.
The efficiency intercept is not represented as the league scoring average, and
the text distinguishes model accounting from causal effects.

Selection requires the exact snapshot hash, game ID, model code hash and saved
total; finite unique terms must reconcile. Unsupported snapshots show an
unavailable message. The data stays in a server component; the runtime release
file list includes it. This is a display guard over verified generated data,
not cryptographic verification of arbitrary browser-supplied records.

TypeScript checking and current-snapshot selection/tamper tests passed. A real
390px Chromium visit to ATL/PIT opened the table and verified 44.770, with no
horizontal overflow. The expanded screenshot was visually reviewed. The default
collapsed state avoids placing the full 20-row accounting table in the normal
reading path.

Scheduled explanation refresh, prepublication verification and broader device
review remain pending. No hosted deployment was performed.
