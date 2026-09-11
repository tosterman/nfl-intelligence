# Inside-20 outcome reconciliation

The retained season now yields 5,998 groups with identifiable offensive
possession evidence. Of these, 1,824 have a pre-snap position strictly inside
the opponent's 20; 1,046 end in an offensive touchdown. All outcome checks pass
against the source's drive-result classification. The other 48 fixed-drive
groups have no qualifying owned possession rows, rather than being counted as
failed offensive possessions. These are exploratory totals, not published rates.

The helper counts a possession once even if it enters, retreats and later scores
from outside the 20. It distinguishes touchdowns by the offense from defensive
returns. Punt-return and blocked-punt touchdowns initially caused 17 outcome
mismatches; retaining the terminal punt reconciles those results without adding
an offensive touchdown. All 6,046 groups still match the source inside-20 flag.

Five outcome regressions cover repeated visits, defensive returns, punt returns,
the exact 20-yard boundary, conversion exclusion and inconsistent scoring.
Together with phase tests, all 11 targeted checks pass.

An independent factual sample matches the [official Bengals–Vikings gamebook](https://static.www.nfl.com/image/upload/v1758541357/gamecenter/f665f7cb-311e-11f0-b670-ae1250fadad1.pdf):
Cincinnati 1 touchdown from 1 red-zone possession, Minnesota 4 from 5. This single
game does not validate all league totals. A publication builder still needs
completed-game schedule matching, strict historical cutoffs, sample/coverage
validation and documented boundary conventions before UI integration.
