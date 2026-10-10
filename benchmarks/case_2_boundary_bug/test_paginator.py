import pytest
from paginator import paginate


def test_normal_pagination():
    data = [1, 2, 3, 4, 5]
    assert paginate(data, page=1, page_size=2) == [1, 2]
    assert paginate(data, page=2, page_size=2) == [3, 4]
    assert paginate(data, page=3, page_size=2) == [5]


def test_empty_list_boundary():
    # Should return empty list, but currently raises IndexError
    assert paginate([], page=1, page_size=10) == []
