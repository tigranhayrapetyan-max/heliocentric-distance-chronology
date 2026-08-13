# Calendar-normalized implementation audit — V2.1

## Why this audit was required

Before the Paper 3 GitHub release, the same physical 3–6 / 7–9 root was observed to have different calendar labels in two files while retaining the same Julian date (JD/TDB). The difference is a calendar-convention representation issue, not an astronomical discrepancy.

Because Paper 3 uses exact historical-day coincidence for 7–9 and 3–6, raw calendar strings must not be compared across different calendar conventions.

## Frozen implementation rule

1. Astronomical instants are identified by **JD/TDB**.
2. Historical exact dates are converted to civil-day JD intervals using the mixed historical calendar convention: **Julian before 15 October 1582 and Gregorian from 15 October 1582 onward**.
3. A direct H2/H3 historical-day match exists only when the exact astronomical root JD falls inside the exact historical civil day. There is **no ±day tolerance** and **no H1 requirement**.
4. H1 year exposure is derived from the physical refined H1 start/end JDs using the same mixed calendar convention. It is not derived by parsing a potentially proleptic-Gregorian display string.
5. The historical register itself is unchanged; this is an implementation normalization only.

## Audit outcome

The calendar normalization does **not change any observed Paper 3 conclusion**:

- narrow negative primary state transitions × H1: **0/8**;
- all primary state transitions × H1: **1/26**;
- clustered all-primary state transitions × H1: **0/22**;
- direct 7–9 same-day historical matches: **0/9**;
- direct 3–6 same-day historical matches: **0/9**.

It changes only small null-distribution quantities because a small number of H1 episodes near civil-year boundaries map to different year labels under proleptic-Gregorian versus mixed Julian/Gregorian representation.

Updated mixed-calendar enrichment values:

- `STATE_NEGATIVE_NARROW_PRIMARY × H1`: p = **1.000000**; null mean = **1.048789**.
- `STATE_ANY_PRIMARY × H1`: p = **0.946565**; null mean = **3.408563**.
- clustered `STATE_ANY_PRIMARY × H1`: p = **1.000000**; null mean = **2.884169**.
- `STATE_POSITIVE_PRIMARY × H1`: p = **1.000000**; null mean = **1.442084**.
- `STATE_ANY_ALL_ELIGIBLE × H1`: p = **0.775473**; null mean = **4.296714**.
- `ACCESSION_PRIMARY × H1`: p = **0.902257**; null mean = **6.161633**.
- `ACCESSION_ALL_ELIGIBLE × H1`: p = **0.830070**; null mean = **11.335048**.
- Tigran II 95/94 BCE sensitivity interval: single-event shift p = **0.257717**.

Historical master SHA-256: `402766d4dd060eea0daec7debe01857db66eb638898cd761e7c4168e7ed18d00`
Astronomical master workbook SHA-256: `a309f2eaa9dec3ec92dd69a26801f7add6131f4002c856203fd10a8243f09d91`
