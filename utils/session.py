import streamlit as st
import pandas as pd
from core.data_loader import get_crypto_data
from typing import Any, Callable
from core.strategy_holder import Strategies


def init_session_state() -> None:
    """
    Initialises variables for use in the app
    Adds variables to streamlit session state, if they are not already in there with default values.
    """
    st.title("Crypto Trading Strategy Backtester")
    defaults = {
        "indicators": [],
        "to plot": ["Close"],
        "signals": None,
        "results": None,
        "saved_runs": [],
        "strategy": None,
        "plot": None,
        "saved_equities": {},
        "stock_details": "",
        "df": None,
        "runs_to_plot": [],
        "last_choice": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def update_data(crypto: str, period: str, interval: str) -> None:
    """
    Sets new stock details,
    Removes any indicators,
    Loads new stock data

    Args:
        crypto (str): The cryptocurrency ticker symbol (e.g. "BTC-USD").
        period (str): The data period to fetch (e.g. "365d", "180d").
        interval (str): The data frequency or granularity (e.g. "1d", "1h", "5m").
    """
    # Update current choice
    st.session_state.last_choice = (crypto, period, interval)
    st.session_state.stock_details = f"Crypto: {crypto}, Granularity: {interval}, Time Period: {period}"
    # Remove indicators if we change the choice
    st.session_state.indicators = []
    st.session_state.df = get_crypto_data(crypto, period, interval)



def run_strategy(StrategyClass: type[Strategies] | Any , params: dict, backtest_method: Callable) -> Strategies:
    """
    Instantiate new strategy, generate signals, test and obtain statistics about strategy.
    
    Args:
        StrategyClass (type[Strategies]) type of strategy to instantiate,
        params (dict) parameters to be used by the given strategy
        backtest_method (callable) function to be used to back test the strategy

    Returns:
        strategy - instance of subclass of Strategies, with all the functions aside from save called.
    """
    
    st.session_state.strategy = StrategyClass(params)
    strategy = st.session_state.strategy
    strategy.generate_signals(st.session_state.df)
    strategy.backtest(st.session_state.df, backtest_method)
    strategy.stats = strategy.compute_stats()
    
    return strategy


def hold_results() -> None:
    """
    Displays dataframe of currently saved results
    """
    if st.session_state.saved_runs:
        st.subheader("Saved Runs")
        # Display previous runs
        df_saved = pd.DataFrame(st.session_state.saved_runs)
        st.dataframe(df_saved)
