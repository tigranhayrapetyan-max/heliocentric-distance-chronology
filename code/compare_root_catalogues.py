#!/usr/bin/env python3
"""Compare generated root CSVs with the disclosed reference catalogue.

The comparison is ordered and tolerance-based. Reference and generated files are
never modified. A JSON summary and optional CSV of matched/unmatched records are
written for auditability.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from statistics import median

CONDITIONS = ("1_8", "3_6", "7_9")


def load(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["_jd"] = float(row["jd_tdb"])
    return sorted(rows, key=lambda r: r["_jd"])


def compare(reference, generated, tolerance_seconds: float):
    tol_days = tolerance_seconds / 86400.0
    i = j = 0
    matches, missing, extra = [], [], []
    while i < len(reference) and j < len(generated):
        r, g = reference[i], generated[j]
        delta_days = g["_jd"] - r["_jd"]
        if abs(delta_days) <= tol_days:
            matches.append((r, g, delta_days * 86400.0)); i += 1; j += 1
        elif g["_jd"] < r["_jd"] - tol_days:
            extra.append(g); j += 1
        else:
            missing.append(r); i += 1
    missing.extend(reference[i:]); extra.extend(generated[j:])
    deltas = [abs(x[2]) for x in matches]
    return {
        "reference_count": len(reference),
        "generated_count": len(generated),
        "matched_within_tolerance": len(matches),
        "missing_reference_roots": len(missing),
        "extra_generated_roots": len(extra),
        "max_abs_delta_seconds": max(deltas) if deltas else None,
        "median_abs_delta_seconds": median(deltas) if deltas else None,
        "status": "pass" if len(matches) == len(reference) == len(generated) else "fail",
    }, matches, missing, extra


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("reference_dir", type=Path)
    ap.add_argument("generated_dir", type=Path)
    ap.add_argument("--tolerance-seconds", type=float, default=120.0)
    ap.add_argument("--output-json", type=Path, default=Path("outputs/root_catalogue_comparison.json"))
    ap.add_argument("--details-csv", type=Path, default=Path("outputs/root_catalogue_comparison_details.csv"))
    args = ap.parse_args()
    report = {"tolerance_seconds": args.tolerance_seconds, "conditions": {}}
    details = []
    overall = True
    for condition in CONDITIONS:
        ref = load(args.reference_dir / f"roots_{condition}.csv")
        gen = load(args.generated_dir / f"roots_{condition}.csv")
        summary, matches, missing, extra = compare(ref, gen, args.tolerance_seconds)
        report["conditions"][condition] = summary
        overall &= summary["status"] == "pass"
        for r, g, delta in matches:
            details.append({"condition":condition,"status":"matched","reference_date":r.get("date_tdb", ""),"generated_date":g.get("date_tdb", ""),"delta_seconds":f"{delta:.9f}"})
        for r in missing:
            details.append({"condition":condition,"status":"missing_reference_root","reference_date":r.get("date_tdb", ""),"generated_date":"","delta_seconds":""})
        for g in extra:
            details.append({"condition":condition,"status":"extra_generated_root","reference_date":"","generated_date":g.get("date_tdb", ""),"delta_seconds":""})
    report["overall_status"] = "pass" if overall else "fail"
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    with args.details_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["condition","status","reference_date","generated_date","delta_seconds"])
        w.writeheader(); w.writerows(details)
    print(json.dumps(report, indent=2))
    return 0 if overall else 2

if __name__ == "__main__":
    raise SystemExit(main())
