#!/usr/bin/env python3
"""
Portfolio Optimization CLI
A command-line tool for portfolio optimization using Modern Portfolio Theory
"""
import click
import json
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style, init
from portfolio import Portfolio
from utils.optimizer import PortfolioOptimizer
from utils.data_fetchers.market_data import MarketDataFetcher

# Initialize colorama
init(autoreset=True)


def print_success(message):
    """Print success message in green"""
    click.echo(Fore.GREEN + message + Style.RESET_ALL)


def print_error(message):
    """Print error message in red"""
    click.echo(Fore.RED + f"Error: {message}" + Style.RESET_ALL)


def print_info(message):
    """Print info message in blue"""
    click.echo(Fore.BLUE + message + Style.RESET_ALL)


def print_warning(message):
    """Print warning message in yellow"""
    click.echo(Fore.YELLOW + message + Style.RESET_ALL)


def format_percentage(value):
    """Format decimal as percentage"""
    return f"{value * 100:.2f}%"


def format_currency(value):
    """Format value as currency"""
    return f"${value:,.2f}"


def load_assets_from_file(filepath: str = "assets.json"):
    """Load assets from JSON file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return [asset['Ticker'] for asset in data.get('assets', [])]
    except FileNotFoundError:
        print_error(f"File {filepath} not found")
        return []
    except json.JSONDecodeError:
        print_error(f"Invalid JSON in {filepath}")
        return []


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Portfolio Optimization CLI

    A tool for optimizing investment portfolios using Mean-Variance optimization (Markowitz model).
    """
    pass


@cli.command()
@click.option('--file', '-f', default='assets.json', help='Path to assets JSON file')
@click.option('--holdings', '-h', help='Holdings as JSON string (e.g., \'{"AAPL": 10, "MSFT": 20}\')')
@click.option('--period', '-p', default='2y', help='Historical data period (1y, 2y, 5y, etc.)')
def analyze(file, holdings, period):
    """Analyze an existing portfolio's risk and return characteristics"""
    print_info("=== Portfolio Analysis ===\n")

    # Load holdings
    if holdings:
        try:
            holdings_dict = json.loads(holdings)
        except json.JSONDecodeError:
            print_error("Invalid JSON format for holdings")
            return
    else:
        # Try to load from file
        print_error("Please provide holdings using --holdings option")
        print_info("Example: --holdings '{\"AAPL\": 10, \"MSFT\": 20}'")
        return

    try:
        # Create portfolio
        portfolio = Portfolio(holdings=holdings_dict)

        # Display portfolio summary
        print_info("Current Holdings:")
        summary_df = portfolio.summary()
        print(tabulate(summary_df, headers='keys', tablefmt='grid', floatfmt='.2f'))
        print()

        # Calculate metrics
        print_info("Portfolio Metrics:")
        metrics = portfolio.calculate_metrics()
        metrics_table = [
            ['Total Value', format_currency(metrics['total_value'])],
            ['Expected Annual Return', format_percentage(metrics['expected_return'])],
            ['Annual Volatility', format_percentage(metrics['volatility'])],
            ['Sharpe Ratio', f"{metrics['sharpe_ratio']:.2f}"]
        ]
        print(tabulate(metrics_table, tablefmt='grid'))
        print()

        # Historical performance
        print_info("Historical Performance:")
        hist_perf = portfolio.calculate_historical_performance()
        perf_table = [
            ['Total Return', format_percentage(hist_perf['total_return'])],
            ['Annualized Return', format_percentage(hist_perf['annualized_return'])],
            ['Annualized Volatility', format_percentage(hist_perf['annualized_volatility'])],
            ['Maximum Drawdown', format_percentage(hist_perf['max_drawdown'])]
        ]
        print(tabulate(perf_table, tablefmt='grid'))

        print_success("\nAnalysis complete!")

    except Exception as e:
        print_error(f"Analysis failed: {str(e)}")


@cli.command()
@click.option('--file', '-f', default='assets.json', help='Path to assets JSON file')
@click.option('--tickers', '-t', help='Comma-separated list of tickers (e.g., AAPL,MSFT,GOOGL)')
@click.option('--strategy', '-s', type=click.Choice(['max_sharpe', 'min_volatility', 'conservative', 'moderate', 'aggressive']),
              default='max_sharpe', help='Optimization strategy')
