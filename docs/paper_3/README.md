# Paper 3 — Armenian historical transitions and frozen astronomical conditions

## Status

Reanalysis completed against an independently reconstructed and frozen Armenian historical master register.

This directory contains the publication-facing reproducibility materials for the Armenian confirmatory test. Historical inclusion was frozen before the astronomical reanalysis, and the historical dataset was not repaired after inspection of astronomical matches.

## Principal result

The principal directional test is:

`STATE_NEGATIVE_NARROW_PRIMARY × H1`

with the narrow negative definition:

`COLLAPSE + SOVEREIGNTY_LOSS`

Observed result:

- N = 8
- H1 matches = 0
- circular-shift null mean ≈ 1.041
- enrichment p = 1.000

The broader all-primary state test produced 1/26 H1 matches (null mean ≈ 3.383; p ≈ 0.9486), and the clustered robustness version produced 0/22.

## Correct historical rule for 7–9 and 3–6

The historical H2/H3 test is a **direct exact-day coincidence test**:

- H2 = corrected 7–9 roots.
- H3 = corrected 3–6 roots.
- A historical match occurs only when the astronomical root calendar day is the same calendar day as an independently sourced historical event with an exact day.
- H1 membership is not required.
- No ±day tolerance is allowed.

Using the frozen Armenian master:

- eligible exact-day historical events = 9
- 7–9 direct same-day matches = 0/9
- 3–6 direct same-day matches = 0/9

The earlier assistant-side reinterpretation of H2/H3 as a historical year-overlap test is superseded by `H2_H3_DIRECT_HISTORICAL_DAY_RULE_CORRECTION_V2.md`.

## Files

### Historical inputs
- `../../data/paper_3/Armenian_Historical_Master_Analysis_Eligible.csv`
- `../../data/paper_3/Historical_Core_Freeze_Manifest.json`
- `../../data/paper_3/Historical_Gaps.csv`

### Frozen astronomical catalogues
- `../../data/paper_3/H1_Episodes_Frozen.csv`
- `../../data/paper_3/H2_7-9_Roots_Frozen.csv`
- `../../data/paper_3/H3_3-6_Roots_Frozen.csv`
- `../../data/paper_3/H4_Exact_Overlaps_Frozen.csv`

### Protocol and results
- `ASTRONOMY_REANALYSIS_PRECOMMIT_V1.md`
- `H2_H3_DIRECT_HISTORICAL_DAY_RULE_CORRECTION_V2.md`
- `H2_H3_DIRECT_SAME_DAY_SUMMARY.csv`
- `TIGRAN_II_ACCESSION_H1_DIAGNOSTIC.csv`
- `EXPECTED_RESULTS.json`

### Reproduction script
Run from the repository root:

```bash
python code/paper_3_reanalysis.py
```

## Interpretation

The initially striking astronomical–historical pattern did not reproduce as an enriched signal after independent historical reconstruction, freezing, and confirmatory testing. The result is therefore reported as a robust negative finding under the frozen historical and astronomical definitions, while individual visually striking coincidences remain valid as descriptive observations rather than evidence of a stable underlying signal.
