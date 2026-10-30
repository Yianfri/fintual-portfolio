from dataclasses import FrozenInstanceError
from decimal import Decimal
from unittest import TestCase

from portfolio.stock import Stock


class StockTests(TestCase):
    def test_current_price_returns_the_supplied_price(self) -> None:
        stock = Stock("AAPL", Decimal("2"), Decimal("190.125"))

        self.assertEqual(stock.current_price(), Decimal("190.125"))

    def test_fractional_quantity_and_price_precision_are_preserved(self) -> None:
        stock = Stock("META", Decimal("0.125"), Decimal("500.123456789"))

        self.assertEqual(stock.quantity, Decimal("0.125"))
        self.assertEqual(stock.current_price(), Decimal("500.123456789"))

    def test_zero_quantity_is_allowed_for_a_stock_not_yet_owned(self) -> None:
        stock = Stock("META", Decimal("0"), Decimal("500"))

        self.assertEqual(stock.quantity, Decimal("0"))

    def test_blank_or_whitespace_containing_symbols_are_rejected(self) -> None:
        for symbol in ("", " ", " AAPL", "AAPL ", "AA PL", "AA\tPL"):
            with (
                self.subTest(symbol=symbol),
                self.assertRaisesRegex(ValueError, "symbol"),
            ):
                Stock(symbol, Decimal("1"), Decimal("100"))

    def test_non_string_symbols_are_rejected(self) -> None:
        for symbol in (None, 123):
            with (
                self.subTest(symbol=symbol),
                self.assertRaisesRegex(TypeError, "symbol"),
            ):
                Stock(symbol, Decimal("1"), Decimal("100"))

    def test_quantities_must_be_decimals(self) -> None:
        for quantity in (1, 0.1, "1", None):
            with (
                self.subTest(quantity=quantity),
                self.assertRaisesRegex(TypeError, "quantity"),
            ):
                Stock("AAPL", quantity, Decimal("100"))

    def test_negative_or_non_finite_quantities_are_rejected(self) -> None:
        for value in ("-1", "NaN", "sNaN", "Infinity", "-Infinity"):
            with (
                self.subTest(value=value),
                self.assertRaisesRegex(ValueError, "quantity"),
            ):
                Stock("AAPL", Decimal(value), Decimal("100"))

    def test_prices_must_be_decimals(self) -> None:
        for price in (100, 0.1, "100", None):
            with (
                self.subTest(price=price),
                self.assertRaisesRegex(TypeError, "last_price"),
            ):
                Stock("AAPL", Decimal("1"), price)

    def test_non_positive_or_non_finite_prices_are_rejected(self) -> None:
        for value in ("0", "-1", "NaN", "sNaN", "Infinity", "-Infinity"):
            with (
                self.subTest(value=value),
                self.assertRaisesRegex(ValueError, "last_price"),
            ):
                Stock("AAPL", Decimal("1"), Decimal(value))

    def test_holding_values_cannot_be_changed_after_validation(self) -> None:
        stock = Stock("AAPL", Decimal("1"), Decimal("100"))

        with self.assertRaises(FrozenInstanceError):
            stock.quantity = Decimal("-1")
        with self.assertRaises(FrozenInstanceError):
            stock.last_price = Decimal("0")
