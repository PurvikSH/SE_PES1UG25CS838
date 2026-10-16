

\# Reflection - Static Code Analysis



\## 1. What did you learn from this lab?



I learned how to use Pylint, Bandit, and Flake8 to analyze Python code. These tools help identify code quality problems, security risks, and formatting errors.



\## 2. Which tool was most useful and why?



Bandit was especially useful because it identified security risks such as disabled TLS certificate verification, missing request timeouts, and unsafe shell command usage.



\## 3. What security improvements did you make?



I moved the API key to an environment variable, enabled normal TLS certificate verification, added an HTTP request timeout, removed shell-based command execution, and used Python's tarfile module for report backups.



\## 4. How did you improve code quality?



I renamed functions using snake\_case, added function docstrings, removed unused imports, fixed formatting errors, handled empty attendance records, and replaced the mutable default argument with None.



\## 5. What were the final analysis results?



Pylint: 9.89/10.



Bandit: No issues identified.



Flake8: No formatting errors.



\## 6. What would you improve in the future?



I would add automated unit tests, validate attendance data, improve error handling, and integrate static code analysis into a continuous integration workflow.



