#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq, minimize_scalar

PROJECT = Path(__file__).resolve().parent
CODE_DIR = PROJECT / "code"
if not CODE_DIR.exists():
    raise SystemExit("Place this script in the project root, next to the code/ folder.")

sys.path.insert(0, str(CODE_DIR))
import horizons_root_generation as h  # noqa: E402

OUT = PROJECT / "outputs" / "refinement_0940"
CACHE = PROJECT / "cache" / "refinement_0940_v2"
OUT.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)

REFERENCE_JD = 2064437.546168981586
GENERATED_JD = 2064437.548106483417
PERIHELION_COARSE_JD = 2046929.969791560667

def fetch(body: str, jds: np.ndarray):
    # Keep every request safely below the observed Horizons TLIST truncation limit.
    return h.fetch_body_series(
        body,
        jds,
        CACHE,
        chunk_size=60,
        timeout=180,
        retries=5,
        offline=False,
        delay_seconds=0.5,
    )

def save(path: Path, samples):
    h.save_samples(path, samples)

# 1) Refine Neptune perihelion q near 0892 CE.
# Use 30-minute samples across +/- 2 days: 193 epochs, automatically split into chunks of 60.
peri_grid = np.arange(
    PERIHELION_COARSE_JD - 2.0,
    PERIHELION_COARSE_JD + 2.0 + 1e-12,
    30.0 / 1440.0,
)
nep_peri = fetch("neptune", peri_grid)
save(OUT / "neptune_perihelion_30min.csv", nep_peri)

px = np.array([s.jd_tdb for s in nep_peri], dtype=float)
py = np.array([s.range_km for s in nep_peri], dtype=float)
ps = CubicSpline(px, py)
pi = int(np.argmin(py))
lo = px[max(0, pi - 2)]
hi = px[min(len(px) - 1, pi + 2)]
pmin = minimize_scalar(
    lambda x: float(ps(x)),
    bounds=(lo, hi),
    method="bounded",
    options={"xatol": 1e-13},
)
peri_jd = float(pmin.x)
q_km = float(pmin.fun)

# 2) Refine the 0940 root.
# Search only the narrow interval covering both prior estimates, plus a 5-minute margin.
root_lo = min(REFERENCE_JD, GENERATED_JD) - 5.0 / 1440.0
root_hi = max(REFERENCE_JD, GENERATED_JD) + 5.0 / 1440.0

# 30-second samples: about 21 epochs per body, far below the limit.
root_grid = np.arange(root_lo, root_hi + 1e-12, 30.0 / 86400.0)

mer = fetch("mercury", root_grid)
nep = fetch("neptune", root_grid)
save(OUT / "mercury_root_30sec.csv", mer)
save(OUT / "neptune_root_30sec.csv", nep)

mx = np.array([s.jd_tdb for s in mer], dtype=float)
my = np.array([s.range_km for s in mer], dtype=float)
nx = np.array([s.jd_tdb for s in nep], dtype=float)
ny = np.array([s.range_km for s in nep], dtype=float)

ms = CubicSpline(mx, my)
ns = CubicSpline(nx, ny)

def f(jd: float) -> float:
    return (float(ns(jd)) - q_km) - float(ms(jd))

vals = np.array([f(x) for x in root_grid], dtype=float)
idx = np.where(vals[:-1] * vals[1:] <= 0.0)[0]
if len(idx) != 1:
    raise RuntimeError(
        f"Expected exactly one sign-changing bracket; found {len(idx)}. "
        f"Minimum |f| in sampled grid: {np.min(np.abs(vals)):.6f} km"
    )

i = int(idx[0])
root_jd = float(
    brentq(
        f,
        root_grid[i],
        root_grid[i + 1],
        xtol=1e-13,
        rtol=4 * np.finfo(float).eps,
    )
)

date_text, *_ = h.format_calendar(root_jd)

result = {
    "status": "pass",
    "method": {
        "perihelion_sampling_seconds": 1800,
        "root_sampling_seconds": 30,
        "horizons_chunk_size": 60,
        "root_solver": "Brent",
        "interpolator": "CubicSpline",
        "time_scale": "TDB",
        "center": "500@10",
        "units": "km",
    },
    "neptune_perihelion": {
        "jd_tdb": peri_jd,
        "date_tdb": h.format_calendar(peri_jd)[0],
        "q_km": q_km,
    },
    "root_1_8": {
        "jd_tdb": root_jd,
        "date_tdb": date_text,
        "residual_km": f(root_jd),
        "delta_from_reference_seconds": (root_jd - REFERENCE_JD) * 86400.0,
        "delta_from_generated_seconds": (root_jd - GENERATED_JD) * 86400.0,
    },
    "reference_catalogue": {
        "jd_tdb": REFERENCE_JD,
        "date_tdb": h.format_calendar(REFERENCE_JD)[0],
        "residual_with_refined_q_km": f(REFERENCE_JD),
    },
    "previous_generation": {
        "jd_tdb": GENERATED_JD,
        "date_tdb": h.format_calendar(GENERATED_JD)[0],
        "residual_with_refined_q_km": f(GENERATED_JD),
    },
}

(OUT / "refinement_0940_result.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)

report = f"""# 0940 CE targeted Horizons refinement

Status: **{result['status']}**

## Refined Neptune perihelion
- JD TDB: {peri_jd:.12f}
- Date TDB: {result['neptune_perihelion']['date_tdb']}
- q: {q_km:.6f} km

## Refined 1–8 root
- JD TDB: {root_jd:.12f}
- Date TDB: {date_text}
- Residual: {f(root_jd):.9f} km
- Difference from reference catalogue: {result['root_1_8']['delta_from_reference_seconds']:.6f} s
- Difference from previous generated root: {result['root_1_8']['delta_from_generated_seconds']:.6f} s

## Residuals at the two prior estimates
- Reference catalogue residual: {result['reference_catalogue']['residual_with_refined_q_km']:.6f} km
- Previous generated residual: {result['previous_generation']['residual_with_refined_q_km']:.6f} km
"""
(OUT / "REFINEMENT_0940_REPORT.md").write_text(report, encoding="utf-8")

print(report)
print(f"\nResults written to: {OUT}")