@click.option('--value', '-v', type=float, default=10000, help='Total portfolio value for allocation')
@click.option('--period', '-p', default='2y', help='Historical data period')
def optimize(file, tickers, strategy, value, period):
    """Optimize portfolio allocation from scratch"""
    print_info("=== Portfolio Optimization ===\n")

    # Load tickers
    if tickers:
        ticker_list = [t.strip().upper() for t in tickers.split(',')]
    else:
        ticker_list = load_assets_from_file(file)

    if not ticker_list:
        print_error("No tickers provided. Use --tickers or ensure assets.json exists")
        return

    print_info(f"Optimizing portfolio with {len(ticker_list)} assets: {', '.join(ticker_list)}")
    print_info(f"Strategy: {strategy}")
    print_info(f"Target portfolio value: {format_currency(value)}\n")

    try:
        # Create optimizer
        optimizer = PortfolioOptimizer(ticker_list, period=period)

        # Optimize based on strategy
        if strategy == 'max_sharpe':
            weights, performance = optimizer.optimize_max_sharpe()
        elif strategy == 'min_volatility':
            weights, performance = optimizer.optimize_min_volatility()
        else:
            weights, performance = optimizer.optimize_by_risk_level(strategy)

        # Display weights
        print_success("Optimal Allocation (Weights):")
        weights_data = [[ticker, format_percentage(weight)] for ticker, weight in weights.items() if weight > 0.001]
        print(tabulate(weights_data, headers=['Ticker', 'Weight'], tablefmt='grid'))
        print()

        # Display expected performance
        print_info("Expected Performance:")
        perf_table = [
            ['Expected Annual Return', format_percentage(performance['expected_return'])],
            ['Expected Volatility', format_percentage(performance['volatility'])],
            ['Sharpe Ratio', f"{performance['sharpe_ratio']:.2f}"]
        ]
        print(tabulate(perf_table, tablefmt='grid'))
        print()

        # Discrete allocation
        print_info("Discrete Allocation (Shares to Buy):")
        allocation, leftover = optimizer.get_discrete_allocation(weights, value)

        if allocation:
            prices = optimizer.market_data.get_current_prices()
            allocation_data = []
            for ticker, shares in allocation.items():
                cost = shares * prices[ticker]
                allocation_data.append([ticker, shares, format_currency(prices[ticker]), format_currency(cost)])

            print(tabulate(allocation_data, headers=['Ticker', 'Shares', 'Price', 'Total Cost'], tablefmt='grid'))
            print(f"\nLeftover cash: {format_currency(leftover)}")
        else:
            print_warning("No discrete allocation generated")

        print_success("\nOptimization complete!")

    except Exception as e:
        print_error(f"Optimization failed: {str(e)}")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--current', '-c', required=True, help='Current holdings as JSON (e.g., \'{"AAPL": 10}\')')
@click.option('--strategy', '-s', type=click.Choice(['max_sharpe', 'min_volatility', 'conservative', 'moderate', 'aggressive']),
              default='max_sharpe', help='Target optimization strategy')
@click.option('--period', '-p', default='2y', help='Historical data period')
def rebalance(current, strategy, period):
    """Get rebalancing recommendations for existing portfolio"""
    print_info("=== Portfolio Rebalancing ===\n")

    # Parse current holdings
    try:
        current_holdings = json.loads(current)
    except json.JSONDecodeError:
        print_error("Invalid JSON format for current holdings")
        return

    try:
        # Create current portfolio
        current_portfolio = Portfolio(holdings=current_holdings)
        current_weights = current_portfolio.get_weights()
        current_value = current_portfolio.get_total_value()

        print_info("Current Portfolio:")
        summary_df = current_portfolio.summary()
        print(tabulate(summary_df, headers='keys', tablefmt='grid', floatfmt='.2f'))
        print(f"\nTotal Value: {format_currency(current_value)}\n")

        # Optimize
        tickers = current_portfolio.get_tickers()
        optimizer = PortfolioOptimizer(tickers, period=period)

        if strategy == 'max_sharpe':
            target_weights, performance = optimizer.optimize_max_sharpe()
        elif strategy == 'min_volatility':
            target_weights, performance = optimizer.optimize_min_volatility()
        else:
            target_weights, performance = optimizer.optimize_by_risk_level(strategy)

        print_success("Target Allocation:")
        target_data = [[ticker, format_percentage(weight)] for ticker, weight in target_weights.items() if weight > 0.001]
        print(tabulate(target_data, headers=['Ticker', 'Weight'], tablefmt='grid'))
        print()

        # Calculate rebalancing trades
        print_info("Rebalancing Trades:")
        prices = current_portfolio.get_current_prices()
        trades = []

        for ticker in tickers:
            current_weight = current_weights.get(ticker, 0)
            target_weight = target_weights.get(ticker, 0)
            weight_diff = target_weight - current_weight

            dollar_diff = weight_diff * current_value
            shares_diff = dollar_diff / prices[ticker]

            if abs(shares_diff) > 0.5:  # Only show significant changes
                action = "BUY" if shares_diff > 0 else "SELL"
                trades.append([
                    ticker,
                    format_percentage(current_weight),
                    format_percentage(target_weight),
                    action,
                    f"{abs(int(shares_diff))} shares",
                    format_currency(abs(dollar_diff))
                ])

        if trades:
            print(tabulate(trades, headers=['Ticker', 'Current %', 'Target %', 'Action', 'Quantity', 'Value'], tablefmt='grid'))
        else:
            print_success("Portfolio is already well-balanced!")

        print()
        print_info("Target Performance:")
        perf_table = [
            ['Expected Annual Return', format_percentage(performance['expected_return'])],
            ['Expected Volatility', format_percentage(performance['volatility'])],
            ['Sharpe Ratio', f"{performance['sharpe_ratio']:.2f}"]
        ]
        print(tabulate(perf_table, tablefmt='grid'))

        print_success("\nRebalancing analysis complete!")

    except Exception as e:
        print_error(f"Rebalancing failed: {str(e)}")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--file', '-f', default='assets.json', help='Path to assets JSON file')
