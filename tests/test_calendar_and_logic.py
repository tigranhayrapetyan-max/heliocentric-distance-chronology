from __future__ import annotations
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from horizons_root_generation import (  # noqa: E402
    format_calendar,
    gregorian_calendar_to_jd,
    julian_calendar_to_jd,
    parse_year_date,
)
from circular_shift_validation_from_csv import merge_intervals  # noqa: E402


def test_j2000_epoch():
    assert math.isclose(gregorian_calendar_to_jd(2000, 1, 1, 12), 2451545.0)


def test_astronomical_bce_roundtrip():
    jd = julian_calendar_to_jd(-138, 2, 6, 2, 30, 31)
    text, year, era, display_year, month, day, time_text, calendar = format_calendar(jd)
    assert year == -138
    assert era == "BCE"
    assert display_year == 139
    assert (month, day) == (2, 6)
    assert time_text == "02:30:31"
    assert calendar == "Julian"
    assert text.startswith("0139 BCE-02-06")


def test_parse_astronomical_date():
    assert math.isclose(parse_year_date("-0138-02-06"), julian_calendar_to_jd(-138, 2, 6))


def test_merge_intervals():
    assert merge_intervals([(3, 5), (1, 2), (2, 4), (8, 9)]) == [(1, 5), (8, 9)]


def test_horizons_input_contains_all_requested_epochs():
    from horizons_root_generation import horizons_input
    values = [2451545.0 + i * 0.25 for i in range(137)]
    text = horizons_input("1", values)
    tlist_line = next(line for line in text.splitlines() if line.startswith("TLIST="))
    assert tlist_line.count("'") == 2 * len(values)
    for value in (values[0], values[80], values[-1]):
        assert f"'{value:.9f}'" in tlist_line
