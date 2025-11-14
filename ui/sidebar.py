import streamlit as st
from core.data_loader import get_crypto_data
from core.indicators import fetch_indicator
from core.strategy_holder import SimpleMeanReversion, BasicMomentum, BasicRSI, Bollinger
from utils.session import update_data
from utils.results import clear_all_saved_runs
from typing import Any



interval_map = {
    "Daily": "1d",
    "Hourly": "1h",
    "5 Minutes": "5m"
}
period_map = {
    "One Year": "365d",
    "Six Months": "180d",
    "One Month": "30d"
}
crypto_map = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD",
    "Apple": "AAPL"
}

strategy_classes = {
    "Simple Mean Reversion": SimpleMeanReversion,
    "Moving Average Crossover": BasicMomentum,
    "Simple RSI": BasicRSI,
    "Bollinger": Bollinger
}

def data_select_box(key):
    crypto = st.selectbox("Select crypto", list(crypto_map.keys()), key="crypto" + key)
    period = st.selectbox("Period", list(period_map.keys()), key="period" + key)
    interval = st.selectbox("Granularity", list(interval_map.keys()), key="interval" + key)
    return crypto_map[crypto], period_map[period], interval_map[interval]


def select_data(specific_location=False) -> None | str:
    """
    Displays sidebar controls for selecting the cryptocurrency, period, and data granularity,
    and loads new market data when the user clicks the 'Get Data' button.
    
    When button pressed, it calls update_data which manages the currently loaded stock variables.

    Returns:
        None
    """
    with st.sidebar.expander("Select Data"):
        crypto, period, interval = data_select_box(key="main page selection")
        
        if st.sidebar.button("Get Data"):
            data_name = update_data(crypto, period, interval, specific_location)
            st.session_state["name"] = data_name

    st.write(st.session_state.stock_details)
        
            


def select_indicator() -> None:
    """
    Displays sidebar controls for selecting a new indicator, 
    allows the user to choose indicator type and the length of the indicator

    adds indicators to the session state and adds columns to the dataframe using fetch_indicator
    Returns:
        None
    """
    indicator_type = st.sidebar.selectbox("Choose Indicator", ["SMA", "EMA", "RSI"])
    window_size = st.sidebar.number_input("Window Size", value=20, step=1)
    new_indicator = (indicator_type, window_size)
    if indicator_type is not None and window_size is not None:
        if st.sidebar.button("Add Indicator"):
            if new_indicator not in st.session_state.indicators:
                st.session_state.indicators.append(new_indicator)
    if st.session_state.stock_details is not None:
        for indicator in st.session_state.indicators: # indicator = (indicator type, window size)
            st.session_state.df = fetch_indicator(st.session_state.df, indicator)
    


def remove_indicator() -> None:
    """
    Displays sidebar controls for removing a given indicator,
    The indicator is removed from the session state and therefore it is removed from the plot, 
    however, the indicator remains as a column in df to avoid unnecessary recalculations

    Returns:
        None
    """
    if st.session_state.indicators:
        indicator_to_remove = st.sidebar.selectbox(
            "Remove Indicator",
            st.session_state.indicators,
            key="remove_sma_select"
        )
        if st.sidebar.button("Remove Selected indicator"):
            if indicator_to_remove != "Select indicator to remove":
                st.session_state.indicators.remove(indicator_to_remove)
                st.rerun()
    else:
        st.write("No added indicators")

    


def select_strategy() -> tuple[type | Any, dict[str, Any]]:
    """
    Displays sidebar controls for selecting a new strategy,
    When a strategy is selected it provides options for adding in the required indicators to test the strategy
    Returns:
        None
        """
    st.sidebar.header("Choose Strategy")
    strategy_type = st.sidebar.selectbox("Strategy", ["None"] + list(strategy_classes.keys()))
    
    StrategyClass = None
    params: dict = {}

    if strategy_type == "None":
        return StrategyClass, params

    StrategyClass = strategy_classes[strategy_type]
    
    for key, cfg in StrategyClass.param_config.items():
        if cfg["type"] == "indicator":
            if st.session_state.indicators:
                params[key] = st.sidebar.selectbox(cfg["label"], st.session_state.indicators)
            else:
                st.sidebar.warning("Add indicators first")
        elif cfg["type"] == "float":
            params[key] = st.sidebar.number_input(cfg["label"], value=cfg["value"], step=cfg["step"], format="%.2f")

    return StrategyClass, params


def test_strategy_button() -> bool:
    """Return True when the 'Test Strategy' button is pressed."""
    return st.sidebar.button("Test Strategy")




def permanently_delete():
    st.sidebar.divider()
    st.sidebar.subheader("Permanently Delete Stored Runs")
    clear_all_saved_runs()