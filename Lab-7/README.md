# Lab 7: Fuzzing for Input Validation Bugs

**Name:** Pramiti Udupa
**SRN:** PES1UG24CS331
**Assigned repository:** [SETAPESU26/L6_L7_26_loan_eligibility](https://github.com/SETAPESU26/L6_L7_26_loan_eligibility) (`Lab 7` folder)

In the assigned repository the handout's `processor.py` and `test_processor.py` are
named `loan_eligibility.py` and `test_loan_eligibility.py`.

## Files

| File | Description |
|------|-------------|
| `loan_eligibility.py` | Fixed application (deliverable 2) |
| `test_loan_eligibility.py` | Completed Hypothesis fuzz tests (deliverable 3) |
| `Lab7_PES1UG24CS331_FuzzTesting_Report.pdf` | Report with all screenshots (deliverable 1) |
| `screenshots/` | Terminal output for every step |

The original buggy version of `loan_eligibility.py` is in the first Lab 7 commit
(`git log -- Lab-7/loan_eligibility.py`).

## Application under test

| Function | Input | Purpose |
|----------|-------|---------|
| `parse_income(income)` | `"50,000"` | Monthly income as an int |
| `monthly_emi(details)` | `"500000,10,5"` (principal, annual rate %, years) | Monthly EMI |
| `pan_category(pan)` | `"ABCPE1234F"` | Holder category from the 4th PAN character |

## Steps and screenshots

```bash
pip install hypothesis pytest
python loan_eligibility.py
python -m pytest test_loan_eligibility.py
```

| Step | Screenshot |
|------|------------|
| 2. Run the buggy application | `01_buggy_run_valid_input.png`, plus the crashes in `02_buggy_crash_parse_income.png`, `03_buggy_crash_monthly_emi.png` and `04_buggy_crash_pan_category.png` |
| 4. Fuzz tests failing on buggy code | `05_fuzz_tests_failing_summary.png` (15 failed, 1 passed), `06_failing_traceback_example.png`, and the falsifying examples in `07`–`10` |
| 5. Run the fixed application | `11_fixed_run_valid_input.png`, `12_fixed_run_invalid_inputs_handled.png` |
| 6. Fuzz tests on fixed code | `13_fuzz_tests_passing_verbose.png`, `14_fuzz_tests_passing.png` (16 passed) |

## Fuzz tests (`test_loan_eligibility.py`)

There are 16 property-based tests. Each function gets:

1. **No-crash fuzzing** with `st.text() | st.none()` (the handout's pattern).
2. **Wrong-type fuzzing** with ints, floats, bools, bytes, lists and dicts.
3. **Behaviour properties:**
   - Valid inputs return the right value: comma-formatted incomes round-trip, the EMI
     covers the principal (and equals `principal / months` at 0%), and every valid PAN
     maps to its category, whatever the case or surrounding whitespace.
   - Invalid inputs return `None`: negative incomes, text without digits, a principal
     or tenure of zero or less, unknown PAN categories and the wrong PAN length.

Every edge case the fuzzer found is pinned with `@example(...)`, so it is re-checked on
every run.

## Bugs found by fuzzing

| # | Function | Falsifying input | Buggy behaviour |
|---|----------|------------------|-----------------|
| 1 | `parse_income` | `None`, `0`, `b''` | `AttributeError` / `TypeError`: no type check |
| 2 | `parse_income` | `''`, `':'`, `'fifty thousand'` | `ValueError` from `int()` |
| 3 | `parse_income` | `'-5,000'`, `'-1'` | Returns a negative income |
| 4 | `parse_income` | `'٣'` (non-ASCII digits), `'9' * 5000` | `int()` accepts Unicode digits; more than 4300 digits raises `ValueError` |
| 5 | `monthly_emi` | `None`, `0`, `b''` | `AttributeError` / `TypeError` |
| 6 | `monthly_emi` | `''`, `'500000,10'` | `ValueError`: not enough values to unpack |
| 7 | `monthly_emi` | `'500000,ten,5'`, `'500000,10.5,5'` | `ValueError`: no decimal rates allowed |
| 8 | `monthly_emi` | `'500000,0,5'`, `'0,0,0'` | `ZeroDivisionError` when the rate is 0 |
| 9 | `monthly_emi` | `'500000,10,999999999'`, `'0,16,4466'` | `OverflowError`: `(1 + r) ** n` too large |
| 10 | `monthly_emi` | `'-500000,10,5'`, `'1000,1,-1'`, `'0,1,1'` | Negative or zero EMI returned |
| 11 | `pan_category` | `None`, `0`, `{}`, `b'\x00\x00\x00\x00'` | `TypeError` / `KeyError` / `AttributeError` |
| 12 | `pan_category` | `''`, `'ABC'` | `IndexError`: string shorter than 4 characters |
| 13 | `pan_category` | `'ABCXE1234F'`, `'AAACA0000A'` | `KeyError` for an unknown category letter |
| 14 | `pan_category` | `'000F'` | Accepts strings that are not PANs at all |
| 15 | `pan_category` | `'  AFACA0000A  '` | Leading spaces shift index 3, giving the wrong category (`Firm` instead of `Company`) |

## Fixes (`loan_eligibility.py`)

- **All functions:** return `None` for anything that is not a `str`, and never raise.
- **`parse_income`:** strips whitespace and only accepts ASCII digits, with commas
  between digit groups (`50,000` and `5,00,000`). Signs, decimals and Unicode digits are
  rejected, and the length is capped at 15 digits.
- **`monthly_emi`:** needs exactly three comma-separated fields, each checked with a regex.
  It enforces the ranges principal 1,000–10^12, rate 0–100% (decimals allowed) and years
  1–50. A 0% rate (or one too small to change `(1 + r) ** n`) uses `principal / n`
  instead of dividing by zero. The result must be finite and positive.
- **`pan_category`:** strips and uppercases ASCII input only, then checks the full PAN
  layout `[A-Z]{5}[0-9]{4}[A-Z]` and looks up the category with `.get()`.
- **`main`:** prints a clear "Invalid ..." message instead of a traceback, and treats
  end-of-input as an empty answer.

## Result

| Run | Result |
|-----|--------|
| Fuzz tests on the buggy code | 15 failed, 1 passed |
| Fuzz tests on the fixed code | 16 passed (also checked with 7 different `--hypothesis-seed` values) |