@click.option('--tickers', '-t', help='Comma-separated list of tickers')
@click.option('--strategy', '-s', type=click.Choice(['max_sharpe', 'min_volatility', 'conservative', 'moderate', 'aggressive']),
              default='max_sharpe', help='Optimization strategy')
@click.option('--period', '-p', default='5y', help='Backtest period')
@click.option('--rebalance', '-r', default='quarterly', type=click.Choice(['monthly', 'quarterly', 'yearly', 'none']),
              help='Rebalancing frequency')
def backtest(file, tickers, strategy, period, rebalance):
    """Backtest optimized portfolio performance"""
    print_info("=== Portfolio Backtest ===\n")

    # Load tickers
    if tickers:
        ticker_list = [t.strip().upper() for t in tickers.split(',')]
    else:
        ticker_list = load_assets_from_file(file)

    if not ticker_list:
        print_error("No tickers provided")
        return

    print_info(f"Backtesting {strategy} strategy on {len(ticker_list)} assets")
    print_info(f"Period: {period}, Rebalancing: {rebalance}\n")

    try:
        # Get historical data
        market_data = MarketDataFetcher(ticker_list, period=period)
        market_data.fetch_prices()

        # Initial optimization
        optimizer = PortfolioOptimizer(ticker_list, period='2y')

        if strategy == 'max_sharpe':
            weights, _ = optimizer.optimize_max_sharpe()
        elif strategy == 'min_volatility':
            weights, _ = optimizer.optimize_min_volatility()
        else:
            weights, _ = optimizer.optimize_by_risk_level(strategy)

        # Create portfolio and backtest
        portfolio = Portfolio.from_weights(ticker_list, weights, 10000)
        hist_perf = portfolio.calculate_historical_performance()

        # Display results
        print_success("Backtest Results:")
        results_table = [
            ['Total Return', format_percentage(hist_perf['total_return'])],
            ['Annualized Return', format_percentage(hist_perf['annualized_return'])],
            ['Annualized Volatility', format_percentage(hist_perf['annualized_volatility'])],
            ['Maximum Drawdown', format_percentage(hist_perf['max_drawdown'])],
            ['Sharpe Ratio', f"{(hist_perf['annualized_return'] - 0.02) / hist_perf['annualized_volatility']:.2f}"]
        ]
        print(tabulate(results_table, tablefmt='grid'))
        print()

        # Compare with equal weight
        equal_weights = {ticker: 1.0 / len(ticker_list) for ticker in ticker_list}
        equal_portfolio = Portfolio.from_weights(ticker_list, equal_weights, 10000)
        equal_perf = equal_portfolio.calculate_historical_performance()

        print_info("Comparison with Equal-Weight Portfolio:")
        comparison = [
            ['Strategy', 'Total Return', 'Volatility', 'Max Drawdown'],
            [strategy.replace('_', ' ').title(),
             format_percentage(hist_perf['total_return']),
             format_percentage(hist_perf['annualized_volatility']),
             format_percentage(hist_perf['max_drawdown'])],
            ['Equal Weight',
             format_percentage(equal_perf['total_return']),
             format_percentage(equal_perf['annualized_volatility']),
             format_percentage(equal_perf['max_drawdown'])]
        ]
        print(tabulate(comparison, headers='firstrow', tablefmt='grid'))

        print_success("\nBacktest complete!")

    except Exception as e:
        print_error(f"Backtest failed: {str(e)}")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--file', '-f', default='assets.json', help='Path to assets JSON file')
@click.option('--tickers', '-t', help='Comma-separated list of tickers')
def compare(file, tickers):
    """Compare different optimization strategies"""
    print_info("=== Strategy Comparison ===\n")

    # Load tickers
    if tickers:
        ticker_list = [t.strip().upper() for t in tickers.split(',')]
    else:
        ticker_list = load_assets_from_file(file)

    if not ticker_list:
        print_error("No tickers provided")
        return

    print_info(f"Comparing strategies for {len(ticker_list)} assets: {', '.join(ticker_list)}\n")

    try:
        optimizer = PortfolioOptimizer(ticker_list, period='2y')
        comparison_df = optimizer.compare_strategies()

        # Format the dataframe
        comparison_df['expected_return'] = comparison_df['expected_return'].apply(format_percentage)
        comparison_df['volatility'] = comparison_df['volatility'].apply(format_percentage)
        comparison_df['sharpe_ratio'] = comparison_df['sharpe_ratio'].apply(lambda x: f"{x:.2f}")

        print(tabulate(comparison_df, headers=['Strategy', 'Expected Return', 'Volatility', 'Sharpe Ratio'], tablefmt='grid'))

        print_success("\nComparison complete!")

    except Exception as e:
        print_error(f"Comparison failed: {str(e)}")


if __name__ == '__main__':
    cli()
