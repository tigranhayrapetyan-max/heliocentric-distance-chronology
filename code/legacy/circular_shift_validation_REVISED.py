#!/usr/bin/env python3
"""
Reproduce the discovery-stage circular time-shift evaluation used in:

Testing Heliocentric Distance Conditions as Chronological Markers in
Armenian Historical and Mythological Traditions

The script uses only the Python standard library. It reads the 1_8, 3_6,
and 7_9 worksheets directly from an .xlsx archive, converts their event
times to Julian days, identifies compact 1_8 windows, and calculates:

1. The observed number of compact 7_9 -> 3_6 pairs separated by 240–300 days.
2. The exact conditional probability under a common circular time shift
   of the complete 3_6 series.
3. A Monte Carlo check using actual random circular shifts.
4. A sensitivity table for alternative compact-window thresholds.

This script reproduces the conditional shift calculation for the supplied roots. The result is unadjusted for the wider exploratory search.
It does not regenerate the roots from JPL Horizons.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import math
import random
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from xml.etree import ElementTree as ET


NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CELL_REF_RE = re.compile(r"([A-Z]+)(\d+)")


@dataclass(frozen=True)
class Event:
    event_id: int
    label: str
    jd: float


def column_number(cell_ref: str) -> int:
    """Return a 1-based Excel column number from a cell reference."""
    match = CELL_REF_RE.fullmatch(cell_ref)
    if not match:
        raise ValueError(f"Invalid cell reference: {cell_ref!r}")
    letters = match.group(1)
    value = 0
    for char in letters:
        value = value * 26 + (ord(char) - ord("A") + 1)
    return value


def parse_shared_strings(archive: zipfile.ZipFile) -> List[str]:
    """Read the shared string table, if present."""
    try:
        xml = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []

    root = ET.fromstring(xml)
    strings: List[str] = []
    for si in root.findall(f"{{{NS_MAIN}}}si"):
        parts = [node.text or "" for node in si.iter(f"{{{NS_MAIN}}}t")]
        strings.append("".join(parts))
    return strings


def workbook_sheet_paths(archive: zipfile.ZipFile) -> Dict[str, str]:
    """Map worksheet display names to worksheet XML paths."""
    workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
    rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))

    rel_targets: Dict[str, str] = {}
    for rel in rels_root.findall(f"{{{NS_PKG_REL}}}Relationship"):
        rel_targets[rel.attrib["Id"]] = rel.attrib["Target"]

    mapping: Dict[str, str] = {}
    sheets = workbook_root.find(f"{{{NS_MAIN}}}sheets")
    if sheets is None:
        return mapping

    for sheet in sheets:
        name = sheet.attrib["name"]
        rel_id = sheet.attrib[f"{{{NS_REL}}}id"]
        target = rel_targets[rel_id].lstrip("/")
        if not target.startswith("xl/"):
            target = f"xl/{target}"
        mapping[name] = target
    return mapping


def cell_text(cell: ET.Element, shared_strings: Sequence[str]) -> Optional[str]:
    """Extract a scalar value from an OOXML cell."""
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        inline = cell.find(f"{{{NS_MAIN}}}is")
        if inline is None:
            return ""
        return "".join((t.text or "") for t in inline.iter(f"{{{NS_MAIN}}}t"))

    value_node = cell.find(f"{{{NS_MAIN}}}v")
    if value_node is None:
        return None

    raw = value_node.text or ""
    if cell_type == "s":
        return shared_strings[int(raw)]
    if cell_type in {"str", "b", "e"}:
        return raw
    return raw


def read_sheet_rows(
    archive: zipfile.ZipFile,
    sheet_path: str,
    shared_strings: Sequence[str],
    start_row: int = 5,
    max_column: int = 9,
) -> Iterable[Dict[int, Optional[str]]]:
    """Yield worksheet rows as {1-based column number: scalar text} mappings."""
    with archive.open(sheet_path) as stream:
        context = ET.iterparse(stream, events=("end",))
        for _, elem in context:
            if elem.tag != f"{{{NS_MAIN}}}row":
                continue

            row_number = int(elem.attrib.get("r", "0"))
            if row_number >= start_row:
                row: Dict[int, Optional[str]] = {}
                for cell in elem.findall(f"{{{NS_MAIN}}}c"):
                    ref = cell.attrib.get("r")
                    if not ref:
                        continue
                    col = column_number(ref)
                    if col <= max_column:
                        row[col] = cell_text(cell, shared_strings)
                if row:
                    yield row
            elem.clear()


def julian_day(
    astronomical_year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    gregorian: bool = False,
) -> float:
    """Convert a civil date with astronomical year numbering to Julian day."""
    y = astronomical_year
    m = month
    fractional_day = day + (hour + minute / 60.0 + second / 3600.0) / 24.0

    if m <= 2:
        y -= 1
        m += 12

    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4) if gregorian else 0
    return (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + fractional_day
        + b
        - 1524.5
    )


def read_events(xlsx_path: Path, sheet_name: str) -> List[Event]:
    """Read event rows from one of the 1_8, 3_6, or 7_9 sheets."""
    with zipfile.ZipFile(xlsx_path) as archive:
        shared_strings = parse_shared_strings(archive)
        sheets = workbook_sheet_paths(archive)
        if sheet_name not in sheets:
            raise KeyError(f"Worksheet {sheet_name!r} not found. Available: {sorted(sheets)}")

        events: List[Event] = []
        for row in read_sheet_rows(archive, sheets[sheet_name], shared_strings):
            if not row.get(1):
                continue

            event_id = int(float(row[1] or "0"))
            label = str(row.get(2) or "")
            astronomical_year = int(float(row.get(5) or "0"))
            month = int(float(row.get(6) or "0"))
            day = int(float(row.get(7) or "0"))
            time_text = str(row.get(8) or "00:00:00")
            calendar = str(row.get(9) or "").strip().lower()

            hour, minute, second = (int(part) for part in time_text.split(":"))
            gregorian = calendar in {"gregorian", "գրիգորյան"}
            jd = julian_day(
                astronomical_year,
                month,
                day,
                hour,
                minute,
                second,
                gregorian=gregorian,
            )
            events.append(Event(event_id, label, jd))

    events.sort(key=lambda event: event.jd)
    return events


def merge_intervals(intervals: Iterable[Tuple[float, float]]) -> List[Tuple[float, float]]:
    ordered = sorted((a, b) for a, b in intervals if a < b)
    if not ordered:
        return []

    merged: List[List[float]] = [[ordered[0][0], ordered[0][1]]]
    for start, end in ordered[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(a, b) for a, b in merged]


def containing_window(jd: float, roots: Sequence[float]) -> Optional[Tuple[float, float]]:
    index = bisect.bisect_left(roots, jd)
    if index == 0 or index >= len(roots):
        return None
    return roots[index - 1], roots[index]


def compact_events(events: Sequence[Event], roots: Sequence[float], threshold: float) -> List[Event]:
    result: List[Event] = []
    for event in events:
        window = containing_window(event.jd, roots)
        if window and window[1] - window[0] <= threshold:
            result.append(event)
    return result


def observed_pairs(
    compact_79: Sequence[Event],
    compact_36: Sequence[Event],
    lag_min: float,
    lag_max: float,
) -> List[Tuple[Event, Event, float]]:
    pairs: List[Tuple[Event, Event, float]] = []
    for event_79 in compact_79:
        for event_36 in compact_36:
            lag = event_36.jd - event_79.jd
            if lag_min <= lag <= lag_max:
                pairs.append((event_79, event_36, lag))
    return pairs


def successful_shift_intervals(
    roots: Sequence[float],
    events_79: Sequence[Event],
    events_36: Sequence[Event],
    threshold: float,
    lag_min: float,
    lag_max: float,
) -> Tuple[List[Tuple[float, float]], float]:
    """
    Return the union of circular shifts that produce at least one success.

    The 1_8 and 7_9 series remain fixed. One common circular displacement
    is applied to every 3_6 center.
    """
    origin = roots[0]
    span = roots[-1] - origin
    compact_79 = compact_events(events_79, roots, threshold)

    compact_windows = [
        (roots[i] - origin, roots[i + 1] - origin)
        for i in range(len(roots) - 1)
        if roots[i + 1] - roots[i] <= threshold
    ]

    target_regions: List[Tuple[float, float]] = []
    for event in compact_79:
        relative = (event.jd - origin) % span
        lag_start = relative + lag_min
        lag_end = relative + lag_max

        if lag_end <= span:
            lag_regions = [(lag_start, lag_end)]
        else:
            lag_regions = [(lag_start, span), (0.0, lag_end - span)]

        for compact_start, compact_end in compact_windows:
            for target_start, target_end in lag_regions:
                start = max(compact_start, target_start)
                end = min(compact_end, target_end)
                if start < end:
                    target_regions.append((start, end))
    target_regions = merge_intervals(target_regions)

    allowed: List[Tuple[float, float]] = []
    for event in events_36:
        relative = (event.jd - origin) % span
        for target_start, target_end in target_regions:
            length = target_end - target_start
            shift_start = (target_start - relative) % span
            shift_end = shift_start + length
            if shift_end <= span:
                allowed.append((shift_start, shift_end))
            else:
                allowed.append((shift_start, span))
                allowed.append((0.0, shift_end - span))

    return merge_intervals(allowed), span


def point_in_intervals(
    value: float,
    interval_starts: Sequence[float],
    interval_ends: Sequence[float],
) -> bool:
    index = bisect.bisect_right(interval_starts, value) - 1
    return index >= 0 and value < interval_ends[index]


def run_test(
    roots: Sequence[float],
    events_79: Sequence[Event],
    events_36: Sequence[Event],
    threshold: float,
    lag_min: float,
    lag_max: float,
    trials: int,
    seed: int,
) -> Dict[str, float]:
    compact_79 = compact_events(events_79, roots, threshold)
    compact_36 = compact_events(events_36, roots, threshold)
    pairs = observed_pairs(compact_79, compact_36, lag_min, lag_max)

    intervals, span = successful_shift_intervals(
        roots, events_79, events_36, threshold, lag_min, lag_max
    )
    permitted_days = sum(end - start for start, end in intervals)
    computed_shift_proportion = permitted_days / span if span else float("nan")

    rng = random.Random(seed)
    starts = [a for a, _ in intervals]
    ends = [b for _, b in intervals]
    hits = sum(
        point_in_intervals(rng.random() * span, starts, ends)
        for _ in range(trials)
    )
    monte_carlo_p = hits / trials if trials else float("nan")

    return {
        "threshold": threshold,
        "compact_79": len(compact_79),
        "compact_36": len(compact_36),
        "observed_pairs": len(pairs),
        "permitted_shift_days": permitted_days,
        "span_days": span,
        "computed_shift_proportion": computed_shift_proportion,
        "monte_carlo_hits": hits,
        "monte_carlo_trials": trials,
        "monte_carlo_p": monte_carlo_p,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reproduce the circular time-shift validation from the planetary coincidence workbook."
    )
    parser.add_argument("workbook", type=Path, help="Path to the .xlsx workbook")
    parser.add_argument("--threshold", type=float, default=30.0, help="Maximum 1_8 window width in days")
    parser.add_argument("--lag-min", type=float, default=240.0, help="Minimum 7_9 to 3_6 lag in days")
    parser.add_argument("--lag-max", type=float, default=300.0, help="Maximum 7_9 to 3_6 lag in days")
    parser.add_argument("--trials", type=int, default=1_000_000, help="Monte Carlo trial count")
    parser.add_argument("--seed", type=int, default=20260804, help="Monte Carlo random seed")
    parser.add_argument(
        "--sensitivity-csv",
        type=Path,
        default=None,
        help="Optional output path for threshold sensitivity results",
    )
    args = parser.parse_args()

    if not args.workbook.exists():
        parser.error(f"Workbook not found: {args.workbook}")
    if args.threshold <= 0:
        parser.error("--threshold must be positive")
    if not (0 <= args.lag_min <= args.lag_max):
        parser.error("Require 0 <= --lag-min <= --lag-max")
    if args.trials < 1:
        parser.error("--trials must be at least 1")

    events_18 = read_events(args.workbook, "1_8")
    events_36 = read_events(args.workbook, "3_6")
    events_79 = read_events(args.workbook, "7_9")
    roots = [event.jd for event in events_18]

    result = run_test(
        roots,
        events_79,
        events_36,
        args.threshold,
        args.lag_min,
        args.lag_max,
        args.trials,
        args.seed,
    )

    print("Planetary coincidence circular-shift validation")
    print("=" * 48)
    print(f"Workbook:                  {args.workbook}")
    print(f"1_8 roots:                 {len(events_18):,}")
    print(f"3_6 centers:               {len(events_36):,}")
    print(f"7_9 centers:               {len(events_79):,}")
    print(f"Temporal span (days):       {result['span_days']:.9f}")
    print(f"Temporal span (years):      {result['span_days'] / 365.2425:.9f}")
    print(f"Compact threshold (days):   {args.threshold:g}")
    print(f"Compact 7_9 centers:        {int(result['compact_79'])}")
    print(f"Compact 3_6 centers:        {int(result['compact_36'])}")
    print(f"Observed qualifying pairs:  {int(result['observed_pairs'])}")
    print(f"Permitted shift-days:       {result['permitted_shift_days']:.9f}")
    print(f"Directly computed conditional shift proportion:        {result['computed_shift_proportion']:.12f}")
    print(
        f"Monte Carlo:                {int(result['monte_carlo_hits']):,}/"
        f"{int(result['monte_carlo_trials']):,} = {result['monte_carlo_p']:.12f}"
    )
    print(f"Random seed:                {args.seed}")

    if args.sensitivity_csv:
        thresholds = [10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 75, 100]
        with args.sensitivity_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "threshold_days",
                    "compact_7_9",
                    "compact_3_6",
                    "observed_pairs",
                    "permitted_shift_days",
                    "computed_shift_proportion",
                ]
            )
            for threshold in thresholds:
                sensitivity = run_test(
                    roots,
                    events_79,
                    events_36,
                    threshold,
                    args.lag_min,
                    args.lag_max,
                    max(1, min(args.trials, 100_000)),
                    args.seed,
                )
                writer.writerow(
                    [
                        threshold,
                        int(sensitivity["compact_79"]),
                        int(sensitivity["compact_36"]),
                        int(sensitivity["observed_pairs"]),
                        f"{sensitivity['permitted_shift_days']:.12f}",
                        f"{sensitivity['computed_shift_proportion']:.12f}",
                    ]
                )
        print(f"Sensitivity CSV:            {args.sensitivity_csv}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, ValueError, zipfile.BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2)
