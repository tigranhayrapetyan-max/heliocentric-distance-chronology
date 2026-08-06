#!/usr/bin/env python3
"""Run root generation, controls, root comparison, and statistical validation."""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="-3999-01-01")
    parser.add_argument("--stop", default="2026-08-03")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--reuse-series", action="store_true")
    parser.add_argument("--trials", type=int, default=1_000_000)
    parser.add_argument("--comparison-tolerance-seconds", type=float, default=120.0)
    parser.add_argument("--chunk-size", type=int, default=64, help="TLIST epochs per Horizons request")
    args = parser.parse_args()
    python = sys.executable
    base = Path(__file__).resolve().parent.parent
    generator = base / "code" / "horizons_root_generation.py"
    validator = base / "code" / "validate_control_cases.py"
    comparer = base / "code" / "compare_root_catalogues.py"
    stats = base / "code" / "circular_shift_validation_from_csv.py"
    reference_dir = base / "data" / "root_catalogue"
    generated_dir = base / "outputs" / "generated_roots"
    cmd = [python, str(generator), "--start", args.start, "--stop", args.stop,
           "--cache-dir", str(base / "cache" / "horizons"),
           "--work-dir", str(base / "outputs"),
           "--output-dir", str(generated_dir), "--chunk-size", str(args.chunk_size)]
    if args.offline: cmd.append("--offline")
    if args.reuse_series: cmd.append("--reuse-series")
    run(cmd)
    run([python, str(validator), str(generated_dir), "--output", str(base / "outputs" / "control_case_validation_full_run.json")])
    run([python, str(comparer), str(reference_dir), str(generated_dir),
         "--tolerance-seconds", str(args.comparison_tolerance_seconds),
         "--output-json", str(base / "outputs" / "root_catalogue_comparison.json"),
         "--details-csv", str(base / "outputs" / "root_catalogue_comparison_details.csv")])
    run([python, str(stats), str(generated_dir), "--trials", str(args.trials),
         "--sensitivity-csv", str(base / "outputs" / "circular_shift_sensitivity_generated.csv")])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
