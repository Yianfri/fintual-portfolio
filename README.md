# Fintual portfolio challenge

A minimal Django project for the Fintual Software Engineer exercise.
The portfolio classes, rebalance calculation, example command, behavioral tests,
and CI workflow will be added incrementally.

## Setup

Prepared with Python 3.12.10 and Django 5.2.18 (LTS). Dependencies are pinned in
`requirements.txt`; `requirements-dev.txt` adds Ruff for linting and formatting.
From the project directory in PowerShell:

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements-dev.txt
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
uv pip check --python .venv\Scripts\python.exe
```

Activation is optional because these commands reference the interpreter explicitly.
No database setup or migration is needed.

## Scope and structure

Calculate suggested purchases and sales from current holdings, supplied prices,
and target allocations. This exercise does not execute trades. Use ordinary
Python classes for the calculation and a Django command for a runnable example.
Keep data in memory; persistence and a web interface are optional extensions.

The current structure is:

```text
fintual-portfolio/
|-- AGENTS.md
|-- .cursor/rules/project-standards.mdc
|-- .editorconfig
|-- .gitattributes
|-- .gitignore
|-- README.md
|-- requirements.txt
|-- requirements-dev.txt
|-- pyproject.toml
|-- manage.py
|-- config/
|   |-- __init__.py
|   `-- settings.py
`-- portfolio/
    |-- __init__.py
    `-- apps.py
```

`manage.py` runs Django commands. `config` contains minimal settings for a
command-line application, not a deployed web server. The `portfolio` app groups
this feature. Future calculation classes will not import Django; commands or
optional HTTP views will delegate to them. Introduce services when they represent
additional behavior, rather than wrapping every class in another layer.

The next domain files are planned as `portfolio/stock.py`,
`portfolio/portfolio.py`, `portfolio/management/commands/rebalance_demo.py`, and
`portfolio/tests/test_rebalance.py`. They have not been implemented yet.

## Project conventions

Rules are defined in [project-standards.mdc](.cursor/rules/project-standards.mdc)
and referenced by [AGENTS.md](AGENTS.md). Use English identifiers, type hints on
public functions, and concise comments that explain intent. Python does not enforce
type hints at runtime; Ruff is not a type checker.

Use `Decimal` for prices, quantities, and weights. Fractional shares, precision,
rounding, fees, cash, and invalid-input behavior still need to be discussed before
implementing the calculation. Keep calculations deterministic and inputs unchanged.

If a frontend is added, reuse components for repeated presentation or behavior.
Support narrow and wide screens, keyboard interaction, labels, and useful validation
feedback. Keep calculation rules in Python.

## Verification and version control

The setup commands check Django configuration, lint, formatting, and dependency
compatibility. There are no portfolio behavior tests yet. Use standard-library
`unittest` for those tests. Once meaningful tests exist, add GitHub Actions to
install dependencies and run the same checks and tests on pushes and pull requests.
No deployment is required for this exercise.

The repository can be private during development. Reviewers need an invitation to
access a private repository; its link alone does not grant access. Before applying,
ensure reviewers can access both the code and the required conversation record.
Fork can open the local Git repository and manage the same commits and branches.

## LLM disclosure

Fintual requires sharing LLM conversations when an LLM is used. The actual
conversation record has not been exported or included yet. A reasoning summary
alone is not the conversation record.

## References

- [Django supported releases](https://www.djangoproject.com/download/)
- [Django management commands](https://docs.djangoproject.com/en/6.1/howto/custom-management-commands/)
- [Python type annotations](https://docs.python.org/3/library/typing.html)
- [Ruff configuration](https://docs.astral.sh/ruff/configuration/)
- [GitHub Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions)
- [GitHub repository visibility](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories)
