"""Lab 7 - Fuzz testing loan_eligibility.py with Hypothesis.

Name: Pramiti Udupa
SRN:  PES1UG24CS331

Each function gets three kinds of property:
  1. no-crash fuzzing on arbitrary text / None (the handout's pattern),
  2. no-crash fuzzing on values of the wrong type,
  3. behaviour properties: valid input gives the right answer and
     invalid input is rejected by returning None.
The @example decorators pin the edge cases that the fuzzer found, so they
are re-checked on every run.
"""
from hypothesis import example, given, settings, strategies as st

from loan_eligibility import CATEGORIES, monthly_emi, pan_category, parse_income

FUZZ = settings(max_examples=300, deadline=None)

# Values of the wrong type that a caller could pass by mistake.
NON_STRINGS = (st.integers() | st.floats() | st.booleans() | st.binary()
               | st.lists(st.text(), max_size=3)
               | st.dictionaries(st.text(), st.integers(), max_size=2))

LETTERS = st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGITS = st.sampled_from("0123456789")


@st.composite
def valid_pans(draw):
    """PAN layout: 3 letters, category letter, letter, 4 digits, letter."""
    head = "".join(draw(st.lists(LETTERS, min_size=3, max_size=3)))
    cat = draw(st.sampled_from(sorted(CATEGORIES)))
    fifth = draw(LETTERS)
    nums = "".join(draw(st.lists(DIGITS, min_size=4, max_size=4)))
    last = draw(LETTERS)
    return head + cat + fifth + nums + last


# ----------------------------------------------------------------------
# parse_income
# ----------------------------------------------------------------------
@FUZZ
@given(st.text() | st.none())
@example(None)
@example("")
@example("fifty thousand")
@example("1,,3")
@example("-5,000")
@example("9" * 5000)
def test_parse_income_no_crash(s):
    try:
        result = parse_income(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_income crashed with: {e!r}"
    assert result is None or (isinstance(result, int) and result >= 0)


@FUZZ
@given(NON_STRINGS)
def test_parse_income_wrong_type_no_crash(value):
    try:
        result = parse_income(value)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_income crashed on {type(value).__name__}: {e!r}"
    assert result is None


@FUZZ
@given(st.integers(min_value=0, max_value=10**12),
       st.sampled_from(["", " ", "  "]))
def test_parse_income_valid_values(n, pad):
    assert parse_income(str(n)) == n
    assert parse_income(f"{n:,}") == n
    assert parse_income(f"{pad}{n:,}{pad}") == n


@FUZZ
@given(st.text(min_size=1).filter(lambda t: not any(c in "0123456789" for c in t)))
def test_parse_income_rejects_text_without_digits(s):
    assert parse_income(s) is None


@FUZZ
@given(st.integers(min_value=1, max_value=10**9))
def test_parse_income_rejects_negative(n):
    assert parse_income(f"-{n}") is None


# ----------------------------------------------------------------------
# monthly_emi
# ----------------------------------------------------------------------
@FUZZ
@given(st.text() | st.none())
@example(None)
@example("")
@example("500000,10")
@example("500000,0,5")
@example("500000,10,0")
@example("500000,ten,5")
@example("500000,10.5,5")
@example("-500000,10,5")
@example("500000,10,999999999")
def test_monthly_emi_no_crash(s):
    try:
        result = monthly_emi(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"monthly_emi crashed with: {e!r}"
    assert result is None or (isinstance(result, float) and result > 0)


@FUZZ
@given(st.lists(st.integers(min_value=-10**6, max_value=10**6), max_size=4)
       .map(lambda xs: ",".join(map(str, xs))))
def test_monthly_emi_comma_separated_integers_no_crash(s):
    try:
        monthly_emi(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"monthly_emi crashed on {s!r}: {e!r}"


@FUZZ
@given(NON_STRINGS)
def test_monthly_emi_wrong_type_no_crash(value):
    try:
        result = monthly_emi(value)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"monthly_emi crashed on {type(value).__name__}: {e!r}"
    assert result is None


@FUZZ
@given(principal=st.integers(min_value=1000, max_value=10**9),
       rate=st.integers(min_value=0, max_value=50),
       years=st.integers(min_value=1, max_value=40))
@example(principal=500000, rate=10, years=5)
@example(principal=120000, rate=0, years=1)
def test_monthly_emi_valid_values(principal, rate, years):
    emi = monthly_emi(f"{principal},{rate},{years}")
    n = years * 12
    assert emi is not None
    # Total repaid must cover the principal; interest only adds to it.
    assert emi * n >= principal - 0.01 * n
    if rate == 0:
        assert emi == round(principal / n, 2)
    else:
        assert emi > principal / n - 0.01
    # The EMI can never be more than the whole principal plus one month's interest.
    assert emi <= principal * (1 + rate / 1200) + 0.01


@FUZZ
@given(principal=st.integers(min_value=-10**9, max_value=0),
       rate=st.integers(min_value=0, max_value=50),
       years=st.integers(min_value=1, max_value=40))
def test_monthly_emi_rejects_non_positive_principal(principal, rate, years):
    assert monthly_emi(f"{principal},{rate},{years}") is None


@FUZZ
@given(principal=st.integers(min_value=1000, max_value=10**9),
       rate=st.integers(min_value=0, max_value=50),
       years=st.integers(max_value=0))
def test_monthly_emi_rejects_non_positive_tenure(principal, rate, years):
    assert monthly_emi(f"{principal},{rate},{years}") is None


# ----------------------------------------------------------------------
# pan_category
# ----------------------------------------------------------------------
@FUZZ
@given(st.text() | st.none())
@example(None)
@example("")
@example("ABC")
@example("ABCXE1234F")
@example("ABCßE1234F")
def test_pan_category_no_crash(s):
    try:
        result = pan_category(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"pan_category crashed with: {e!r}"
    assert result is None or result in CATEGORIES.values()


@FUZZ
@given(NON_STRINGS)
def test_pan_category_wrong_type_no_crash(value):
    try:
        result = pan_category(value)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"pan_category crashed on {type(value).__name__}: {e!r}"
    assert result is None


@FUZZ
@given(valid_pans())
def test_pan_category_valid_pans(pan):
    expected = CATEGORIES[pan[3]]
    assert pan_category(pan) == expected
    assert pan_category(pan.lower()) == expected
    assert pan_category(f"  {pan}  ") == expected


@FUZZ
@given(valid_pans(), st.sampled_from(sorted(set("ABDEGIJKLMNOQRSTUVWXYZ"))))
def test_pan_category_rejects_unknown_category(pan, letter):
    assert pan_category(pan[:3] + letter + pan[4:]) is None


@FUZZ
@given(st.text(max_size=20).filter(lambda t: len(t.strip()) != 10))
def test_pan_category_rejects_wrong_length(s):
    assert pan_category(s) is None
