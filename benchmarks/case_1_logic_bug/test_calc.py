import pytest
from calc import safe_divide


def test_normal_division():
    assert safe_divide(10.0, 2.0) == 5.0


def test_division_by_zero_raises_value_error():
    with pytest.raises(ValueError, match="Division by zero"):
        safe_divide(10.0, 0.0)
