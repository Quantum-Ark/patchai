def calculate_tiered_price(base_price: float, tier: str, quantity: int) -> float:
    if quantity <= 0:
        raise ValueError('Quantity must be greater than 0')
    multiplier = 1.0
    if tier.lower() == 'gold':
        multiplier -= 0.20
    elif tier.lower() == 'silver':
        multiplier -= 0.10

    if quantity >= 10:
        multiplier -= 0.05

    return round(base_price * quantity * multiplier, 2)
