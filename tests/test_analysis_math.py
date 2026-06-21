"""Unit tests for the analysis math — the conversions the conclusions rest on.

These don't need the warehouse; they check the pure functions/constants so a
refactor can't silently change the energy-balance or uncertainty arithmetic.
"""

from __future__ import annotations

import math

from analysis import _common as c


def test_kcal_per_lb_constant() -> None:
    assert c.KCAL_PER_LB_FAT == 3500.0


def test_implied_fat_change_math() -> None:
    # 39,190 kcal deficit / 3500 ≈ 11.2 lb
    assert round(-39190 / c.KCAL_PER_LB_FAT, 1) == -11.2


def test_precision_band_propagation() -> None:
    # two independent scans, CV=1%: band = 1.96 * sqrt((cv*a)^2 + (cv*b)^2)
    band = c.lean_precision_band95(119.5, 127.9, cv=0.01)
    expected = 1.96 * math.sqrt((0.01 * 119.5) ** 2 + (0.01 * 127.9) ** 2)
    assert math.isclose(band, expected, rel_tol=1e-9)
    assert round(band, 2) == 3.43


def test_gallons_equivalent() -> None:
    # 7.4 lb lean == exactly one gallon of water by BodySpec's coefficient
    assert math.isclose(c.gallons_equivalent(7.4), 1.0, rel_tol=1e-9)


def test_newbie_muscle_bound_over_window() -> None:
    # 1 lb/week over 30 days ≈ 4.29 lb upper bound
    assert round(c.NEWBIE_MUSCLE_LB_PER_WEEK_MAX * (c.WINDOW_DAYS / 7.0), 2) == 4.29


def test_water_share_of_lean_gain() -> None:
    # +8.4 lb lean, <=4.29 real muscle -> remainder is water, a real share
    lean_delta = 8.4
    real = min(lean_delta, c.NEWBIE_MUSCLE_LB_PER_WEEK_MAX * (c.WINDOW_DAYS / 7.0))
    water = lean_delta - real
    assert water > 0
    assert round(100 * water / lean_delta) == 49
