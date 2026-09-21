def suggest_price(
    product_name,
    category,
    quantity,
    location,
    quality_details,
):
    """
    Generate an advisory agricultural product price.

    This is an AI-assisted pricing heuristic for demonstration.
    The returned value is only a suggestion and never changes
    the seller's final product price automatically.
    """

    product_name = (product_name or "").strip().lower()
    category = (category or "").strip().lower()
    location = (location or "").strip().lower()
    quality_details = (quality_details or "").strip().lower()

    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValueError("Quantity must be a valid number.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0.")

    base_prices = {
        "rice": 50,
        "wheat": 40,
        "potato": 25,
        "tomato": 35,
        "onion": 30,
        "maize": 30,
        "corn": 30,
        "apple": 80,
        "mango": 70,
    }

    category_prices = {
        "grains": 40,
        "vegetables": 30,
        "fruits": 60,
        "pulses": 70,
        "spices": 100,
    }

    base_price = base_prices.get(
        product_name,
        category_prices.get(category, 50),
    )

    quality_multiplier = 1.0

    if any(
        word in quality_details
        for word in ("excellent", "premium", "high quality", "organic")
    ):
        quality_multiplier = 1.20
    elif any(
        word in quality_details
        for word in ("good", "fresh", "quality")
    ):
        quality_multiplier = 1.10
    elif any(
        word in quality_details
        for word in ("poor", "low quality")
    ):
        quality_multiplier = 0.85

    location_multiplier = 1.0

    if any(
        region in location
        for region in ("delhi", "mumbai", "bangalore", "bengaluru")
    ):
        location_multiplier = 1.05

    quantity_multiplier = 1.0

    if quantity >= 1000:
        quantity_multiplier = 0.90
    elif quantity >= 500:
        quantity_multiplier = 0.95
    elif quantity < 10:
        quantity_multiplier = 1.05

    suggested_price = (
        base_price
        * quality_multiplier
        * location_multiplier
        * quantity_multiplier
    )

    return round(max(suggested_price, 1), 2)