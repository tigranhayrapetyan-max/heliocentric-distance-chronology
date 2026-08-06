# Heliocentric Distance Chronology

## v1.0.0 — Clean-Room Validation Release

**A clean-room, independently validated, and reproducible scientific software platform for reconstructing and analysing heliocentric-distance chronologies from JPL Horizons ephemerides.**

> **Every scientific result should be reproducible, transparent, and honestly reported.**

## Why this project exists

Computational historical-astronomy research requires more than a reported result: the ephemeris source, numerical definitions, root-detection rules, tolerances, provenance, and validation procedure must be open to independent scrutiny. HDC provides that computational framework while keeping astronomical reconstruction separate from historical interpretation.

No claim of priority is made for the general class of astronomical ephemeris software. This release documents a clean-room implementation of the specific heliocentric-distance chronology framework used in the accompanying research.

## Validated baseline

The released baseline reconstructs three heliocentric-distance conditions:

- **1–8:** `[r_Neptune(t) − q_Neptune] = r_Mercury(t)` — 7,863 events;
- **3–6:** `[r_Saturn(t) − q_Saturn] = r_Earth–Moon(t)` — 447 events;
- **7–9:** `[r_Pluto(t) − q_Pluto] = r_Uranus(t)` — 42 events.

The 139 BCE control case passed. A targeted high-resolution refinement also documented one legacy 0940 CE timestamp offset without changing the identity or total count of the astronomical event catalogue.

## Design principles

- validated baselines and experiments are kept separate;
- generated outputs are not edited manually;
- scientific parameters are version controlled;
- discrepancies and limitations are documented;
- historical interpretation is separated from astronomical computation;
- future analysis modules are designed to be configurable rather than hypothesis-specific.

## Repository layout

```text
code/                validated computation and validation scripts
config/baseline/     immutable released parameter profiles
config/experiments/  named alternative scientific configurations
config/schemas/      machine-readable configuration contracts
data/                disclosed source catalogues and inputs
docs/                validation, reproducibility, papers, and supplementary material
outputs/             released generated roots and validation reports
provenance/          historical assignment provenance
tests/               offline numerical and logic tests
tools/               validation, release, checksum, and maintenance utilities
.github/              issue and contribution templates
```

Large regenerable Horizons time-series files are excluded from the GitHub source package and may be archived with the Zenodo record.

## Installation

Python 3.11 or later is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Reproduce the baseline

```bash
python code/run_pipeline.py --start=-3999-01-01 --stop=2026-08-03 --trials 1000000
```

The immutable parameter profile is `config/baseline/published_v1.json`. See `REPRODUCIBILITY.md` and `docs/VALIDATION_STATUS.md` before interpreting or extending the results.

## Configurable research direction

Scientific alternatives should be expressed as named configuration files and isolated output namespaces. Templates for Mars–Saturn and Venus–Saturn 8° experiments are included under `config/experiments/`. They define the architecture of the planned angular-enclosure module and are deliberately marked as non-executable design templates in v1.0.0; the validated distance-root engine is not silently extended beyond its tested scope.

## Scientific responsibility and AI assistance

The project used a collaborative human–AI development workflow for implementation, documentation, debugging, and research-software engineering. Scientific questions, methodological decisions, validation criteria, interpretation, and release approval remain the responsibility of the named human researcher and authors. See `HUMAN_AI_COLLABORATION.md`.

## Citation and archiving

Citation metadata are provided in `CITATION.cff`. The release is intended for archival through Zenodo after the private repository is made public at the appropriate publication stage.

## License

Code is released under the MIT License. Data and documentation are covered by CC BY 4.0 unless a source file states otherwise.
