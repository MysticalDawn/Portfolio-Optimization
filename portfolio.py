"""
Simple Portfolio Optimization using Mean-Variance (Markowitz) Model

This script demonstrates the basics of portfolio optimization:
1. Fetch historical stock data
2. Calculate expected returns and covariance
3. Find optimal portfolio weights using different strategies
"""

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize


def fetch_stock_data(tickers: list[str], period: str = "2y") -> pd.DataFrame:
    """
    Fetch historical adjusted close prices for given tickers.

    Args:
        tickers: List of stock symbols (e.g., ['AAPL', 'GOOGL', 'MSFT'])
        period: Historical period ('1y', '2y', '5y', etc.)

    Returns:
        DataFrame with adjusted close prices
    """
    data = yf.download(tickers, period=period, auto_adjust=True)["Close"]
    return data.dropna()


def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily returns from price data."""
    return prices.pct_change().dropna()


def portfolio_performance(
    weights: np.ndarray, mean_returns: np.ndarray, cov_matrix: np.ndarray
) -> tuple[float, float]:
    """
    Calculate portfolio expected return and volatility.

    Args:
        weights: Portfolio weights
        mean_returns: Expected returns for each asset
        cov_matrix: Covariance matrix of returns

    Returns:
        Tuple of (expected_return, volatility)
    """
    expected_return = np.dot(weights, mean_returns) * 252  # Annualized
    volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
    return expected_return, volatility


def negative_sharpe_ratio(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = 0.02,
) -> float:
    """Calculate negative Sharpe ratio (for minimization)."""
    ret, vol = portfolio_performance(weights, mean_returns, cov_matrix)
    return -(ret - risk_free_rate) / vol


def portfolio_volatility(
    weights: np.ndarray, mean_returns: np.ndarray, cov_matrix: np.ndarray
) -> float:
    """Calculate portfolio volatility (for minimization)."""
    _, vol = portfolio_performance(weights, mean_returns, cov_matrix)
    return vol


def optimize_portfolio(
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    objective: str = "max_sharpe",
    risk_free_rate: float = 0.02,
) -> np.ndarray:
    """
    Find optimal portfolio weights.

    Args:
        mean_returns: Expected returns for each asset
        cov_matrix: Covariance matrix
        objective: 'max_sharpe' or 'min_volatility'
        risk_free_rate: Risk-free rate for Sharpe calculation

    Returns:
        Optimal portfolio weights
    """
    n_assets = len(mean_returns)
    initial_weights = np.ones(n_assets) / n_assets

    # Constraints: weights sum to 1
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}

    # Bounds: each weight between 0 and 1 (long-only)
    bounds = tuple((0, 1) for _ in range(n_assets))

    if objective == "max_sharpe":
        result = minimize(
            negative_sharpe_ratio,
            initial_weights,
            args=(mean_returns, cov_matrix, risk_free_rate),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
    else:  # min_volatility
        result = minimize(
            portfolio_volatility,
            initial_weights,
            args=(mean_returns, cov_matrix),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

    return result.x


def display_results(
    tickers: list[str],
    weights: np.ndarray,
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = 0.02,
):
    """Display optimization results."""
    ret, vol = portfolio_performance(weights, mean_returns, cov_matrix)
    sharpe = (ret - risk_free_rate) / vol

    print("\n" + "=" * 50)
    print("OPTIMAL PORTFOLIO ALLOCATION")
    print("=" * 50)

    for ticker, weight in zip(tickers, weights):
        if weight > 0.001:  # Only show non-zero allocations
            print(f"  {ticker:6s}: {weight*100:6.2f}%")

    print("-" * 50)
    print(f"  Expected Return:  {ret*100:6.2f}%")
    print(f"  Volatility:       {vol*100:6.2f}%")
    print(f"  Sharpe Ratio:     {sharpe:6.2f}")
    print("=" * 50)


# =============================================================================
# MAIN EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Define assets to optimize
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "META"]

    print("Fetching stock data...")
    prices = fetch_stock_data(tickers, period="2y")

    # Calculate returns
    returns = calculate_returns(prices)
    mean_returns = returns.mean().values
    cov_matrix = returns.cov().values

    # Optimize for Maximum Sharpe Ratio
    print("\n>>> Optimizing for Maximum Sharpe Ratio...")
    weights_sharpe = optimize_portfolio(
        mean_returns, cov_matrix, objective="max_sharpe"
    )
    display_results(tickers, weights_sharpe, mean_returns, cov_matrix)

    # Optimize for Minimum Volatility
    print("\n>>> Optimizing for Minimum Volatility...")
    weights_min_vol = optimize_portfolio(
        mean_returns, cov_matrix, objective="min_volatility"
    )
    display_results(tickers, weights_min_vol, mean_returns, cov_matrix)
