from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Stock:
    """A holding valued using a supplied snapshot of its latest available price."""

    symbol: str
    quantity: Decimal
    last_price: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str):
            raise TypeError("symbol must be a string")
        if not self.symbol or any(char.isspace() for char in self.symbol):
            raise ValueError("symbol must be nonempty and contain no whitespace")

        if not isinstance(self.quantity, Decimal):
            raise TypeError("quantity must be a Decimal")
        if not self.quantity.is_finite() or self.quantity < 0:
            raise ValueError("quantity must be finite and nonnegative")

        if not isinstance(self.last_price, Decimal):
            raise TypeError("last_price must be a Decimal")
        if not self.last_price.is_finite() or self.last_price <= 0:
            raise ValueError("last_price must be finite and greater than zero")

    def current_price(self) -> Decimal:
        return self.last_price
