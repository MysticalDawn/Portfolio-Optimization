"""
Portfolio optimization algorithms.

Each algorithm implements the BaseOptimizer interface and can be used
interchangeably for portfolio optimization.

Available algorithms:
    - MeanVariance: Classic Markowitz optimization
    - MonteCarloResampling: Resampled efficient frontier with estimation uncertainty
"""

from portfolio_optimization.algorithms.base import BaseOptimizer
from portfolio_optimization.algorithms.mean_variance import MeanVariance
from portfolio_optimization.algorithms.monte_carlo_resampling import MonteCarloResampling

# Registry of available algorithms
ALGORITHMS = {
    "mean_variance": MeanVariance,
    "monte_carlo_resampling": MonteCarloResampling,
}


def get_algorithm(name: str) -> type[BaseOptimizer]:
    """
    Get an algorithm class by name.

    Args:
        name: Algorithm identifier (e.g., "monte_carlo_resampling")

    Returns:
        Algorithm class

    Raises:
        ValueError: If algorithm name is not recognized
    """
    if name not in ALGORITHMS:
        available = ", ".join(ALGORITHMS.keys())
        raise ValueError(f"Unknown algorithm '{name}'. Available: {available}")
    return ALGORITHMS[name]


def list_algorithms() -> list[str]:
    """Return list of available algorithm names."""
    return list(ALGORITHMS.keys())


__all__ = [
    "BaseOptimizer",
    "MeanVariance",
    "MonteCarloResampling",
    "ALGORITHMS",
    "get_algorithm",
    "list_algorithms",
]
