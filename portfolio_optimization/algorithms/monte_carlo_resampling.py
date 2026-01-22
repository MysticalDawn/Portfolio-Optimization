"""Monte Carlo Resampling portfolio optimization algorithm."""

import numpy as np

from portfolio_optimization.algorithms.base import BaseOptimizer, OptimizationResult
from portfolio_optimization.utils.solvers import minimize_variance_portfolio
from portfolio_optimization.utils.formatting import (
    print_header,
    print_subheader,
    print_key_value,
    print_results,
)


class MonteCarloResampling(BaseOptimizer):
    """
    Monte Carlo Resampling portfolio optimizer.

    This implements the resampled efficient frontier approach by Michaud (1998),
    which accounts for estimation uncertainty in expected returns and covariances.

    The algorithm:
    1. Estimate expected returns with shrinkage toward a conservative target
    2. Compute estimation uncertainty from historical data
    3. Run Monte Carlo simulations sampling from the return distribution
    4. For each simulation, compute optimal portfolios across target returns
    5. Average weights across simulations for robust estimates
    """

    name = "monte_carlo_resampling"
    description = "Resampled Efficient Frontier with estimation uncertainty"

    def optimize(
        self,
        shrinkage_intensity: float = 0.7,
        num_simulations: int = 500,
        num_portfolios: int = 10,
        verbose: bool = True,
    ) -> OptimizationResult:
        """
        Run Monte Carlo resampling optimization.

        Args:
            shrinkage_intensity: Weight for shrinkage target vs sample mean (0-1).
                Higher values pull expected returns toward a more conservative estimate.
            num_simulations: Number of Monte Carlo simulations to run
            num_portfolios: Number of portfolios on the efficient frontier
            verbose: If True, print progress information

        Returns:
            OptimizationResult with averaged weights across simulations
        """
        self._ensure_data_loaded()

        # =====================================================================
        # EXPECTED RETURNS ESTIMATION (SHRINKAGE)
        # =====================================================================
        mean_sample = np.mean(self.yearly_returns, axis=1)
        mean_target = np.divide(mean_sample, 2.2)

        mean_shrunk = (
            shrinkage_intensity * mean_target + (1 - shrinkage_intensity) * mean_sample
        ).squeeze()

        # =====================================================================
        # ESTIMATION UNCERTAINTY
        # =====================================================================
        yearly_returns_array = np.array(
            [df.values.flatten() for df in self.yearly_returns]
        )
        num_periods = yearly_returns_array.shape[1]
        estimation_uncertainty = self.covariance_matrix / num_periods

        # =====================================================================
        # TARGET RETURNS (EFFICIENT FRONTIER)
        # =====================================================================
        min_return = float(np.min(mean_shrunk))
        max_return = float(np.max(mean_shrunk))
        target_returns = np.linspace(min_return, max_return, num_portfolios)

        # =====================================================================
        # MONTE CARLO SIMULATION
        # =====================================================================
        weight_storage = np.zeros(
            (num_simulations, num_portfolios, len(self.tickers))
        )

        if verbose:
            print_header("MONTE CARLO RESAMPLING OPTIMIZATION")
            print_key_value("Algorithm", self.description)
            print_key_value("Assets", ", ".join(self.tickers))
            print_key_value("Period", self.period)
            print_key_value("Shrinkage Intensity", f"{shrinkage_intensity:.1%}")
            print_key_value("Simulations", num_simulations)
            print_key_value("Frontier Points", num_portfolios)
            print_subheader("Running Simulations")

        for i in range(num_simulations):
            # Sample expected returns from uncertainty distribution
            sampled_returns = np.random.multivariate_normal(
                mean_shrunk, estimation_uncertainty
            )

            # Optimize for each target return level
            for k, target_return in enumerate(target_returns):
                optimal_weights = minimize_variance_portfolio(
                    sampled_returns, target_return, self.covariance_matrix
                )
                weight_storage[i, k, :] = optimal_weights

            # Progress indicator
            if verbose and ((i + 1) % 100 == 0 or i == num_simulations - 1):
                print(f"  Progress: {i + 1:>5} / {num_simulations} simulations")

        # =====================================================================
        # AGGREGATE RESULTS
        # =====================================================================
        average_weights = np.mean(weight_storage, axis=0)

        # Calculate volatilities for each portfolio
        volatilities = np.array([
            self.calculate_portfolio_volatility(average_weights[i])
            for i in range(num_portfolios)
        ])

        result = OptimizationResult(
            weights=average_weights,
            expected_returns=target_returns,
            volatilities=volatilities,
            tickers=self.tickers,
            covariance_matrix=self.covariance_matrix,
            algorithm_name=self.name,
            metadata={
                "shrinkage_intensity": shrinkage_intensity,
                "num_simulations": num_simulations,
                "mean_shrunk": mean_shrunk,
                "estimation_uncertainty": estimation_uncertainty,
            },
        )

        if verbose:
            print_results(result)
            print_header("OPTIMIZATION COMPLETE")

        return result
