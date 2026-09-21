from price_suggestion import suggest_price


def test_suggest_price_returns_positive_value():
    price = suggest_price(
        product_name="Rice",
        category="Grains",
        quantity=100,
        location="Delhi",
        quality_details="Fresh and good quality",
    )

    assert price > 0


def test_suggest_price_handles_premium_quality():
    normal_price = suggest_price(
        product_name="Rice",
        category="Grains",
        quantity=100,
        location="Delhi",
        quality_details="Good quality",
    )

    premium_price = suggest_price(
        product_name="Rice",
        category="Grains",
        quantity=100,
        location="Delhi",
        quality_details="Premium organic quality",
    )

    assert premium_price > normal_price


def test_suggest_price_rejects_invalid_quantity():
    try:
        suggest_price(
            product_name="Rice",
            category="Grains",
            quantity=-10,
            location="Delhi",
            quality_details="Good quality",
        )
        assert False
    except ValueError as error:
        assert str(error) == "Quantity must be greater than 0."