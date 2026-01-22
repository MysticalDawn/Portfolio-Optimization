"""
Basic Portfolio Optimization Example

A simple starting point demonstrating Mean-Variance portfolio optimization
with a single stock. This serves as a minimal working example before
scaling up to multiple assets and more sophisticated methods.
"""

import numpy as np
import yfinance as yf

# 1. Fetch stock data
tickers = ["AAPL"]
prices = yf.download(tickers, period="1y", auto_adjust=True)["Close"]
print(prices)

# 2. Calculate daily returns
returns = prices.pct_change().dropna()
print(returns)

# 3. Calculate expected return and risk for each stock
expected_returns = returns.mean() * 252  # Annualized (252 trading days)
cov_matrix = returns.cov() * 252  # Annualized

print("Expected Annual Returns:")
print(expected_returns)
print("\nCovariance Matrix:")
print(cov_matrix)

# 4. Equal-weight portfolio as baseline
weights = np.array([1])

# 5. Portfolio metrics
portfolio_return = np.dot(weights, expected_returns)
portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
sharpe_ratio = portfolio_return / portfolio_volatility

print(f"\n--- Equal Weight Portfolio ---")
print(f"Expected Return: {portfolio_return:.2%}")
print(f"Volatility: {portfolio_volatility:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
