"""Code (line/statement) coverage tests for loan_eligibility.py.

Lab 6 - Code and Branch Coverage
Name : Pramiti Udupa
SRN  : PES1UG24CS331

Goal: execute every statement of loan_eligibility.py at least once.

Run:
    coverage run -m pytest CodeCoverageTest_PES1UG24CS331_loan_eligibility.py
    coverage report -m

These tests reach 100% statement coverage. They deliberately do not try to
take every decision both ways, so a branch-coverage run
(coverage run --branch ...) still shows partial branches. The branch
coverage test file adds the tests for those.
"""
import pytest

from loan_eligibility import credit_band, is_eligible, interest_rate


# ---------------------------------------------------------------------------
# Starter test cases given with the assignment
# ---------------------------------------------------------------------------
def test_excellent_band():
    assert credit_band(800) == "excellent"


def test_eligible():
    assert is_eligible(30, 50000, "salaried", 800) is True


# ---------------------------------------------------------------------------
# credit_band(): reach every return statement and the raise
# ---------------------------------------------------------------------------
def test_invalid_score_raises():
    # Line 6: a score outside 300..900 raises ValueError
    with pytest.raises(ValueError, match="invalid score"):
        credit_band(250)


def test_good_band():
    # Line 10
    assert credit_band(700) == "good"


def test_fair_band():
    # Line 12
    assert credit_band(600) == "fair"


def test_poor_band():
    # Line 13
    assert credit_band(400) == "poor"


# ---------------------------------------------------------------------------
# is_eligible(): reach every return / raise statement
# ---------------------------------------------------------------------------
def test_unknown_employment_raises():
    # Line 18
    with pytest.raises(ValueError, match="unknown employment"):
        is_eligible(30, 50000, "student", 800)


def test_underage_not_eligible():
    # Line 20
    assert is_eligible(18, 50000, "salaried", 800) is False


def test_low_income_not_eligible():
    # Line 22
    assert is_eligible(30, 20000, "salaried", 800) is False


def test_poor_credit_not_eligible():
    # Line 24
    assert is_eligible(30, 50000, "salaried", 400) is False


# ---------------------------------------------------------------------------
# interest_rate(): reach every rate assignment and both adjustments
# ---------------------------------------------------------------------------
def test_rate_excellent_self_employed_with_collateral():
    # Lines 29-31, 36-40: 8 + 1 - 2
    assert interest_rate(800, "self_employed", True) == 7


def test_rate_good_self_employed_with_collateral():
    # Lines 32-33: 10 + 1 - 2
    assert interest_rate(700, "self_employed", True) == 9


def test_rate_fair_self_employed_with_collateral():
    # Lines 34-35: 13 + 1 - 2
    assert interest_rate(600, "self_employed", True) == 12
