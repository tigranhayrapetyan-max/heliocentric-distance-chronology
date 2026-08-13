# Changelog

## [1.1.0] — Paper 2 / Paper 3 Reproducibility Release

### Added
- reproducibility-facing materials for Paper 2, including the finalized submission manifest and Supplementary Table S1 provenance data;
- independently frozen Armenian historical analysis input for Paper 3;
- mixed-calendar H1 exposure-year derivative based on refined JD/TDB intervals;
- explicit direct exact-day historical matching rule for corrected 7–9 and 3–6 roots;
- calendar-normalization audit distinguishing physical JD/TDB instants from display-calendar labels;
- Paper 3 precommit, expected results, deterministic cluster robustness documentation, and reanalysis algorithm;
- byte-for-byte verified Paper 3 reanalysis source stored as Base64 with decoding instructions.

### Verified
- principal Paper 3 negative-state H1 test: 0/8, enrichment p = 1.000000;
- all-primary state H1 test: 1/26, enrichment p = 0.946565;
- clustered all-primary state H1 test: 0/22, enrichment p = 1.000000;
- direct 7–9 historical exact-day matches: 0/9;
- direct 3–6 historical exact-day matches: 0/9;
- Tigran II accession remains a sensitivity-only H1 overlap, single-event p = 0.257717.

### Methodological clarification
- historical exact-day comparisons are performed by physical JD/TDB overlap with mixed civil-calendar conversion (Julian before 15 October 1582; Gregorian thereafter), not by comparing raw date strings;
- the calendar normalization changes small null-distribution quantities but does not change any observed Paper 3 conclusion;
- historical selection remained frozen and was not repaired after astronomical inspection.

## [1.0.0] — Clean-Room Validation Release

### Added
- clean-room JPL Horizons reconstruction workflow;
- reproducibility, provenance, control-case, and catalogue-comparison materials;
- configuration architecture separating validated baselines from experiments;
- targeted 0940 CE high-resolution refinement procedure;
- project philosophy, repository constitution, and human–AI collaboration statement.

### Fixed
- perihelion-boundary discontinuities that produced false 1–8 roots;
- hidden double crossings within same-sign coarse intervals;
- incorrect propagation of `residual_km` metadata.

### Validated
- 1–8 catalogue count: 7,863 events;
- 3–6 catalogue count: 447 events;
- 7–9 catalogue count: 42 events;
- 139 BCE control case;
- the single 0940 CE legacy timestamp discrepancy.
