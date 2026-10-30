from decimal import Decimal
from unittest import TestCase

from portfolio.portfolio import Portfolio
from portfolio.stock import Stock


class PortfolioTests(TestCase):
    def setUp(self) -> None:
        self.meta = Stock("META", Decimal("2"), Decimal("500"))
        self.apple = Stock("AAPL", Decimal("3"), Decimal("200"))
        self.stocks = [self.meta, self.apple]
        self.allocations = {"META": Decimal("0.40"), "AAPL": Decimal("0.60")}

    def test_stores_the_holdings_and_target_allocations(self) -> None:
        portfolio = Portfolio(self.stocks, self.allocations)

        self.assertEqual(portfolio.stocks, (self.meta, self.apple))
        self.assertEqual(portfolio.allocations, self.allocations)

    def test_target_stock_can_have_zero_current_quantity(self) -> None:
        apple = Stock("AAPL", Decimal("0"), Decimal("200"))

        portfolio = Portfolio([self.meta, apple], self.allocations)

        self.assertEqual(portfolio.stocks[1].quantity, Decimal("0"))
        self.assertEqual(portfolio.allocations["AAPL"], Decimal("0.60"))

    def test_a_current_holding_can_be_absent_from_the_target(self) -> None:
        portfolio = Portfolio(self.stocks, {"AAPL": Decimal("1")})

        self.assertIn(self.meta, portfolio.stocks)
        self.assertNotIn("META", portfolio.allocations)

    def test_zero_and_full_target_weights_are_allowed(self) -> None:
        allocations = {"META": Decimal("0"), "AAPL": Decimal("1")}

        portfolio = Portfolio(self.stocks, allocations)

        self.assertEqual(portfolio.allocations, allocations)

    def test_empty_stock_collection_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one Stock"):
            Portfolio([], {})

    def test_non_stock_items_are_rejected(self) -> None:
        with self.assertRaisesRegex(TypeError, "Stock instances"):
            Portfolio(["META"], {"META": Decimal("1")})

    def test_duplicate_symbols_are_rejected(self) -> None:
        another_meta = Stock("META", Decimal("1"), Decimal("500"))

        with self.assertRaisesRegex(ValueError, "duplicate.*META"):
            Portfolio([self.meta, another_meta], {"META": Decimal("1")})

    def test_target_without_a_supplied_stock_price_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "no supplied Stock.*MSFT"):
            Portfolio(self.stocks, {"MSFT": Decimal("1")})

    def test_non_string_target_symbols_are_rejected(self) -> None:
        with self.assertRaisesRegex(TypeError, "symbols must be strings"):
            Portfolio(self.stocks, {123: Decimal("1")})

    def test_target_weights_must_be_decimals(self) -> None:
        for weight in (1, 0.4, "1", None):
            with (
                self.subTest(weight=weight),
                self.assertRaisesRegex(TypeError, "Decimal"),
            ):
                Portfolio(self.stocks, {"META": weight})

    def test_out_of_range_or_non_finite_weights_are_rejected(self) -> None:
        for weight in ("-0.1", "1.1", "NaN", "sNaN", "Infinity", "-Infinity"):
            with (
                self.subTest(weight=weight),
                self.assertRaisesRegex(ValueError, "within"),
            ):
                Portfolio(self.stocks, {"META": Decimal(weight)})

    def test_target_weights_must_sum_to_one(self) -> None:
        for allocations in (
            {},
            {"META": Decimal("0.4"), "AAPL": Decimal("0.5")},
            {"META": Decimal("0.6"), "AAPL": Decimal("0.6")},
        ):
            with (
                self.subTest(allocations=allocations),
                self.assertRaisesRegex(ValueError, "sum to exactly 1"),
            ):
                Portfolio(self.stocks, allocations)

    def test_a_nearly_one_total_is_not_silently_rounded_to_one(self) -> None:
        allocations = {
            "META": Decimal("0.40"),
            "AAPL": Decimal("0.60000000000000000000000000001"),
        }

        with self.assertRaisesRegex(ValueError, "sum to exactly 1"):
            Portfolio(self.stocks, allocations)

    def test_mutating_input_collections_does_not_change_the_portfolio(self) -> None:
        portfolio = Portfolio(self.stocks, self.allocations)

        self.stocks.clear()
        self.allocations.clear()

        self.assertEqual(portfolio.stocks, (self.meta, self.apple))
        self.assertEqual(
            portfolio.allocations,
            {"META": Decimal("0.40"), "AAPL": Decimal("0.60")},
        )

    def test_mutating_returned_allocations_does_not_change_the_portfolio(self) -> None:
        portfolio = Portfolio(self.stocks, self.allocations)

        returned_allocations = portfolio.allocations
        returned_allocations["META"] = Decimal("1")

        self.assertEqual(portfolio.allocations, self.allocations)
