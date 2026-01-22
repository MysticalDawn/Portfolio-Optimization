"""
Portfolio Optimization Package

A flexible framework for portfolio optimization supporting multiple algorithms.

Usage:
    from portfolio_optimization.algorithms import MonteCarloResampling

    optimizer = MonteCarloResampling(period="10y")
    result = optimizer.optimize(num_simulations=500)

Available algorithms:
    - MonteCarloResampling: Resampled efficient frontier
    - (More coming: MeanVariance, BlackLitterman, RiskParity, etc.)
"""

__version__ = "1.0.0"

from portfolio_optimization.algorithms import (
    BaseOptimizer,
    MeanVariance,
    MonteCarloResampling,
    get_algorithm,
    list_algorithms,
)

__all__ = [
    "BaseOptimizer",
    "MeanVariance",
    "MonteCarloResampling",
    "get_algorithm",
    "list_algorithms",
]
