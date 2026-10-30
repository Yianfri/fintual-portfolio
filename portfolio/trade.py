from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass(frozen=True)
class Trade:
    """A proposed trade, with quantity and amount expressed as positive magnitudes."""

    symbol: str
    action: Literal["BUY", "SELL"]
    quantity: Decimal
    amount: Decimal
