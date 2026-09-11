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

The development refresh workflow now retains total explanations after new
forecast replay, and preserves the artifact/archive in Git and recovery output.
Both publication paths run a separate verifier before publishing. It restores
the linked input manifest, requires the current edition identity, reproduces
the explanations and checks exact displayed terms. Raw floating-point terms
allow only 1e-9 numerical variation; displayed values have no tolerance.

The real artifact passed this verifier. Tamper tests, both builder tests and
all 33 publication tests passed locally. The previous hosted CI run failed
because new tests read working inputs rather than the exact archived bundle;
CI preparation fetches source inputs. Tests now restore their linked archive
into a temporary directory. Hosted verification of that fix remains pending.

The builder targets newly generated forecasts, matching the release replay
scope. Earlier unsupported snapshots remain explicitly unavailable in the UI.
Actual scheduled operation and broader device review remain pending. No hosted
deployment was performed.

Empty-edition follow-up: the builder now compares the exact new-forecast ID set
with replay results. A verified edition with no new forecasts yields an empty
explanation set; omitted explanations for actual new forecasts still fail.
Three builder tests passed, including this empty case. UI selection tests use a
fixed archived explanation sample so a legitimate empty future edition does not
invalidate historical regression coverage. Empty record sets are withheld.
TypeScript checks passed, and the current 15-record artifact was rebuilt under
the updated explanation code identity. Hosted CI was still running at this
checkpoint.
