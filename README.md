# Heliocentric Distance Chronology

## v1.1.0 — Paper 2 / Paper 3 Reproducibility Release

A clean-room, independently validated, and reproducible scientific platform for reconstructing and analysing heliocentric-distance chronologies from JPL Horizons ephemerides.

> Every scientific result should be reproducible, transparent, and honestly reported.

Version 1.1.0 preserves the validated v1.0.0 astronomical baseline and adds publication-facing reproducibility materials for Paper 2 and the independently frozen Armenian confirmatory tests for Paper 3.

## Validated astronomical baseline

- 1–8: 7,863 events.
- 3–6: 447 events.
- 7–9: 42 events.
- The 139 BCE control case passed.
- A targeted high-resolution refinement documented one legacy 0940 CE timestamp offset without changing event identity or catalogue count.

## Paper 2

The `docs/paper_2` directory contains public provenance and supplementary materials associated with the post-Flood genealogy study. Unpublished manuscript files are intentionally not mirrored in the public repository before publication.

## Paper 3

The `docs/paper_3` and `data/paper_3` directories contain the independently frozen Armenian historical-test materials. The canonical V2.1 implementation uses physical JD/TDB instants and a mixed historical civil calendar: Julian before 15 October 1582 and Gregorian thereafter.

Corrected 7–9 and 3–6 historical tests are direct exact-day coincidence tests. H1 membership is not required and no plus/minus-day tolerance is permitted.

Canonical results:

- negative primary state transitions × H1: 0/8, enrichment p = 1.000000;
- all primary state transitions × H1: 1/26, p = 0.946565;
- clustered all-primary state transitions × H1: 0/22, p = 1.000000;
- direct 7–9 historical exact-day matches: 0/9;
- direct 3–6 historical exact-day matches: 0/9.

Historical selection was frozen before astronomical reanalysis and was not repaired after match inspection.

## Reproducibility

The validated astronomical generator, configuration files, root catalogues, control-case materials, provenance records, and statistical validation code remain in their existing repository locations. Paper 3 expected outputs, calendar-normalization audit, source checksum, decoding instructions, and reanalysis algorithm are documented under `docs/paper_3`.

The verified Paper 3 source is stored byte-for-byte as `code/paper_3_reanalysis.py.b64`; its decoded SHA-256 is recorded in the Paper 3 documentation.

## Design principles

- validated baselines and experiments are kept separate;
- generated outputs are not edited manually;
- scientific parameters are version controlled;
- discrepancies and limitations are documented;
- historical interpretation is separated from astronomical computation.

## Scientific responsibility and AI assistance

The project used a collaborative human–AI workflow for implementation, documentation, debugging, and research-software engineering. Scientific questions, methodological decisions, validation criteria, interpretation, and release approval remain the responsibility of the named human researcher and authors. See `HUMAN_AI_COLLABORATION.md`.

## Citation and archiving

Citation metadata are provided in `CITATION.cff`. The existing archival record is Zenodo DOI `10.5281/zenodo.21825866`. The v1.1.0 GitHub release should be archived as a new version of the same record.

## License

Code is released under the MIT License. Data and documentation are covered by CC BY 4.0 unless a source file states otherwise.
