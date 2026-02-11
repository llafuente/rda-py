# init
```bash
pip install pytest pytest-cov pytest-mock sphinx sphinx_rtd_theme ahk ahk[binary]
```

# static typing test (mypy)

```bash
mypy .\src\automation.py > mypy2
# diff mypy mypy2
```

There are some known issues we just skip atm.

For future develper check [mypy output](./mypy)

# test

```bash
pytest --cov=src --cov-report html
explorer .\htmlcov\index.html
```

# Generate documentation

```bash
sphinx-build.bat -b html .\docs\source\ .\docs\html
explorer .\docs\html
```