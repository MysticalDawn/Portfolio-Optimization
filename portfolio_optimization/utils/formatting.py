"""Output formatting utilities."""

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from portfolio_optimization.algorithms.base import OptimizationResult


def print_header(title: str, width: int = 60) -> None:
    """Print a section header."""
    print(f"\n{'=' * width}")
    print(f" {title}")
    print(f"{'=' * width}")


def print_subheader(title: str, width: int = 60) -> None:
    """Print a subsection header."""
    print(f"\n{'-' * width}")
    print(f" {title}")
    print(f"{'-' * width}")


def print_key_value(key: str, value, indent: int = 2) -> None:
    """Print a key-value pair with consistent formatting."""
    print(f"{' ' * indent}{key}: {value}")


def print_table_row(columns: list, widths: list) -> None:
    """Print a formatted table row."""
    row = ""
    for col, width in zip(columns, widths):
        row += f"{str(col):>{width}}  "
    print(f"  {row}")


def print_results(result: "OptimizationResult") -> None:
    """
    Print optimization results in a formatted table.

    Args:
        result: OptimizationResult from an optimizer
    """
    print_subheader("Efficient Frontier Results")

    tickers = result.tickers
    ticker_width = max(len(t) for t in tickers)
    col_widths = [8] + [ticker_width + 2] * len(tickers) + [10]

    # Table header
    header = ["Return"] + tickers + ["Volatility"]
    print_table_row(header, col_widths)
    print(f"  {'-' * sum(w + 2 for w in col_widths)}")

    # Table rows
    for i in range(len(result.expected_returns)):
        weights_pct = [f"{w * 100:.1f}%" for w in result.weights[i]]
        row = (
            [f"{result.expected_returns[i] * 100:.2f}%"]
            + weights_pct
            + [f"{result.volatilities[i] * 100:.2f}%"]
        )
        print_table_row(row, col_widths)
