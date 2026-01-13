# Portfolio Optimization CLI

A command-line tool for portfolio optimization using Modern Portfolio Theory (Mean-Variance optimization / Markowitz model). Optimize your investment portfolio based on risk tolerance, analyze existing holdings, get rebalancing recommendations, and backtest strategies.

## Features

- **Optimize**: Find optimal portfolio allocation for a given risk level
- **Analyze**: Evaluate risk/return metrics of your current portfolio
- **Rebalance**: Get trade recommendations to rebalance to optimal allocation
- **Backtest**: Test historical performance of optimization strategies
- **Compare**: Compare different optimization strategies side-by-side

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The tool is ready to use!

## Quick Start

### 1. Define Your Assets

Create an `assets.json` file with your asset universe:

```json
{
  "assets": [
    {"Ticker": "AAPL"},
    {"Ticker": "MSFT"},
    {"Ticker": "GOOGL"},
    {"Ticker": "NVDA"},
    {"Ticker": "AMD"}
  ]
}
```

### 2. Optimize Portfolio

Find the optimal allocation using maximum Sharpe ratio:

```bash
python cli.py optimize --value 10000
```

Or specify tickers directly:

```bash
python cli.py optimize --tickers AAPL,MSFT,GOOGL --value 10000 --strategy moderate
```

### 3. Analyze Existing Portfolio

Check metrics for your current holdings:

```bash
python cli.py analyze --holdings '{"AAPL": 10, "MSFT": 15, "GOOGL": 5}'
```

### 4. Get Rebalancing Recommendations

Compare current vs optimal allocation:

```bash
python cli.py rebalance --current '{"AAPL": 10, "MSFT": 15}' --strategy max_sharpe
```

### 5. Backtest Performance

Test how a strategy would have performed historically:

```bash
python cli.py backtest --period 5y --strategy max_sharpe
```

## Commands Reference

### `optimize`

Optimize portfolio allocation from scratch.

**Options:**
- `--file, -f`: Path to assets JSON file (default: assets.json)
- `--tickers, -t`: Comma-separated list of tickers (e.g., AAPL,MSFT,GOOGL)
- `--strategy, -s`: Optimization strategy
  - `max_sharpe` (default): Maximum risk-adjusted returns
  - `min_volatility`: Minimum volatility portfolio
  - `conservative`: 10% target volatility
  - `moderate`: 15% target volatility
  - `aggressive`: 25% target volatility
- `--value, -v`: Total portfolio value (default: 10000)
- `--period, -p`: Historical data period (default: 2y)

**Example:**
```bash
python cli.py optimize --tickers AAPL,MSFT,GOOGL,NVDA --strategy moderate --value 50000
```

**Output:**
- Optimal allocation weights
- Expected return, volatility, and Sharpe ratio
- Discrete allocation (exact number of shares to buy)
- Leftover cash

---

### `analyze`

Analyze an existing portfolio's risk and return characteristics.

**Options:**
- `--holdings, -h`: Current holdings as JSON (required)
- `--period, -p`: Historical data period (default: 2y)

**Example:**
```bash
python cli.py analyze --holdings '{"AAPL": 10, "MSFT": 20, "NVDA": 15}'
```

**Output:**
- Current portfolio summary (quantity, value, weight)
- Expected annual return and volatility
- Sharpe ratio
- Historical performance metrics
- Maximum drawdown

---

### `rebalance`

Get rebalancing recommendations for an existing portfolio.

**Options:**
- `--current, -c`: Current holdings as JSON (required)
- `--strategy, -s`: Target optimization strategy (default: max_sharpe)
- `--period, -p`: Historical data period (default: 2y)

**Example:**
```bash
python cli.py rebalance --current '{"AAPL": 10, "MSFT": 15, "GOOGL": 8}' --strategy moderate
```

**Output:**
- Current portfolio summary
- Target allocation weights
- Specific buy/sell trades needed
- Expected performance after rebalancing

---

### `backtest`

Backtest optimized portfolio performance over historical data.

