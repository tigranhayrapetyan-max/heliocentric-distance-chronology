# Validation report — v0.9.0 release candidate

## Disclosed catalogue

| Condition | Count |
|---|---:|
| 1-8 | 7,863 |
| 3-6 | 447 |
| 7-9 | 42 |

## Discovery-stage circular-shift reproduction

- Compact-window threshold: 30 days
- Lag rule: 240–300 days
- Compact 7-9 centers: 2
- Compact 3-6 centers: 11
- Observed qualifying pairs: 1
- Permitted shift-days: 3,491.768437586
- Temporal span: 2,171,669.213483796 days
- Conditional shift proportion: 0.0016078730664439102
- Monte Carlo: 1,649 / 1,000,000 = 0.001649
- Seed: 20260804

The original workbook-based script and the independent CSV-based script reproduced the same deterministic result and fixed-seed Monte Carlo result. Deterministic threshold-sensitivity results also agree.

These values are conditional, unadjusted discovery-stage statistics. They are not global multiplicity-corrected significance levels.

## Offline software tests

Five tests passed: J2000 conversion, BCE calendar round-trip, astronomical-date parsing, interval merging, and synthetic root-generation logic.

## Pending astronomical validation

The NASA/JPL Horizons root generator was not network-tested in the build environment because external DNS access was unavailable. The 139 BCE control case, full catalogue regeneration, and root-by-root comparison remain required before v1.0.0.
