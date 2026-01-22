"""Base class for portfolio optimization algorithms."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import pandas as pd

from portfolio_optimization.config import load_assets
from portfolio_optimization.data import (
    fetch_ticker_data,
    calculate_monthly_returns,
    calculate_yearly_returns,
)


@dataclass
class OptimizationResult:
    """Container for optimization results."""

    weights: np.ndarray  # Shape: (num_portfolios, num_assets)
    expected_returns: np.ndarray  # Shape: (num_portfolios,)
    volatilities: np.ndarray  # Shape: (num_portfolios,)
    tickers: list[str]
    covariance_matrix: np.ndarray
    algorithm_name: str
    metadata: dict  # Algorithm-specific additional data


class BaseOptimizer(ABC):
    """
    Abstract base class for portfolio optimization algorithms.

    Subclasses must implement the `optimize` method with their specific
    optimization logic.
    """

    name: str = "base"
    description: str = "Base optimizer"

    def __init__(self, period: str = "10y"):
        """
        Initialize the optimizer.

        Args:
            period: Historical data period (e.g., "5y", "10y")
        """
        self.period = period
        self.tickers: list[str] = []
        self.data: list[pd.DataFrame] = []
        self.monthly_returns: list[pd.DataFrame] = []
        self.yearly_returns: list[pd.DataFrame] = []
        self.covariance_matrix: np.ndarray | None = None
        self._data_loaded = False

    def load_data(self) -> None:
        """Load and prepare market data for optimization."""
        self.tickers = load_assets()
        self.data = [fetch_ticker_data(ticker, period=self.period) for ticker in self.tickers]
        self.monthly_returns = [calculate_monthly_returns(d) for d in self.data]
        self.yearly_returns = [calculate_yearly_returns(d) for d in self.data]

        # Compute covariance matrix
        yearly_returns_array = np.array([df.values.flatten() for df in self.yearly_returns])
        self.covariance_matrix = np.cov(yearly_returns_array)
        self._data_loaded = True

    def _ensure_data_loaded(self) -> None:
        """Ensure data is loaded before optimization."""
        if not self._data_loaded:
            self.load_data()

    @abstractmethod
    def optimize(self, **kwargs) -> OptimizationResult:
        """
        Run the optimization algorithm.

        Args:
            **kwargs: Algorithm-specific parameters

        Returns:
            OptimizationResult containing weights and metrics
        """
        pass

    def calculate_portfolio_volatility(self, weights: np.ndarray) -> float:
        """Calculate portfolio volatility given weights."""
        if self.covariance_matrix is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        return float(np.sqrt(weights.T @ self.covariance_matrix @ weights))

    def calculate_portfolio_return(
        self, weights: np.ndarray, expected_returns: np.ndarray
    ) -> float:
        """Calculate expected portfolio return given weights."""
        return float(np.sum(weights * expected_returns))
