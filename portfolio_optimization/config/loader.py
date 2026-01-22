"""Asset configuration loader."""

import json
from pathlib import Path


def load_assets() -> list[str]:
    """Load the list of asset tickers from the configuration file."""
    assets_path = Path(__file__).parent / "assets.json"
    with open(assets_path, "r") as f:
        return json.load(f)["assets"]
