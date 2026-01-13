"""
Portfolio optimization using PyPortfolioOpt
"""
import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from typing import Dict, List, Optional, Tuple
from utils.data_fetchers.market_data import MarketDataFetcher


class PortfolioOptimizer:
    """Mean-Variance portfolio optimization using Markowitz model"""

    def __init__(self, tickers: List[str], period: str = "2y"):
        """
        Initialize optimizer

        Args:
            tickers: List of ticker symbols to optimize
            period: Historical data period for optimization
        """
        self.tickers = tickers
        self.period = period
        self.market_data = MarketDataFetcher(tickers, period=period)
        self.market_data.fetch_prices()

        # Calculate expected returns and covariance
        self.expected_returns = self.market_data.get_expected_returns()
        self.cov_matrix = self.market_data.get_covariance_matrix()

    def optimize_max_sharpe(self, risk_free_rate: float = 0.02) -> Tuple[Dict[str, float], Dict]:
        """
        Optimize for maximum Sharpe ratio

        Args:
            risk_free_rate: Annual risk-free rate

        Returns:
            Tuple of (weights dictionary, performance dictionary)
        """
        ef = EfficientFrontier(self.expected_returns, self.cov_matrix)
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(risk_free_rate=risk_free_rate, verbose=False)

        return cleaned_weights, {
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2]
        }

    def optimize_min_volatility(self) -> Tuple[Dict[str, float], Dict]:
        """
        Optimize for minimum volatility

        Returns:
            Tuple of (weights dictionary, performance dictionary)
        """
        ef = EfficientFrontier(self.expected_returns, self.cov_matrix)
        weights = ef.min_volatility()
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(verbose=False)

        return cleaned_weights, {
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2]
        }

    def optimize_efficient_risk(self, target_volatility: float) -> Tuple[Dict[str, float], Dict]:
        """
        Optimize for maximum return given a target volatility

        Args:
            target_volatility: Target annual volatility (e.g., 0.15 for 15%)

        Returns:
            Tuple of (weights dictionary, performance dictionary)
        """
        ef = EfficientFrontier(self.expected_returns, self.cov_matrix)
        weights = ef.efficient_risk(target_volatility=target_volatility)
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(verbose=False)

        return cleaned_weights, {
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2]
        }

    def optimize_efficient_return(self, target_return: float) -> Tuple[Dict[str, float], Dict]:
        """
        Optimize for minimum risk given a target return

        Args:
            target_return: Target annual return (e.g., 0.15 for 15%)

        Returns:
            Tuple of (weights dictionary, performance dictionary)
        """
        ef = EfficientFrontier(self.expected_returns, self.cov_matrix)
        weights = ef.efficient_return(target_return=target_return)
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(verbose=False)

        return cleaned_weights, {
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2]
        }

    def optimize_by_risk_level(self, risk_level: str) -> Tuple[Dict[str, float], Dict]:
        """
        Optimize based on risk level description

        Args:
            risk_level: 'conservative', 'moderate', or 'aggressive'

        Returns:
            Tuple of (weights dictionary, performance dictionary)
        """
        risk_targets = {
            'conservative': 0.10,  # 10% volatility target
            'moderate': 0.15,      # 15% volatility target
            'aggressive': 0.25     # 25% volatility target
        }

        if risk_level.lower() not in risk_targets:
            raise ValueError(f"Risk level must be one of: {list(risk_targets.keys())}")

        target_vol = risk_targets[risk_level.lower()]

        try:
            return self.optimize_efficient_risk(target_vol)
        except Exception:
            # If target volatility not achievable, use max Sharpe instead
            print(f"Warning: Could not achieve {target_vol:.0%} volatility. Using max Sharpe instead.")
            return self.optimize_max_sharpe()

    def get_discrete_allocation(self, weights: Dict[str, float], total_portfolio_value: float) -> Tuple[Dict[str, int], float]:
        """
        Convert continuous weights to discrete share quantities

        Args:
            weights: Dictionary of ticker weights
            total_portfolio_value: Total value to allocate

        Returns:
            Tuple of (discrete allocation dictionary, leftover cash)
        """
        latest_prices = self.market_data.get_current_prices()

        da = DiscreteAllocation(weights, latest_prices, total_value=total_portfolio_value)
        allocation, leftover = da.greedy_portfolio()

        return allocation, leftover

    def calculate_efficient_frontier(self, num_points: int = 100) -> pd.DataFrame:
        """
        Calculate points along the efficient frontier

        Args:
            num_points: Number of portfolios to calculate

        Returns:
            DataFrame with return, volatility, and sharpe ratio for each portfolio
        """
        # Get range of returns
        min_ret = self.expected_returns.min()
        max_ret = self.expected_returns.max()

        target_returns = np.linspace(min_ret, max_ret, num_points)

        frontier_data = []
        for target_ret in target_returns:
            try:
                ef = EfficientFrontier(self.expected_returns, self.cov_matrix)
                ef.efficient_return(target_return=target_ret)
                perf = ef.portfolio_performance(verbose=False)

                frontier_data.append({
                    'return': perf[0],
                    'volatility': perf[1],
                    'sharpe': perf[2]
                })
            except Exception:
                continue

        return pd.DataFrame(frontier_data)

    def compare_strategies(self) -> pd.DataFrame:
        """
        Compare different optimization strategies

        Returns:
            DataFrame comparing max Sharpe, min volatility, and risk-targeted portfolios
        """
        strategies = {}

        # Max Sharpe
        _, perf = self.optimize_max_sharpe()
        strategies['Max Sharpe'] = perf

        # Min Volatility
        _, perf = self.optimize_min_volatility()
        strategies['Min Volatility'] = perf

        # Risk levels
        for risk_level in ['conservative', 'moderate', 'aggressive']:
            try:
                _, perf = self.optimize_by_risk_level(risk_level)
                strategies[risk_level.capitalize()] = perf
            except Exception:
                pass

        return pd.DataFrame(strategies).T
