import pytest
from pricing import calculate_tiered_price


def test_standard_tier():
    # 100 * 1 * 1.0 = 100.0
    assert calculate_tiered_price(100.0, "standard", 1) == 100.0


def test_gold_tier_discount():
    # 100 * 1 * 0.8 = 80.0
    assert calculate_tiered_price(100.0, "gold", 1) == 80.0


def test_silver_tier_volume_discount():
    # 100 * 10 * (1 - 0.10 - 0.05) = 100 * 10 * 0.85 = 850.0
    assert calculate_tiered_price(100.0, "silver", 10) == 850.0
