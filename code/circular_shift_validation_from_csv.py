#!/usr/bin/env python3
"""Reproduce the circular-shift statistic from root CSV files."""
from __future__ import annotations

import argparse
import bisect
import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Event:
    condition: str
    jd: float
    label: str


def load_events(path: Path) -> list[Event]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        events = [
            Event(row.get("condition", path.stem.replace("roots_", "")), float(row["jd_tdb"]), row.get("date_tdb", ""))
            for row in reader
        ]
    return sorted(events, key=lambda item: item.jd)


def merge_intervals(intervals: Iterable[tuple[float, float]]) -> list[tuple[float, float]]:
    ordered = sorted((a, b) for a, b in intervals if a < b)
    if not ordered:
        return []
    merged: list[list[float]] = [[ordered[0][0], ordered[0][1]]]
    for start, end in ordered[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(a, b) for a, b in merged]


def containing_window(jd: float, roots: Sequence[float]) -> tuple[float, float] | None:
    index = bisect.bisect_left(roots, jd)
    return None if index == 0 or index >= len(roots) else (roots[index - 1], roots[index])


def compact(events: Sequence[Event], roots: Sequence[float], threshold: float) -> list[Event]:
    result = []
    for event in events:
        window = containing_window(event.jd, roots)
        if window and window[1] - window[0] <= threshold:
            result.append(event)
    return result


def observed_pairs(a: Sequence[Event], b: Sequence[Event], lag_min: float, lag_max: float):
    return [(x, y, y.jd - x.jd) for x in a for y in b if lag_min <= y.jd - x.jd <= lag_max]


def successful_shift_intervals(
    roots: Sequence[float], events_79: Sequence[Event], events_36: Sequence[Event], threshold: float, lag_min: float, lag_max: float
) -> tuple[list[tuple[float, float]], float]:
    origin, span = roots[0], roots[-1] - roots[0]
    compact_79 = compact(events_79, roots, threshold)
    compact_windows = [(roots[i] - origin, roots[i + 1] - origin) for i in range(len(roots) - 1) if roots[i + 1] - roots[i] <= threshold]
    target_regions: list[tuple[float, float]] = []
    for event in compact_79:
        rel = (event.jd - origin) % span
        lag_start, lag_end = rel + lag_min, rel + lag_max
        lag_regions = [(lag_start, lag_end)] if lag_end <= span else [(lag_start, span), (0.0, lag_end - span)]
        for c_start, c_end in compact_windows:
            for t_start, t_end in lag_regions:
                start, end = max(c_start, t_start), min(c_end, t_end)
                if start < end:
                    target_regions.append((start, end))
    target_regions = merge_intervals(target_regions)
    allowed: list[tuple[float, float]] = []
    for event in events_36:
        rel = (event.jd - origin) % span
        for start, end in target_regions:
            length = end - start
            shift_start = (start - rel) % span
            shift_end = shift_start + length
            if shift_end <= span:
                allowed.append((shift_start, shift_end))
            else:
                allowed.extend([(shift_start, span), (0.0, shift_end - span)])
    return merge_intervals(allowed), span


def in_intervals(value: float, starts: Sequence[float], ends: Sequence[float]) -> bool:
    index = bisect.bisect_right(starts, value) - 1
    return index >= 0 and value < ends[index]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_dir", type=Path)
    parser.add_argument("--threshold", type=float, default=30.0)
    parser.add_argument("--lag-min", type=float, default=240.0)
    parser.add_argument("--lag-max", type=float, default=300.0)
    parser.add_argument("--trials", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=20260804)
    parser.add_argument("--sensitivity-csv", type=Path)
    args = parser.parse_args()

    events_18 = load_events(args.root_dir / "roots_1_8.csv")
    events_36 = load_events(args.root_dir / "roots_3_6.csv")
    events_79 = load_events(args.root_dir / "roots_7_9.csv")
    roots = [event.jd for event in events_18]

    def evaluate(threshold: float, trials: int):
        compact_79 = compact(events_79, roots, threshold)
        compact_36 = compact(events_36, roots, threshold)
        pairs = observed_pairs(compact_79, compact_36, args.lag_min, args.lag_max)
        intervals, span = successful_shift_intervals(roots, events_79, events_36, threshold, args.lag_min, args.lag_max)
        permitted = sum(end - start for start, end in intervals)
        starts, ends = [a for a, _ in intervals], [b for _, b in intervals]
        rng = random.Random(args.seed)
        hits = sum(in_intervals(rng.random() * span, starts, ends) for _ in range(trials))
        return {
            "threshold_days": threshold,
            "compact_7_9": len(compact_79),
            "compact_3_6": len(compact_36),
            "observed_pairs": len(pairs),
            "permitted_shift_days": permitted,
            "span_days": span,
            "computed_shift_proportion": permitted / span,
            "monte_carlo_hits": hits,
            "monte_carlo_trials": trials,
            "monte_carlo_proportion": hits / trials,
        }

    result = evaluate(args.threshold, args.trials)
    for key, value in result.items():
        print(f"{key}: {value}")

    if args.sensitivity_csv:
        thresholds = [10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 75, 100]
        args.sensitivity_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.sensitivity_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(evaluate(10, 1).keys()))
            writer.writeheader()
            for threshold in thresholds:
                writer.writerow(evaluate(threshold, min(args.trials, 100_000)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
