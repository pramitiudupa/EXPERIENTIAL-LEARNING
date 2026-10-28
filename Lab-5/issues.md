# Lab 5: Static Code Analysis — Issue Table

**Name:** Pramiti Udupa
**SRN:** PES1UG24CS331
**File analysed:** `dairy_collection.py`

Line numbers refer to the **original** file. Rows are ordered by severity (High → Medium → Low/style).

| # | Issue | Type | Tool / Code | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|---------|-------------|--------------|
| 1 | Shell command injection | Security (High) | Bandit B605 | 31 | `os.system("echo printing slip for " + farmer)` passes the farmer name to a shell. A name like `Gopal; rm -rf ~` would run extra commands. | Removed the shell call entirely and print the slip with `print(f"printing slip for {farmer}")`. Removed the now-unused `import os`. |
| 2 | Weak MD5 hash | Security (High) | Bandit B324 | 16 | `hashlib.md5` is broken for security use (collisions are easy to produce), yet it is used to build a farmer token. | Replaced with `hashlib.sha256(...)`. Token is now 64 hex characters instead of 32. |
| 3 | SQL injection via string formatting | Security (Medium) / Bug | Bandit B608 | 11 | The INSERT is built with `str.format`, so user data becomes part of the SQL. A farmer named `O'Brien` crashes with `OperationalError: near "Brien": syntax error`, and a crafted name could inject SQL. | Used a parameterised query: `VALUES (?, ?, ?, ?)` with the values passed as a tuple. Verified `O'Brien` is now stored correctly. |
| 4 | Crash on empty ledger | Bug | Found while reviewing the fixes | 25–27 | `max(rows, ...)` raises `ValueError: max() iterable argument is empty` when no milk has been recorded. | `top_farmer` now returns `None` when there are no rows. |
| 5 | Global DB connection shadowed in every function | Code quality | Pylint W0621 | 6, 10, 19, 24, 34 | A module-level `conn` is created on import and every function takes a parameter also named `conn` (redefined-outer-name). Importing the file also created a database and ran the demo. | Moved connection setup into `create_connection()`, created it inside `main()`, closed it at the end, and added an `if __name__ == "__main__":` guard. |
| 6 | Comparison to None with `==` | Bug-prone | Flake8 E711 / Pylint C0121 | 36 | `fat == None` can behave unexpectedly with objects that override `==`. | Changed to `fat is None`. (Later, in the Pylint commit, the magic number 3.5 also became the constant `LOW_FAT_THRESHOLD`.) |
| 7 | Unused import | Code quality | Flake8 F401 / Pylint W0611 | 2 | `json` is imported but never used. | Removed the import. |
| 8 | Ambiguous variable name | Style | Flake8 E741 | 26 | `l` is easily confused with `1` and `I`. | Renamed to `best`. |
| 9 | Lines too long | Style | Flake8 E501 / Pylint C0301 | 7, 11, 20, 25 | Lines exceed the 79-character PEP 8 limit (up to 124 characters). | Split SQL strings across lines using implicit string concatenation and wrapped call arguments. |
| 10 | Non-snake_case function names | Style | Pylint C0103 | 10, 15, 19, 24, 30, 34 | `recordMilk`, `farmerToken`, `dailyTotal`, `topFarmer`, `printSlip`, `lowFat` break PEP 8 naming. | Renamed to `record_milk`, `farmer_token`, `daily_total`, `top_farmer`, `print_slip`, `low_fat`. |
| 11 | Missing docstrings | Documentation | Pylint C0114 / C0116 | 1, 10, 15, 19, 24, 30, 34, 39 | No module docstring and no function docstrings. | Added a module docstring and a one-line docstring to every function. |
| 12 | Old-style string formatting | Style | Pylint C0209 | 11, 21 | `.format()` and `%` formatting where an f-string is clearer. | Line 11 became a parameterised query (row 3); line 21 now uses `f"Total: {...:.1f} litres"`. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 2.00/10 (24 messages) | **10.00/10** (0 messages) |
| Bandit | 3 issues (2 High, 1 Medium) | **0 issues** |
| Flake8 | 7 issues | **0 issues** (empty report means no violations) |

The program still produces the same demonstration output (total of 32.5 litres, top farmer Lata, Lata flagged as low-fat, slip printed for Gopal). The only intended change in output is the farmer token, which is now SHA-256 instead of MD5.

Reports are in `reports/before/` and `reports/after/`.

## Commits

1. Fix Bandit security issues (rows 1–3), with the before reports
2. Fix Flake8 style issues (rows 6–9)
3. Fix Pylint issues (rows 4, 5, 10–12), with the after reports, issue table and reflection
