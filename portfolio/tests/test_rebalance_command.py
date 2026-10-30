import subprocess
import sys
from pathlib import Path
from unittest import TestCase


class RebalanceCommandTests(TestCase):
    def run_demo(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "manage.py", "rebalance_demo", *arguments],
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_default_demo_prints_expected_trades(self) -> None:
        result = self.run_demo()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SELL META: 0.72 shares; 360.00 USD", result.stdout)
        self.assertIn("BUY AAPL: 1.8 shares; 360.00 USD", result.stdout)

    def test_balanced_targets_report_no_trades(self) -> None:
        result = self.run_demo("--meta-weight", "0.625", "--aapl-weight", "0.375")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Portfolio is already balanced.", result.stdout)

    def test_invalid_total_returns_a_clear_error_and_nonzero_status(self) -> None:
        result = self.run_demo("--meta-weight", "0.50")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("allocations must sum to exactly 1", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_weight_returns_a_clear_error_and_nonzero_status(self) -> None:
        result = self.run_demo("--meta-weight", "invalid")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Target weights must be decimal numbers", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_non_finite_weight_returns_a_domain_error(self) -> None:
        result = self.run_demo("--meta-weight", "NaN")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("allocation for META must be finite", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
