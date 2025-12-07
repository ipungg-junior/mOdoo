
# Rupiah Formatting Utility
def format_rupiah(amount):
    """Format a number into Indonesian Rupiah currency format.

    Args:
        amount (float or int): The amount of money to format.

    Returns:
        str: The formatted currency string in Rupiah.
    """
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        raise ValueError("Invalid amount. Please provide a numeric value.")

    is_negative = amount < 0
    amount = abs(amount)

    # Format the number with thousands separator and two decimal places
    formatted_amount = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    if is_negative:
        return f"{formatted_amount}"
    else:
        return f"{formatted_amount}"