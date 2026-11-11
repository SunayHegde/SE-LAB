from hypothesis import given, settings, strategies as st
from restaurant_bill_parser import clean_dish_name, parse_item_prices, split_amount

# Strategies: random Unicode text, None, plus inputs shaped like real
# user input so Hypothesis also explores the "almost valid" cases
# (empty items, spaces, decimals, zero/negative people, extra slashes).
price_like = st.lists(
    st.one_of(st.integers(-1000, 100000).map(str), st.just(""),
              st.just(" "), st.just("12.5"), st.just("abc")),
    max_size=6,
).map(",".join)

split_like = st.builds(
    lambda a, b, extra: f"{a}/{b}" + extra,
    st.one_of(st.integers(-1000, 100000).map(str), st.just(""), st.just("12.5")),
    st.one_of(st.integers(-5, 20).map(str), st.just(""), st.just("x")),
    st.sampled_from(["", "/2", " "]),
)


@settings(max_examples=300)
@given(st.text() | st.none())
def test_clean_dish_name_no_crash(s):
    try:
        result = clean_dish_name(s)
    except Exception as e:
        assert False, f"clean_dish_name crashed with: {e!r}"
    assert isinstance(result, str)
    assert not any(ch in result for ch in "*#~")


@settings(max_examples=300)
@given(st.text() | st.none() | price_like)
def test_parse_item_prices_no_crash(s):
    try:
        result = parse_item_prices(s)
    except Exception as e:
        assert False, f"parse_item_prices crashed with: {e!r}"
    assert isinstance(result, list)
    assert all(isinstance(p, int) and p >= 0 for p in result)


@settings(max_examples=300)
@given(st.text() | st.none() | split_like)
def test_split_amount_no_crash(s):
    try:
        result = split_amount(s)
    except Exception as e:
        assert False, f"split_amount crashed with: {e!r}"
    assert result is None or (isinstance(result, int) and result >= 0)
