"""Branch coverage tests for loan_eligibility.py.

Lab 6 - Code and Branch Coverage
Name : Pramiti Udupa
SRN  : PES1UG24CS331

Goal: make every decision (if / elif / else) in loan_eligibility.py go both
ways (True and False), and check the boundary values of each condition.

Run:
    coverage run --branch -m pytest BranchCoverageTest_PES1UG24CS331_loan_eligibility.py
    coverage report -m

The code coverage tests reached 100% statement coverage but left two partial
branches in interest_rate():
    36->38  "employment == 'self_employed'" was never False
    38->40  "has_collateral" was never False
The tests below take those branches as well, and also cover the boundary
values that statement coverage does not need.
"""
import pytest

from loan_eligibility import MIN_INCOME, credit_band, is_eligible, interest_rate


# ---------------------------------------------------------------------------
# Starter test cases given with the assignment
# ---------------------------------------------------------------------------
def test_excellent_band():
    assert credit_band(800) == "excellent"


def test_eligible():
    assert is_eligible(30, 50000, "salaried", 800) is True


# ---------------------------------------------------------------------------
# credit_band()
#   line 5 : score < 300 or score > 900   -> True (raise) / False
#   line 7 : score >= 750                  -> True / False
#   line 9 : score >= 650                  -> True / False
#   line 11: score >= 550                  -> True / False
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("score", [0, 299, 901, 1000, -50])
def test_credit_band_invalid_scores_raise(score):
    # Both halves of the "or": below 300 and above 900
    with pytest.raises(ValueError, match="invalid score"):
        credit_band(score)


@pytest.mark.parametrize(
    "score, expected",
    [
        (300, "poor"),        # lowest valid score
        (549, "poor"),        # just below "fair"
        (550, "fair"),        # "fair" lower boundary
        (649, "fair"),        # just below "good"
        (650, "good"),        # "good" lower boundary
        (749, "good"),        # just below "excellent"
        (750, "excellent"),   # "excellent" lower boundary
        (900, "excellent"),   # highest valid score
    ],
)
def test_credit_band_boundaries(score, expected):
    assert credit_band(score) == expected


# ---------------------------------------------------------------------------
# is_eligible()
#   line 17: employment not in MIN_INCOME      -> True (raise) / False
#   line 19: age < 21 or age > 60              -> True / False
#   line 21: income < MIN_INCOME[employment]   -> True / False
#   line 23: credit_band(score) == "poor"      -> True / False
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("employment", ["student", "unemployed", "", "Salaried"])
def test_unknown_employment_raises(employment):
    with pytest.raises(ValueError, match="unknown employment"):
        is_eligible(30, 50000, employment, 800)


def test_unknown_employment_checked_before_age():
    # The employment check comes first, so a bad age does not hide it
    with pytest.raises(ValueError, match="unknown employment"):
        is_eligible(10, 50000, "retired", 800)


@pytest.mark.parametrize("age", [18, 20, 61, 75])
def test_age_out_of_range_not_eligible(age):
    assert is_eligible(age, 50000, "salaried", 800) is False


@pytest.mark.parametrize("age", [21, 40, 60])
def test_age_in_range_eligible(age):
    # 21 and 60 are the inclusive limits
    assert is_eligible(age, 50000, "salaried", 800) is True


@pytest.mark.parametrize("employment", ["salaried", "self_employed"])
def test_income_just_below_minimum_not_eligible(employment):
    income = MIN_INCOME[employment] - 1
    assert is_eligible(30, income, employment, 800) is False


@pytest.mark.parametrize("employment", ["salaried", "self_employed"])
def test_income_at_minimum_eligible(employment):
    income = MIN_INCOME[employment]
    assert is_eligible(30, income, employment, 800) is True


def test_self_employed_needs_higher_income():
    # 30000 is enough for salaried (25000) but not self_employed (40000)
    assert is_eligible(30, 30000, "salaried", 800) is True
    assert is_eligible(30, 30000, "self_employed", 800) is False


@pytest.mark.parametrize("score", [300, 549])
def test_poor_credit_not_eligible(score):
    assert is_eligible(30, 50000, "salaried", score) is False


@pytest.mark.parametrize("score", [550, 650, 750])
def test_fair_good_excellent_credit_eligible(score):
    assert is_eligible(30, 50000, "self_employed", score) is True


def test_invalid_score_raises_from_is_eligible():
    # credit_band() is only reached after age and income pass
    with pytest.raises(ValueError, match="invalid score"):
        is_eligible(30, 50000, "salaried", 950)


def test_age_rejected_before_score_is_checked():
    # An invalid score is never looked at when the age already fails
    assert is_eligible(65, 50000, "salaried", 950) is False


# ---------------------------------------------------------------------------
# interest_rate()
#   line 30: band == "excellent"         -> True / False
#   line 32: band == "good"              -> True / False (else: fair / poor)
#   line 36: employment == "self_employed" -> True / False
#   line 38: has_collateral              -> True / False
# All 4 bands x 2 employment types x 2 collateral values = 16 combinations.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "score, employment, has_collateral, expected",
    [
        (800, "salaried", False, 8),
        (800, "salaried", True, 6),
        (800, "self_employed", False, 9),
        (800, "self_employed", True, 7),
        (700, "salaried", False, 10),
        (700, "salaried", True, 8),
        (700, "self_employed", False, 11),
        (700, "self_employed", True, 9),
        (600, "salaried", False, 13),
        (600, "salaried", True, 11),
        (600, "self_employed", False, 14),
        (600, "self_employed", True, 12),
        (400, "salaried", False, 13),
        (400, "salaried", True, 11),
        (400, "self_employed", False, 14),
        (400, "self_employed", True, 12),
    ],
)
def test_interest_rate_all_combinations(score, employment, has_collateral, expected):
    assert interest_rate(score, employment, has_collateral) == expected


@pytest.mark.parametrize(
    "score, expected",
    [(750, 8), (749, 10), (650, 10), (649, 13), (550, 13), (549, 13)],
)
def test_interest_rate_band_boundaries(score, expected):
    assert interest_rate(score, "salaried", False) == expected


@pytest.mark.parametrize("has_collateral", [0, None, ""])
def test_interest_rate_falsy_collateral_gives_no_discount(has_collateral):
    assert interest_rate(800, "salaried", has_collateral) == 8


def test_interest_rate_invalid_score_raises():
    with pytest.raises(ValueError, match="invalid score"):
        interest_rate(100, "salaried", True)
