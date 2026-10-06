from decimal import Decimal, ROUND_HALF_UP


CENT = Decimal("0.01")
ONE_HUNDRED = Decimal("100")


def to_decimal(value):
    """Convert a value to Decimal without using float arithmetic."""
    if isinstance(value, Decimal):
        return value

    return Decimal(str(value))


def money(value):
    """Round a value to the nearest cent using standard half-up rounding."""
    return to_decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def line_total(quantity, unit_price):
    """Return the total for one invoice line."""
    quantity = to_decimal(quantity)
    unit_price = to_decimal(unit_price)

    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    if unit_price < 0:
        raise ValueError("Unit price cannot be negative.")

    return money(quantity * unit_price)


def calculate_subtotal(line_items):
    """Return the sum of all invoice line totals."""
    subtotal = Decimal("0.00")

    for item in line_items:
        subtotal += line_total(
            item["quantity"],
            item["unit_price"],
        )

    return money(subtotal)


def calculate_discount(subtotal, discount_percent):
    """Return the discount amount."""
    subtotal = money(subtotal)
    discount_percent = to_decimal(discount_percent)

    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount percent must be between 0 and 100.")

    discount = subtotal * discount_percent / ONE_HUNDRED
    return money(discount)


def calculate_tax(taxable_amount, tax_percent):
    """Return the tax amount."""
    taxable_amount = money(taxable_amount)
    tax_percent = to_decimal(tax_percent)

    if tax_percent < 0:
        raise ValueError("Tax percent cannot be negative.")

    tax = taxable_amount * tax_percent / ONE_HUNDRED
    return money(tax)


def calculate_invoice(line_items, discount_percent=0, tax_percent=0):
    """Calculate subtotal, discount, tax, and grand total."""
    subtotal = calculate_subtotal(line_items)

    discount = calculate_discount(
        subtotal,
        discount_percent,
    )

    taxable_amount = money(subtotal - discount)

    tax = calculate_tax(
        taxable_amount,
        tax_percent,
    )

    grand_total = money(taxable_amount + tax)

    return {
        "subtotal": subtotal,
        "discount": discount,
        "taxable_amount": taxable_amount,
        "tax": tax,
        "grand_total": grand_total,
    }