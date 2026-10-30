from collections.abc import Mapping, Sequence
from decimal import (
    ROUND_HALF_EVEN,
    Context,
    Decimal,
    DecimalException,
    Underflow,
    localcontext,
)
from fractions import Fraction

from portfolio.stock import Stock
from portfolio.trade import Trade


class Portfolio:
    """A snapshot of holdings and their desired allocation by value."""

    def __init__(
        self,
        stocks: Sequence[Stock],
        allocations: Mapping[str, Decimal],
    ) -> None:
        stock_snapshot = tuple(stocks)
        allocation_snapshot = dict(allocations)

        if not stock_snapshot:
            raise ValueError("stocks must contain at least one Stock")

        symbols: set[str] = set()
        for stock in stock_snapshot:
            if not isinstance(stock, Stock):
                raise TypeError("stocks must contain only Stock instances")
            if stock.symbol in symbols:
                raise ValueError(f"duplicate stock symbol: {stock.symbol}")
            symbols.add(stock.symbol)

        for symbol, weight in allocation_snapshot.items():
            if not isinstance(symbol, str):
                raise TypeError("allocation symbols must be strings")
            if symbol not in symbols:
                raise ValueError(f"allocation has no supplied Stock: {symbol}")
            if not isinstance(weight, Decimal):
                raise TypeError(f"allocation for {symbol} must be a Decimal")
            if not weight.is_finite() or not 0 <= weight <= 1:
                raise ValueError(
                    f"allocation for {symbol} must be finite and within [0, 1]"
                )

        # Compare the exact supplied weights without Decimal context rounding.
        if sum(Fraction(weight) for weight in allocation_snapshot.values()) != 1:
            raise ValueError("allocations must sum to exactly 1")

        self._stocks = stock_snapshot
        self._allocations = allocation_snapshot

    @property
    def stocks(self) -> tuple[Stock, ...]:
        return self._stocks

    @property
    def allocations(self) -> dict[str, Decimal]:
        """Return a copy so callers cannot change the validated allocation."""
        return self._allocations.copy()

    def rebalance(self) -> list[Trade]:
        """Propose fractional trades at supplied prices without changing holdings."""
        # Exact intermediates avoid generating trades from rounding alone.
        current_values = {
            stock.symbol: Fraction(stock.quantity) * Fraction(stock.current_price())
            for stock in self._stocks
        }
        total_value = sum(current_values.values(), Fraction(0))
        trades: list[Trade] = []

        try:
            with localcontext(Context(prec=28, rounding=ROUND_HALF_EVEN)) as context:
                context.traps[Underflow] = True
                for stock in self._stocks:
                    weight = Fraction(self._allocations.get(stock.symbol, Decimal(0)))
                    difference = total_value * weight - current_values[stock.symbol]
                    if difference == 0:
                        continue

                    amount = abs(difference)
                    quantity = amount / Fraction(stock.current_price())
                    trades.append(
                        Trade(
                            symbol=stock.symbol,
                            action="BUY" if difference > 0 else "SELL",
                            quantity=Decimal(quantity.numerator)
                            / Decimal(quantity.denominator),
                            amount=Decimal(amount.numerator)
                            / Decimal(amount.denominator),
                        )
                    )
        except DecimalException as exc:
            raise ValueError("trade values exceed the supported decimal range") from exc

        return trades
