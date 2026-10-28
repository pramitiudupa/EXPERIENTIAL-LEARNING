# Lab 5: Static Code Analysis — Reflection

**Name:** Pramiti Udupa
**SRN:** PES1UG24CS331
**File analysed:** `dairy_collection.py`

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the style issues reported by Flake8 and Pylint: removing the unused `json` import, renaming `l` to `best`, changing `fat == None` to `fat is None`, adding docstrings and converting function names to snake_case. Each of these is a local, mechanical change and the tool message says exactly what to do.

The hardest was the `redefined-outer-name` warning (W0621). It is not fixed by editing one line. The real cause was a design problem: a global database connection was created when the module was imported, and every function also took a parameter called `conn`. Fixing it properly meant moving the setup into a `create_connection()` function, creating the connection inside `main()`, closing it at the end and adding an `if __name__ == "__main__":` guard, while making sure the output stayed the same.

The SQL injection fix was also important to get right. Simply silencing Bandit would have hidden a real bug: a farmer named `O'Brien` crashed the original program with `OperationalError`. Switching to a parameterised query fixed both the security issue and the crash.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

There were no strict false positives, but some findings were stronger than the actual risk in this program:

- **Bandit B324 (MD5)** is rated High severity. Here the hash is only used as a farmer identifier token, not for passwords or signatures, so the practical risk is low. Bandit cannot know the intent, which is why it suggests `usedforsecurity=False` as an alternative. I still switched to SHA-256 because it costs nothing and is the safer default.
- **Bandit B605 (`os.system`)** would be a real injection risk with user input, but in the demo the farmer name is a hard-coded string. It is still worth fixing because the function would be dangerous once names came from users.
- **Overlap between tools:** the same problem was sometimes reported twice (for example, `fat == None` by Flake8 E711 and Pylint C0121, and the unused import by Flake8 F401 and Pylint W0611). These are duplicates rather than false positives, but they inflate the issue count.

Static analysis also missed a real bug: `topFarmer` crashed with `ValueError` on an empty ledger. No tool flagged it, which shows these tools complement testing rather than replace it.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run Flake8 and Pylint inside the editor (VS Code extensions) so problems show up while typing, and use a `pre-commit` hook that runs Flake8 and Bandit before every commit so bad code never enters the repository.
- **In CI:** add a GitHub Actions workflow that runs all three tools on every push and pull request. The build fails if Bandit reports any Medium or High issue, if Flake8 reports any violation, or if the Pylint score drops below a threshold such as 9.5 (`pylint --fail-under=9.5`).
- **Configuration:** keep shared settings in `pyproject.toml` / `.flake8` so everyone uses the same rules, and only suppress a warning with an inline comment (for example `# nosec` or `# pylint: disable=...`) together with a written reason.
- **Prioritise by severity:** fix security findings first, then bugs, then style, the same order used in this lab.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Scores:** Pylint went from 2.00/10 to 10.00/10, Bandit from 3 issues (2 High, 1 Medium) to 0, and Flake8 from 7 issues to 0.
- **Security:** no shell is invoked any more, all SQL uses parameterised queries, and the token uses SHA-256 instead of MD5.
- **Robustness:** names containing apostrophes such as `O'Brien` are stored correctly instead of crashing, and `top_farmer` returns `None` on an empty ledger instead of raising `ValueError`.
- **Readability:** snake_case names, docstrings on every function, f-strings, a named constant `LOW_FAT_THRESHOLD` instead of the magic number 3.5, and every line within 79 characters.
- **Reusability:** the module can now be imported (for example in tests) without creating a database or running the demo, because setup happens inside `main()` behind the `__main__` guard. The program output is unchanged apart from the longer SHA-256 token.
