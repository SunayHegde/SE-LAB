# Reflection

**1. Which issues were the easiest to fix, and which were the hardest? Why?**

The easiest were the Flake8 style issues — unused imports, trailing whitespace, `!= None`, long lines. Each has a clear code, an exact line number and one obvious fix. The hardest were the ones that needed a design decision rather than a mechanical edit. The mutable default `audit_log=[]` was easy to change to `None`, but it pushed `create_ticket` over Pylint's argument limit, so I had to decide between changing the API and accepting a justified `disable`. Replacing `global TICKETS` also needed some thought: mutating the dict in place with `clear()`/`update()` keeps every existing reference valid, while rebinding the name does not.

**2. Did the static analysis tools report any false positives? If so, describe one example.**

Mostly no, but a few findings were stricter than the real risk. Bandit's B307 on `eval("print('unsafe demo')")` is technically a false positive in impact: the string is a hard-coded literal, so nothing can be injected. I still fixed it because `eval` is never needed there and the pattern is dangerous if it is copied. Pylint's R0913 (too many arguments) is a judgement call rather than a defect — six parameters are reasonable for creating a ticket. The more important lesson was the opposite: the tools missed real bugs. The program crashes with `KeyError` when you type a ticket id that doesn't exist, and `len(TICKETS) + 1` can reuse an existing id after loading tickets from a file. I only found those by running the program and reading the code.

**3. How would you integrate static analysis tools into your actual software development workflow?**

Locally, run Flake8 and Pylint in the editor and through a `pre-commit` hook so style problems never reach a commit. In CI (for example GitHub Actions), run all three on every push and pull request: fail the build on any Bandit Medium/High finding, on any Flake8 error, and if the Pylint score drops below a threshold such as 9.5. Keep the tool configuration (line length, enabled checks) in a shared `pyproject.toml`/`setup.cfg` so everyone uses the same rules, and require a comment next to every inline `# pylint: disable` or `# nosec`.

**4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?**

- **Score:** Pylint went from 5.00/10 to 10.00/10; Bandit and Flake8 went from 2 and 12 findings to zero.
- **Robustness:** an unknown ticket id no longer crashes the program; files are always closed and use UTF-8 on every OS; errors are logged instead of silently swallowed; the audit log no longer leaks between calls; ids can't collide after loading.
- **Security:** no `eval` in the code.
- **Readability:** every function has a docstring, names follow PEP 8, the ticket dictionary is one key per line, and conditions like `is_open` are a single readable expression instead of an if/else.
