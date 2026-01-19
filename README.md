# Portfolio Optimization

Simple Mean-Variance (Markowitz) portfolio optimization.

## Quick Start

```bash
pip install -r requirements.txt
python portfolio.py
```

## What it does

1. Fetches historical stock prices
2. Calculates expected returns and risk (covariance)
3. Finds optimal portfolio weights using two strategies:
   - **Max Sharpe**: Maximize risk-adjusted returns
   - **Min Volatility**: Minimize portfolio risk
