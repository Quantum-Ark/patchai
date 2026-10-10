def safe_divide(x: float, y: float) -> float:
    """Divide x by y. Needs to handle y == 0 by raising ValueError."""
    if y == 0:
        raise ValueError('Division by zero')
    return x / y
