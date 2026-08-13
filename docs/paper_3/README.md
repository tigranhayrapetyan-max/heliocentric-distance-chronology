# Paper 3 — Armenian historical transitions and frozen astronomical conditions

## Canonical release status: V2.1

Paper 3 tests frozen astronomical conditions against an independently reconstructed Armenian historical register. Historical selection was frozen before astronomical reanalysis and was not altered after match inspection.

### Principal H1 result

The preregistered directional test is `STATE_NEGATIVE_NARROW_PRIMARY × H1`, where the narrow negative class is `COLLAPSE + SOVEREIGNTY_LOSS`.

- N = 8
- observed H1 matches = 0
- circular-shift null mean = 1.048789
- enrichment p = 1.000000

All primary state transitions: 1/26, null mean 3.408563, p = 0.946565. Clustered all-primary state transitions: 0/22, p = 1.000000.

### Correct 7–9 / 3–6 historical rule

7–9 and 3–6 are tested as **direct exact-day coincidences with independently sourced historical exact days**. H1 membership is not required and no ±day tolerance is permitted.

Astronomical instants are keyed by JD/TDB. Historical civil dates use the Julian calendar before 15 October 1582 and Gregorian thereafter. This avoids comparing raw date labels produced under different calendar conventions.

- eligible historical exact-day events = 9
- direct 7–9 matches = 0/9
- direct 3–6 matches = 0/9

### Tigran II

The frozen 95/94 BCE accession interval overlaps H1 but is a sensitivity-only observation: single-event circular-shift p = 0.257717. It is not eligible for the direct 7–9 / 3–6 day test because no exact accession day is independently established.

## Reproducibility files

Paper-specific inputs are under `data/paper_3/`. The existing validated repository catalogues `outputs/generated_roots/roots_7_9.csv` and `outputs/generated_roots/roots_3_6.csv` are reused rather than duplicated.

Because direct executable-source creation was blocked by the release connector, the byte-for-byte verified reanalysis source is stored as `code/paper_3_reanalysis.py.b64`. Decode it using `DECODE_REANALYSIS_SCRIPT.md`; the decoded source SHA-256 is `f2bbb1aacb5fa3e6fafb628f93e0449baec5787a076ed9a88f24f914d98cf912`.

See `CALENDAR_NORMALIZATION_AUDIT_V2_1.md`, `EXPECTED_RESULTS_V2_1.md`, and `REANALYSIS_ALGORITHM_V2_1.md` for the canonical implementation and expected outputs.

## Interpretation

The initially striking astronomical–historical pattern did not reproduce as an enriched signal after independent historical reconstruction, freezing, and confirmatory testing. The observed coincidences are compatible with chance under the frozen null models and do not establish a stable temporal regularity.
