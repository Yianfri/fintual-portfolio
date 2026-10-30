from decimal import ROUND_DOWN, Context, Decimal, Inexact, localcontext
from unittest import TestCase

from portfolio.portfolio import Portfolio
from portfolio.stock import Stock
from portfolio.trade import Trade


class RebalanceTests(TestCase):
    def test_output_rounding_uses_half_even_at_28_significant_digits(self) -> None:
        stocks = [
            Stock("META", Decimal("2.000000000000000000000000001"), Decimal("1")),
            Stock("AAPL", Decimal("0"), Decimal("1")),
        ]
        allocations = {"META": Decimal("0.5"), "AAPL": Decimal("0.5")}

        self.assertEqual(
            Portfolio(stocks, allocations).rebalance(),
            [
                Trade("META", "SELL", Decimal("1"), Decimal("1")),
                Trade("AAPL", "BUY", Decimal("1"), Decimal("1")),
            ],
        )

    def setUp(self) -> None:
        self.stocks = [
            Stock("META", Decimal("2"), Decimal("500")),
            Stock("AAPL", Decimal("3"), Decimal("200")),
        ]
        self.allocations = {"META": Decimal("0.40"), "AAPL": Decimal("0.60")}

    def test_overweight_stock_is_sold_and_underweight_stock_is_bought(self) -> None:
        portfolio = Portfolio(self.stocks, self.allocations)

        self.assertEqual(
            portfolio.rebalance(),
            [
                Trade("META", "SELL", Decimal("0.72"), Decimal("360")),
                Trade("AAPL", "BUY", Decimal("1.8"), Decimal("360")),
            ],
        )

    def test_balanced_portfolio_needs_no_trades(self) -> None:
        stocks = [
            Stock("META", Decimal("8"), Decimal("50")),
            Stock("AAPL", Decimal("6"), Decimal("100")),
        ]

        self.assertEqual(Portfolio(stocks, self.allocations).rebalance(), [])

    def test_zero_value_portfolio_needs_no_trades(self) -> None:
        stocks = [
            Stock("META", Decimal("0"), Decimal("500")),
            Stock("AAPL", Decimal("0"), Decimal("200")),
        ]

        self.assertEqual(Portfolio(stocks, self.allocations).rebalance(), [])

    def test_single_stock_with_full_allocation_needs_no_trades(self) -> None:
        portfolio = Portfolio([self.stocks[0]], {"META": Decimal("1")})

        self.assertEqual(portfolio.rebalance(), [])

    def test_omitted_or_zero_target_sells_the_entire_holding(self) -> None:
        for allocations in (
            {"AAPL": Decimal("1")},
            {"META": Decimal("0"), "AAPL": Decimal("1")},
        ):
            with self.subTest(allocations=allocations):
                self.assertEqual(
                    Portfolio(self.stocks, allocations).rebalance(),
                    [
                        Trade("META", "SELL", Decimal("2"), Decimal("1000")),
                        Trade("AAPL", "BUY", Decimal("5"), Decimal("1000")),
                    ],
                )

    def test_target_stock_not_yet_owned_is_bought(self) -> None:
        stocks = [self.stocks[0], Stock("AAPL", Decimal("0"), Decimal("200"))]

        self.assertEqual(
            Portfolio(stocks, self.allocations).rebalance(),
            [
                Trade("META", "SELL", Decimal("1.2"), Decimal("600")),
                Trade("AAPL", "BUY", Decimal("3"), Decimal("600")),
            ],
        )

    def test_repeating_share_quantity_is_rounded_to_28_significant_digits(self) -> None:
        stocks = [
            Stock("META", Decimal("1"), Decimal("10")),
            Stock("AAPL", Decimal("0"), Decimal("3")),
        ]
        allocations = {"META": Decimal("0.5"), "AAPL": Decimal("0.5")}

        self.assertEqual(
            Portfolio(stocks, allocations).rebalance(),
            [
                Trade("META", "SELL", Decimal("0.5"), Decimal("5")),
                Trade(
                    "AAPL",
                    "BUY",
                    Decimal("1.666666666666666666666666667"),
                    Decimal("5"),
                ),
            ],
        )

    def test_applying_proposed_quantities_reaches_targets_within_rounding(self) -> None:
        stocks = [
            Stock("META", Decimal("1"), Decimal("10")),
            Stock("AAPL", Decimal("0"), Decimal("3")),
        ]
        allocations = {"META": Decimal("0.5"), "AAPL": Decimal("0.5")}
        trades = Portfolio(stocks, allocations).rebalance()
        quantities = {stock.symbol: stock.quantity for stock in stocks}
        prices = {stock.symbol: stock.current_price() for stock in stocks}

        with localcontext(Context(prec=50)):
            for trade in trades:
                change = trade.quantity if trade.action == "BUY" else -trade.quantity
                quantities[trade.symbol] += change
                self.assertGreater(trade.quantity, 0)
                self.assertGreater(trade.amount, 0)
                self.assertLessEqual(
                    abs(trade.quantity * prices[trade.symbol] - trade.amount),
                    Decimal("1e-26"),
                )

            values = {
                symbol: quantity * prices[symbol]
                for symbol, quantity in quantities.items()
            }
            total = sum(values.values())
            self.assertLessEqual(abs(total - Decimal("10")), Decimal("1e-26"))
            for symbol, weight in allocations.items():
                self.assertGreaterEqual(quantities[symbol], 0)
                self.assertLessEqual(
                    abs(values[symbol] / total - weight), Decimal("1e-27")
                )

    def test_repeated_calls_return_the_same_plan_without_changing_holdings(
        self,
    ) -> None:
        portfolio = Portfolio(self.stocks, self.allocations)
        before_stocks = portfolio.stocks
        before_allocations = portfolio.allocations

        first = portfolio.rebalance()
        second = portfolio.rebalance()

        self.assertEqual(first, second)
        self.assertEqual(portfolio.stocks, before_stocks)
        self.assertEqual(portfolio.allocations, before_allocations)
        self.assertEqual(
            [stock.quantity for stock in self.stocks], [Decimal("2"), Decimal("3")]
        )

    def test_caller_decimal_context_does_not_change_the_plan_or_get_modified(
        self,
    ) -> None:
        stocks = [
            Stock("META", Decimal("1"), Decimal("10")),
            Stock("AAPL", Decimal("0"), Decimal("3")),
        ]
        portfolio = Portfolio(stocks, {"META": Decimal("0.5"), "AAPL": Decimal("0.5")})
        expected = portfolio.rebalance()

        with localcontext() as caller:
            caller.prec = 4
            caller.rounding = ROUND_DOWN
            caller.traps[Inexact] = True
            original_flags = caller.flags.copy()

            self.assertEqual(portfolio.rebalance(), expected)
            self.assertEqual(caller.prec, 4)
            self.assertEqual(caller.rounding, ROUND_DOWN)
            self.assertEqual(caller.flags, original_flags)

    def test_precise_balanced_holdings_do_not_produce_rounding_only_trades(
        self,
    ) -> None:
        stocks = [
            Stock(
                "META", Decimal("0.123456789123456789"), Decimal("0.987654321987654321")
            ),
            Stock(
                "AAPL", Decimal("0.123456789123456789"), Decimal("0.987654321987654321")
            ),
        ]
        allocations = {"META": Decimal("0.5"), "AAPL": Decimal("0.5")}

        self.assertEqual(Portfolio(stocks, allocations).rebalance(), [])
