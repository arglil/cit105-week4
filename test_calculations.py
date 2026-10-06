from decimal import Decimal

import pytest

from calculations import (
    calculate_discount,
    calculate_invoice,
    calculate_subtotal,
    line_total,
    money,
)


def test_normal_invoice_calculation():
    """Normal invoice calculates subtotal, discount, tax, and total."""
    items = [
        {
            "quantity": Decimal("2"),
            "unit_price": Decimal("25.00"),
        },
        {
            "quantity": Decimal("1"),
            "unit_price": Decimal("50.00"),
        },
    ]

    result = calculate_invoice(
        items,
        discount_percent=Decimal("10"),
        tax_percent=Decimal("7"),
    )

    assert result["subtotal"] == Decimal("100.00")
    assert result["discount"] == Decimal("10.00")
    assert result["taxable_amount"] == Decimal("90.00")
    assert result["tax"] == Decimal("6.30")
    assert result["grand_total"] == Decimal("96.30")


def test_empty_invoice():
    """An invoice with no line items should total zero."""
    result = calculate_invoice(
        [],
        discount_percent=Decimal("0"),
        tax_percent=Decimal("7"),
    )

    assert result["subtotal"] == Decimal("0.00")
    assert result["grand_total"] == Decimal("0.00")


def test_zero_quantity():
    """A line item with zero quantity should have a zero total."""
    result = line_total(
        Decimal("0"),
        Decimal("99.99"),
    )

    assert result == Decimal("0.00")


def test_negative_quantity_rejected():
    """Negative quantities should raise an error."""
    with pytest.raises(ValueError):
        line_total(
            Decimal("-1"),
            Decimal("25.00"),
        )


def test_half_cent_rounding():
    """An exact half-cent should round up to the nearest cent."""
    result = money(Decimal("10.005"))

    assert result == Decimal("10.01")


def test_one_hundred_percent_discount():
    """A 100 percent discount should reduce the final total to zero."""
    items = [
        {
            "quantity": Decimal("1"),
            "unit_price": Decimal("125.00"),
        }
    ]

    result = calculate_invoice(
        items,
        discount_percent=Decimal("100"),
        tax_percent=Decimal("7"),
    )

    assert result["discount"] == Decimal("125.00")
    assert result["taxable_amount"] == Decimal("0.00")
    assert result["tax"] == Decimal("0.00")
    assert result["grand_total"] == Decimal("0.00")


def test_large_money_value_keeps_precision():
    """Large currency values should remain exact with Decimal."""
    items = [
        {
            "quantity": Decimal("1000000"),
            "unit_price": Decimal("999999999.99"),
        }
    ]

    subtotal = calculate_subtotal(items)

    assert subtotal == Decimal("999999999990000.00")


def test_discount_is_applied_before_tax():
    """Tax should be calculated from the discounted subtotal."""
    items = [
        {
            "quantity": Decimal("1"),
            "unit_price": Decimal("100.00"),
        }
    ]

    result = calculate_invoice(
        items,
        discount_percent=Decimal("10"),
        tax_percent=Decimal("10"),
    )

    assert result["subtotal"] == Decimal("100.00")
    assert result["discount"] == Decimal("10.00")
    assert result["taxable_amount"] == Decimal("90.00")
    assert result["tax"] == Decimal("9.00")
    assert result["grand_total"] == Decimal("99.00")


def test_discount_above_one_hundred_rejected():
    """Discounts greater than 100 percent should be rejected."""
    with pytest.raises(ValueError):
        calculate_discount(
            Decimal("100.00"),
            Decimal("101"),
        )