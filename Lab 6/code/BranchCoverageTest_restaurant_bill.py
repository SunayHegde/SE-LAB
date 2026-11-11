"""Branch coverage tests for restaurant_bill.py.

Goal: make every decision evaluate to both True and False, including
each operand of the compound `or` / `and` conditions and the boundary
values (guests 7/8, party 12/13, free tables 1/2, party size 6/7).
"""
import pytest
from restaurant_bill import bill_total, split_bill, table_wait


# ---------- bill_total ----------
# Decision 1: section not in SERVICE_CHARGE

def test_section_unknown_true():
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("patio", 1000, 2, False)


@pytest.mark.parametrize("section, expected", [
    ("dine_in", 1155),   # 10% service
    ("takeaway", 1050),  # 0% service
    ("rooftop", 1207),   # 15% service: 1150 + 57
])
def test_section_known_false(section, expected):
    assert bill_total(section, 1000, 2, False) == expected


# Decision 2: food_total < 0 or guests < 1

def test_food_total_negative():
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -1, 2, False)


def test_guests_zero():
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", 1000, 0, False)


def test_valid_order_boundaries():
    # food_total == 0 and guests == 1 are both allowed
    assert bill_total("dine_in", 0, 1, False) == 0


# Decision 3: is_happy_hour and section != "takeaway"

def test_happy_hour_dine_in_discounted():
    # 1000 -> 800, service 80, total 880, tax 44
    assert bill_total("dine_in", 1000, 2, True) == 924


def test_happy_hour_takeaway_not_discounted():
    # takeaway is excluded from the happy-hour discount
    assert bill_total("takeaway", 1000, 2, True) == 1050


def test_no_happy_hour_not_discounted():
    assert bill_total("dine_in", 1000, 2, False) == 1155


# Decision 4: guests >= 8

def test_guests_eight_extra_service():
    assert bill_total("dine_in", 1000, 8, False) == 1365


def test_guests_seven_no_extra_service():
    assert bill_total("dine_in", 1000, 7, False) == 1155


def test_takeaway_large_party_still_charged():
    # 0% service but +200 for 8+ guests: 1200 + 60
    assert bill_total("takeaway", 1000, 8, False) == 1260


def test_all_branches_true_together():
    # rooftop happy hour, 10 guests: 500 -> 400, service 60 + 200,
    # total 660, tax 33
    assert bill_total("rooftop", 500, 10, True) == 693


# ---------- split_bill ----------
# Decision 5: people < 1

def test_people_zero_raises():
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(1000, 0, 10)


def test_one_person_pays_all():
    assert split_bill(1000, 1, 0) == 1000


# Decision 6: tip_percent < 0

def test_negative_tip_raises():
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(1000, 2, -1)


def test_zero_tip_allowed():
    assert split_bill(1000, 2, 0) == 500


# Decision 7: grand_total % people != 0

def test_even_split_no_round_up():
    assert split_bill(1000, 4, 10) == 275


def test_uneven_split_rounds_up():
    assert split_bill(1000, 3, 0) == 334


# ---------- table_wait ----------
# Decision 8: party_size > 12

def test_party_thirteen_call_ahead():
    assert table_wait(13, 5, False) == "call ahead"


def test_party_twelve_not_call_ahead():
    assert table_wait(12, 5, False) == "seat now"


# Decision 9: has_reservation

def test_reservation_seat_now_even_with_no_tables():
    assert table_wait(4, 0, True) == "seat now"


def test_no_reservation_goes_on_to_table_check():
    assert table_wait(4, 0, False) == "waitlist"


# Decision 10: free_tables == 0

def test_free_tables_one_not_waitlisted_for_small_party():
    assert table_wait(4, 1, False) == "seat now"


# Decision 11: party_size > 6 and free_tables < 2

def test_big_party_one_table_waitlist():
    assert table_wait(7, 1, False) == "waitlist"


def test_big_party_two_tables_seat_now():
    assert table_wait(7, 2, False) == "seat now"


def test_party_six_one_table_seat_now():
    assert table_wait(6, 1, False) == "seat now"
