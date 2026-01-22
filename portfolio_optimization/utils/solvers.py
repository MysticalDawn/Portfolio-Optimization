"""Common optimization solvers used across algorithms."""

import numpy as np
import scipy.optimize as optimize


def minimize_variance_portfolio(
    expected_returns: np.ndarray,
    target_return: float,
    covariance_matrix: np.ndarray,
    allow_short: bool = False,
) -> np.ndarray:
    """
    Find the minimum variance portfolio for a given target return.

    Uses quadratic optimization to find weights that minimize portfolio variance
    while achieving the target return.

    Args:
        expected_returns: Expected returns for each asset
        target_return: Target portfolio return to achieve
        covariance_matrix: Covariance matrix of asset returns
        allow_short: If True, allow short selling (negative weights)

    Returns:
        Optimal portfolio weights as numpy array
    """
    num_assets = len(expected_returns)

    def objective(weights: np.ndarray) -> float:
        """Minimize portfolio variance."""
        return float(weights.T @ covariance_matrix @ weights)

    constraints = [
        # Weights must sum to 1
        {"type": "eq", "fun": lambda w: np.sum(w) - 1},
        # Portfolio return must equal target
        {"type": "eq", "fun": lambda w: np.sum(w * expected_returns) - target_return},
    ]

    # Set bounds based on short selling allowance
    if allow_short:
        bounds = tuple((-1, 1) for _ in range(num_assets))
    else:
        bounds = tuple((0, 1) for _ in range(num_assets))

    # Start with equal weights
    initial_weights = np.ones(num_assets) / num_assets

    result = optimize.minimize(
        objective,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    return result.x


def maximize_sharpe_portfolio(
    expected_returns: np.ndarray,
    covariance_matrix: np.ndarray,
    risk_free_rate: float = 0.0,
    allow_short: bool = False,
) -> np.ndarray:
    """
    Find the maximum Sharpe ratio portfolio.

    Args:
        expected_returns: Expected returns for each asset
        covariance_matrix: Covariance matrix of asset returns
        risk_free_rate: Risk-free rate for Sharpe calculation
        allow_short: If True, allow short selling

    Returns:
        Optimal portfolio weights
    """
    num_assets = len(expected_returns)

    def negative_sharpe(weights: np.ndarray) -> float:
        """Negative Sharpe ratio (for minimization)."""
        portfolio_return = np.sum(weights * expected_returns)
        portfolio_volatility = np.sqrt(weights.T @ covariance_matrix @ weights)
        if portfolio_volatility == 0:
            return 0
        return -(portfolio_return - risk_free_rate) / portfolio_volatility

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

    if allow_short:
        bounds = tuple((-1, 1) for _ in range(num_assets))
    else:
        bounds = tuple((0, 1) for _ in range(num_assets))

    initial_weights = np.ones(num_assets) / num_assets

    result = optimize.minimize(
        negative_sharpe,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    return result.x


def minimize_volatility_portfolio(
    covariance_matrix: np.ndarray,
    allow_short: bool = False,
) -> np.ndarray:
    """
    Find the global minimum variance portfolio.

    Args:
        covariance_matrix: Covariance matrix of asset returns
        allow_short: If True, allow short selling

    Returns:
        Optimal portfolio weights
    """
    num_assets = covariance_matrix.shape[0]

    def objective(weights: np.ndarray) -> float:
        return float(weights.T @ covariance_matrix @ weights)

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

    if allow_short:
        bounds = tuple((-1, 1) for _ in range(num_assets))
    else:
        bounds = tuple((0, 1) for _ in range(num_assets))

    initial_weights = np.ones(num_assets) / num_assets

    result = optimize.minimize(
        objective,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    return result.x
