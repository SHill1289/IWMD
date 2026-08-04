import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
from breadthlab.calculations import calculate_security_features, calculate_daily_breadth


def test_advances_declines():
    prices = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"]),
        "symbol": ["A", "A", "B", "B"],
        "close": [10, 11, 10, 9],
    })
    features = calculate_security_features(prices)
    daily = calculate_daily_breadth(features)
    row = daily.loc[daily.date == pd.Timestamp("2024-01-02")].iloc[0]
    assert row.advances == 1
    assert row.declines == 1
    assert row.ad_net == 0
