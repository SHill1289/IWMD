from pathlib import Path
import sys
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breadthlab.providers import download_market_data
from breadthlab.calculations import calculate_security_features, calculate_daily_breadth, add_benchmark_features
from breadthlab.scoring import add_breadth_score
from breadthlab.storage import replace_table, database_status
from breadthlab.demo import make_demo

st.title("Data Manager")
st.write("Load deterministic demo data or download current-constituent S&P 500 history.")

st.subheader("Database status")
st.json(database_status())

col1, col2 = st.columns(2)
with col1:
    if st.button("Load demo dataset", type="primary"):
        with st.spinner("Building demo data..."):
            prices, constituents, benchmark, features, daily = make_demo()
            for name, frame in [("prices", prices), ("constituents", constituents), ("benchmark", benchmark), ("security_features", features), ("daily_breadth", daily)]:
                replace_table(name, frame)
        st.success("Demo dataset loaded.")

with col2:
    start = st.date_input("Live history start", value="2018-01-01")
    if st.button("Download live S&P 500 data"):
        with st.spinner("Downloading and calculating. This can take several minutes..."):
            result = download_market_data(start=str(start))
            features = calculate_security_features(result.prices)
            daily = calculate_daily_breadth(features)
            daily = add_benchmark_features(daily, result.benchmark)
            daily = add_breadth_score(daily)
            for name, frame in [("prices", result.prices), ("constituents", result.constituents), ("benchmark", result.benchmark), ("security_features", features), ("daily_breadth", daily)]:
                replace_table(name, frame)
        st.success("Live data loaded.")

st.warning("Historical live calculations use today's index membership and therefore contain survivorship bias.")