**Options:**
- `--file, -f`: Path to assets JSON file (default: assets.json)
- `--tickers, -t`: Comma-separated list of tickers
- `--strategy, -s`: Optimization strategy (default: max_sharpe)
- `--period, -p`: Backtest period (default: 5y)
- `--rebalance, -r`: Rebalancing frequency (monthly/quarterly/yearly/none)

**Example:**
```bash
python cli.py backtest --tickers AAPL,MSFT,GOOGL --strategy max_sharpe --period 5y
```

**Output:**
- Total and annualized returns
- Volatility and maximum drawdown
- Sharpe ratio
- Comparison with equal-weight portfolio

---

### `compare`

Compare different optimization strategies side-by-side.

**Options:**
- `--file, -f`: Path to assets JSON file (default: assets.json)
- `--tickers, -t`: Comma-separated list of tickers

**Example:**
```bash
python cli.py compare --tickers AAPL,MSFT,GOOGL,NVDA,AMD
```

**Output:**
- Table comparing all strategies
- Expected return, volatility, and Sharpe ratio for each

---

## Optimization Strategies Explained

### Max Sharpe Ratio
Maximizes risk-adjusted returns (return per unit of risk). Best for investors seeking optimal balance between risk and return.

### Min Volatility
Minimizes portfolio volatility. Best for conservative investors prioritizing capital preservation.

### Conservative (10% target volatility)
Targets 10% annual volatility. Low-risk approach suitable for risk-averse investors.

### Moderate (15% target volatility)
Targets 15% annual volatility. Balanced risk/return profile for average investors.

### Aggressive (25% target volatility)
Targets 25% annual volatility. Higher risk/return profile for risk-tolerant investors.

## Technical Details

### Optimization Method
Uses **Modern Portfolio Theory (MPT)** / Markowitz Mean-Variance optimization:
- Maximizes expected return for a given level of risk
- Considers correlations between assets
- Constructs efficient frontier of optimal portfolios

### Libraries Used
- **yfinance**: Free market data from Yahoo Finance
- **PyPortfolioOpt**: Pre-built optimization algorithms
- **pandas/numpy**: Data manipulation and numerical computing
- **click**: CLI framework
- **tabulate**: Formatted table output

### Risk Metrics
- **Volatility**: Standard deviation of returns (annualized)
- **Sharpe Ratio**: (Return - Risk-free rate) / Volatility
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Expected Return**: Mean historical return (annualized)

## Examples

### Example 1: Tech Portfolio Optimization
```bash
python cli.py optimize \
  --tickers AAPL,MSFT,GOOGL,META,NVDA,AMD,TSLA \
  --strategy moderate \
  --value 100000
```

### Example 2: Diversified Portfolio Analysis
```bash
python cli.py analyze \
  --holdings '{"SPY": 50, "AGG": 30, "GLD": 10, "VNQ": 5}'
```

### Example 3: Rebalance with Max Sharpe
```bash
python cli.py rebalance \
  --current '{"AAPL": 25, "MSFT": 25, "GOOGL": 25, "NVDA": 25}' \
  --strategy max_sharpe
```

### Example 4: Backtest Conservative Strategy
```bash
python cli.py backtest \
  --tickers AAPL,MSFT,JNJ,PG,KO \
  --strategy conservative \
  --period 10y
```

## Notes

- All prices and returns are based on adjusted close prices
- Historical data is fetched from Yahoo Finance (free, no API key required)
- Optimization uses 2 years of historical data by default
- Returns and volatility are annualized (252 trading days/year)
- Risk-free rate defaults to 2% for Sharpe ratio calculations

## Troubleshooting

**Issue**: "Could not fetch data for ticker X"
- **Solution**: Check ticker symbol is correct and traded on Yahoo Finance

**Issue**: "Target volatility not achievable"
- **Solution**: Assets may not support desired risk level; try a different strategy

**Issue**: ModuleNotFoundError
- **Solution**: Run `pip install -r requirements.txt`

## License

MIT License

## Contributing

Contributions welcome! Please submit issues and pull requests.
