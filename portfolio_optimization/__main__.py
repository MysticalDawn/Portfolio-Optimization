"""
Entry point for running portfolio optimization.

Usage:
    python -m portfolio_optimization
"""

from portfolio_optimization.algorithms import get_algorithm, list_algorithms
from portfolio_optimization.utils.formatting import print_header


def get_user_input(prompt: str, default: str) -> str:
    """Get user input with a default value."""
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input if user_input else default


def get_int_input(prompt: str, default: int) -> int:
    """Get integer input with validation."""
    while True:
        user_input = input(f"{prompt} [{default}]: ").strip()
        if not user_input:
            return default
        try:
            return int(user_input)
        except ValueError:
            print("  Please enter a valid number.")


def get_float_input(prompt: str, default: float) -> float:
    """Get float input with validation."""
    while True:
        user_input = input(f"{prompt} [{default}]: ").strip()
        if not user_input:
            return default
        try:
            return float(user_input)
        except ValueError:
            print("  Please enter a valid number.")


def select_algorithm() -> str:
    """Let user select an algorithm from available options."""
    available = list_algorithms()

    print("\nAvailable algorithms:")
    for i, name in enumerate(available, 1):
        algo_class = get_algorithm(name)
        print(f"  {i}. {name}: {algo_class.description}")

    while True:
        choice = input(f"\nSelect algorithm (1-{len(available)}) [1]: ").strip()
        if not choice:
            return available[0]
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available):
                return available[idx]
            print(f"  Please enter a number between 1 and {len(available)}.")
        except ValueError:
            print("  Please enter a valid number.")


def main() -> None:
    """Run portfolio optimization with interactive user input."""
    print_header("PORTFOLIO OPTIMIZATION")
    print("Configure your optimization parameters below.")
    print("Press Enter to use default values.\n")

    # Select algorithm
    algorithm_name = select_algorithm()
    algorithm_class = get_algorithm(algorithm_name)

    print(f"\nSelected: {algorithm_class.description}")
    print("-" * 40)

    # Common parameters
    period = get_user_input("Historical data period (e.g., 5y, 10y)", "10y")

    # Algorithm-specific parameters
    portfolios = get_int_input("Number of portfolios on frontier", 10)

    if algorithm_name == "monte_carlo_resampling":
        shrinkage = get_float_input("Shrinkage intensity (0.0 - 1.0)", 0.7)
        simulations = get_int_input("Number of simulations", 500)

        print("\n")
        optimizer = algorithm_class(period=period)
        optimizer.optimize(
            shrinkage_intensity=shrinkage,
            num_simulations=simulations,
            num_portfolios=portfolios,
        )
    else:
        # Mean-variance and other simple algorithms
        print("\n")
        optimizer = algorithm_class(period=period)
        optimizer.optimize(num_portfolios=portfolios)


if __name__ == "__main__":
    main()
