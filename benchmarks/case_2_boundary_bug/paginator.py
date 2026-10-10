from typing import List, Any


def paginate(items: List[Any], page: int, page_size: int) -> List[Any]:
    """Returns items for the specified 1-based page number."""
    if page_size <= 0:
        raise ValueError('page_size must be positive')
    if page < 1:
        raise ValueError('page must be >= 1')
    if len(items) == 0:
        return []
    start = (page - 1) * page_size
    return items[start:start + page_size]
