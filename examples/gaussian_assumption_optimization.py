"""
Markowitz Portfolio Optimization
Assumptions:
- returns follow normal distribution
- one year investment period
- ten years estimation period

Constraints:
- Long-only constraint (weights >= 0)
- Turnover constraint (sum of weight changes <= turnover_limit)
"""

import numpy as np
import yfinance as yf
from scipy.optimize import minimize

# 1. Fetch stock data
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "JPM"]
prices_monthly = yf.download(tickers, period="10y", auto_adjust=True)["Close"]
prices_monthly.head()
# 2. Calculate daily returns
log_returns_monthly = (np.log(prices_monthly) - np.log(prices_monthly.shift(1))).dropna()

# 3. Expected return and covariance (annualized)
log_returns_monthly_mean = np.mean(log_returns_monthly)
log_returns_monthly_cov = np.cov(log_returns_monthly.T)

log_returns_yearly_mean = 12 * log_returns_monthly_mean
log_returns_yearly_cov = 12 * log_returns_monthly_cov

p_0 = prices_monthly.iloc[0].to_numpy()

m_P = p_0 * np.exp(log_returns_yearly_mean + 0.5 * np.diag(log_returns_yearly_cov))
S_P = np.outer(m_P, m_P) * (np.exp(log_returns_yearly_cov) - 1)

expected_returns = 1 / p_0 * m_P - 1
cov_matrix = 1 / np.outer(p_0, p_0) * S_P

n = len(tickers)

# 4. Previous weights (e.g. equal-weight as starting portfolio)
prev_weights = np.ones(n) / n

# ── Optimization ──────────────────────────────────────────────────────────────

def portfolio_volatility(weights):
    return np.sqrt(weights.T @ cov_matrix @ weights)

# Target: maximize Sharpe ratio  →  minimize negative Sharpe
def neg_returns(weights):
    return - weights @ expected_returns

risk_threshold = 0.20  # maximum annualized volatility (e.g. 20%)

constraints = [
    # Weights sum to 1
    {"type": "eq",  "fun": lambda w: np.sum(w) - 1},
    # Turnover constraint
    {"type": "ineq", "fun": lambda w: (turnover_trades / 252) - np.sum(np.abs(w - prev_weights))},
    # Risk constraint: volatility <= risk_threshold
    {"type": "ineq", "fun": lambda w: risk_threshold - portfolio_volatility(w)},
]

bounds = [(0, 1)] * n          # Long-only: each weight in [0, 1]
turnover_trades = 52           # This is the number of trades in a year (e.g. turnover_trades = 52 means you hold the portoflio for a week) 
x0 = prev_weights.copy()       # Start from current portfolio

result = minimize(
    neg_returns,
    x0,
    method="SLSQP",
    bounds=bounds,
    constraints=constraints,
)

# ── Results ───────────────────────────────────────────────────────────────────

opt_weights = result.x
opt_return  = opt_weights @ expected_returns
opt_vol     = portfolio_volatility(opt_weights)
opt_sharpe  = opt_return / opt_vol
turnover    = np.sum(np.abs(opt_weights - prev_weights))

print("─" * 40)
print(f"{'Asset':<8} {'Prev':>8} {'Optimal':>8} {'Change':>8}")
print("─" * 40)
for t, pw, ow in zip(tickers, prev_weights, opt_weights):
    print(f"{t:<8} {pw:>8.1%} {ow:>8.1%} {ow - pw:>+8.1%}")
print("─" * 40)
print(f"\nExpected Return : {opt_return:.2%}")
print(f"Volatility      : {opt_vol:.2%}")
print(f"Sharpe Ratio    : {opt_sharpe:.2f}")
print(f"Turnover        : {turnover:.2%}  (limit: {turnover_trades})")
