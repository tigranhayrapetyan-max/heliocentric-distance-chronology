from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from horizons_root_generation import Sample, generate_roots  # noqa: E402


def test_synthetic_root_generation_runs():
    # A synthetic outer orbit with clear repeated minima and an inner signal.
    x = np.linspace(0.0, 400.0, 801)
    outer = 100.0 + 20.0 * (1.0 - np.cos(2 * np.pi * x / 100.0))
    inner = 20.0 + 10.0 * np.sin(2 * np.pi * x / 20.0)
    outer_samples = [Sample(float(a), float(b)) for a, b in zip(x, outer)]
    inner_samples = [Sample(float(a), float(b)) for a, b in zip(x, inner)]
    records = generate_roots("3_6", inner_samples, outer_samples, 100.0, 300.0, 1e-9)
    assert isinstance(records, list)
    assert all(abs(record.residual_km) < 1e-5 for record in records)
