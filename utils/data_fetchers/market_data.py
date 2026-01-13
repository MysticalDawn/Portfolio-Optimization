"""
Market data fetching utilities using yfinance
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class MarketDataFetcher:
    """Fetch and process market data for portfolio optimization"""

    def __init__(self, tickers: List[str], period: str = "2y", interval: str = "1d"):
        """
        Initialize market data fetcher

        Args:
            tickers: List of stock ticker symbols
            period: Data period (1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max)
            interval: Data interval (1d, 1wk, 1mo)
        """
        self.tickers = tickers
        self.period = period
        self.interval = interval
        self._prices = None
        self._returns = None

    def fetch_prices(self) -> pd.DataFrame:
        """
        Fetch historical adjusted close prices

        Returns:
            DataFrame with dates as index and tickers as columns
        """
        print(f"Fetching historical data for {len(self.tickers)} assets...")
        data = yf.download(self.tickers, period=self.period, interval=self.interval, progress=False)

        if len(self.tickers) == 1:
            self._prices = pd.DataFrame(data['Adj Close'])
            self._prices.columns = self.tickers
        else:
            self._prices = data['Adj Close']

        # Drop any tickers with insufficient data
        self._prices = self._prices.dropna(axis=1, how='all')
        missing = set(self.tickers) - set(self._prices.columns)
        if missing:
            print(f"Warning: Could not fetch data for: {missing}")

        return self._prices

    def calculate_returns(self) -> pd.DataFrame:
        """
        Calculate daily returns

        Returns:
            DataFrame of daily returns
        """
        if self._prices is None:
            self.fetch_prices()

        self._returns = self._prices.pct_change().dropna()
        return self._returns

    def get_expected_returns(self, method: str = "mean") -> pd.Series:
        """
        Calculate expected returns

        Args:
            method: 'mean' for historical mean, 'capm' for CAPM expected returns

        Returns:
            Series of expected annual returns for each ticker
        """
        if self._returns is None:
            self.calculate_returns()

        if method == "mean":
            # Annualized mean return
            return self._returns.mean() * 252
        else:
            raise NotImplementedError(f"Method {method} not implemented yet")

    def get_covariance_matrix(self) -> pd.DataFrame:
        """
        Calculate covariance matrix of returns

        Returns:
            Annualized covariance matrix
        """
        if self._returns is None:
            self.calculate_returns()

        # Annualized covariance matrix
        return self._returns.cov() * 252

    def get_correlation_matrix(self) -> pd.DataFrame:
        """Get correlation matrix of returns"""
        if self._returns is None:
            self.calculate_returns()
        return self._returns.corr()

    def get_current_prices(self) -> Dict[str, float]:
        """
        Get most recent prices for each ticker

        Returns:
            Dictionary mapping ticker to current price
        """
        if self._prices is None:
            self.fetch_prices()

        latest_prices = self._prices.iloc[-1].to_dict()
        return latest_prices

    def get_asset_info(self, ticker: str) -> Dict:
        """
        Get asset information

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with asset info (name, sector, etc.)
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0)
            }
        except Exception as e:
            print(f"Warning: Could not fetch info for {ticker}: {e}")
            return {'ticker': ticker, 'name': ticker}

    @property
    def prices(self) -> pd.DataFrame:
        """Get prices DataFrame"""
        if self._prices is None:
            self.fetch_prices()
        return self._prices

    @property
    def returns(self) -> pd.DataFrame:
        """Get returns DataFrame"""
        if self._returns is None:
            self.calculate_returns()
        return self._returns
