from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from breadthlab.providers import download_market_data
from breadthlab.calculations import (
    calculate_security_features,
    calculate_daily_breadth,
    add_benchmark_features,
)
from breadthlab.scoring import add_breadth_score
from breadthlab.storage import replace_table


START_DATE = "2018-01-01"


def refresh_market_data():
    print("IWMD daily market data refresh")
    print(f"Downloading market history from {START_DATE}...")

    result = download_market_data(start=START_DATE)

    print("Calculating security-level breadth features...")
    features = calculate_security_features(result.prices)

    print("Calculating daily market breadth...")
    daily = calculate_daily_breadth(features)

    print("Adding benchmark features...")
    daily = add_benchmark_features(daily, result.benchmark)

    print("Calculating Breadth Score...")
    daily = add_breadth_score(daily)

    tables = {
        "prices": result.prices,
        "constituents": result.constituents,
        "benchmark": result.benchmark,
        "security_features": features,
        "daily_breadth": daily,
    }

    for name, frame in tables.items():
        print(f"Saving {name}...")
        replace_table(name, frame)

    print("Market database refreshed successfully.")

    return tables


def export_parquet(tables):
    parquet_dir = ROOT / "data" / "parquet"
    parquet_dir.mkdir(parents=True, exist_ok=True)

    for name, frame in tables.items():
        output = parquet_dir / f"{name}.parquet"

        print(f"Exporting {name} -> {output}")

        frame.to_parquet(
            output,
            index=False,
        )

    print("Parquet dataset refreshed successfully.")


if __name__ == "__main__":
    tables = refresh_market_data()
    export_parquet(tables)

    latest_date = tables["daily_breadth"]["date"].max()

    print(f"IWMD refresh complete. Latest market date: {latest_date}")