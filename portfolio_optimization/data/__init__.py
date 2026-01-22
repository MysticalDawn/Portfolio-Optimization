"""Data fetching and returns calculation module."""

from portfolio_optimization.data.fetcher import fetch_ticker_data
from portfolio_optimization.data.returns import (
    calculate_monthly_returns,
    calculate_yearly_returns,
)

__all__ = [
    "fetch_ticker_data",
    "calculate_monthly_returns",
    "calculate_yearly_returns",
]
