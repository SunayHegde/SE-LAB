def _to_int(value):
    """Convert a string to an int, or return None if it is not a whole number."""
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        # ValueError: not a whole number (e.g. '', 'abc', '12.5', or a
        # string with more digits than Python's int() limit).
        return None


def clean_dish_name(name):
    """
    Removes the chef's-special markers (*, #, ~) and title-cases the name.
    Returns an empty string for None or any non-string input.
    """
    if not isinstance(name, str):
        return ""
    for ch in ['*', '#', '~']:
        name = name.replace(ch, '')
    return name.strip().title()


def parse_item_prices(text):
    """
    Parses comma-separated prices into a list of ints.
    Blank, non-numeric and negative entries are skipped.
    Returns an empty list for None or any non-string input.
    """
    if not isinstance(text, str):
        return []
    prices = []
    for part in text.split(','):
        price = _to_int(part)
        if price is not None and price >= 0:
            prices.append(price)
    return prices


def split_amount(text):
    """
    Splits 'TOTAL/PEOPLE' into the amount each person pays.
    Returns None if the input is not exactly two whole numbers separated
    by '/', if the total is negative, or if people is zero or negative.
    """
    if not isinstance(text, str):
        return None
    parts = text.split('/')
    if len(parts) != 2:
        return None
    total, people = _to_int(parts[0]), _to_int(parts[1])
    if total is None or people is None or total < 0 or people <= 0:
        return None
    return total // people


def main():
    print("==== Running clean_dish_name ====")
    value = input("Enter a dish name from the menu (e.g. *paneer tikka*): ")
    name = clean_dish_name(value)
    print("Dish name:", name if name else "(invalid dish name)")

    print("\n==== Running parse_item_prices ====")
    value = input("Enter item prices separated by commas (e.g. 250,180,320): ")
    print("Item prices:", parse_item_prices(value))

    print("\n==== Running split_amount ====")
    value = input("Enter the bill and number of people as TOTAL/PEOPLE (e.g. 1200/4): ")
    share = split_amount(value)
    if share is None:
        print("Invalid input: use TOTAL/PEOPLE with whole numbers and at least 1 person")
    else:
        print("Each person pays:", share)


if __name__ == "__main__":
    main()
