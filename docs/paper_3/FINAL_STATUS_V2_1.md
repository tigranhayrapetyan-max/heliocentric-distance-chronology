# Paper 3 final implementation status — V2.1

Canonical implementation for release uses physical JD/TDB normalization.

Historical exact-day matching for 7–9 and 3–6 is a direct same-day test: the astronomical root must fall inside the exact historical civil day. H1 membership is not required and no ±day tolerance is allowed.

Civil calendar conversion is Julian before 15 October 1582 and Gregorian from 15 October 1582 onward. H1 exposure years are likewise derived from refined H1 JD intervals under this mixed-calendar convention rather than from display strings.

Canonical results: negative primary state × H1 = 0/8, p=1.000000; all primary state × H1 = 1/26, p=0.946565; clustered all-primary state = 0/22, p=1.000000; 7–9 direct same-day = 0/9; 3–6 direct same-day = 0/9. Tigran II remains a sensitivity-only H1 overlap with single-event shift p=0.257717.

See `CALENDAR_NORMALIZATION_AUDIT_V2_1.md` and `EXPECTED_RESULTS_V2_1.md`.
