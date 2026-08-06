# Changelog

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
