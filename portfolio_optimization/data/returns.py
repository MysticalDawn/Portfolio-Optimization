"""Returns calculation utilities."""

import pandas as pd


def calculate_monthly_returns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly returns from daily price data.

    Args:
        data: DataFrame with 'Close' column containing daily prices

    Returns:
        DataFrame with monthly percentage returns
    """
    monthly_prices = data["Close"].resample("ME").ffill()
    return monthly_prices.pct_change().dropna()


def calculate_yearly_returns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate yearly returns from daily price data.

    Args:
        data: DataFrame with 'Close' column containing daily prices

    Returns:
        DataFrame with yearly percentage returns
    """
    yearly_prices = data["Close"].resample("YE").ffill()
    return yearly_prices.pct_change().dropna()
