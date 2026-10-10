import pytest
from pricing import calculate_tiered_price


def test_invalid_quantity_raises_value_error():
    """Reproduction test: negative or zero quantity must raise ValueError."""
    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        calculate_tiered_price(50.0, "standard", 0)

    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        calculate_tiered_price(50.0, "gold", -5)
