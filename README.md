# ~Robotnik~ Robotic Desktop Automation in Python (rda-py)

Automate desktop applications (attended an unattended) in python using AutoHotKey:

* *out-of-scope* Java access bridge for Java applications
* *out-of-scope* Microsoft UI Automation for Window native application and UWP
* Images for remote application, RDP, Citrix, Horizon (It requires an interactive desktop)
* (OS) Mouse / Keyboard / Screen / Clipboard

This project is a migration of [rda-ahk](https://github.com/llafuente/rda-ahk) with a narrow scope.

The project if fully typed and checked with `mypy`.

## Documentation



## development

### Initialize/start project

```bash
pip install -r requirements.txt
```

### static typing test (mypy)

```bash
mypy .\src\rda\automation.py > mypy2
# diff mypy mypy2
```

There are some known issues we just skip atm.

Developer should check [mypy output](./mypy) for those that are just skipped.

### Unit test

It's currently at 100% lines and branches.

Please do your best as I do mine :)

```bash
pytest --cov=src --cov-report html
explorer .\htmlcov\index.html
```

### Generate documentation

```bash
sphinx-build.exe -b html .\docs\source\ .\docs\html
explorer .\docs\html\index.html
```