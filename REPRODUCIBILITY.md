# Reproducibility

## Baseline environment

Python 3.11 or later is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Fast offline checks

```bash
pytest -q
```

## Published baseline

The immutable published parameter profile is stored at:

```text
config/baseline/published_v1.json
```

The current v1 generator preserves its validated command-line interface. The configuration files establish the stable parameter contract for subsequent engine generalisation; experimental templates clearly state when a module is not yet executable in v1.0.0.

## Full regeneration

```bash
python code/run_pipeline.py --start=-3999-01-01 --stop=2026-08-03 --trials 1000000
```

Network-derived time series are intentionally excluded from the GitHub source package because they are regenerable and one file exceeds GitHub's browser-upload limit. They should be archived with the Zenodo release or regenerated from JPL Horizons.
