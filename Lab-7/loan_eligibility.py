"""Loan eligibility helpers, hardened against the inputs found by fuzz testing.

Lab 7 - Fuzzing for Input Validation Bugs
Name: Pramiti Udupa
SRN:  PES1UG24CS331

Every public function validates its input first and returns None when the
input is invalid, instead of raising an exception that would crash the caller.
"""
import math
import re

CATEGORIES = {"P": "Individual", "C": "Company", "H": "HUF", "F": "Firm"}

# Digits with optional comma grouping: "50000", "50,000", "5,00,000".
# Only ASCII digits are accepted, and commas must sit between digits.
INCOME_PATTERN = re.compile(r"[0-9]+(?:,[0-9]+)*")
MAX_INCOME_DIGITS = 15          # keeps int() far below Python's 4300-digit limit

PRINCIPAL_PATTERN = re.compile(r"[0-9]{1,13}")
RATE_PATTERN = re.compile(r"[0-9]{1,3}(?:\.[0-9]{1,4})?")
YEARS_PATTERN = re.compile(r"[0-9]{1,3}")
MIN_PRINCIPAL = 1_000
MAX_PRINCIPAL = 10**12
MAX_RATE = 100.0                # percent per annum
MAX_YEARS = 50

# PAN layout: 3 letters, category letter, letter, 4 digits, check letter.
PAN_PATTERN = re.compile(r"[A-Z]{3}[A-Z][A-Z][0-9]{4}[A-Z]")


def parse_income(income):
    """Return the income as a non-negative int, or None if it is invalid.

    Accepts "50000", "50,000" and Indian grouping such as "5,00,000",
    with optional surrounding whitespace.
    """
    if not isinstance(income, str):
        return None
    text = income.strip()
    if not INCOME_PATTERN.fullmatch(text):
        return None
    digits = text.replace(",", "")
    if len(digits) > MAX_INCOME_DIGITS:
        return None
    return int(digits)


def monthly_emi(details):
    """Return the monthly EMI for "principal,rate,years", or None if invalid.

    principal: whole rupees, MIN_PRINCIPAL to MAX_PRINCIPAL
    rate:      annual interest in percent, 0 to MAX_RATE (up to 4 decimals)
    years:     loan tenure, 1 to MAX_YEARS
    A 0% rate is valid and gives principal / months.
    """
    if not isinstance(details, str):
        return None
    parts = [part.strip() for part in details.split(",")]
    if len(parts) != 3:
        return None
    principal_text, rate_text, years_text = parts
    if not (PRINCIPAL_PATTERN.fullmatch(principal_text)
            and RATE_PATTERN.fullmatch(rate_text)
            and YEARS_PATTERN.fullmatch(years_text)):
        return None

    principal = int(principal_text)
    rate = float(rate_text)
    years = int(years_text)
    if not (MIN_PRINCIPAL <= principal <= MAX_PRINCIPAL
            and 0 <= rate <= MAX_RATE
            and 1 <= years <= MAX_YEARS):
        return None

    r = rate / 1200
    n = years * 12
    growth = (1 + r) ** n
    if r == 0 or growth == 1:
        # Zero (or vanishingly small) interest: the formula would divide by zero.
        emi = principal / n
    else:
        emi = principal * r * growth / (growth - 1)
    if not math.isfinite(emi) or emi <= 0:
        return None
    return round(emi, 2)


def pan_category(pan):
    """Return the holder category for a PAN such as "ABCPE1234F", or None.

    The PAN must be 10 ASCII characters in the official layout (case and
    surrounding whitespace are ignored) and the 4th character must be one of
    the categories this system supports.
    """
    if not isinstance(pan, str):
        return None
    text = pan.strip()
    if not text.isascii():
        return None
    text = text.upper()
    if not PAN_PATTERN.fullmatch(text):
        return None
    return CATEGORIES.get(text[3])


def read_input(prompt):
    """input() that treats end-of-input as an empty answer instead of crashing."""
    try:
        return input(prompt)
    except EOFError:
        print()
        return ""


def main():
    """Ask for each value, run the matching function and print the result."""
    print("==== Running parse_income ====")
    user_input = read_input("Enter monthly income (e.g. 50,000): ")
    result = parse_income(user_input)
    if result is None:
        print("Invalid income: enter a whole number of rupees, e.g. 50,000")
    else:
        print("Income:", result)

    print("\n==== Running monthly_emi ====")
    user_input = read_input("Enter principal,rate,years (e.g. 500000,10,5): ")
    result = monthly_emi(user_input)
    if result is None:
        print(f"Invalid loan details: principal {MIN_PRINCIPAL:,}-{MAX_PRINCIPAL:,}, "
              f"rate 0-{MAX_RATE:g}%, years 1-{MAX_YEARS}, e.g. 500000,10,5")
    else:
        print("Monthly EMI:", result)

    print("\n==== Running pan_category ====")
    user_input = read_input("Enter a PAN number (e.g. ABCPE1234F): ")
    result = pan_category(user_input)
    if result is None:
        print("Invalid PAN: expected format AAAPA9999A with category "
              f"{'/'.join(CATEGORIES)} as the 4th letter")
    else:
        print("PAN Category:", result)


if __name__ == "__main__":
    main()
