# Static Analysis Issues — `support_ticket_tracker.py`

Line numbers refer to the **original** file. Reports are in `reports/before/` and `reports/after/`.

**Results:** Pylint 5.00/10 → **10.00/10** · Bandit 2 issues → **0** · Flake8 12 issues → **0**

| # | Issue | Tool / Code | Severity | Type | Line(s) | Description | Fix Approach |
|---|-------|-------------|----------|------|---------|-------------|--------------|
| 1 | Use of `eval` | Bandit B307, Pylint W0123 | Medium (Bandit) | Security | 92 | `eval()` executes any string as code. Here the string is fixed, but the pattern is dangerous if it ever takes input, and it is unnecessary. | Replaced `eval("print('unsafe demo')")` with a plain `print("unsafe demo")`. |
| 2 | Bare `except` with `pass` | Bandit B110, Flake8 E722, Pylint W0702 | Low (Bandit) | Bug / Security | 24–25 | `except: pass` swallows every exception, including `KeyboardInterrupt` and real bugs, and hides the failure. | Catch only `KeyError` (unknown ticket id), log a warning, return `False`. |
| 3 | Mutable default argument | Pylint W0102 | Warning | Bug | 10, 16 | `audit_log=[]` is created once and shared by every call, so entries from earlier calls leak into later ones. | Default changed to `None`, a new list is created inside the function. Optional args made keyword-only. |
| 4 | Files opened without `with` / encoding | Pylint R1732, W1514 | Warning | Bug / Robustness | 46, 53 | If writing or parsing fails, the file is never closed; the encoding depends on the OS (e.g. cp1252 on Windows). | Use `with open(path, ..., encoding="utf-8")` and `json.dump`/`json.load`. |
| 5 | `global` statement | Pylint W0603 | Warning | Design | 52 | `load_tickets` rebinds the module-level `TICKETS`, so any code holding a reference to the old dict keeps stale data. | Mutate in place with `TICKETS.clear()` + `TICKETS.update(data)`. |
| 6 | Crash on unknown ticket id (not flagged by tools) | Found by running the program | High (runtime) | Bug | 66–67, 87–89 | Entering an id that does not exist at the prompt crashes with `KeyError: '9'`. | `close_ticket` checks the id and returns `False`; `main` prints “No ticket with id …”. `is_open` also returns `False` for unknown ids. |
| 7 | Ticket id collisions after loading (not flagged by tools) | Code review | Medium | Bug | 13 | `len(TICKETS) + 1` can reuse an existing id if ids are not contiguous (e.g. after loading a file), silently overwriting a ticket. | New helper `_next_ticket_id()` uses `max(existing ids) + 1`. |
| 8 | Unused argument `notify` | Pylint W0613 | Warning | Bug | 20 | `notify=True` was silently ignored. | Implemented: logs a notification when `notify` is set. |
| 9 | Unused imports / variable | Flake8 F401, F841; Pylint W0611, W0612 | Low | Code quality | 4, 5, 84 | `sys`, `random` and `count` were never used. | Removed. |
| 10 | Comparison to `None` with `!=` | Flake8 E711, Pylint C0121 | Low | Style / Bug | 37 | `!= None` can be overridden by `__ne__`; identity check is correct. | Changed to `is not None`. |
| 11 | Non-snake_case name | Pylint C0103 | Convention | Style | 66 | `closeTicket` breaks PEP 8 naming. | Renamed to `close_ticket`. |
| 12 | f-string in logging call | Pylint W1203 | Warning | Performance / Style | 85 | f-string is formatted even if the log level is disabled. | `logging.info("Tickets created: %d", len(TICKETS))`. |
| 13 | Lines too long, trailing whitespace | Flake8 E501, W291; Pylint C0301, C0303 | Low | Style | 10, 14, 63, 71, 79, 80, 84 | Lines over 79 chars, trailing spaces. | Wrapped lines, ticket dict split one key per line, whitespace removed. |
| 14 | Missing docstrings | Pylint C0114, C0116 | Convention | Documentation | 1 + every function | No module or function docstrings. | Added docstrings throughout. |
| 15 | Simplifiable logic | Pylint R1703, R1705, C1802, C0209, R1714 | Refactor | Readability | 16, 37, 60, 71 | `if …: return True else: return False`, `not len(...)`, `%` formatting. | `return ... in (...)`, `if not TICKETS`, f-strings. |

**Not changed:** Pylint R0913 (too many arguments, 6/5) on `create_ticket`. The six inputs are part of the function's API; the three optional ones are now keyword-only (fixing R0917), and R0913 is disabled for that one line with a comment explaining why.
