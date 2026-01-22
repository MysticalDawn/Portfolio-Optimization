# Portfolio Optimization

A flexible framework for portfolio optimization supporting multiple algorithms.

## Features

- **Pluggable Algorithms**: Easy to add and switch between optimization methods
- **Monte Carlo Resampling**: Accounts for estimation uncertainty (Michaud, 1998)
- **Shrinkage Estimation**: Reduces overfitting to historical data
- **Efficient Frontier**: Generates optimal portfolios across risk-return spectrum
- **Data Caching**: Avoids redundant API calls to yfinance

## Project Structure

```
portfolio-optimization/
├── portfolio_optimization/       # Main package
│   ├── __init__.py
│   ├── __main__.py               # CLI entry point
│   ├── algorithms/               # Optimization algorithms
│   │   ├── base.py               # Abstract base class
│   │   └── monte_carlo_resampling.py
│   ├── config/                   # Configuration
│   │   ├── loader.py
│   │   └── assets.json
│   ├── data/                     # Data handling
│   │   ├── fetcher.py
│   │   └── returns.py
│   └── utils/                    # Shared utilities
│       ├── solvers.py            # Optimization solvers
│       └── formatting.py         # Output formatting
├── examples/
│   └── basic_portfolio.py
├── cache/                        # Data cache (gitignored)
├── requirements.txt
└── README.md
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run interactive optimization
python -m portfolio_optimization
```

You'll be guided through:
1. Selecting an optimization algorithm
2. Configuring parameters (period, simulations, etc.)
3. Viewing results

## Adding New Algorithms

To add a new optimization algorithm:

1. Create a new file in `portfolio_optimization/algorithms/`
2. Inherit from `BaseOptimizer`
3. Implement the `optimize()` method
4. Register in `algorithms/__init__.py`

Example:

```python
from portfolio_optimization.algorithms.base import BaseOptimizer, OptimizationResult

class MyNewAlgorithm(BaseOptimizer):
    name = "my_algorithm"
    description = "My custom optimization approach"

    def optimize(self, **kwargs) -> OptimizationResult:
        self._ensure_data_loaded()
        # Your optimization logic here
        ...
```

## Available Algorithms

| Algorithm | Description |
|-----------|-------------|
| `mean_variance` | Classic Markowitz Mean-Variance optimization |
| `monte_carlo_resampling` | Resampled efficient frontier with estimation uncertainty |

*More coming: black_litterman, risk_parity, hierarchical_risk_parity, etc.*

## Configuration

Edit `portfolio_optimization/config/assets.json` to customize the asset universe:

```json
{
    "assets": ["AAPL", "GOOGL", "MSFT", ...]
}
```

## Programmatic Usage

```python
from portfolio_optimization import MonteCarloResampling

# Initialize optimizer
optimizer = MonteCarloResampling(period="10y")

# Run optimization
result = optimizer.optimize(
    shrinkage_intensity=0.7,
    num_simulations=500,
    num_portfolios=10,
)

# Access results
print(result.weights)           # Portfolio weights
print(result.expected_returns)  # Target returns
print(result.volatilities)      # Portfolio volatilities
print(result.tickers)           # Asset tickers
```

## Interactive CLI

```
============================================================
 PORTFOLIO OPTIMIZATION
============================================================
Configure your optimization parameters below.
Press Enter to use default values.

Available algorithms:
  1. mean_variance: Classic Markowitz Mean-Variance optimization
  2. monte_carlo_resampling: Resampled Efficient Frontier with estimation uncertainty

Select algorithm (1-2) [1]: 
Historical data period (e.g., 5y, 10y) [10y]: 
Shrinkage intensity (0.0 - 1.0) [0.7]: 
Number of simulations [500]: 
Number of portfolios on frontier [10]: 
```
