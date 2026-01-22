"""Classic Mean-Variance (Markowitz) portfolio optimization."""

import numpy as np

from portfolio_optimization.algorithms.base import BaseOptimizer, OptimizationResult
from portfolio_optimization.utils.solvers import minimize_variance_portfolio
from portfolio_optimization.utils.formatting import (
    print_header,
    print_subheader,
    print_key_value,
    print_results,
)


class MeanVariance(BaseOptimizer):
    """
    Classic Mean-Variance (Markowitz) portfolio optimizer.

    The foundational approach to portfolio optimization introduced by
    Harry Markowitz in 1952. Finds portfolios that maximize expected
    return for a given level of risk (or minimize risk for a given return).

    The algorithm:
    1. Calculate expected returns from historical annual returns
    2. Calculate covariance matrix from historical data
    3. For each target return, find the minimum variance portfolio
    4. Return the efficient frontier
    """

    name = "mean_variance"
    description = "Classic Markowitz Mean-Variance optimization"

    def optimize(
        self,
        num_portfolios: int = 10,
        verbose: bool = True,
    ) -> OptimizationResult:
        """
        Run Mean-Variance optimization.

        Args:
            num_portfolios: Number of portfolios on the efficient frontier
            verbose: If True, print progress information

        Returns:
            OptimizationResult with optimal weights for each target return
        """
        self._ensure_data_loaded()

        # =====================================================================
        # EXPECTED RETURNS (simple historical average)
        # =====================================================================
        expected_returns = np.array([
            df.values.mean() for df in self.yearly_returns
        ])

        # =====================================================================
        # TARGET RETURNS (EFFICIENT FRONTIER)
        # =====================================================================
        min_return = float(np.min(expected_returns))
        max_return = float(np.max(expected_returns))
        target_returns = np.linspace(min_return, max_return, num_portfolios)

        # =====================================================================
        # OPTIMIZATION
        # =====================================================================
        weights = np.zeros((num_portfolios, len(self.tickers)))

        if verbose:
            print_header("MEAN-VARIANCE OPTIMIZATION")
            print_key_value("Algorithm", self.description)
            print_key_value("Assets", ", ".join(self.tickers))
            print_key_value("Period", self.period)
            print_key_value("Frontier Points", num_portfolios)
            print_subheader("Computing Efficient Frontier")

        for i, target_return in enumerate(target_returns):
            optimal_weights = minimize_variance_portfolio(
                expected_returns, target_return, self.covariance_matrix
            )
            weights[i] = optimal_weights

            if verbose:
                print(f"  Portfolio {i + 1}/{num_portfolios}: target return = {target_return:.2%}")

        # =====================================================================
        # CALCULATE VOLATILITIES
        # =====================================================================
        volatilities = np.array([
            self.calculate_portfolio_volatility(weights[i])
            for i in range(num_portfolios)
        ])

        result = OptimizationResult(
            weights=weights,
            expected_returns=target_returns,
            volatilities=volatilities,
            tickers=self.tickers,
            covariance_matrix=self.covariance_matrix,
            algorithm_name=self.name,
            metadata={
                "historical_returns": expected_returns,
            },
        )

        if verbose:
            print_results(result)
            print_header("OPTIMIZATION COMPLETE")

        return result
