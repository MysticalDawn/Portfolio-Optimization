"""
Portfolio class for managing holdings and performing analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from utils.data_fetchers.market_data import MarketDataFetcher


class Portfolio:
    """Represents an investment portfolio with holdings and provides analysis methods"""

    def __init__(self, holdings: Optional[Dict[str, float]] = None, cash: float = 0.0):
        """
        Initialize portfolio

        Args:
            holdings: Dictionary mapping ticker to quantity owned
            cash: Cash balance in portfolio
        """
        self.holdings = holdings or {}
        self.cash = cash
        self._market_data = None
        self._current_prices = None

    @classmethod
    def from_weights(cls, tickers: List[str], weights: Dict[str, float], total_value: float):
        """
        Create portfolio from allocation weights

        Args:
            tickers: List of ticker symbols
            weights: Dictionary mapping ticker to weight (should sum to 1)
            total_value: Total portfolio value

        Returns:
            Portfolio instance
        """
        fetcher = MarketDataFetcher(tickers)
        current_prices = fetcher.get_current_prices()

        holdings = {}
        for ticker in tickers:
            if ticker in weights and ticker in current_prices:
                dollar_amount = weights[ticker] * total_value
                holdings[ticker] = dollar_amount / current_prices[ticker]

        return cls(holdings=holdings)

    def get_tickers(self) -> List[str]:
        """Get list of tickers in portfolio"""
        return list(self.holdings.keys())

    def get_market_data(self, period: str = "2y") -> MarketDataFetcher:
        """Get market data fetcher for portfolio tickers"""
        if self._market_data is None:
            self._market_data = MarketDataFetcher(self.get_tickers(), period=period)
            self._market_data.fetch_prices()
        return self._market_data

    def get_current_prices(self) -> Dict[str, float]:
        """Get current market prices for all holdings"""
        if self._current_prices is None:
            fetcher = MarketDataFetcher(self.get_tickers())
            self._current_prices = fetcher.get_current_prices()
        return self._current_prices

    def get_position_values(self) -> Dict[str, float]:
        """
        Calculate current value of each position

        Returns:
            Dictionary mapping ticker to dollar value
        """
        prices = self.get_current_prices()
        return {ticker: qty * prices[ticker] for ticker, qty in self.holdings.items()}

    def get_total_value(self) -> float:
        """Calculate total portfolio value (holdings + cash)"""
        position_values = self.get_position_values()
        return sum(position_values.values()) + self.cash

    def get_weights(self) -> Dict[str, float]:
        """
        Calculate current portfolio weights

        Returns:
            Dictionary mapping ticker to weight (fraction of total value)
        """
        position_values = self.get_position_values()
        total_value = self.get_total_value()

        if total_value == 0:
            return {ticker: 0.0 for ticker in self.holdings.keys()}

        return {ticker: value / total_value for ticker, value in position_values.items()}

    def calculate_metrics(self, risk_free_rate: float = 0.02) -> Dict:
        """
        Calculate portfolio performance metrics

        Args:
            risk_free_rate: Annual risk-free rate for Sharpe ratio

        Returns:
            Dictionary of metrics (return, volatility, Sharpe ratio, etc.)
        """
        weights = self.get_weights()
        market_data = self.get_market_data()

        # Get expected returns and covariance
        expected_returns = market_data.get_expected_returns()
        cov_matrix = market_data.get_covariance_matrix()

        # Calculate portfolio return and volatility
        weights_series = pd.Series(weights)
        portfolio_return = (weights_series * expected_returns).sum()
        portfolio_variance = np.dot(weights_series, np.dot(cov_matrix, weights_series))
        portfolio_volatility = np.sqrt(portfolio_variance)

        # Sharpe ratio
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0

        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio,
            'total_value': self.get_total_value()
        }

    def calculate_historical_performance(self) -> Dict:
        """
        Calculate actual historical performance

        Returns:
            Dictionary with cumulative return, max drawdown, etc.
        """
        market_data = self.get_market_data()
        returns = market_data.returns
        weights = pd.Series(self.get_weights())

        # Calculate portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)

        # Cumulative returns
        cumulative_returns = (1 + portfolio_returns).cumprod()
        total_return = cumulative_returns.iloc[-1] - 1

        # Max drawdown
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()

        # Annualized metrics
        num_years = len(portfolio_returns) / 252
        annualized_return = (1 + total_return) ** (1 / num_years) - 1
        annualized_volatility = portfolio_returns.std() * np.sqrt(252)

        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_volatility,
            'max_drawdown': max_drawdown,
            'cumulative_returns': cumulative_returns
        }

    def summary(self) -> pd.DataFrame:
        """
        Generate portfolio summary table

        Returns:
            DataFrame with ticker, quantity, price, value, weight
        """
        prices = self.get_current_prices()
        position_values = self.get_position_values()
        weights = self.get_weights()

        data = []
        for ticker in self.holdings.keys():
            data.append({
                'Ticker': ticker,
                'Quantity': self.holdings[ticker],
                'Price': prices[ticker],
                'Value': position_values[ticker],
                'Weight': weights[ticker]
            })

        df = pd.DataFrame(data)
        df = df.sort_values('Value', ascending=False)

        return df

    def __repr__(self):
        return f"Portfolio(holdings={len(self.holdings)}, total_value=${self.get_total_value():,.2f})"
