
import streamlit as st
import pandas as pd
from core.data_loader import get_crypto_data
from typing import Any, Callable
from core.strategy_holder import Strategies, strategy_classes
from core.graphsandstats import compare_strategy_inputs, compare_strategy_results, get_current_ratio
from utils.results import preliminary_save

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
        "last_choice": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def update_data(crypto: str, period: str, interval: str, specific_location=False) -> None | str:
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
    if specific_location:
        data_name = f"{crypto}_{interval}_{period}"
        st.session_state[data_name] = get_crypto_data(crypto, period, interval)
        return data_name

    else:
        st.session_state.df = get_crypto_data(crypto, period, interval)
        
    

    

def run_strategy(StrategyClass: type[Strategies] | Any , params: dict, backtest_method: Callable, data, data_location, equities_location) -> Strategies:
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
    strategy.generate_signals(data)
    strategy.backtest(data, backtest_method)
    strategy.stats = strategy.compute_stats()
    preliminary_save(data_location, equities_location)
    return strategy


def hold_results(data_location) -> None:
    """
    Displays dataframe of currently saved results
    """
    if data_location:
        st.subheader("Saved Runs")
        # Display previous runs
        df_saved = pd.DataFrame(data_location)
        st.dataframe(df_saved)


def compare_strategies():

    if len(st.session_state.saved_runs) == 0:
        return
    strategy_names = [
        f"{i+1}: {r['Strategy']}" for i, r in enumerate(st.session_state.saved_runs)
    ]
    st.subheader("Compare Two Strategies")

    # Get selectboxes for choosing strategies to compare
    col1, col2 = st.columns(2)
    choice1 = col1.selectbox("Select First Strategy", strategy_names)
    choice2 = col2.selectbox("Select Second Strategy", strategy_names)

    strategy1 = st.session_state.saved_runs[strategy_names.index(choice1)]
    strategy2 = st.session_state.saved_runs[strategy_names.index(choice2)]

    parameters = strategy_classes[strategy1['Strategy']].param_config.copy()
    del parameters["cost_per_trade"]

    if st.button("Compare Strategies"):
        # Calculate the distance between strategy parameters
        inputs_metric = compare_strategy_inputs(strategy1, strategy2, parameters)
        results_metric = compare_strategy_results(strategy1, strategy2, parameters)
        current_ratio = get_current_ratio(inputs_metric, results_metric)
        if inputs_metric == float("inf"):
            st.error("The strategies are either using different data or of different class.")
        else:
            st.write(f"Distance metric between strategies: **{inputs_metric:.3f}**")
            st.write(f"Change in profit between strategies: **{results_metric:.3f}**")
            st.write(f"Gives a ratio of: **{current_ratio}**")


def test_stability():
    if len(st.session_state.saved_runs) == 0:
        return
    strategy_names = [
        f"{i+1}: {r['Strategy']}" for i, r in enumerate(st.session_state.saved_runs)
    ]
    st.subheader("Test Strategy Stability")

    choice = st.selectbox("Choose Strategy", strategy_names) # Choice is just a number
    main_strategy = st.session_state.saved_runs[strategy_names.index(choice)] # This is now the dictionary of the strategy

    parameters = strategy_classes[main_strategy["Strategy"]].param_config.copy()
    del parameters["cost_per_trade"]

    ratios = []
    if st.button("Test Stability"):
    # Compare it to other strategies by cycling through st.session_state.saved_runs
        for current_run in st.session_state.saved_runs:
            # Get the parameters to use
            inputs_metric = compare_strategy_inputs(main_strategy, current_run, parameters)
            results_metric = compare_strategy_results(main_strategy, current_run, parameters)
            current_ratio = get_current_ratio(inputs_metric, results_metric)
            ratios.append(current_ratio)
        
        
        lipschitz_estimate = max(ratios)
        st.write(f"Estimate for Lipschitz Constant: {lipschitz_estimate}")


def init_optimiser_session_state() -> None:
    """
    Initialises variables for use in the app
    Adds variables to streamlit session state, if they are not already in there with default values.
    """
    st.title("Strategy Optimiser")
    defaults = {
        "strategy_name": None,
        "random_runs": {},
        "name": None,
        "stock_details": "",
        "current_results": "",
        "current_equities": "",
        "current_optimiser_results": pd.DataFrame()
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value