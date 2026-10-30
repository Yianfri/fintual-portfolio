from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError, CommandParser

from portfolio.portfolio import Portfolio
from portfolio.stock import Stock


class Command(BaseCommand):
    help = "Show proposed trades for an example portfolio using supplied USD prices."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--meta-weight", default="0.40", help="META target fraction, e.g. 0.40."
        )
        parser.add_argument(
            "--aapl-weight", default="0.60", help="AAPL target fraction, e.g. 0.60."
        )

    def handle(self, *args: object, **options: object) -> None:
        try:
            allocations = {
                "META": Decimal(str(options["meta_weight"])),
                "AAPL": Decimal(str(options["aapl_weight"])),
            }
        except InvalidOperation as exc:
            raise CommandError(
                "Target weights must be decimal numbers, e.g. 0.40."
            ) from exc

        stocks = [
            Stock("META", Decimal("2"), Decimal("500")),
            Stock("AAPL", Decimal("3"), Decimal("200")),
        ]
        try:
            trades = Portfolio(stocks, allocations).rebalance()
        except (TypeError, ValueError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            "Proposed trades using supplied USD prices; no orders are executed."
        )
        if not trades:
            self.stdout.write("Portfolio is already balanced.")
        for trade in trades:
            self.stdout.write(
                f"{trade.action} {trade.symbol}: {trade.quantity:f} shares; "
                f"{trade.amount:.2f} USD"
            )
