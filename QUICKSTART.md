# Quick Start Guide

## Setup (First Time Only)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python cli.py --help
   ```

## Try It Out

### Example 1: Optimize Your Portfolio
Using the default assets in `assets.json` (NOVT, NVDA, AMD, RBRK, EQIX):

```bash
python cli.py optimize --value 10000
```

### Example 2: Compare Strategies
See which strategy works best for your assets:

```bash
python cli.py compare
```

### Example 3: Analyze Holdings
If you currently own these stocks:

```bash
python cli.py analyze --holdings '{"NVDA": 5, "AMD": 10, "EQIX": 3}'
```

### Example 4: Get Rebalancing Advice
```bash
python cli.py rebalance --current '{"NVDA": 5, "AMD": 10, "EQIX": 3}' --strategy moderate
```

### Example 5: Backtest Performance
See how the strategy would have performed:

```bash
python cli.py backtest --strategy max_sharpe --period 3y
```

## Common Use Cases

### "I want to invest $50,000 in tech stocks"
```bash
python cli.py optimize \
  --tickers AAPL,MSFT,GOOGL,NVDA,AMD,TSLA \
  --value 50000 \
  --strategy moderate
```

### "How is my current portfolio performing?"
```bash
python cli.py analyze --holdings '{"AAPL": 10, "MSFT": 15, "GOOGL": 8}'
```

### "Should I rebalance my portfolio?"
```bash
python cli.py rebalance --current '{"AAPL": 10, "MSFT": 15}' --strategy max_sharpe
```

### "Which strategy has the best risk/return?"
```bash
python cli.py compare --tickers AAPL,MSFT,GOOGL,NVDA
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Modify `assets.json` to include your preferred stocks
- Experiment with different strategies and risk levels
- Use backtesting to validate strategies before investing

## Tips

1. **Start with comparison**: Run `compare` first to see all strategies
2. **Use realistic values**: Enter your actual investment amount
3. **Consider transaction costs**: The tool doesn't account for trading fees
4. **Rebalance periodically**: Run `rebalance` quarterly or annually
5. **Backtest first**: Always backtest a strategy before using it

## Help

For detailed help on any command:
```bash
python cli.py COMMAND --help
```

For example:
```bash
python cli.py optimize --help
python cli.py analyze --help
```
