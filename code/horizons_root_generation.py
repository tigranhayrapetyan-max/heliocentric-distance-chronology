#!/usr/bin/env python3
"""Generate heliocentric-distance equality roots from NASA/JPL Horizons.

This is a clean-room reconstruction from the published reproducibility protocol.
It supports cached/offline processing and records request metadata and checksums.

Conditions
----------
1-8: [r_Neptune(t) - q_Neptune(orbit)] - r_Mercury(t) = 0
3-6: [r_Saturn(t)  - q_Saturn(orbit)]  - r_EarthMoon(t) = 0
7-9: [r_Pluto(t)   - q_Pluto(orbit)]   - r_Uranus(t) = 0

The script intentionally does not assign historical meaning to any root.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import math
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import numpy as np
import requests
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq, minimize_scalar

API_URL = "https://ssd.jpl.nasa.gov/api/horizons_file.api"
KM_PER_AU = 149_597_870.700
TROPICAL_YEAR_DAYS = 365.2425

BODY_IDS = {
    "mercury": "1",
    "earth_moon": "3",
    "saturn": "6",
    "uranus": "7",
    "neptune": "8",
    "pluto": "9",
}

CONDITIONS = {
    "1_8": {"inner": "mercury", "outer": "neptune", "inner_step_days": 2.0, "outer_step_days": 20.0, "padding_days": 65_000.0},
    "3_6": {"inner": "earth_moon", "outer": "saturn", "inner_step_days": 11.0, "outer_step_days": 11.0, "padding_days": 13_000.0},
    "7_9": {"inner": "uranus", "outer": "pluto", "inner_step_days": 30.0, "outer_step_days": 30.0, "padding_days": 100_000.0},
}

EXPECTED_CONTROL = {
    "7_9": "BCE 0139-02-06 02:30:31",
    "3_6": "BCE 0139-10-26 18:46:33",
}


@dataclass(frozen=True)
class Sample:
    jd_tdb: float
    range_km: float


@dataclass(frozen=True)
class Perihelion:
    orbit_index: int
    jd_tdb: float
    q_km: float


@dataclass(frozen=True)
class RootRecord:
    condition: str
    jd_tdb: float
    date_tdb: str
    astronomical_year: int
    era: str
    display_year: int
    month: int
    day: int
    time_tdb: str
    calendar: str
    outer_body: str
    outer_orbit_index: int
    outer_phase: str
    perihelion_jd_tdb: float
    perihelion_date_tdb: str
    perihelion_q_km: float
    outer_distance_km: float
    delta_outer_km: float
    inner_distance_km: float
    residual_km: float
    roots_in_orbit: int = 0


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def chunked(values: Sequence[float], size: int) -> Iterator[Sequence[float]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def julian_calendar_to_jd(
    astronomical_year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: float = 0.0,
) -> float:
    """Convert a proleptic Julian-calendar date to Julian Day (astronomical years)."""
    y = astronomical_year
    m = month
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(365.25 * (y + 4716))
    b = math.floor(30.6001 * (m + 1))
    fraction = (hour + minute / 60.0 + second / 3600.0) / 24.0
    return a + b + day + fraction - 1524.5


def gregorian_calendar_to_jd(
    astronomical_year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: float = 0.0,
) -> float:
    y = astronomical_year
    m = month
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    correction = 2 - a + math.floor(a / 4)
    fraction = (hour + minute / 60.0 + second / 3600.0) / 24.0
    return (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + day
        + correction
        + fraction
        - 1524.5
    )


def parse_year_date(text: str) -> float:
    """Parse YYYY-MM-DD using astronomical year numbering and mixed calendar.

    Examples: -0138-02-06, 2026-08-05. Dates before 1582-10-15 use Julian.
    """
    match = re.fullmatch(r"([+-]?\d{1,6})-(\d{2})-(\d{2})", text.strip())
    if not match:
        raise ValueError(f"Expected astronomical YYYY-MM-DD, got {text!r}")
    year, month, day = map(int, match.groups())
    if (year, month, day) >= (1582, 10, 15):
        return gregorian_calendar_to_jd(year, month, day)
    return julian_calendar_to_jd(year, month, day)


def jd_to_calendar(jd: float) -> tuple[int, int, int, int, int, float, str]:
    """Convert JD to mixed Julian/Gregorian calendar with astronomical year."""
    z = math.floor(jd + 0.5)
    f = jd + 0.5 - z
    if z >= 2_299_161:
        alpha = math.floor((z - 1_867_216.25) / 36_524.25)
        a = z + 1 + alpha - math.floor(alpha / 4)
        calendar = "Gregorian"
    else:
        a = z
        calendar = "Julian"
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)
    day_decimal = b - d - math.floor(30.6001 * e) + f
    day = math.floor(day_decimal)
    frac = day_decimal - day
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    total_seconds = frac * 86400.0
    hour = int(total_seconds // 3600)
    minute = int((total_seconds - hour * 3600) // 60)
    second = total_seconds - hour * 3600 - minute * 60
    if second >= 59.9995:
        second = 0.0
        minute += 1
    if minute >= 60:
        minute = 0
        hour += 1
    # A root near midnight can roll; for reporting this is sub-second only.
    if hour >= 24:
        hour = 23
        minute = 59
        second = 59.999
    return year, month, day, hour, minute, second, calendar


def format_calendar(jd: float) -> tuple[str, int, str, int, int, int, str, str]:
    year, month, day, hour, minute, second, calendar = jd_to_calendar(jd)
    rounded_second = int(round(second))
    if rounded_second == 60:
        rounded_second = 59
    era = "BCE" if year <= 0 else "CE"
    display_year = 1 - year if year <= 0 else year
    time_text = f"{hour:02d}:{minute:02d}:{rounded_second:02d}"
    date_text = f"{display_year:04d} {era}-{month:02d}-{day:02d} {time_text}"
    return date_text, year, era, display_year, month, day, time_text, calendar


def make_tlist(start_jd: float, stop_jd: float, step_days: float) -> np.ndarray:
    if stop_jd <= start_jd:
        raise ValueError("stop_jd must exceed start_jd")
    count = int(math.floor((stop_jd - start_jd) / step_days)) + 1
    values = start_jd + np.arange(count, dtype=float) * step_days
    if values[-1] < stop_jd - 1e-8:
        values = np.append(values, stop_jd)
    return values


def horizons_input(command: str, jd_values: Sequence[float]) -> str:
    tlist = " ".join(f"'{jd:.9f}'" for jd in jd_values)
    return "\n".join(
        [
            "!$$SOF",
            f"COMMAND='{command}'",
            "OBJ_DATA='NO'",
            "MAKE_EPHEM='YES'",
            "TABLE_TYPE='VECTORS'",
            "CENTER='500@10'",
            "TIME_TYPE='TDB'",
            "REF_SYSTEM='ICRF'",
            "REF_PLANE='FRAME'",
            "VEC_CORR='NONE'",
            "OUT_UNITS='KM-D'",
            "VEC_TABLE='3'",
            "CSV_FORMAT='YES'",
            "VEC_LABELS='YES'",
            "CAL_TYPE='MIXED'",
            "TIME_DIGITS='FRACSEC'",
            "TLIST_TYPE='JD'",
            f"TLIST={tlist}",
            "!$$EOF",
            "",
        ]
    )


def parse_horizons_result(text: str) -> list[Sample]:
    if "$$SOE" not in text or "$$EOE" not in text:
        excerpt = text[:1500].replace("\n", " ")
        raise RuntimeError(f"Horizons response contains no ephemeris block: {excerpt}")
    before, rest = text.split("$$SOE", 1)
    block, _ = rest.split("$$EOE", 1)

    # Horizons CSV vector output normally has a header line before $$SOE.
    header_candidates = [line.strip() for line in before.splitlines() if "JDTDB" in line and "," in line]
    header = next((line for line in reversed(header_candidates)), "")
    names = [field.strip().strip('"') for field in next(csv.reader([header]))] if header else []

    rows: list[Sample] = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("*"):
            continue
        fields = [field.strip().strip('"') for field in next(csv.reader([line]))]
        try:
            jd = float(fields[0])
        except (ValueError, IndexError):
            continue

        range_value: float | None = None
        if names and len(names) <= len(fields):
            normalized = [re.sub(r"[^A-Z]", "", name.upper()) for name in names]
            for candidate in ("RG", "RANGE"):
                if candidate in normalized:
                    range_value = float(fields[normalized.index(candidate)])
                    break
        if range_value is None:
            # VEC_TABLE=3 CSV generally ends with LT, RG, RR (plus possible blank field).
            numeric_tail: list[float] = []
            for field in fields[2:]:
                try:
                    numeric_tail.append(float(field))
                except ValueError:
                    pass
            if len(numeric_tail) < 3:
                raise RuntimeError(f"Could not identify range column in line: {line}")
            range_value = numeric_tail[-2]
        rows.append(Sample(jd, range_value))
    if not rows:
        raise RuntimeError("No Horizons samples parsed")
    return rows


def fetch_body_series(
    body_name: str,
    jd_values: Sequence[float],
    cache_dir: Path,
    *,
    chunk_size: int = 5000,
    timeout: int = 180,
    retries: int = 5,
    offline: bool = False,
    delay_seconds: float = 0.35,
) -> list[Sample]:
    body_id = BODY_IDS[body_name]
    body_dir = cache_dir / body_name
    body_dir.mkdir(parents=True, exist_ok=True)
    all_samples: list[Sample] = []
    metadata_records: list[dict[str, object]] = []

    for index, values in enumerate(chunked(list(jd_values), chunk_size), start=1):
        request_text = horizons_input(body_id, values)
        request_hash = sha256_bytes(request_text.encode("utf-8"))
        stem = f"chunk_{index:05d}_{request_hash[:12]}"
        response_path = body_dir / f"{stem}.json"
        request_path = body_dir / f"{stem}.input.txt"
        request_path.write_text(request_text, encoding="utf-8")

        if response_path.exists():
            payload = json.loads(response_path.read_text(encoding="utf-8"))
        else:
            if offline:
                raise FileNotFoundError(f"Missing cached response in offline mode: {response_path}")
            last_error: Exception | None = None
            for attempt in range(1, retries + 1):
                try:
                    # The Horizons File API expects the run-stream as an actual
                    # multipart file upload. Sending it as a normal form field can
                    # silently truncate long TLIST requests.
                    response = requests.post(
                        API_URL,
                        data={"format": "json"},
                        files={
                            "input": (
                                "horizons_input.txt",
                                request_text.encode("ascii"),
                                "text/plain",
                            )
                        },
                        timeout=timeout,
                        headers={"User-Agent": "heliocentric-distance-chronology/0.9.2"},
                    )
                    response.raise_for_status()
                    payload = response.json()
                    if "error" in payload:
                        raise RuntimeError(f"Horizons reported an error: {payload['error']}")
                    if "result" not in payload:
                        raise RuntimeError(f"Unexpected Horizons payload keys: {sorted(payload)}")
                    response_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                    break
                except Exception as exc:  # network/server failures need retry
                    last_error = exc
                    if attempt == retries:
                        raise RuntimeError(f"Horizons request failed after {retries} attempts") from exc
                    time.sleep(min(30.0, 2.0 ** attempt))
            else:  # pragma: no cover
                raise RuntimeError("Unreachable retry state") from last_error
            time.sleep(delay_seconds)

        result = str(payload["result"])
        samples = parse_horizons_result(result)
        if len(samples) != len(values):
            raise RuntimeError(
                "Horizons returned an incomplete TLIST response: "
                f"requested {len(values)} epochs but parsed {len(samples)}. "
                "The cached response is retained for diagnosis; do not use the "
                "result for root generation."
            )
        expected_first = float(values[0])
        expected_last = float(values[-1])
        if (
            abs(samples[0].jd_tdb - expected_first) > 1e-6
            or abs(samples[-1].jd_tdb - expected_last) > 1e-6
        ):
            raise RuntimeError(
                "Horizons TLIST boundary mismatch: "
                f"requested {expected_first:.9f}..{expected_last:.9f}, "
                f"received {samples[0].jd_tdb:.9f}..{samples[-1].jd_tdb:.9f}."
            )
        all_samples.extend(samples)
        signature = payload.get("signature", {})
        metadata_records.append(
            {
                "chunk": index,
                "points_requested": len(values),
                "first_jd": float(values[0]),
                "last_jd": float(values[-1]),
                "request_sha256": request_hash,
                "response_file": response_path.name,
                "response_sha256": sha256_file(response_path),
                "api_signature": signature,
            }
        )

    # Remove duplicate boundary samples introduced by chunking.
    unique: dict[float, Sample] = {round(sample.jd_tdb, 9): sample for sample in all_samples}
    ordered = sorted(unique.values(), key=lambda item: item.jd_tdb)
    (body_dir / "query_manifest.json").write_text(
        json.dumps(
            {
                "body_name": body_name,
                "body_id": body_id,
                "api_url": API_URL,
                "created_unix": time.time(),
                "chunks": metadata_records,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return ordered


def save_samples(path: Path, samples: Sequence[Sample]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["jd_tdb", "range_km"])
        writer.writerows((f"{s.jd_tdb:.12f}", f"{s.range_km:.6f}") for s in samples)


def load_samples(path: Path) -> list[Sample]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [Sample(float(row["jd_tdb"]), float(row["range_km"])) for row in reader]


def find_perihelia(samples: Sequence[Sample]) -> tuple[list[Perihelion], CubicSpline]:
    x = np.array([sample.jd_tdb for sample in samples], dtype=float)
    y = np.array([sample.range_km for sample in samples], dtype=float)
    if len(x) < 7:
        raise ValueError("At least seven outer-body samples are required")
    spline = CubicSpline(x, y)
    minima_indices = [i for i in range(1, len(y) - 1) if y[i] < y[i - 1] and y[i] <= y[i + 1]]
    perihelia: list[Perihelion] = []
    for orbit_index, i in enumerate(minima_indices):
        result = minimize_scalar(
            lambda value: float(spline(value)),
            bounds=(x[i - 1], x[i + 1]),
            method="bounded",
            options={"xatol": 1e-10},
        )
        perihelia.append(Perihelion(orbit_index, float(result.x), float(result.fun)))
    if len(perihelia) < 2:
        raise RuntimeError("Fewer than two outer-body perihelia detected; increase padding or interval")
    return perihelia, spline


def orbit_index_for_time(jd: float, perihelia: Sequence[Perihelion]) -> int:
    """Assign time to the revolution beginning at the most recent perihelion."""
    times = np.array([item.jd_tdb for item in perihelia])
    position = int(np.searchsorted(times, jd, side="right")) - 1
    if position < 0:
        return 0
    if position >= len(times):
        return len(times) - 1
    return position


def generate_roots(
    condition: str,
    inner_samples: Sequence[Sample],
    outer_samples: Sequence[Sample],
    nominal_start_jd: float,
    nominal_stop_jd: float,
    root_tolerance_days: float,
) -> list[RootRecord]:
    perihelia, outer_spline = find_perihelia(outer_samples)
    inner_x = np.array([sample.jd_tdb for sample in inner_samples], dtype=float)
    inner_y = np.array([sample.range_km for sample in inner_samples], dtype=float)
    inner_spline = CubicSpline(inner_x, inner_y)

    def components(jd: float) -> tuple[float, float, float, Perihelion]:
        orbit_idx = orbit_index_for_time(jd, perihelia)
        peri = perihelia[orbit_idx]
        outer = float(outer_spline(jd))
        inner = float(inner_spline(jd))
        return outer, outer - peri.q_km, inner, peri

    def fn_for_orbit(jd: float, orbit_idx: int) -> float:
        """Continuous root function within one outer-body revolution.

        The perihelion distance q changes between revolutions, so brackets must
        never cross a perihelion boundary.
        """
        outer = float(outer_spline(jd))
        inner = float(inner_spline(jd))
        return (outer - perihelia[orbit_idx].q_km) - inner

    grid = inner_x[(inner_x >= nominal_start_jd) & (inner_x <= nominal_stop_jd)]
    peri_times = np.array([item.jd_tdb for item in perihelia], dtype=float)
    peri_q = np.array([item.q_km for item in perihelia], dtype=float)

    # Evaluate four sub-intervals per native sample interval. This detects
    # short same-sign excursions containing two roots while remaining fully
    # vectorized over the multi-millennial series.
    subdivisions = 4
    lefts = grid[:-1]
    widths = grid[1:] - grid[:-1]
    dense_grid = np.empty(len(lefts) * subdivisions + 1, dtype=float)
    for offset in range(subdivisions):
        dense_grid[offset:-1:subdivisions] = lefts + (offset / subdivisions) * widths
    dense_grid[-1] = grid[-1]

    orbit_indices = np.searchsorted(peri_times, dense_grid, side="right") - 1
    orbit_indices = np.clip(orbit_indices, 0, len(perihelia) - 1).astype(int)
    values = outer_spline(dense_grid) - peri_q[orbit_indices] - inner_spline(dense_grid)

    same_orbit = orbit_indices[:-1] == orbit_indices[1:]
    sign_change = values[:-1] * values[1:] < 0.0
    exact_zero = values[:-1] == 0.0
    bracket_positions = np.flatnonzero(same_orbit & (sign_change | exact_zero))
    brackets: list[tuple[float, float, int]] = []
    for i in bracket_positions:
        if exact_zero[i]:
            brackets.append((float(dense_grid[i] - 1e-8), float(dense_grid[i] + 1e-8), int(orbit_indices[i])))
        else:
            brackets.append((float(dense_grid[i]), float(dense_grid[i + 1]), int(orbit_indices[i])))

    roots: list[float] = []
    for left, right, orbit_idx in brackets:
        try:
            root = float(
                brentq(
                    lambda jd, idx=orbit_idx: fn_for_orbit(jd, idx),
                    left,
                    right,
                    xtol=root_tolerance_days,
                    rtol=4 * np.finfo(float).eps,
                )
            )
        except ValueError:
            continue
        if nominal_start_jd <= root <= nominal_stop_jd:
            if not roots or abs(root - roots[-1]) > 1e-7:
                roots.append(root)

    records: list[RootRecord] = []
    per_orbit_counts: dict[int, int] = {}
    temp: list[tuple[float, float, float, float, float, Perihelion]] = []
    for root in roots:
        outer, delta_outer, inner, peri = components(root)
        residual = delta_outer - inner
        temp.append((root, outer, delta_outer, inner, residual, peri))
        per_orbit_counts[peri.orbit_index] = per_orbit_counts.get(peri.orbit_index, 0) + 1

    outer_name = CONDITIONS[condition]["outer"]
    for root, outer, delta_outer, inner, residual, peri in temp:
        date_text, astronomical_year, era, display_year, month, day, time_text, calendar = format_calendar(root)
        peri_date, *_ = format_calendar(peri.jd_tdb)
        radial_derivative = float(outer_spline(root, 1))
        phase = "Receding from perihelion" if radial_derivative >= 0 else "Approaching perihelion"
        records.append(
            RootRecord(
                condition=condition,
                jd_tdb=root,
                date_tdb=date_text,
                astronomical_year=astronomical_year,
                era=era,
                display_year=display_year,
                month=month,
                day=day,
                time_tdb=time_text,
                calendar=calendar,
                outer_body=outer_name,
                outer_orbit_index=peri.orbit_index,
                outer_phase=phase,
                perihelion_jd_tdb=peri.jd_tdb,
                perihelion_date_tdb=peri_date,
                perihelion_q_km=peri.q_km,
                outer_distance_km=outer,
                delta_outer_km=delta_outer,
                inner_distance_km=inner,
                residual_km=residual,
                roots_in_orbit=per_orbit_counts[peri.orbit_index],
            )
        )
    return records


def write_roots(path: Path, records: Sequence[RootRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(RootRecord.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = asdict(record)
            for key, value in row.items():
                if isinstance(value, float):
                    row[key] = f"{value:.12f}"
            writer.writerow(row)


def read_roots(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_control(root_dir: Path, tolerance_seconds: float = 120.0) -> dict[str, object]:
    report: dict[str, object] = {"tolerance_seconds": tolerance_seconds, "checks": []}
    for condition, expected_text in EXPECTED_CONTROL.items():
        path = root_dir / f"roots_{condition}.csv"
        if not path.exists():
            report["checks"].append({"condition": condition, "status": "missing", "path": str(path)})
            continue
        expected_parts = re.fullmatch(r"BCE\s+(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)", expected_text)
        assert expected_parts
        display_year, month, day, hour, minute, second = map(int, expected_parts.groups())
        expected_jd = julian_calendar_to_jd(1 - display_year, month, day, hour, minute, second)
        candidates = read_roots(path)
        if not candidates:
            report["checks"].append({"condition": condition, "status": "empty"})
            continue
        nearest = min(candidates, key=lambda row: abs(float(row["jd_tdb"]) - expected_jd))
        delta_seconds = abs(float(nearest["jd_tdb"]) - expected_jd) * 86400.0
        report["checks"].append(
            {
                "condition": condition,
                "expected": expected_text,
                "nearest": nearest.get("date_tdb"),
                "delta_seconds": delta_seconds,
                "status": "pass" if delta_seconds <= tolerance_seconds else "fail",
            }
        )
    count_18 = None
    path_18 = root_dir / "roots_1_8.csv"
    if path_18.exists():
        rows = read_roots(path_18)
        count_18 = sum(1 for row in rows if row["era"] == "BCE" and int(row["display_year"]) == 139)
        report["checks"].append(
            {"condition": "1_8_count_139_BCE", "expected": 8, "observed": count_18, "status": "pass" if count_18 == 8 else "fail"}
        )
    report["overall_status"] = (
        "pass" if report["checks"] and all(item.get("status") == "pass" for item in report["checks"]) else "incomplete_or_fail"
    )
    return report


def run_condition(args: argparse.Namespace, condition: str) -> None:
    config = CONDITIONS[condition]
    nominal_start = parse_year_date(args.start)
    nominal_stop = parse_year_date(args.stop)
    padded_start = nominal_start - float(config["padding_days"])
    padded_stop = nominal_stop + float(config["padding_days"])
    inner_step = float(config["inner_step_days"])
    outer_step = float(config["outer_step_days"])

    cache_dir = args.cache_dir / condition
    series_dir = args.work_dir / "series" / condition
    root_dir = args.output_dir
    series_dir.mkdir(parents=True, exist_ok=True)
    root_dir.mkdir(parents=True, exist_ok=True)

    outer_grid = make_tlist(padded_start, padded_stop, outer_step)
    inner_grid = make_tlist(nominal_start, nominal_stop, inner_step)

    inner_path = series_dir / f"{config['inner']}.csv"
    outer_path = series_dir / f"{config['outer']}.csv"

    if args.reuse_series and inner_path.exists():
        inner_samples = load_samples(inner_path)
    else:
        inner_samples = fetch_body_series(
            str(config["inner"]), inner_grid, cache_dir, chunk_size=args.chunk_size, offline=args.offline
        )
        save_samples(inner_path, inner_samples)

    if args.reuse_series and outer_path.exists():
        outer_samples = load_samples(outer_path)
    else:
        outer_samples = fetch_body_series(
            str(config["outer"]), outer_grid, cache_dir, chunk_size=args.chunk_size, offline=args.offline
        )
        save_samples(outer_path, outer_samples)

    records = generate_roots(
        condition,
        inner_samples,
        outer_samples,
        nominal_start,
        nominal_stop,
        root_tolerance_days=args.root_tolerance_days,
    )
    output_path = root_dir / f"roots_{condition}.csv"
    write_roots(output_path, records)
    logging.info("%s: wrote %s roots to %s", condition, len(records), output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conditions", nargs="+", choices=sorted(CONDITIONS), default=sorted(CONDITIONS))
    parser.add_argument("--start", default="-3999-01-01", help="Astronomical year date; -3999 = 4000 BCE")
    parser.add_argument("--stop", default="2026-08-03", help="Astronomical year date")
    parser.add_argument("--cache-dir", type=Path, default=Path("cache/horizons"))
    parser.add_argument("--work-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/root_catalogue"))
    parser.add_argument("--chunk-size", type=int, default=5000, help="TLIST values per Horizons request (max 10000)")
    parser.add_argument("--root-tolerance-days", type=float, default=1e-9)
    parser.add_argument("--offline", action="store_true", help="Require cached Horizons responses")
    parser.add_argument("--reuse-series", action="store_true", help="Reuse generated range CSV files")
    parser.add_argument("--validate-control", action="store_true")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s %(levelname)s %(message)s")
    if args.chunk_size < 2 or args.chunk_size > 10_000:
        raise SystemExit("--chunk-size must be between 2 and 10000")
    for directory in (args.cache_dir, args.work_dir, args.output_dir):
        directory.mkdir(parents=True, exist_ok=True)
    for condition in args.conditions:
        run_condition(args, condition)
    manifest = {
        "script": Path(__file__).name,
        "script_sha256": sha256_file(Path(__file__)),
        "conditions": args.conditions,
        "start": args.start,
        "stop": args.stop,
        "root_tolerance_days": args.root_tolerance_days,
        "body_ids": BODY_IDS,
        "condition_config": CONDITIONS,
    }
    (args.output_dir / "generation_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if args.validate_control:
        report = validate_control(args.output_dir)
        report_path = args.work_dir / "control_case_validation.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0 if report["overall_status"] == "pass" else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
