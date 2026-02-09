# init
```bash
pip install pytest pytest-cov pygetwindow sphinx sphinx_rtd_theme
```

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