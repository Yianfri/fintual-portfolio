# Fintual portfolio challenge

A small Python module that proposes trades from supplied prices and target
allocations, with a Django command for running an example. No orders are executed.

## Setup

Prepared with Python 3.12.10 and Django 5.2.18 (LTS). Dependencies are pinned in
`requirements.txt`; `requirements-dev.txt` adds Ruff. Python 3.12 is required;
`uv` is optional. From the repository directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

If using `uv`, the equivalent setup is:

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements-dev.txt
```

On macOS/Linux, create the environment with `python3 -m venv .venv` and use
`.venv/bin/python` instead of `.\.venv\Scripts\python.exe` in the commands below.
For example, install dependencies with
`.venv/bin/python -m pip install -r requirements-dev.txt`.

Activation is optional. No database setup, migrations, or network price source is needed.

## Run the checks

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m unittest discover -s portfolio/tests -v
```

## Run the example

```powershell
.\.venv\Scripts\python.exe manage.py rebalance_demo
```

The example holds 2 META shares at USD 500 and 3 AAPL shares at USD 200: values of
USD 1,000 and USD 600. A 40%/60% target requires USD 640 in META and USD 960 in AAPL:

```text
Proposed trades using supplied USD prices; no orders are executed.
SELL META: 0.72 shares; 360.00 USD
BUY AAPL: 1.8 shares; 360.00 USD
```

Try targets matching the current holdings, which require no trades:

```powershell
.\.venv\Scripts\python.exe manage.py rebalance_demo --meta-weight 0.625 --aapl-weight 0.375
```

Weights are fractions: `0.40` means 40%. Invalid inputs produce a readable error
on stderr and a nonzero exit status. For example, `--meta-weight 0.50` with the
default AAPL weight fails because the weights would total 110%.

## Model and calculation

`Stock` represents a holding: symbol, quantity, and supplied latest price. The
exercise's wording about receiving a price is interpreted as passing it to the
constructor; `current_price()` returns that snapshot. Stock is immutable.

```python
from decimal import Decimal

from portfolio.portfolio import Portfolio
from portfolio.stock import Stock

portfolio = Portfolio(
    stocks=[
        Stock("META", Decimal("2"), Decimal("500")),
        Stock("AAPL", Decimal("3"), Decimal("200")),
    ],
    allocations={"META": Decimal("0.40"), "AAPL": Decimal("0.60")},
)
trades = portfolio.rebalance()
```

Rebalance values each holding as quantity times price, adds them to obtain the
total value, and calculates each target value as total times weight. Target value
minus current value determines BUY (positive) or SELL (negative). Dividing the
absolute difference by the price gives the share quantity.

Each returned `Trade` contains `symbol`, `action` (BUY or SELL), `quantity`, and
`amount`. Quantity and amount are positive magnitudes. Results follow input stock
order and omit unchanged holdings. They are a proposal, not an execution sequence.
Rebalance does not change holdings or allocations.

## Assumptions and numeric policy

- All prices and holdings use one currency. The demo uses USD; there is no FX conversion.
- Fractional shares are allowed. There are no fees, taxes, cash balance, deposits,
  withdrawals, or broker restrictions on fractional shares.
- Quantities must be finite, nonnegative Decimal values; prices must be finite,
  strictly positive Decimal values. Floats are not silently converted.
- Symbols are nonempty strings without whitespace and matched case-sensitively.
  Exchange membership is not checked; duplicate holding symbols are rejected.
- Supply at least one Stock. Every target requires a supplied Stock and price;
  quantity zero represents a stock not yet owned. Omitted targets mean weight zero.
- Target weights must be finite Decimals in [0, 1] and sum to exactly 1. Invalid
  totals are rejected, not normalized. A zero-value portfolio returns no trades.
- Inputs are copied. Public access returns a tuple of immutable holdings and a
  copy of the allocation mapping.

Inputs and outputs use `Decimal`. Internally, `Fraction` preserves exact values
during valuation, target calculation, and comparison. This avoids creating trades
solely because intermediate arithmetic was rounded.

Output amounts and quantities use a local decimal context with 28 significant
digits and `ROUND_HALF_EVEN`, preserving the caller's context. Recurring fractions
and values requiring more digits are approximations; applying output quantities
may leave tiny rounding residuals. Unsupported output ranges raise `ValueError`.
The domain result does not impose fixed decimal places. Only the demo displays
money to two decimal places. Broker precision and cash reconciliation are outside scope.

## Structure and verification

- `portfolio/stock.py`: holding and input validation.
- `portfolio/portfolio.py`: collections, target validation, and rebalance.
- `portfolio/trade.py`: immutable trade proposal.
- `portfolio/management/commands/rebalance_demo.py`: parsing and output formatting.
- `portfolio/tests/`: model tests, calculation tests, and CLI integration tests.
- `config/settings.py`: minimal Django configuration for the command-line exercise.
- `.github/workflows/tests.yml`: Django check, Ruff, and tests on pushes and pull requests.

Core tests use standard-library unittest, independently of Django, a database, or
the network. Integration tests run the actual Django CLI in separate processes,
checking output and error exit statuses. Tests cover expected trades, balanced
and zero-value portfolios, omitted/new targets, fractions, rounding, approximate
value conservation, repeatability, and preservation of inputs and decimal context.

The checks have also [passed on GitHub Actions](https://github.com/Yianfri/fintual-portfolio/actions/runs/41127268423).
Deployment and a frontend are not required. Project conventions are in
[project-standards.mdc](.cursor/rules/project-standards.mdc), referenced by
[AGENTS.md](AGENTS.md). Type hints document interfaces; Ruff is not a type checker.

## Submission and LLM disclosure

An LLM assisted with implementation, tests, documentation, and discussion of design
decisions. Conversation records are available here, as required by the exercise:

- [Shared conversation on ChatGPT](https://chatgpt.com/s/cx_6ae5df6fcd888191807909bc77db45e0).
- [Conversation transcript in this repository](docs/ai-conversation.md).

The repository transcript preserves user and assistant messages in their original
language; it is not a reasoning summary. The export scope and snapshot cutoff are documented at
the beginning of that file. Refresh the record if further conversations change
the solution.

Before applying, ensure reviewers can access the code and conversation record.
A private repository requires reviewer invitations; its link alone grants no access.

## References

- [Django supported releases](https://www.djangoproject.com/download/)
- [Django management commands and errors](https://docs.djangoproject.com/en/6.1/howto/custom-management-commands/)
- [Decimal arithmetic](https://docs.python.org/3/library/decimal.html)
- [Exact fractions](https://docs.python.org/3/library/fractions.html)
- [Ruff configuration](https://docs.astral.sh/ruff/configuration/)
