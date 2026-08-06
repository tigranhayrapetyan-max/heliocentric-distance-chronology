#!/usr/bin/env python3
"""Validate generated roots against the manuscript's mandatory 139 BCE controls."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from horizons_root_generation import validate_control


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_dir", type=Path)
    parser.add_argument("--tolerance-seconds", type=float, default=120.0)
    parser.add_argument("--output", type=Path, default=Path("outputs/control_case_validation.json"))
    args = parser.parse_args()
    report = validate_control(args.root_dir, args.tolerance_seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
