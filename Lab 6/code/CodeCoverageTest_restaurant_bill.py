"""Code (line) coverage tests for restaurant_bill.py.

Goal: execute every line of restaurant_bill.py at least once.
"""
import pytest
from restaurant_bill import bill_total, split_bill, table_wait


# ---------- bill_total ----------

def test_dine_in_bill():
    # service 10% = 100, total 1100, tax 5% = 55
    assert bill_total("dine_in", 1000, 2, False) == 1155


def test_unknown_section_raises():
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("patio", 1000, 2, False)


def test_negative_food_total_raises():
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -1, 2, False)


def test_happy_hour_discount_dine_in():
    # food 1000 -> 800, service 80, total 880, tax 44
    assert bill_total("dine_in", 1000, 2, True) == 924


def test_large_party_extra_service():
    # service 100 + 200 large-party charge, total 1300, tax 65
    assert bill_total("dine_in", 1000, 8, False) == 1365


# ---------- split_bill ----------

def test_even_split():
    assert split_bill(1000, 4, 10) == 275


def test_split_zero_people_raises():
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(1000, 0, 10)


def test_split_negative_tip_raises():
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(1000, 2, -5)


def test_uneven_split_rounds_up():
    # 1000 / 3 = 333 remainder 1 -> 334
    assert split_bill(1000, 3, 0) == 334


# ---------- table_wait ----------

def test_very_large_party_call_ahead():
    assert table_wait(13, 5, False) == "call ahead"


def test_reservation_seated_now():
    assert table_wait(4, 0, True) == "seat now"


def test_no_free_tables_waitlist():
    assert table_wait(4, 0, False) == "waitlist"


def test_big_party_one_table_waitlist():
    assert table_wait(8, 1, False) == "waitlist"


def test_small_party_free_table_seated():
    assert table_wait(4, 3, False) == "seat now"
