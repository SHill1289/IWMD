import streamlit as st

st.set_page_config(
    page_title="IWMD | Market Breadth Research",
    page_icon="📈",
    layout="wide",
)

st.logo(
    "assets/iwmd_logo.png",
    size="large",
)

st.image(
    "assets/iwmd_logo.png",
    width=360,
)

st.markdown(
    '<div class="iwmd-subtitle">Market Breadth Research & Market Internals</div>',
    unsafe_allow_html=True,
)

st.write(
    "A research platform for monitoring market participation, breadth, "
    "leadership, regime changes, and historical market behavior."
)

st.info(
    "Start with the Dashboard for the current market-internals picture, "
    "then use Historical Analogs and Rule Backtest for deeper research."
)